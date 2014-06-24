# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division, print_function
import re

from ...gloo import Program, VertexShader, FragmentShader
from .function import Function, FunctionChain
from . import parsing
from ...util import logger
from ...ext.six import string_types


"""
API issues to work out:


Need to think more about efficiency:
    - ability to re-assign hooks or modify chains and have dependencies
      automatically re-calculated
        => need to track {dep: [refs...]} so that deps are only removed when no
           more referrers are present.
        => same goes for shared variables..
    - ability to assign new program variable values to an existing program
    - caching compilation of individual functions if possible
    - remember variable name assignments, only recompute when necessary.
    - Ideally, one Function may appear in multiple ModularPrograms
      (with the same variable assignments each time)

Need ability to assign function calls to program variables
    (specifically, to replace uniforms with texture lookup for Collections)

Possibly move hook/chain features out to ModularShader; keep ModularProgram
more focused on compilation.
    Maybe ModularShader is a subclass of Function? Or vice-versa?


"""


class ModularProgram(Program):
    """
    Shader program that is composed of main shader functions combined with
    any number of Functions. Each function that is included in the
    program provides the definition to a function prototype (hook) that is
    declared in the main code.

    Arguments:

    vmain : str
        GLSL code for vertex shader main function
    fmain : str
        GLSL code for fragment shader main function

    Upon initialization, the GLSL code is searched for undefined function
    prototypes.


    Example:

        vertex_code = '''
        vec4 swappable_function();

        void main() {
            gl_Position = swappable_function();
        }
        '''

        fragment_code = '''
        void main() {
            gl_FragColor = vec4(1, 1, 1, 1);
        }
        '''

        prog = ModularProgram(vertex_code, fragment_code)

    This example contains one hook--the undefined 'swappable_function'
    prototype. Any function may be attached to this hook:

        func = Function('''
        attribute vec2 input_position;
        vec4 swappable_function() {
            return vec4(input_position, 0, 1);
        }
        ''')

        # attach to the shader:
        prog.set_hook('swappable_function', func)

        # Data assigned to the function will be passed on to the program when
        # it is activated.
        func['input_position'] = VertexBuffer(...)

    """
    def __init__(self, vmain, fmain):
        Program.__init__(self)
        self.vmain = vmain
        self.fmain = fmain

        # keep track of attached shaders
        self.vshader = None
        self.fshader = None

        # Garbage collection system: keep track of all objects (functions and
        # variables) included in the program and their referrers. When no
        # referrers are found, remove the object from here and from
        # the namespaces / caches.
        # TODO: Not implemented yet..
        self._referrers = {}  # {obj: [list of referrers]}

        # cache of compilation results for each function and variable
        self._object_names = {}  # {object: name}
        self._object_code = {}   # {object: code}
        self.namespace = None    # {name: object} (only valid for one compile)

        # lists all hooks (function prototypes in both shaders. Format is:
        # {'hook_name': ((vertex|fragment), args, rtype)}
        self._hooks = {}

        # hook definitions
        self._hook_defs = {}  # {'hook_name': Function}

        self._find_hooks()

    def add_chain(self, hook, chain=None):
        """
        Attach a new FunctionChain to *hook*.

        This allows callbacks to be added to the chain with add_callback.
        """
        if chain is None:
            chain = FunctionChain(name=hook)

        self.set_hook(hook, chain)

    def add_callback(self, hook, function, pre=False):
        """
        Add a new function to the end of the FunctionChain attached to
        *hook*.

        If *pre* is True, then the function is added to the beginning
        of the chain. Raises TypeError if there is no FunctionChain attached
        to *hook*.
        """
        if hook not in self._hooks:
            raise Exception('This program has no hook named "%s"' % hook)
        hook_def = self._hook_defs.get(hook, None)

        if (hook_def is None or not isinstance(hook_def, FunctionChain)):
            raise TypeError("Cannot add callback to hook '%s'; not a "
                            "FunctionChain. (%s)" % (hook, type(hook_def)))

        if pre:
            hook_def.insert(0, function)
        else:
            hook_def.append(function)

        # TODO: remove or resurrect
        #self._install_dep_callbacks(function)
        self._need_build = True

    def remove_callback(self, hook, function):
        """
        Remove *function* from the chain attached to *hook*.
        """
        if hook not in self._hooks:
            raise Exception('This program has no hook named "%s"' % hook)
        hook_def = self._hook_defs.get(hook, None)

        if (hook_def is None or not isinstance(hook_def, FunctionChain)):
            raise TypeError("Cannot remove callback from hook '%s'; not a "
                            "FunctionChain. (%s)" % (hook, type(hook_def)))

        hook_def.remove(function)

        # TODO: remove or resurrect
        #self._remove_dep_callbacks(function)
        self._need_build = True

    def __setitem__(self, name, value):
        if name in self._hooks:
            self.set_hook(name, value)
        else:
            super(ModularProgram, self).__setitem__(name, value)

    def set_hook(self, hook_name, function):
        """
        Use *function* as the definition of *hook*. If the function does not
        have the correct name, a wrapper will be created by calling
        `function.wrap(hook_name)`.

        Arguments:

        hook_name : str
            The name of the hook to be defined by *function*. There must exist
            a corresponding function prototype in the GLSL main function code.
        function : Function instance or list
            The function that provides the definition for the *hook_name*
            prototype. The function must have a compatible return type and
            arguments. If this function does not have the correct name, then
            a wrapper function will be automatically created with the correct
            name.
            If *function* is a list, then a FunctionChain is automatically
            created with the given functions.

        """

        if hook_name not in self._hooks:
            raise NameError("This program has no hook named '%s'" % hook_name)

        if hook_name in self._hook_defs:
            if function is self._hook_defs[hook_name]:
                return
            else:
                self.unset_hook(hook_name)

        if isinstance(function, list):
            function = FunctionChain(hook_name, function, anonymous=False)

        self._hook_defs[hook_name] = function
        self._need_build = True

    def unset_hook(self, hook_name):
        func = self._hook_defs[hook_name]
        # removing function; also remove all other objects that no longer serve
        # a purpose here..
        self._forget_object(func)
        self._hook_defs[hook_name] = None
        self._need_build = True

    def _forget_object(self, obj):
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

    # TODO: might remove this functionality.
    # It is not currently in use..
    #def _install_dep_callbacks(self, function):
    #    ## Search through all dependencies of this function for callbacks
    #    ## and install them.

    #    for dep in function.all_deps():
    #        for hook_name, cb in dep.callbacks:
    #            self.add_callback(hook_name, cb)

    def _build(self):
        # generate all code..
        self._compile()

        if self.vshader is not None:
            self.detach([self.vshader, self.fshader])
            self.vshader = self.fshader = None

        vs = VertexShader(self.vert_code)
        fs = FragmentShader(self.frag_code)
        self.attach([vs, fs])
        self.vshader = vs
        self.fshader = fs

        # set all variables..
        self._apply_variables()

        # and continue.
        super(ModularProgram, self)._build()

    def _find_hooks(self):
        # Locate all undefined function prototypes in both shaders
        vprots = parsing.find_prototypes(self.vmain)
        fprots = parsing.find_prototypes(self.fmain)
        self._hooks = {}
        for shader_type, prots in [('vertex', vprots), ('fragment', fprots)]:
            for name, args, rtype in prots:
                if name in self._hooks:
                    raise ValueError("Function prototype declared twice: '%s'"
                                     % name)
                self._hooks[name] = (shader_type, args, rtype)

    def _compile(self):
        # generate self.vert_code, self.frag_code, and self.namespace.

        # list of objects that must be assembled to produce the shaders
        # these lists contain a combination of ShaderObjects and strings
        objects = {'vertex': [], 'fragment': []}

        # list of all ShaderObjects
        all_objs = []

        # map of {name: object} for this compilation
        self.namespace = namespace = {}

        # 1) Walk over all hook definitions and collect a list of their object
        # dependencies
        for hook_name, func in self._hook_defs.items():
            self._check_hook(hook_name)
            shader, hook_args, hook_rtype = self._hooks[hook_name]

            # insert a hook comment
            header = "\n//------- Begin hook %s -------\n\n" % hook_name
            objects[shader].append(header)

            # record all dependencies of this hook in topological order
            func_deps = self._function_dependencies(func)
            objects[shader].extend(func_deps)

            # collect dependencies, but exclude the hook itself because it
            # has a required name.
            all_objs.extend(func_deps[:-1])

            # add hook to namespace
            if hook_name in namespace:
                raise Exception('Cannot assign %s to hook %s; name already in '
                                'use by %s.' %
                                (func, hook_name, namespace[hook_name]))
            self._set_object_name(func, hook_name)

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

        # 6) Assemble shaders
        self.vert_code = '\n'.join(shader_code['vertex'])
        self.frag_code = '\n'.join(shader_code['fragment'])

        logger.debug('==================== VERTEX SHADER ====================')
        logger.debug(self.vert_code)
        logger.debug('=================== FRAGMENT SHADER ===================')
        logger.debug(self.frag_code)
        logger.debug('====================== NAMESPACE ======================')
        logger.debug(self.namespace)

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

    def _check_hook(self, hook_name):
        """
        Raise an exception if the function attached to *hook_name* does not
        have the required signature.
        """
        # TODO: If this is expensive, perhaps we can skip it and just let
        # the compiler generate an error.
        shader, hook_args, hook_rtype = self._hooks[hook_name]
        func = self._hook_defs[hook_name]

        if func.rtype != hook_rtype:
            raise TypeError("function does not return correct type for hook "
                            "'%s' (returns %s, should be %s)" %
                            (hook_name, func.rtype, hook_rtype))
        if len(func.args) != len(hook_args):
            raise TypeError("function does not accept correct number of "
                            "arguments for hook '%s' (accepts %d, should "
                            "be %d)"
                            % (hook_name, len(func.args), len(hook_args)))
        for i, arg in enumerate(func.args):
            if arg[0] != hook_args[i][0]:
                fnsig = ", ".join([arg[0] for arg in func.args])
                hksig = ", ".join([arg[0] for arg in hook_args])
                raise TypeError("function has incorrect signature for hook "
                                "'%s' (signature is (%s), should be (%s))" %
                                (hook_name, fnsig, hksig))

    def _apply_variables(self):
        """
        Apply all program variables that are carried by the components of this
        program.
        """
        logger.debug("Apply variables:")
        for name, spec in self.namespace.items():
            if isinstance(spec, Function) or spec.vtype == 'varying':
                continue
            logger.debug("    %s = %s" % (name, spec.value))
            self[name] = spec.value
