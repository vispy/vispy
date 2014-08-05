# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division


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
    def __init__(self, **objects):
        # cache of compilation results for each function and variable
        self._object_names = {}  # {object: name}
        self._object_code = {}   # {object: code}
        #self.namespace = None    # {name: object}
        self.objects = objects

    def __getitem__(self, item):
        """
        Return the name of the specified object, if it has been assigned one.        
        """
        return self._object_names[item]

    def compile(self):
        """ Compile all code and return a dict {name: code} where the keys 
        are determined by the keyword arguments passed to __init__().
        """
        # Walk over all dependencies, assign a unique name to each.
        # Names are only changed if there is a conflict.
        all_deps = {}
        
        for obj_name, obj in self.objects.items():
            
            # Collect all dependencies by name, also pop duplicates
            unique_deps = []
            deps_by_name = {}
            for dep in obj.dependencies(sort=True):
                # Ensure we handle each dependency just once
                if dep in unique_deps:
                    continue
                unique_deps.append(dep)
                # Put this name in the right box
                if dep.name is None or dep in self._object_names:
                    continue
                deps_with_this_name = deps_by_name.setdefault(dep.name, [])
                deps_with_this_name.append(dep)
            
            # Rename these dependencies that need a new name
            for name, deps_with_this_name in deps_by_name.items():
                if len(deps_with_this_name) == 1:
                    dep = deps_with_this_name[0]
                    #namespace[name] = dep
                    self._object_names[dep] = name
                else:
                    for i, dep in enumerate(deps_with_this_name):
                        newname = name + '_%i' % (i+1)
                        #namespace[newname] = dep
                        self._object_names[dep] = newname
            
            all_deps[obj] = unique_deps
        
        # Now we have a complete namespace; concatenate all definitions
        # together in topological order.
        compiled = {}
        
        for name, obj in self.objects.items():
            code = ['// Generated code by function composition', 
                    '#version 120', '']
            for dep in all_deps[obj]:
                dep_code = dep.definition(self._object_names)
                if dep_code is not None:
                    code.append(dep_code)
                
            compiled[name] = '\n'.join(code)
            
        self.code = compiled
        return compiled
