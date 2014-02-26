# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division
import logging

from ..gloo import Program, VertexShader, FragmentShader
from .function import *
from . import parsing



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
        
        # Collection of all names declared in each shader.
        # {'function_name': Function, 'variable_name': VariableReference, ...}
        self.namespaces = {
            'vertex': {},
            'fragment': {},
            }
        
        # Garbage collection system: keep track of all objects (functions and
        # variables) included in the program and their referrers. When no 
        # referrers are found, remove the object from here and from
        # the namespaces / caches.
        # TODO: Not implemented yet..
        self.referrers = {}  # {obj: [list of referrers]}
        
        # cache of compilation results for each function and variable
        self._function_cache = {}  # {function: (name, code)}
        self._variable_cache = {}  # {variable: (name, code)}
        
        # lists all hooks (function prototypes in both shaders. Format is:
        # {'hook_name': ((vertex|fragment), args, rtype)}
        self._hooks = {}
        
        # hook definitions
        self._hook_defs = {}  # {'hook_name': Function}
        
        self._find_hooks()
        
        # force _update to be called when the program is activated.
        self._need_update = True

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
        self._need_update = True
            
    def __setitem__(self, name, value):
        if name in self._hooks:
            self.set_hook(name, value)
        else:
            super(ModularProgram, self).__setitem__(name, value)

        
    def set_hook(self, hook_name, function, replace=False):
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
            
            if not replace:
                raise RuntimeError("Cannot set hook '%s'; this hook is already set "
                                "(with %s)." % 
                                (hook_name, self._hook_defs[hook_name]))
            # TODO: Allow hooks to be redefined. This requires properly
            # flushing out cached compilation results that need to be 
            # recompiled.
        
        if isinstance(function, list):
            function = FunctionChain("$%s_hook" % hook_name, function)
        
        self._hook_defs[hook_name] = function
        self._need_update = True
                
    # TODO: might remove this functionality. 
    # It is not currently in use..
    #def _install_dep_callbacks(self, function):
        ## Search through all dependencies of this function for callbacks
        ## and install them.
        
        #for dep in function.all_deps():
            #for hook_name, cb in dep.callbacks:
                #self.add_callback(hook_name, cb)
        
    def _update(self):
        # generate all code..
        self._compile()
        
        self.attach(VertexShader(self.vert_code), 
                    FragmentShader(self.frag_code))
        
        # set all variables..
        self._apply_variables()
        
        # and continue.
        super(ModularProgram, self)._update()

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
        """
        Generate complete vertex and fragment shader code by compiling hook
        definitions and concatenating each to the shaders.
        """
        code = {'vertex': [self.vmain], 'fragment': [self.fmain]}
        
        for hook_name, func in self._hook_defs.items():
            self._check_hook(hook_name)
            shader, hook_args, hook_rtype = self._hooks[hook_name]
            n, c = self._resolve_function(func, shader, hook_name)
            code[shader].append(c)
        self.vert_code = '\n'.join(code['vertex'])
        self.frag_code = '\n'.join(code['fragment'])
            
    def _resolve_function(self, func, shader, func_name=None):
        """
        Generate complete code needed for one function (including dependencies).
        
        Return (function_name, code).
        """
        func_res = self._function_cache.get(func, None)
        if func_res is not None:
            return func_res
        
        
        code = ""
        subs = {}
        
        # resolve function name
        if func.is_anonymous:
            if func_name is None:
                func_name = func.name.lstrip('$')
            func_name = self._suggest_name(shader, func_name, func)
            subs[func.name.lstrip('$')] = func_name
        else:
            if func.name != func_name:
                raise Exception("Cannot compile function %s with name %s; "
                                "function is not anonymous." 
                                % (func, func_name))
        self.namespaces[shader][func_name] = func
        
        # resolve all variable names and generate declarations if needed
        for local_name in func.template_vars:
            var = func[local_name]
            n, c = self._resolve_variable(var, shader)
            if n not in self.namespaces[shader]:
                code += c
                self.namespaces[shader][n] = var
            subs[local_name] = n
            
        # resolve all dependencies
        dep_names = {}
        for dep in func.deps:
            n, c = self._resolve_function(dep, shader)
            dep_names[dep] = n
            code += c
            code += "\n\n"
            
        # compile code with the suggested substitutions and dependency names
        code += func.compile(subs, dep_names)
        
        func_res = (func_name, code)
        self._function_cache[func] = func_res
        return func_res
    
    def _resolve_variable(self, var, shader):
        """
        Decide on a name for *var* and generate its declaration code.
        
        Return (variable_name, declaration_code).
        """
        var_res = self._variable_cache.get(var, None)
        if var_res is not None:
            return var_res
        
        if var.anonymous:
            name = self._suggest_name(shader, var.name, var)
        else:
            self._check_name(shader, var.name, var)
            name = var.name
        try:
            decl = "%s %s %s;\n" % (var.vtype, var.dtype, name)
        except KeyError:
            raise Exception("%s has not been assigned a value" % var)
        var_res = (name, decl)
        self._variable_cache[var] = var_res
        return var_res
        
    def _check_name(self, shader, name, val):
        """
        Check that *name* correctly refers to *val* in the program namespace,
        if it is present.
        """
        for nsname in self.namespaces:
            if (name in self.namespaces[nsname] and 
                self.namespaces[nsname][name] != val):
                raise Exception("Cannot use name '%s' for variable %s; already "
                                "used by %s." % 
                                (name, val, self.namespaces[nsname][name]))
                
    def _suggest_name(self, shader, name, val):
        """
        Suggest a new name for *val* if the given *name* is already in use.        
        """
        ns = {}
        for nsname in self.namespaces:
            ns.update(self.namespaces[nsname])
        
        if name in ns and ns[name] is not val:
            m = re.match(r'(.*)_(\d+)', name)
            if m is None:
                base_name = name
                index = 1
            else:
                base_name, index = m.groups()
            while True:
                name = base_name + '_' + str(index)
                if name not in ns or ns[name] is val:
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
                            "arguments for hook '%s' (accepts %d, should be %d)"
                            % (hook_name, len(func.args), len(hook_args)))
        for i, arg in enumerate(func.args):
            if arg[0] != hook_args[i][0]:
                fnsig = ", ".join([arg[0] for arg in func.args])
                hksig = ", ".join([arg[0] for arg in hook_args])
                raise TypeError("function has incorrect signature for hook '%s'"
                                " (signature is (%s), should be (%s))" % 
                                (hook_name, fnsig, hksig))
    
    def _apply_variables(self):
        """
        Apply all program variables that are carried by the components of this 
        program.
        """
        for namespace in self.namespaces.values():
            for name, spec in namespace.items():
                if isinstance(spec, Function) or spec.vtype == 'varying':
                    continue
                self[name] = spec.value
