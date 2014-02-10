# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import print_function, division, absolute_import
import string

from ..gloo import Program, VertexShader, FragmentShader
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
        
        self._post_hooks = []
        
        # force _update to be called when the program is activated.
        self._need_update = True

    def add_post_hook(self, function):
        """
        Add a new function to be called at the end of the vertex shader.
        """
        self._post_hooks.append(function)

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
    
    def _generate_code(self):
        vcode = self.vmain
        fcode = self.fmain
        vdeps = set()
        fdeps = set()
        
        # first, look for FragmentShaderFunctions and add vertex code to the 
        # post-hook
        for hook_name, func in self._hook_defs.items():
            for dep in func.all_deps():
                if isinstance(dep, FragmentShaderFunction):
                    self.add_post_hook(dep.vertex_post)

        # Install shader chain for post_hooks
        post_chain = ShaderFunctionChain('post_hook', self._post_hooks)
        self.set_hook('post_hook', post_chain)

        # Now add code for all hooks and dependencies in order.
        for hook_name, func in self._hook_defs.items():
            shader, hook_args, hook_rtype = self._hooks[hook_name]
            if shader == 'vertex':
                for dep in func.all_deps():
                    if dep.name not in vdeps:
                        print("++vertex dep++")
                        print(dep)
                        print(dep.code)
                        vcode += dep.code
                        vdeps.add(dep.name)
                #vcode += func.code
                
            elif shader == 'fragment': 
                for dep in func.all_deps():
                    if dep.name not in fdeps:
                        print("++fragment dep++")
                        print(dep)
                        print(dep.code)
                        fcode += dep.code
                        fdeps.add(dep.name)
                #fcode += func.code
                
            else:
                raise Exception("Unsupported shader type: %s" % shader)

        print ("--vertex------------------------------")
        print (vcode)
        print ("--fragment------------------------------")
        print (fcode)
        print ("--------------------------------")
        return vcode, fcode
         
    def _apply_variables(self):
        """
        Apply all program variables that are carried by the components of this 
        program.
        """
        print("apply variables:")
        for hook_name, func in self._hook_defs.items():
            for dep in func.all_deps():
                for name, value in dep._program_values.items():
                    print(name, value, dep)
                    self[name] = value
        


class ShaderFunction(object):
    """
    This class represents a single function in GLSL. Its *code* property 
    contains the entire GLSL code of the function as well as any program
    variable declarations it depends on. ShaderFunctions also have a list
    of dependencies, which are other ShaderFunctions that must be included
    in the program because they are called from this function.
    
    A CompositeProgram generates its code by concatenating the *code* property
    of multiple ShaderFunctions and their dependencies; each function is
    included exactly once, even if it is depended upon multiple times.
    """    
    def __init__(self, code=None, name=None, args=None, rtype=None, deps=None):
        """
        Arguments:
        
        code : str
        name : None or str
            The name of the function as defined in *code*.
            If None, this value will be automatically parsed from *code*.
        args : None or list of tuples
            Describes the arguments accepted by this function.
            Each tuple contains two strings ('type', 'name').
            If None, this value will be automatically parsed from *code*.
        rtype : None or str
            String indicating the return type of the function.
            If None, this value will be automatically parsed from *code*.
        deps : None or list of ShaderFunctions
            Lists functions that are called by this function, and therefore must
            be included by a CompositeProgram when compiling the complete
            program.
        """
        self.set_code(code, name, args, rtype)
        self._deps = deps or []
        self._program_values = {}
        
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
        Return a new ShaderFunction that wraps this function, using program 
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
        
            func.bind(name='new_func_name', 
                      b=('uniform', 'vec2', 'input_b'), 
                      c=('attribute', 'vec3', 'input_c'))
                      
        Would return a ShaderFunction with the following code:
        
            uniform vec2 input_b;
            attribute vec3 input_c;
            vec4 new_func_name(float a) {
                return my_function(a, input_b, input_c);
            }
        
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
        self._program_values[var] = value

    def all_deps(self):
        """
        Return complete, ordered list of functions required by this function.
        (including this function)
        """
        deps = []
        for fn in self._deps:
            deps.extend(fn.all_deps())
            deps.append(fn)
        deps.append(self)
        return deps
    
    def __repr__(self):
        return "<ShaderFunction %s>" % self.name


class FragmentShaderFunction(ShaderFunction):
    """
    ShaderFunction meant to be used in fragment shaders when some supporting 
    code must also be introduced to the vertex shader post-hook, usually to
    initialize one or more varyings.    
    """
    def __init__(self, code, vertex_post=None):
        super(FragmentShaderFunction, self).__init__(code)
        self.vertex_post = vertex_post

    def bind(self, name, **kwds):
        """
        Behaves exactly as ShaderFunction.bind(), with one exception:
        any *attribute* variables bound to a shader function are actually
        introduced via a separate piece of code in the vertex shader.
        
        
        
        """


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
        The GLSL code that defines this function.
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
        
    
class ShaderFunctionChain(ShaderFunction):
    def __init__(self, name, funcs):
        ShaderFunction.__init__(self)
        self._funcs = funcs
        self._deps = funcs
        self._code = None
        self.name = name
        if len(funcs) > 0:
            self.rtype = funcs[-1].rtype
            self.args = funcs[0].args[:]
        else:
            self.rtype = 'void'
            self.args = []
        
    @property
    def code(self):
        """
        The GLSL code that defines this function.
        """
        if self._code is None:
            code = self.generate_function_code()
            self.set_code(code)
        return self._code
        
    def generate_function_code(self):
        
        args = ", ".join(["%s %s" % arg for arg in self.args])
        code = "%s %s(%s) {\n" % (self.rtype, self.name, args)
        
        if self.rtype == 'void':
            for fn in self._funcs:
                code += "    %s();\n" % fn.name
        else:
            code += "    return "
            for fn in self._funcs[::-1]:
                code += "%s(\n           " % fn.name
            code += "    %s%s;\n" % (self.args[0][1], ')'*len(self._funcs))
        
        code += "}\n"
        
        return code
        
        
class ShaderFunctionTemplate(object):
    """
    Template-based shader function generator. This allows to generate new 
    ShaderFunction instances with a custom function name and with any custom
    program variable names substituted in. This has effectively the same
    functionality as ShaderFunction.bind(), but avoids the use of wrapper
    functions.
    
    Arguments:
    
    template : str
        A template string used to construct ShaderFunction instances.
        Uses string.Template formatting style ('$name' substitutions). 
        Must contain $func_name in place of the function name, and $var_name for 
        each variable declared in the *var_names* argument.
    var_names : list
        List of the names of program variables that must be added to the code
        and substituted in the template.
    deps : list(ShaderFunction)
        List of ShaderFunctions that are required by this function.
        
    See bind() for more information about the construction of ShaderFunctions
    from templates. 

    Example that converts a vec2 input variable to vec4:
    
        template = ShaderFunctionTemplate('''
            vec4 $func_name() {
                return vec4($input, 0, 1);
            }
        ''', var_names=['input'])
        
        func = template.bind(name='my_function', 
                             input=('uniform', 'vec2', 'my_input_uniform'))
                             
    If we include *func* in a CompositeProgram, it will generate the following 
    code:
    
        uniform vec2 my_input_uniform;
        vec4 my_function() {
            return vec4(my_input_uniform, 0, 1);
        }
        
    """
    def __init__(self, template, var_names, deps=()):
        self.template = string.Template(template)
        self.var_names = var_names
        self.deps = deps
    
    def bind(self, name, **kwds):
        """
        Return a ShaderFunction whose code is constructed by the following 
        rules:
        
        * $func_name is replaced with the contents of the *name* argument
        * each keyword represents a program variable:
            
            template_name=('uniform|attribute|varying', type, name)
            
          The declaration for this variable will be automatically added to 
          the returned function code, and $template_name will be substituted
          with *name*.

        """
        var_names = self.var_names[:]
        subs = {'func_name': name}
        code = ""
        for name, var_spec in kwds.items():
            var_names.remove(name)
            subs[name] = var_spec[2]
            if name in self.var_names:
                code += "%s %s %s;\n" % var_spec
        
        if var_names:
            raise Exception('Unsubstituted template variables in bind(): %s' % var_names)
           
        kwds['func_name'] = name
        code += self.template.substitute(**subs)
        return ShaderFunction(code, deps=self.deps[:])

