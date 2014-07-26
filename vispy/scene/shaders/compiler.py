# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division, print_function


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
    def __init__(self):
        # cache of compilation results for each function and variable
        self._object_names = {}  # {object: name}
        self._object_code = {}   # {object: code}
        self.namespace = None    # {name: object} (only valid for one compile)

        # Garbage collection system: keep track of all objects (functions and
        # variables) included in the program and their referrers. When no
        # referrers are found, remove the object from here and from
        # the namespaces / caches.
        # TODO: Not implemented yet..
        self._referrers = {}  # {obj: [list of referrers]}

    
    def clear(self):
        """
        Clear the cached namespace.        
        """
    
    def __getitem__(self, item):
        """
        Return the name of the specified object, if it has been assigned one.        
        """
    
    def compile(objects, prefix=None):
        """
        
        objects   Structure describing shaders and objects to be compiled.
                  {'shader_name': {object: name, ...}, ...}
        names     Dict of pre-existing names to avoid.
        prefix    String prefix to use when selecting object names.
        """
        
        # list of all ShaderObjects
        all_objs = []

        # map of {name: object} for this compilation
        self.namespace = namespace = {}

        ## 1) Walk over all hook definitions and collect a list of their object
        ## dependencies
        #for hook_name, func in self._hook_defs.items():
            #self._check_hook(hook_name)
            #shader, hook_args, hook_rtype = self._hooks[hook_name]

            ## insert a hook comment
            #header = "\n//------- Begin hook %s -------\n\n" % hook_name
            #objects[shader].append(header)

        for shader, objs in objects.items():
            new_objects = []
            for obj in objs:
                if isinstance(obj, str):
                    new_objects.append(obj)
                    continue
                
                # Todo: allow unnamed objects here?
                obj, name = obj
                
                # record all dependencies of this hook in topological order
                deps = self._object_dependencies(obj)
                new_objects.extend(deps)

                # collect dependencies, but exclude the hook itself because it
                # has a required name.
                all_objs.extend(deps[:-1])

                ## add hook to namespace
                if name in namespace:
                    raise Exception('Cannot assign %s to name %s; this name is'
                                    'already in use by %s.' %
                                    (obj, name, namespace[name]))
                self._set_object_name(obj, name)
            
            # rewrite list of objects for this shader to include all 
            # dependencies.
            objects[shader] = new_objects

        # 2) Add objects with fixed names to the namespace
        anon = []  # keep track of all anonymous objects
        for obj in all_objs:
            if obj.is_anonymous:
                anon.append(obj)
            else:
                if obj.name in namespace and namespace[obj.name] is not obj:
                    raise Exception("Name collision: %s requires name %s, "
                                    "but this name is in use by %s." %
                                    (obj, obj.name, namespace[obj.name]))
                namespace[obj.name] = obj
                self._object_names[obj] = obj.name

        # 3) Next, objects with cached names are added. If there are conflicts
        #    at this stage, we simply forget the cached name.
        unnamed = []  # keep track of everything else that still needs a name

        for obj in anon:
            name = self._object_names.get(obj, None)
            if name is None:
                unnamed.append(obj)
            else:
                if name in namespace:
                    if namespace[name] is not obj:
                        unnamed.append(obj)
                        del self._object_names[obj]
                else:
                    namespace[name] = obj

        # 4) Finally, all unnamed objects are assigned names. For each object,
        #    we must clear the code caches of its referrers.
        for obj in unnamed:
            name = self._suggest_name(namespace, obj.name)
            self._set_object_name(obj, name)

        # 5) Now we have a complete namespace; compile all objects that lack
        #    a code cache and assemble a list of code strings for each shader.
        shader_code = {'vertex': [self.vmain], 'fragment': [self.fmain]}
        for shader, obj_list in objects.items():
            code = shader_code[shader]
            names = set()
            for obj in obj_list:
                if isinstance(obj, string_types):
                    code.append(obj)
                else:
                    name = self._object_names[obj]
                    if name in names:
                        # already added to this shader; avoid duplicates
                        continue
                    obj_code = self._object_code.get(obj, None)
                    if obj_code is None:
                        obj_code = obj.compile(self._object_names)
                        self._object_code[obj] = obj_code
                    code.append(obj_code)
                    names.add(name)

        logger.debug('==================== VERTEX SHADER ====================')
        logger.debug(self.vert_code)
        logger.debug('=================== FRAGMENT SHADER ===================')
        logger.debug(self.frag_code)
        logger.debug('====================== NAMESPACE ======================')
        logger.debug(self.namespace)
        
        return shader_code

    def _function_dependencies(self, obj):
        objs = []
        for dep in obj.dependencies:
            objs.extend(self._function_dependencies(dep))
        objs.append(obj)
        return objs

    def _set_object_name(self, obj, name):
        self.namespace[name] = obj
        old_name = self._object_names.get(obj, None)
        self._object_names[obj] = name
        if old_name != name:
            # name has changed; must recompile this object
            # and everything that refers to it.
            self._object_code.pop(obj, None)
            for ref in self._referrers.get(obj, ()):
                self._object_code.pop(ref, None)

    def _suggest_name(self, ns, name):
        """
        Suggest a name similar to *name* that does not exist in *ns*.
        """
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

    def forget_object(self, obj):
        # Remove obj from namespaces, forget any cached information about it,
        # remove from referrer lists
        self._object_names.pop(obj, None)
        self._object_code.pop(obj, None)
        self._referrers.pop(obj, None)
        for dep in obj.dependencies:
            referrers = self._referrers.get(dep, None)
            if referrers is None:
                continue
            referrers.remove(obj)
            if len(referrers) == 0:
                self._forget_object(dep)

