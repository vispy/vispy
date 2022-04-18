# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division
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

    def __init__(self, namespace=None, **shaders):
        # cache of compilation results for each function and variable
        if namespace is None:
            namespace = {}
        self._object_names = namespace  # {object: name}
        self.shaders = shaders

    def __getitem__(self, item):
        """Return the name of the specified object, if it has been assigned one."""
        return self._object_names[item]

    def compile(self, pretty=True):
        """Compile all code and return a dict {name: code} where the keys
        are determined by the keyword arguments passed to __init__().

        Parameters
        ----------
        pretty : bool
            If True, use a slower method to mangle object names. This produces
            GLSL that is more readable.
            If False, then the output is mostly unreadable GLSL, but is about
            10x faster to compile.
        """
        # Authoritative mapping of {obj: name}
        self._object_names = {}

        #
        # 1. collect list of dependencies for each shader
        #

        # maps {shader_name: [deps]}
        self._shader_deps = {}

        for shader_name, shader in self.shaders.items():
            this_shader_deps = []
            self._shader_deps[shader_name] = this_shader_deps
            dep_set = set()

            for dep in shader.dependencies(sort=True):
                # visit each object no more than once per shader
                if dep.name is None or dep in dep_set:
                    continue
                this_shader_deps.append(dep)
                dep_set.add(dep)

        #
        # 2. Assign names to all objects.
        #
        if pretty:
            self._rename_objects_pretty()
        else:
            self._rename_objects_fast()

        #
        # 3. Now we have a complete namespace; concatenate all definitions
        # together in topological order.
        #
        compiled = {}
        obj_names = self._object_names

        for shader_name, shader in self.shaders.items():
            code = []
            version = shader.version_pragma
            for dep in self._shader_deps[shader_name]:
                dep_code = dep.definition(obj_names, version, shader)
                if dep_code is not None:
                    code.append(dep_code)

            if version is not None:
                code.insert(0, '#version %s %s' % version)

            compiled[shader_name] = '\n'.join(code)

        self.code = compiled
        return compiled

    def _rename_objects_fast(self):
        """Rename all objects quickly to guaranteed-unique names using the
        id() of each object.

        This produces mostly unreadable GLSL, but is about 10x faster to
        compile.
        """
        for shader_name, deps in self._shader_deps.items():
            for dep in deps:
                name = dep.name
                if name != 'main':
                    ext = '_%x' % id(dep)
                    name = name[:32-len(ext)] + ext
                self._object_names[dep] = name

    def _rename_objects_pretty(self):
        """Rename all objects like "name_1" to avoid conflicts. Objects are
        only renamed if necessary.

        This method produces more readable GLSL, but is rather slow.
        """
        #
        # 1. For each object, add its static names to the global namespace
        #    and make a list of the shaders used by the object.
        #

        # {name: obj} mapping for finding unique names
        # initialize with reserved keywords.
        self._global_ns = dict([(kwd, None) for kwd in gloo.util.KEYWORDS])
        # functions are local per-shader
        self._shader_ns = dict([(shader, {}) for shader in self.shaders])

        # for each object, keep a list of shaders the object appears in
        obj_shaders = {}

        for shader_name, deps in self._shader_deps.items():
            for dep in deps:
                # Add static names to namespace
                for name in dep.static_names():
                    self._global_ns[name] = None

                obj_shaders.setdefault(dep, []).append(shader_name)

        #
        # 2. Assign new object names
        #
        name_index = {}
        for obj, shaders in obj_shaders.items():
            name = obj.name
            if self._name_available(obj, name, shaders):
                # hooray, we get to keep this name
                self._assign_name(obj, name, shaders)
            else:
                # boo, find a new name
                while True:
                    index = name_index.get(name, 0) + 1
                    name_index[name] = index
                    ext = '_%d' % index
                    new_name = name[:32-len(ext)] + ext
                    if self._name_available(obj, new_name, shaders):
                        self._assign_name(obj, new_name, shaders)
                        break

    def _is_global(self, obj):
        """Return True if *obj* should be declared in the global namespace.

        Some objects need to be declared only in per-shader namespaces:
        functions, static variables, and const variables may all be given
        different definitions in each shader.
        """
        # todo: right now we assume all Variables are global, and all
        # Functions are local. Is this actually correct? Are there any
        # global functions? Are there any local variables?
        from .variable import Variable
        return isinstance(obj, Variable)

    def _name_available(self, obj, name, shaders):
        """Return True if *name* is available for *obj* in *shaders*."""
        if name in self._global_ns:
            return False
        shaders = self.shaders if self._is_global(obj) else shaders
        for shader in shaders:
            if name in self._shader_ns[shader]:
                return False
        return True

    def _assign_name(self, obj, name, shaders):
        """Assign *name* to *obj* in *shaders*."""
        if self._is_global(obj):
            assert name not in self._global_ns
            self._global_ns[name] = obj
        else:
            for shader in shaders:
                ns = self._shader_ns[shader]
                assert name not in ns
                ns[name] = obj
        self._object_names[obj] = name
