# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import print_function, division, absolute_import
import string

from ..gloo import Program, VertexShader, FragmentShader
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
            
        
    def set_hook(self, hook_name, function):
        """
        Use *function* as the definition of *hook*. If the function does not
        have the correct name, a wrapper will be created by calling
        `function.bind(hook_name)`.
        
        Arguments:
        
        hook_name : str
            The name of the hook to be defined by *function*. There must exist 
            a corresponding function prototype in the GLSL main function code.
        function : Function instance
            The function that provides the definition for the *hook_name*
            prototype. The function must have a compatible return type and
            arguments. If this function does not have the correct name, then
            a wrapper function will be automatically created with the correct
            name.
        """
        
        if hook_name not in self._hooks:
            raise NameError("This program has no hook named '%s'" % hook_name)
        
        if hook_name in self._hook_defs and not replace:
            raise RuntimeError("Cannot set hook '%s'; this hook is already set "
                               "(with %s)." % 
                               (hook_name, self._hook_defs[hook_name]))
        
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
        
        self._install_dep_callbacks(function)
                
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
        
        # add code for all hooks and dependencies in order.
        for hook_name, func in self._hook_defs.items():
            shader, hook_args, hook_rtype = self._hooks[hook_name]
            if shader == 'vertex':
                vcode += "\n\n//  -------- Begin hook '%s' --------\n" % hook_name
                for dep in func.all_deps():
                    if dep.name not in vdeps:
                        #print("++vertex dep++")
                        #print(dep)
                        #print(dep.code)
                        vcode += "\n\n" + dep.code
                        vdeps.add(dep.name)
                #vcode += func.code
                
            elif shader == 'fragment': 
                fcode += "\n\n//  -------- Begin hook '%s' --------\n" % hook_name
                for dep in func.all_deps():
                    if dep.name not in fdeps:
                        #print("++fragment dep++")
                        #print(dep)
                        #print(dep.code)
                        fcode += "\n\n" + dep.code
                        fdeps.add(dep.name)
                #fcode += func.code
                
            else:
                raise Exception("Unsupported shader type: %s" % shader)

        #print ("--vertex------------------------------")
        #print (vcode)
        #print ("--fragment------------------------------")
        #print (fcode)
        #print ("--------------------------------")
        
        return vcode, fcode
         
    def _apply_variables(self):
        """
        Apply all program variables that are carried by the components of this 
        program.
        """
        #print("apply variables:")
        for hook_name, func in self._hook_defs.items():
            #print("  ", hook_name, func)
            for dep in func.all_deps():
                #print("    ", dep)
                for name, value in dep._program_values.items():
                    #print("      ", name, value, dep)
                    self[name] = value
        

class Function(object):
    """
    This class represents a single function in GLSL. Its *code* property 
    contains the entire GLSL code of the function as well as any program
    variable declarations it depends on. Functions also have a list
    of dependencies, which are other Functions that must be included
    in the program because they are called from this function.
    
    A CompositeProgram generates its code by concatenating the *code* property
    of multiple Functions and their dependencies; each function is
    included exactly once, even if it is depended upon multiple times.
    """    
    def __init__(self, code=None, name=None, args=None, rtype=None, deps=None,
                 variables=None):
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
        deps : None or list of Functions
            Lists functions that are called by this function, and therefore must
            be included by a CompositeProgram when compiling the complete
            program.
        variables : None or dict
            Dict describing program variables declared in this function's code.
            See variable_names property.
        """
        self.set_code(code, name, args, rtype, variables)
        self._deps = deps[:] if deps is not None else []
        self._program_values = {}
        
        self._callbacks = []
        
    @property
    def code(self):
        """
        The GLSL code that defines this function. Does not include dependencies,
        program variables, hooks, etc. (see also: generate_code())
        """
        return self._code
    
    @property
    def bindings(self):
        """
        Dict of {name: type} pairs describing function arguments that may be 
        bound to new program variables.
        
        The names are the allowed keyword arguments to bind().
        
        For normal Function instances, bindings are simply the function 
        arguments. 
        """
        return self._bindings
        
    @property
    def callbacks(self):
        """
        List of (hook, function) pairs.
        
        When this function is added to a program, each pair will cause
        program.add_callback(hook, function) to be called.
        """
        return self._callbacks

    def set_code(self, code, name=None, args=None, rtype=None, variables=None):
        """
        Set the GLSL code for this function.
        
        Optionally, the name, arguments, and return type may be specified. If
        these are omitted, then the values will be automatically parsed from
        the code.
        """
        if code is None:
            self._code = self.name = self.args = self.rtype = None
            return
        
        self._code = self.clean_code(code)
        if name is None:
            self.name, self.args, self.rtype = parsing.parse_function_signature(self.code)
        else:
            self.name = name
            self.args = args
            self.rtype = rtype
            
        self._bindings = dict([(a[1], a[0]) for a in self.args])
            
        if variables is None:
            self.variables = parsing.find_program_variables(self.code)
        else:
            self.variables = variables
            
        self._arg_types = dict([(a[1], a[0]) for a in self.args])

    def bind(self, name, **kwds):
        """
        Return a new Function that wraps this function, using program 
        variables to supply input to some of its arguments.
        
        This is analogous to python bound methods, where the first argument
        is automatically supplied (but in this case, any argument(s) may be
        bound to uniforms/attributes/varyings).
        
        The primary purpose of this is to allow multiple instances of the same
        Function to be used in the final program, where each instance
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
                      
        Would return a Function with the following code:
        
            uniform vec2 input_b;
            attribute vec3 input_c;
            vec4 new_func_name(float a) {
                return my_function(a, input_b, input_c);
            }
        
        """
        return BoundFunction(self, name, kwds)
     
    def __setitem__(self, var, value):
        """
        Set the value of a program variable declared in this function's code.
        
        Any CompositeProgram that depends on this function will automatically
        apply the variable when it is activated.
        """
        if var not in self.variables:
            raise NameError("Variable '%s' does not exist in this function." 
                            % var)
        self._program_values[var] = value

    def all_deps(self):
        """
        Return complete, ordered list of functions required by this function.
        (including this function)
        """
        deps = []
        for fn in self._deps:
            deps.extend(fn.all_deps())
            #deps.append(fn)
        deps.append(self)
        return deps
    
    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.name)
    
    @staticmethod
    def clean_code(code):
        lines = code.split("\n")
        min_indent = 100
        while lines[0].strip() == "":
            lines.pop(0)
        while lines[-1].strip() == "":
            lines.pop()
        for line in lines:
            if line.strip() != "":
                indent = len(line) - len(line.lstrip())
                min_indent = min(indent, min_indent)
        if min_indent > 0:
            lines = [line[min_indent:] for line in lines]
        code = "\n".join(lines)
        return code
        


class BoundFunction(Function):
    """
    A BoundFunction is a wrapper around a Function that 'binds' zero or more 
    of the function's input arguments to program variables.
    
    Arguments:
    parent_function : Function instance
        The Function to be wrapped
    name : str
        The name of the new GLSL function that wraps *parent_function*
    **bound_args : tuple
        The name of each keyword argument must match one of the argument names
        for *parent_function*. The value is a tuple that specifies a new
        program variable to declare: 
        ('uniform'|'attribute'|'varying', name)
        This program variable will be used to supply the value to the
        corresponding input argument to *parent_function*.

    
    For example:
    
        func = Function('''
        vec4 transform(vec4 pos, mat4 matrix) {
            return vec4 matrix * pos;
        }
        ''')
        
        bound = BoundFunction(func, 
                              name='my_transform', 
                              matrix=('uniform', 'my_matrix'))
                              
    In this example, the BoundFunction *bound* calls the original Function 
    *func* using a new uniform variable *my_matrix* as the *matrix* argument.
    When *bound* is included in a CompositeProgram, the following code is
    generated:
    
        vec4 transform(vec4 pos, mat4 matrix) {
            return vec4 matrix * pos;
        }
        
        uniform mat4 my_matrix;
        vec4 my_transform(vec4 pos) {
            return transform(pos, my_matrix);
        }
    """
    def __init__(self, parent_function, name, bound_args):
        self._parent = parent_function
        self._name = name
        self._bound_arguments = bound_args
        
        Function.__init__(self)
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
        for bname, varspec in self._bound_arguments.items():
            vtype, vname = varspec
            dtype = self._parent.bindings[bname]
            code += "%s %s %s;\n" % (vtype, dtype, vname)
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
                args.append(self._bound_arguments[argname][1])
            else:
                args.append(argname)
        ret = "return " if self._parent.rtype is not 'void' else ""
        code += "    %s%s(%s);\n" % (ret, self._parent.name, ", ".join(args))
        
        code += "}\n"
        
        return code
        
    
class FunctionChain(Function):
    """
    Function subclass that generates GLSL code to call a list of Functions 
    in order. 
    
    Arguments:
    
    name : str
        The name of the generated function
    funcs : list of Functions
        The list of Functions that will be called by the generated GLSL code.
        
        
    Example:
    
        func1 = Function('void my_func_1() {}')
        func2 = Function('void my_func_2() {}')
        chain = FunctionChain('my_func_chain', [func1, func2])
        
    If *chain* is included in a CompositeProgram, it will generate the following
    output:
    
        void my_func_1() {}
        void my_func_2() {}
        
        void my_func_chain() {
            my_func_1();
            my_func_2();
        }

    The return type of the generated function is the same as the return type
    of the last function in the chain. Likewise, the arguments for the 
    generated function are the same as the first function in the chain.
    
    If the return type is not 'void', then the return value of each function
    will be used to supply the first input argument of the next function in
    the chain. For example:
    
        vec3 my_func_1(vec3 input) {return input + vec3(1, 0, 0);}
        void my_func_2(vec3 input) {return input + vec3(0, 1, 0);}
        
        vec3 my_func_chain(vec3 input) {
            return my_func_2(my_func_1(input));
        }
    
    """
    def __init__(self, name, funcs=()):
        Function.__init__(self)
        self._funcs = list(funcs)
        self._deps = list(funcs)
        self._code = None
        self.name = name
        self._update_signature()
        
    def _update_signature(self):
        funcs = self._funcs
        if len(funcs) > 0:
            self.rtype = funcs[-1].rtype
            self.args = funcs[0].args[:]
        else:
            self.rtype = 'void'
            self.args = []
        self._bindings = dict([(a[1], a[0]) for a in self.args])
        
    @property
    def code(self):
        """
        The GLSL code that defines this function.
        """
        if self._code is None:
            code = self.generate_function_code()
            self.set_code(code)
        return self._code

    def append(self, function):
        """ Append a new function to the end of this chain.
        """
        self._funcs.append(function)
        self._deps.append(function)
        self._update_signature()
        
    def insert(self, index, function):
        """ Insert a new function into the chain at *index*.
        """
        self._funcs.insert(index, function)
        self._deps.insert(index, function)
        self._update_signature()
        
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
        
        
class FunctionTemplate(object):
    """
    Template-based shader function generator. This allows to generate new 
    Function instances with a custom function name and with any custom
    program variable names substituted in. This has effectively the same
    functionality as Function.bind(), but avoids the use of wrapper
    functions.
    
    Arguments:
    
    template : str
        A template string used to construct Function instances.
        Uses string.Template formatting style ('$name' substitutions). 
        Must contain $func_name in place of the function name, and $var_name for 
        each variable declared in the *var_names* argument.
    bindings : list
        List of the variables that must be specified when calling bind(). Each
        variable is given as "type var_name".
    deps : list(Function)
        List of Functions that are required by this function.
        
    See bind() for more information about the construction of Functions
    from templates. 

    Example that converts a vec2 input variable to vec4:
    
        template = FunctionTemplate('''
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
    def __init__(self, template, bindings=(), deps=()):
        self.template = string.Template(Function.clean_code(template))
        self.deps = deps[:]
        self._bindings = {}
        for b in bindings:
            i = b.index(' ')
            b = (b[:i], b[i+1:])
            self._bindings[b[1]] = b[0]
        
        ## Do a fake replacement and parse for function signature
        ##  [removed; don't think this will be necessary..]
        subs = dict([(n, n) for n in self.bindings.keys() + ['func_name']])
        code = self.template.substitute(**subs)
        name, self.args, self.rtype = parsing.parse_function_signature(code)
        self.name = None

    @property
    def bindings(self):
        return self._bindings.copy()
        
    def bind(self, name, **kwds):
        """
        Return a Function whose code is constructed by the following 
        rules:
        
        * $func_name is replaced with the contents of the *name* argument
        * each keyword represents a program variable:
            
            template_name=('uniform|attribute|varying', type, name)
            
          The declaration for this variable will be automatically added to 
          the returned function code, and $template_name will be substituted
          with *name*.

        """
        var_names = self._bindings.keys()
        subs = {'func_name': name}
        code = ""
        for var_name, var_spec in kwds.items():
            var_names.remove(var_name)
            subs[var_name] = var_spec[1]
            if var_name in self._bindings:
                dtype = self._bindings[var_name]
                code += "%s %s %s;\n" % (var_spec[0], dtype, var_spec[1])
            else:
                raise KeyError("Variable name '%s' is not bindable. Bindings "
                               "are: %s" % (var_name, self._bindings.keys()))
        
        if var_names:
            raise Exception('Unsubstituted template variables in bind(%s): %s' % 
                            (name, var_names))
           
        code += self.template.substitute(**subs)
        return Function(code, deps=self.deps[:])



class FragmentFunction(object):
    """
    Function meant to be used in fragment shaders when some supporting 
    code must also be introduced to a vertex shader chain, usually to
    initialize one or more varyings.
    
    Parameters:
        frag_func : Function or FunctionTemplate
            To be bound in the fragment shader
        vert_func : Function or FunctionTemplate
            To be included in the vertex shader chain given by *vert_hook*
        link_vars : list of tuples
            Each tuple indicates (type, vertex_var, fragment_var) variables that 
            should be bound to the same varying.
        vert_hook : str
            Name of the vertex shader function chain to which vert_callback 
            should be added. Default is 'vert_post_hook'.
    
    """
    def __init__(self, fragment_func, vertex_func, 
                 link_vars, vert_hook='vert_post_hook'):
        self.frag_func = fragment_func
        self.vert_func = vertex_func
        self.link_vars = link_vars
        self._vert_hook = vert_hook
        
        for vname, fname in link_vars:
            vtype = vertex_func.bindings.get(vname, None)
            ftype = fragment_func.bindings.get(fname, None)
            if vtype is None:
                raise NameError("Variable name '%s' is not bindable in vertex "
                                "shader. Names are: %s" %
                                (vname, vertex_func.bindings.keys()))
            if ftype is None:
                raise NameError("Variable name '%s' is not bindable in fragment"
                                " shader. Names are: %s" %
                                (fname, fragment_func.bindings.keys()))
            if vtype != ftype:
                raise TypeError("Linked variables '%s' and '%s' must have the"
                                "same type. (types are %s, %s)" % 
                                (vname, fname, vtype, ftype))

    def bind(self, name, **kwds):
        """
        * bind both this function and its vertex shader component to new functions
        * automatically bind varyings        
        """
        # separate kwds into fragment variables and vertex variables
        # TODO: should this be made explicit in the bind() arguments, or
        #       can we just require that the vertex and fragment functions 
        #       never have the same variable names?
        frag_vars = {}
        vert_vars = {}
        
        # add varyings to each
        for vname, fname in self.link_vars:
            # This is likely to be a unique name...
            var_type = self.vert_func.bindings[vname]
            var_name = "%s_%s_%s_var" % (name, vname, fname)
            var = ('varying', var_name)
            vert_vars[vname] = var
            frag_vars[fname] = var
        
        # TODO: this is a little sketchy.. can we always unambiguously decide
        # which variable goes to which function, or should this be made more
        # explicit?
        for bind_name in kwds:
            if bind_name not in frag_vars and bind_name in self.frag_func.bindings:
                frag_vars[bind_name] = kwds[bind_name]
            elif bind_name in self.vert_func.bindings:
                vert_vars[bind_name] = kwds[bind_name]
            else:
                raise KeyError("The name '%s' is not bindable in %s" %
                               (bind_name, self))
                    
        
        
        # bind both functions
        frag_bound = self.frag_func.bind(name, **frag_vars)
        
        # also likely to be a unique name...
        vert_name = name + "_support"
        vert_bound = self.vert_func.bind(vert_name, **vert_vars)
        
        frag_bound._callbacks.append((self._vert_hook, vert_bound))
        
        # make it easy to access the vertex support function
        # to assign variables.
        frag_bound.fragment_support = vert_bound
        
        return frag_bound

