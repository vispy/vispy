# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division
import re

class Compiler(object):
    """
    Compiler is used to convert Function and Variable instances into 
    ready-to-use GLSL code. This class selects names for all anonymous objects
    to avoid name collisions, and caches these names to speed up recompilation.
    
    Summary of procedure:
    1. For each object to be compiled, the hierarchy of its dependencies is
       collected.
    2. Objects with fixed names are added to the namespace
    3. Objecs with cached names are added to the namespace, unless the cached
       name conflicts with another object in the namespace.
    4. New names are assigned to all anonymous objects.
    5. All objects are compiled and code is concatenated into a single string.
    
    """
    def __init__(self, **objects):
        # cache of compilation results for each function and variable
        self._object_names = {}  # {object: name}
        self._object_code = {}   # {object: code}
        self.namespace = None    # {name: object}
        self.objects = objects

        # Garbage collection system: keep track of all objects (functions and
        # variables) included in the program and their referrers. When no
        # referrers are found, remove the object from here and from
        # the namespaces / caches.
        # TODO: Not implemented yet..
        self._referrers = {}  # {obj: [list of referrers]}

    def __getitem__(self, item):
        """
        Return the name of the specified object, if it has been assigned one.        
        """
        return self._object_names[item]

    def compile(self):
        """
        
        objects   Structure describing shaders and objects to be compiled.
                  {'shader_name': {object: name, ...}, ...}
        names     Dict of pre-existing names to avoid.
        prefix    String prefix to use when selecting object names.
        """
        
        # map of {name: object} for this compilation
        self.namespace = namespace = {}

        # Walk over all dependencies, assign a unique name to each.
        # Names are only changed if there is a conflict.
        named_objects = []  # objects with names; may need to be renamed
        all_deps = {}
        
        for obj_name, obj in self.objects.items():
            # record all dependencies of this object in topological order
            deps = obj.dependencies()
            all_deps[obj] = deps
            for dep in deps:
                if dep.name is None:
                    continue

                name = self._suggest_name(dep.name)
                namespace[name] = dep
                self._object_names[dep] = name

        # Now we have a complete namespace; concatenate all declarations
        # together in topological order.
        compiled = {}
        
        for name, obj in self.objects.items():
            code = []
            declared = set()
            for dep in all_deps[obj]:
                if dep in declared:
                    continue
                
                dep_code = dep.declaration(self._object_names)
                if dep_code is not None:
                    code.append(dep_code)
                
                declared.add(dep)
            
            compiled[name] = '\n\n'.join(code)
            
        return compiled

    def _suggest_name(self, name):
        """
        Suggest a name similar to *name* that does not exist in *ns*.
        """
        if name == 'main':  # do not rename main functions
            return name
        ns = self.namespace
        if name in ns:
            m = re.match(r'(.*)_(\d+)', name)
            if m is None:
                base_name = name
                index = 1
            else:
                base_name, index = m.groups()
            while True:
                name = base_name + '_' + str(index)
                if name not in ns:
                    break
                index += 1
        return name

