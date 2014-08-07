# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import re

from ... import gloo


class Compiler(object):
    """
    Compiler is used to convert Function and Variable instances into 
    ready-to-use GLSL code. This class handles name mangling to ensure that
    there are no name collisions amongst global objects. The final name of
    each object may be retrieved using ``Compiler.__getitem__(obj)``.
    
    Accepts multiple root Functions as keyword arguments. ``compile()`` then
    returns a dict of GLSL strings with the same keys.
    
    Example::
    
        # initialize with two main functions
        compiler = Compiler(vert=v_func, frag=f_func)
        
        # compile and extract shaders
        code = compiler.compile()
        v_code = code['vert']
        f_code = code['frag']
        
        # look up name of some object
        name = compiler[obj]
    
    """
    def __init__(self, **shaders):
        # cache of compilation results for each function and variable
        self._object_names = {}  # {object: name}
        self.shaders = shaders

    def __getitem__(self, item):
        """
        Return the name of the specified object, if it has been assigned one.        
        """
        return self._object_names[item]

    def compile(self):
        """ Compile all code and return a dict {name: code} where the keys 
        are determined by the keyword arguments passed to __init__().
        """
        
        #
        #  First: assign names to all objects to avoid collisions
        #
        
        # Authoritative mapping of {obj: name}
        self._object_names = {}
        
        # {name: obj} mapping for finding unique names
        # initialize with reserved keywords.
        namespace = dict([(kwd, None) for kwd in gloo.util.KEYWORDS])
        
        # maps {shader_name: [deps]}
        shader_deps = {}
        
        # groups together objects that all ask for the same name.
        # maps {requested_name, [objects]}
        requested_names = {}
        
        for shader_name, shader in self.shaders.items():
            this_shader_deps = []
            shader_deps[shader_name] = this_shader_deps
            dep_set = set()
            
            for dep in shader.dependencies(sort=True):
                # visit each object no more than once per shader
                if dep.name is None or dep in dep_set:
                    continue
                this_shader_deps.append(dep)
                dep_set.add(dep)
                
                # Add static names to namespace
                for name in dep.static_names():
                    namespace[name] = None
                
                # group together objects by name
                requested_names.setdefault(dep.name, []).append(dep)
                
            
        #
        # Assign names for all objects that do not need to be renamed
        #
        conflicts = []
        for name, deps in requested_names.items():
            if len(deps) == 1 and name not in namespace:
                # hooray, we get to keep this name.
                dep = deps[0]
                namespace[name] = dep
                self._object_names[dep] = name
            else:
                conflicts.append(name)

        #
        # Rename all objects with name conflicts
        #
        name_index = {}
        for name in conflicts:
            objs = requested_names[name]
            while len(objs) > 0:
                index = name_index.get(name, 0) + 1
                name_index[name] = index
                new_name = name + '_%d' % index
                if new_name not in namespace:
                    obj = objs.pop()
                    namespace[name] = obj
                    self._object_names[obj] = name
        
        #
        # Now we have a complete namespace; concatenate all definitions
        # together in topological order.
        #
        compiled = {}
        obj_names = self._object_names
        
        for shader_name, shader in self.shaders.items():
            code = ['// Generated code by function composition', 
                    '#version 120', '']
            for dep in shader_deps[shader_name]:
                dep_code = dep.definition(obj_names)
                if dep_code is not None:
                    # strip out version pragma if present; check requested version
                    regex = r'#version (\d+)'
                    m = re.search(regex, dep_code)
                    if m is not None:
                        if m.group(1) != '120':
                            raise RuntimeError("Currently only GLSL #version "
                                               "120 is supported.")
                        dep_code = re.sub(regex, '', dep_code)
                    code.append(dep_code)
                
            compiled[shader_name] = '\n'.join(code)
            
        self.code = compiled
        return compiled
