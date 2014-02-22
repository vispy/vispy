# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..gloo import Program, VertexShader, FragmentShader
from .function import *
from . import parsing



"""
API issues to work out:

  - Currently, program variables are set when the program is built. To 
    optimize, it must be possible to set new variables on a pre-built
    program.
  
  - Any useful way to make FunctionTemplate and FragmentFunction subclasses
    of Function? (and should we want to?)
        Perhaps we need a more general superclass for all of these?
        
        Common attributes:
            code  (= None for functions that must be bound)
            name  (also may be None)
            args
            rtype
            bindings
            bind()
            

  - Would be awesome if Function.bind() could optionally accept variable
    values instead of (type, name) specifications. This would simplify most
    uses of bind() and additionally allow the function and program to decide
    on a suitable (unique) variable name.

  - Would like FragmentFunction to have a convenience method that auto-generates
    vertex shader support code for translating attributes into varyings.
    (but this must be optional, because some components may need more complex
    support code)
    
    
"""



class CompositeProgram(Program):
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
        
        prog = CompositeProgram(vertex_code, fragment_code)
        
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
            
    def __setitem__(self, name, value):
        if name in self._hooks:
            self.set_hook(name, value)
        else:
            super(CompositeProgram, self).__setitem__(name, value)

        
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
                
    def _install_dep_callbacks(self, function):
        # Search through all dependencies of this function for callbacks
        # and install them.
        for dep in function.all_deps():
            for hook_name, cb in dep.callbacks:
                self.add_callback(hook_name, cb)
    
        
    def _update(self):
        # generate all code..
        vcode, fcode = self._generate_code()
        
        self.attach(VertexShader(vcode), FragmentShader(fcode))
        
        # set all variables..
        self._apply_variables()
        
        # and continue.
        super(CompositeProgram, self)._update()

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
                
    def _generate_code(self):
        # Assemble main shader functions along with their hook definitions
        # into a single block of code.
        
        vcode = self.vmain
        fcode = self.fmain
        vdeps = set()
        fdeps = set()
        
                
        ## All this was taken from set_hook:
                
            ## make sure the function definition fits the hook.
            #shader, hook_args, hook_rtype = self._hooks[hook_name]
            #if function.rtype != hook_rtype:
                #raise TypeError("function does not return correct type for hook "
                                #"'%s' (returns %s, should be %s)" % (hook_name, function.rtype, hook_rtype))
            #if len(function.args) != len(hook_args):
                #raise TypeError("function does not accept correct number of arguments for hook "
                                #"'%s' (accepts %d, should be %d)" % (hook_name, len(function.args), len(hook_args)))
            #for i, arg in enumerate(function.args):
                #if arg[0] != hook_args[i][0]:
                    #fnsig = ", ".join([arg[0] for arg in function.args])
                    #hksig = ", ".join([arg[0] for arg in hook_args])
                    #raise TypeError("function has incorrect signature for hook "
                                    #"'%s' (signature is (%s), should be (%s))" % (hook_name, fnsig, hksig))
            
            ## if the name is incorrect, make a wrapper with the correct name.
            #if function.name != hook_name:
                #function = function.resolve(hook_name)
                
            #self._install_dep_callbacks(function)

        
        
        # add code for all hooks and dependencies in order.
        for hook_name, func in self._hook_defs.items():
            shader, hook_args, hook_rtype = self._hooks[hook_name]
            if shader == 'vertex':
                vcode += "\n\n//  -------- Begin hook '%s' --------\n" % hook_name
                for dep in func.all_deps():
                    if dep is func:
                        if dep.name is None:
                            vcode += "\n\n" + dep.compile(self, name=hook_name)
                        else:
                            vcode += "\n\n" + dep.compile(self)
                    elif dep not in vdeps:
                        #print("++vertex dep++")
                        #print(dep)
                        #print(dep.code)
                        vcode += "\n\n" + dep.compile(self, prefix=hook_name)
                        vdeps.add(dep)
                #vcode += func.code
                
            elif shader == 'fragment': 
                fcode += "\n\n//  -------- Begin hook '%s' --------\n" % hook_name
                for dep in func.all_deps():
                    if dep is func:
                        if dep.name is None:
                            fcode += "\n\n" + dep.compile(self, name=hook_name)
                        else:
                            fcode += "\n\n" + dep.compile(self)
                    elif dep not in fdeps:
                        #print("++fragment dep++")
                        #print(dep)
                        #print(dep.code)
                        fcode += "\n\n" + dep.compile(self, prefix=hook_name)
                        fdeps.add(dep)
                #fcode += func.code
                
            else:
                raise Exception("Unsupported shader type: %s" % shader)

        print ("-------------------------VERTEX------------------------------")
        print (vcode)
        print ("\n-----------------------FRAGMENT------------------------------")
        print (fcode)
        print ("--------------------------------")
        
        return vcode, fcode
         
    def _apply_variables(self):
        """
        Apply all program variables that are carried by the components of this 
        program.
        """
        logging.debug("apply variables:")
        for hook_name, func in self._hook_defs.items():
            logging.debug("  ", hook_name, func)
            for dep in func.all_deps():
                logging.debug("    ", dep)
                for name, spec in dep._program_values.items():
                    logging.debug("      ", name, value, dep)
                    self[name] = spec[2]
        

