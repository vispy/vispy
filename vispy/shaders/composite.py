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
    
        func = ShaderFunction('''
        attribute vec2 input_position;
        vec4 func_definition() {
            return vec4(input_position, 0, 1);
        }
        ''')
        
        # attach to the shader:
        prog.set_hook('swappable_function', func)
        
    In this example, a wrapper function is generated with the correct name
    'swappable_function' that calls the attached 'func_definition'. The output
    program code looks like:
    
        vec4 swappable_function();
        
        void main() {
            gl_Position = swappable_function();
        }        
    
        attribute vec2 input_position;
        vec4 func_definition() {
            return vec4(input_position, 0, 1);
        }
        
        vec4 swappable_function() {
            return func_definition();
        }
        
    """
    def __init__(self, vmain, fmain):
        Program.__init__(self)
        self.vmain = vmain
        self.fmain = fmain
        
        # Collection of all names declared in each shader.
        self.namespaces = {
            'vertex': {},
            'fragment': {},
            }
        
        # Garbage collection system: keep track of all objects (functions and
        # variables) included in the program and their referrers. When no 
        # referrers are found, remove the object.
        # Format is {obj: [list of referrers]}
        self.referrers = {}
        
        # cache of compilation results for each function and variable
        self._function_cache = {}  
        self._variable_cache = {}
        
        # lists all hooks (function prototypes in both shaders. Format is:
        # {'hook_name': ((vertex|fragment), args, rtype)}
        self._hooks = {}
        
        # hook definitions
        self._hook_defs = {}
        
        self._find_hooks()
        
        # force _update to be called when the program is activated.
        self._need_update = True

    def add_chain(self, hook, chain=None):
        """ Attach a new FunctionChain to *hook*. 
        
        This allows callbacks to be added to the chain with add_callback.
        """
        if chain is None:
            chain = FunctionChain(name=hook)
        
        self.set_hook(hook, chain)
        
    def add_callback(self, hook, function, pre=False):
        """ Add a new function to the end of the FunctionChain attached to 
        *hook*. if *pre* is True, then the function is added to the beginning
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
            
        self._install_dep_callbacks(function)
        self._need_update = True
            
    def __setitem__(self, name, value):
        if name in self._hooks:
            self.set_hook(name, value)
        else:
            super(ModularProgram, self).__setitem__(name, value)

        
    def set_hook(self, hook_name, function):
        """
        Use *function* as the definition of *hook*. If the function does not
        have the correct name, a wrapper will be created by calling
        `function.bind(hook_name)`.
        
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
        
        if hook_name in self._hook_defs and not replace:
            raise RuntimeError("Cannot set hook '%s'; this hook is already set "
                               "(with %s)." % 
                               (hook_name, self._hook_defs[hook_name]))
        
        if isinstance(function, list):
            function = FunctionChain("$%s_hook" % hook_name, function)
        
        
        self._hook_defs[hook_name] = function
        self._need_update = True
                
    def _install_dep_callbacks(self, function):
        # Search through all dependencies of this function for callbacks
        # and install them.
        for dep in function.all_deps():
            for hook_name, cb in dep.callbacks:
                self.add_callback(hook_name, cb)
    
        
    def _update(self):
        # generate all code..
        self._compile()
        
        self.attach(VertexShader(self.vert_code), FragmentShader(self.frag_code))
        
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
                    raise ValueError("Function prototype declared twice: '%s'" % name)
                self._hooks[name] = (shader_type, args, rtype)

    def _compile(self):
        """
        Generate complete vertex and fragment shader code
        
        
        """
        code = {'vertex': [self.vmain], 'fragment': [self.fmain]}
        
        for hook_name, func in self._hook_defs.items():
            shader, hook_args, hook_rtype = self._hooks[hook_name]
            
            if func not in self._function_cache:
                self._resolve_function(func, shader, hook_name)
            code[shader].append(self._function_cache[func][1])
        self.vcode = '\n'.join(code['vertex'])
        self.fcode = '\n'.join(code['fragment'])
            
    def _resolve_function(self, func, shader, func_name):
        """
        Generate complete code needed for one function, store in 
        self._func_code_cache
        """
        code = ""
        subs = {}
        
        # resolve function name
        if func_name is not None:
            subs[func.name.lstrip('$')] = func_name
        
        # resolve all variable names and generate declarations if needed
        for local_name, var in func.template_vars.items():
            if var not in self._variable_cache:
                self._resolve_variable(var, shader)
            n, c = self._variable_cache[var]
            if n not in self.namespaces[shader]:
                code += c
                self.namespaces[shader][n] = var
            subs[var.name] = n
            
        # resolve all dependencies
        dep_names = {}
        for dep in func.deps:
            if dep not in self._function_cache:
                self._resolve_function(dep, shader)
            dep_names[dep] = self._function_cache[dep][0]
            
        # compile code with the suggested substitutions and dependency names
        c = func.compile(subs, dep_names)
        
        code += c
        self._function_cache[func] = (func_name, code)

    
    def _resolve_variable(self, var, shader):
        """
        Decide on a name for *var* and generate its declaration code.        
        """
        # TODO: If this references another variable, call _resolve_variable on
        # the ref'd variable and use the resulting name.
        
        if var.name.startswith('$'):
            name = self.suggest_name(var.name)
        else:
            self.check_name(shader, var.name, var)
            name = var.name
        decl = "%s %s %s;\n" % (var.vtype, var.dtype, name)
        self._variable_cache[var] = (name, decl)
        
    def check_name(self, shader, name, val):
        """
        Check that *name* correctly refers to *val* in the program namespace,
        if it is present.
        """
        nsnames = self.namespaces.keys()
        for nsname in nsnames:
            if name in self.namespaces[nsname] and self.namespaces[nsname][name] != val:
                raise Exception("Cannot use name '%s' for variable %s; already used by %s." % (var.name, var, self.namespaces[nsname][name]))
                
    #def _compile(self):
        ## Assemble main shader functions along with their hook definitions
        ## into a single block of code.
        
        #vcode = [self.vmain]
        #fcode = [self.fmain]
        #namespace = {}  # total namespace of program
        #vnames = {}  # vertex shader namespace
        #fnames = {}  # fragment shader namespace
        
        
        ## add code for all hooks and dependencies in order.
        
        #for hook_name, func in self._hook_defs.items():
            #shader, hook_args, hook_rtype = self._hooks[hook_name]
            
            
            ### make sure the function definition fits the hook.
            ## TODO: If this is expensive, perhaps we can skip it and just let 
            ## the compiler generate an error.
            #if func.rtype != hook_rtype:
                #raise TypeError("function does not return correct type for hook "
                                #"'%s' (returns %s, should be %s)" % (hook_name, func.rtype, hook_rtype))
            #if len(func.args) != len(hook_args):
                #raise TypeError("function does not accept correct number of arguments for hook "
                                #"'%s' (accepts %d, should be %d)" % (hook_name, len(func.args), len(hook_args)))
            #for i, arg in enumerate(func.args):
                #if arg[0] != hook_args[i][0]:
                    #fnsig = ", ".join([arg[0] for arg in func.args])
                    #hksig = ", ".join([arg[0] for arg in hook_args])
                    #raise TypeError("function has incorrect signature for hook "
                                    #"'%s' (signature is (%s), should be (%s))" % (hook_name, fnsig, hksig))
            
            #if not func.is_anonymous and func.name != hook_name:
                #func = func.wrap(name=hook_name)
            
            #if shader == 'vertex':
                #code = vcode
                #shader_ns = vnames
            #else:
                #code = fcode
                #shader_ns = fnames
            
            #code.append("\n\n//  -------- Begin hook '%s' --------\n" % 
                        #hook_name)
            
            #n, c = func.compile(self, name=hook_name)
            #code.append(c)

        #vcode = '\n'.join(vcode)
        #fcode = '\n'.join(fcode)
        #print ("-------------------------VERTEX------------------------------")
        #print (vcode)
        #print ("\n-----------------------FRAGMENT------------------------------")
        #print (fcode)
        #print ("--------------------------------")
        ##print("final namespace:", namespace)
        
        #self.vert_code = vcode
        #self.frag_code = fcode
        #self.vert_ns = vnames
        #self.frag_ns = fnames
         
    def _apply_variables(self, namespace):
        """
        Apply all program variables that are carried by the components of this 
        program.
        """
        #print("apply variables:")
        for name, spec in namespace.items():
            if isinstance(spec, Function):
                continue
            #print("  ", name, spec)
            if spec[0] != 'varying':
                self[name] = spec[2]
        #for hook_name, func in self._hook_defs.items():
            #print("  ", hook_name, func)
            #for dep in func.all_deps():
                #print("    ", dep)
                #for name, spec in dep._program_values.items():
                    #print("      ", name, spec, dep)
                    #self[name] = spec[2]
        

