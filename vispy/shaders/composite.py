# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import print_function, division, absolute_import

from ..gloo import Program
from . import parsing


"""

should be able to do something like:

    s = CompositeProgram(vcode, fcode)
    # this auto-detects undefined function prototypes
    
    # or we can do this to auto-generate the prototype
    # (but of course the code must internally call this function already)
    s.add_hook('my_hook_name', return='vec4', args=['vec4 arg1', 'float arg2'])

    fn = ShaderFunction(...)
    bound_fn = fn.bind(arg2=('varying', 'my_var_name'))
    s.set_hook('my_hook_name', bound_fn)

maybe also this:

    s.add_attribute('vec4 my_attribute')
    bf = fn.bind(arg2=s.my_attribute)
    
fragment functions allow installation of code to vertex post_hook:

    ffn = FragmentFunction(...)
    s.set_hook(ffn) # may add variables and post_hook entries to vertex shader

    # note this means that CompositeProgram must have a post_hook function chain.

"""

class CompositeProgram(Program):
    """
    Shader program that is composed of main shader functions combined with
    any number of ShaderFunctions. Each function that is included in the
    program provides the definition to a function prototype (hook) that is
    declared in the main code.
    
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

    def _update(self):
        # generate all code..
        vcode, fcode = self.generate_code()
        self.attach(VertexShader(vcode), FragmentShader(fcode))
        
        # set all variables..
        self.vmain.apply_variables(self)
        self.fmain.apply_variables(self)
        
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
        
    def set_hook(self, hook_name, function):
        """
        Use *function* as the definition of *hook*. If the function does not
        have the correct name, a wrapper will be created by calling
        `function.bind(hook_name)`.
        """
        
        if hook_name not in self._hooks:
            raise NameError("This program has no hook named '%s'" % hook_name)
        
        # make sure the function definition fits the hook.
        shader, hook_args, hook_rtype = self._hooks[hook_name]
        if function.rtype != hook_rtype:
            raise TypeError("function does not return correct type for hook "
                            "'%s' (returns %s, should be %s)" % (hook_name, function.rtype, hook_rtype))
        if len(function.args) != len(hook_args):
            raise TypeError("function does not accept correct number of arguments for hook "
                            "'%s' (accepts %d, should be %d)" % (hook_name, len(function.args), len(hook_args)))
        for i, arg in enumerate(function.args):
            if arg[0] != hook_args[i][0]:
                fnsig = ", ".join([arg[0] for arg in function.args])
                hksig = ", ".join([arg[0] for arg in hook_args])
                raise TypeError("function has incorrect signature for hook "
                                "'%s' (signature is (%s), should be (%s))" % (hook_name, fnsig, hksig))
           
        # if the name is incorrect, make a wrapper with the correct name.
        if function.name != hook_name:
            function = function.bind(hook_name)
        
        self._hook_defs[hook_name] = function
    
    def generate_code(self):
        vcode = self.vmain
        fcode = self.fmain
        vdeps = set()
        fdeps = set()
        
        for hook_name, func in self._hook_defs.items():
            shader, hook_args, hook_rtype = self._hooks[hook_name]
            if shader == 'vertex':
                for dep in func.all_deps():
                    if dep.name not in vdeps:
                        vcode += dep.code
                        vdeps.add(dep.name)
                vcode += func.code
                
            elif shader == 'fragment': 
                for dep in func.all_deps():
                    if dep.name not in fdeps:
                        fcode += dep.code
                        fdeps.add(dep.name)
                fcode += func.generate_code()
                
            else:
                raise Exception("Unsupported shader type: %s" % shader)
            
        return vcode, fcode
            

#class CompositeMainFunction:
    #def __init__(self, code, shader):
        #"""
        #*code* is the GLSL source containing the main() definition for this 
        #shader.
        #*shader* is 'vertex' or 'fragment'.
        #"""
        #self.code = code
        #self.shader = shader
        


class ShaderFunction:
    def __init__(self, code=None, name=None, args=None, rtype=None):
        """
        *args* must be a list of ('type', 'name') tuples.        
        """
        self.set_code(code, name, args, rtype)
        self._deps = []
        
    @property
    def code(self):
        """
        The GLSL code that defines this function. Does not include dependencies,
        program variables, hooks, etc. (see also: generate_code())
        """
        return self._code

    def set_code(self, code, name=None, args=None, rtype=None):
        """
        Set the GLSL code for this function.
        
        Optionally, the name, arguments, and return type may be specified. If
        these are omitted, then the values will be automatically parsed from
        the code.
        """
        self._code = code
        if code is None:
            self.name = self.args = self.rtype = None
            return
        
        if name is None:
            self.name, self.args, self.rtype = parsing.parse_function_signature(self.code)
        else:
            self.name = name
            self.args = args
            self.rtype = rtype
        self._arg_types = dict([(a[1], a[0]) for a in self.args])

    def bind(self, name, **kwds):
        """
        Return a bound function that wraps this function, using program 
        variables to supply input to some of its arguments.
        
        This is analogous to python bound methods, where the first argument
        is automatically supplied (but in this case, any argument(s) may be
        bound to uniforms/attributes/varyings).
        
        The primary purpose of this is to allow multiple instances of the same
        ShaderFunction to be used in the final program, where each instance
        generates a new bound function with unique attribute/uniform inputs. 
        
        Keyword arguments are used to bind specific function arguments; each
        must be a string specifying the program variable that will supply
        the value to that argument, or (uniform|attribute|varying) to specify
        that the variable should be generated automatically. 
        
        For example, if the original function looks like:
        
            vec4 my_function(float a, vec2 b, vec3 c) { ... }
            
        Then the following bind call:
        
            func.bind('new_func_name', b='input_b', c='input_c')
                      
        Would return a ShaderFunction with the following code:
        
            vec4 new_func_name(float a) {
                return my_function(a, input_b, input_c);
            }
        
        Note that this procedure assumes that input_b and input_c are variables
        that exist and have the correct type.
        """
        return BoundShaderFunction(self, name, kwds)
     

    def apply_variables(self, program):
        pass
        

    def add_variable(self, vtype, dtype, name):
        """
        Add code for a program variable declaration to this function. 
        
        Example:
        
            fn.add_variable('attribute', 'vec3', 'input_pos')
        
        """

    def __setitem__(self, var, value):
        """
        Set the value of a program variable declared on this function.        
        """

    def all_deps(self):
        """
        Return complete, ordered list of functions required by this function.
        """
        deps = []
        for fn in self._deps:
            deps.extend(fn.all_deps())
            deps.append(fn)
        return deps

class BoundShaderFunction(ShaderFunction):
    def __init__(self, parent_function, name, bound_args):
        self._parent = parent_function
        self._name = name
        self._bound_arguments = bound_args
        ShaderFunction.__init__(self)
        self._deps.append(self._parent)
        self.set_code(self.generate_function_code())

    @property
    def code(self):
        """
        The GLSL code that defines this function. Does not include dependencies,
        program variables, hooks, etc. (see also: generate_code())
        """
        if self._code is None:
            code = self.generate_function_code()
            self.set_code(code)
        return self._code
        
    def generate_function_code(self):
        code = ""
        
        # Generate attribute/uniform declarations
        for arg in self._bound_arguments.values():
            code += "%s %s %s;\n" % arg
        code += "\n"
        
        # new function signature
        fn_args = self._parent.args
        arg_defs = ["%s %s" % x for x in fn_args[:] if x[1] not in self._bound_arguments]
        new_sig = ", ".join(arg_defs)
        code += "%s %s(%s) {\n" % (self._parent.rtype, self._name, new_sig)
        
        # call original function
        args = []
        for dtype, argname in fn_args:
            if argname in self._bound_arguments:
                args.append(self._bound_arguments[argname][2])
            else:
                args.append(argname)
        code += "    return %s(%s);\n" % (self._parent.name, ", ".join(args))
        
        code += "}\n"
        
        return code
        
    