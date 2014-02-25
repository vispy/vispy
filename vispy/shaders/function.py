# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division
import string
import logging
import random
import re

from . import parsing


class Function(object):
    """
    This class represents a single function in GLSL. Its *code* property 
    contains the entire GLSL code of the function as well as any program
    variable declarations it depends on. Functions also have a list
    of dependencies, which are other Functions that must be included
    in the program because they are called from this function.
    
    A ModularProgram generates its code by concatenating the *code* property
    of multiple Functions and their dependencies; each function is
    included exactly once, even if it is depended upon multiple times.
    """    
    #def __init__(self, code=None, name=None, args=None, rtype=None, deps=None,
                 #variables=None):
        #"""
        #Arguments:
        
        #code : str
        #name : None or str
            #The name of the function as defined in *code*.
            #If None, this value will be automatically parsed from *code*.
        #args : None or list of tuples
            #Describes the arguments accepted by this function.
            #Each tuple contains two strings ('type', 'name').
            #If None, this value will be automatically parsed from *code*.
        #rtype : None or str
            #String indicating the return type of the function.
            #If None, this value will be automatically parsed from *code*.
        #deps : None or list of Functions
            #Lists functions that are called by this function, and therefore must
            #be included by a ModularProgram when compiling the complete
            #program.
        #variables : None or dict
            #Dict describing program variables declared in this function's code.
            #See variable_names property.
        #"""
        #self._name = None
        #self._template_name = None
        #self.rtype = None
        #self.args = None
        #self.template_vars = {}
        
        #self._set_code(code, name, args, rtype, variables)
        #self._deps = deps[:] if deps is not None else []
        #self._program_values = {}    # values for attribute/uniforms carried by this function;
                                     ## will be set on any ModularProgram the function is
                                     ## attached to.
        #self._template_cache = None  # stores a string.Template object
        #self._callbacks = []         # Functions that should be installed on a
                                     ## particular ModularProgram hook.
                                     
                                     
    def __init__(self, code=None, deps=()):
        if code is not None and not isinstance(code, basestring):
            raise ValueError("code argument must be string or None (got %s)" % type(code))
        self._code = code
        self._deps = deps
        self._signature = None
        self._program_vars = None  # variables defined in the program code
        self._program_values = {}
        self._template_vars = None # template variables used in the program code (excluding the function name)
        self._callbacks = []
        self._str_template = None
        
    @property
    def code(self):
        """
        The GLSL code that defines this function. Does not include dependencies,
        program variables, hooks, etc. (see also: generate_code())
        """
        return self._code
    
    @property
    def name(self):
        """
        Function name as given in the code.
        
        Anonymous functions have name starting with $
        """
        return self.signature[0]

    @property
    def is_anonymous(self):
        """ Indicates whether this is an anonymous function (the function name
        begins with "$". Anonymous functions must be wrapped before they can
        be used in a program."""
        return self.name.startswith('$')
    
    @property
    def args(self):
        """
        [(arg_name, arg_type), ...]
        """
        return self.signature[1]

    @property
    def rtype(self):
        """
        Return type of this function.
        
        """
        return self.signature[2]

    @property
    def signature(self):
        """
        Function signature; (name, args, return_type)
        
        """
        if self._signature is None:
            self._parse_signature()
        return self._signature
    
    @property
    def template_vars(self):
        """
        List of all template variables in the code.
        
        """
        if self._template_vars is None:
            self._parse_template_vars()
        return self._template_vars
    
    @property
    def program_vars(self):
        """
        dict of program variables declared by this code
        {var_name: (vtype, dtype)}
        
        """
        if self._program_vars is None:
            self._parse_program_vars()
        return self._program_vars
        
    @property
    def deps(self):
        """
        List of dependencies for this function.
        
        """
        return self._deps
        
    #@property
    #def name(self):
        #return self._name
    
    #@name.setter
    #def name(self, n):
        #if self._name is not None:
            #raise Exception('Cannot rename function "%s" to "%s".' % (self._name, n))
        #self._name = n
    
    #@property
    #def bindings(self):
        #"""
        #Dict of {name: type} pairs describing function arguments that may be 
        #bound to new program variables.
        
        #The names are the allowed keyword arguments to bind().
        
        #For normal Function instances, bindings are simply the function 
        #arguments. 
        #"""
        #return self._bindings
        
    @property
    def callbacks(self):
        """
        List of (hook, function) pairs.
        
        When this function is added to a program, each pair will cause
        program.add_callback(hook, function) to be called.
        """
        return self._callbacks

    @property
    def _template(self):
        if self._str_template is None:
            self._str_template = string.Template(Function.clean_code(self.code))
        return self._str_template
        

    #def _set_code(self, code, name=None, args=None, rtype=None, variables=None,
                 #template_vars=None):
        #"""
        #Set the GLSL code for this function.
        
        #Optionally, the name, arguments, and return type may be specified. If
        #these are omitted, then the values will be automatically parsed from
        #the code.
        #"""
        #if code is None:
            #self._code = self.args = self.rtype = None
            #return
        
        #self._code = self.clean_code(code)
        #if name is None:
            #self._parse_code(code)
            
        #else:
            #self.name = name
            #self.args = args
            #self.rtype = rtype
            #self.template_vars = None
            
        
        ## May bind both function arguments and template variables
        ##self._bindings = dict([(a[1], a[0]) for a in self.args])
        ##self._bindings.update(self.template_vars)
            
        #if variables is None:
            #self.variables = parsing.find_program_variables(self.code)
        #else:
            #self.variables = variables
            
        #self._arg_types = dict([(a[1], a[0]) for a in self.args])
        
    def _parse_signature(self):
        # Search code for function signature and template variables
        name, args, rtype = parsing.parse_function_signature(self.code)
        self._signature = (name, args, rtype)
        
    def _parse_template_vars(self):        
        self._template_vars = {}
        for var in parsing.find_template_variables(self.code):
            if var == self.name:
                continue
            vname = var.lstrip('$')
            self._template_vars[vname] = VariableReference(self, vname)

    def _parse_program_vars(self):
        raise NotImplementedError

    #def resolve(self, name=None):
        #"""
        #Return a new Function that wraps this function, using program 
        #variables to supply input to some of its arguments.
        
        #This is analogous to python bound methods, where the first argument
        #is automatically supplied (but in this case, any argument(s) may be
        #bound to uniforms/attributes/varyings).
        
        #The primary purpose of this is to allow multiple instances of the same
        #Function to be used in the final program, where each instance
        #generates a new bound function with unique attribute/uniform inputs. 
        
        #Keyword arguments are used to bind specific function arguments; each
        #must be a string specifying the program variable that will supply
        #the value to that argument, or (uniform|attribute|varying) to specify
        #that the variable should be generated automatically. 
        
        #For example, if the original function looks like:
        
            #vec4 my_function(float a, vec2 b, vec3 c) { ... }
            
        #Then the following bind call:
        
            #func.bind(name='new_func_name', 
                      #b=('uniform', 'vec2', 'input_b'), 
                      #c=('attribute', 'vec3', 'input_c'))
                      
        #Would return a Function with the following code:
        
            #uniform vec2 input_b;
            #attribute vec3 input_c;
            #vec4 new_func_name(float a) {
                #return my_function(a, input_b, input_c);
            #}
        
        #"""
        #if self.is_anonymous:
            ## Decide which kwds refer to arguments and which refer to template variables:
            #sub_kwds = {}
            #arg_kwds = {}
            #for vname,val in kwds.items():
                #if vname in self.template_vars:
                    #sub_kwds[vname] = val
                #else:
                    #arg_kwds[vname] = val
            
            ## Do template substitutions now if necessary
            #if name is not None or len(sub_kwds) > 0:
                #wrapper = self._wrap_template(name, **kwds)
            #else:
                #wrapper = self
            
            ## Bind arguments if necessary
            #if len(arg_kwds) > 0:
                #wrapper = BoundFunction(wrapper, name, arg_kwds)
                
            #return wrapper
        #else:
            ## create a function wrapper
            #if name is None:
                #name = "$func_name" # no name specified; make the new function anonymous.
            #return BoundFunction(self, name, kwds)

    #def compile(self, program, name=None):
        #"""
        #Generate the complete code, including all dependencies, that defines
        #this function. Returns (func_name, code).
        
        #The *program_ns* argument is a dict containing all globally declared
        #names in the program, whereas *shader_ns* contains names declared
        #in the shader. This method is responsible for adding new names
        #to both namespaces as needed and for ensuring that previously-declared
        #names are not redeclared.
        
        #For program varibles, program_ns[var] must be (vtype, dtype, data); this
        #will be used to assign data to the program after it is compiled.
        
        #If supplied, *name* determines the name that must be assigned to this 
        #function in the returned code.
        #"""
        
        ## First decide on a name for this function
        #if not self.is_anonymous:
            #if name is not None and name != self.name:
                #raise Exception("Function already has name '%s'; cannot use " 
                                #"requested name '%s'" % (self.name, name))
            
            #name = self.name
            
        #if name is None:
            ## free to choose a suitable name.
            #func_name = self.name.lstrip('$')
            
            ## Add to namespace, possibly changing name to ensure uniqueness.
            #func_name = self.add_to_namespace(program_ns, func_name, self)
            #shader_ns[func_name] = self
            
            
        #else:
            ## Must use the given name
            #if name in program_ns and program_ns[name] is not self:
                #raise Exception("Program namespace already has a different "
                                #"Function named %s." % name)
            #program_ns[name] = self
            #shader_ns[name] = self
            #func_name = name
            
        #template_subs = {}  # accumulates necessary template substitutions
        #if self.is_anonymous:
            #template_subs[self.name.lstrip('$')] = func_name
            
            
        
        ## Visit all dependencies, begin assembling code and values
        #dep_names, code = self._compile_deps(program_ns, shader_ns, func_name)

        
        ## Select template variable names based on function name
        #var_names = {}
        #code += "\n"
        #for name, spec in self._program_values.items():
            #if isinstance(spec, VariableReference):
                ## TODO: look up variable in the current namespace
                ## What do do if it is not defined yet?? Need to re-assign 
                ## the referenced variable as a named variable?
                ##    no; need to remember the original assignment for future use.
                ##    Maybe leave the referenced variable as-is?
                ##        - What if it is anonymous? need to assign a name just
                ##          for this compilation!
                    
                #raise NotImplementedError
            #if len(spec) == 2:
                #spec = spec + (None,)
            #vtype, dtype, data = spec
            
            ## Decide based on spec whether this variable is already assigned to
            ## a specific program variable name
            #if vtype == 'varying':
                #var_name = data
                #anonymous = data is None
            #else:
                #if isinstance(data, basestring):
                    #var_name = data
                    #anonymous = False
                #else:
                    #var_name = name
                    #anonymous = True
            
            #if anonymous:
                #var_name = self.add_to_namespace(program_ns, var_name, spec)
                #added = True
            #else:
                #if var_name in namespace:
                    #if namespace[var_name] is spec:
                        #pass # already have this variable and the correct data
                    #else:
                        #raise Exception("Cannot declare program variable %s as %s; "
                                        #"already declared as %s." % 
                                        #(var_name, spec, namespace[var_name]))
                    #added = False
                #else:
                    #namespace[var_name] = spec
                    #added = True
            
            #if added:
                ## declare new variable and add to namespace.
                #code += '%s %s %s;\n' % (vtype, dtype, var_name)
            
            #var_names[name] = var_name
            #template_subs[name] = var_name
        
        #code += self._generate_code(template_subs, dep_names)
        
        #return CompileResult(self, code, func_name, var_names)
        
    def compile(self, template_subs, dep_names):
        """
        Generate the final code for this function (excluding dependencies)
        using the given template substitutions. *dep_names* contains {dep: name}
        for each dependency and may be used by subclasses to modify the final 
        code.
        """
        if len(template_subs) > 0:
            try:
                return self._template.substitute(**template_subs)
            except KeyError as err:
                raise KeyError("Must specify variable $%s in substitution" % 
                            err.args[0])

    def _compile_deps(self, program, func_name):
        """
        Compile each dependency, return a dict of {name: dep} pairs and a single
        concatenated code string.
        """
        code = ""
        dep_names = {} # keep track of the names of our dependencies in case
                       # we need to modify the code to match
        for dep in self.deps:
            n, c = dep.compile(program)
            code += c + "\n"
            dep_names[dep] = n
        
        return dep_names, code
     
    def wrap(self, name=None, **kwds):
        """
        Create a wrapper function that calls this function with any of its
        arguments filled in ..
        
        """
        raise NotImplementedError
     
    def set_value(self, name, spec):
        if name not in self.template_vars:
            raise NameError("Variable '%s' does not exist in this function." 
                            % name)
        self._program_values[name] = spec
        
     
    def __setitem__(self, var, value):
        """
        Set the value of a program variable declared in this function's code.
        
        Any ModularProgram that depends on this function will automatically
        apply the variable when it is activated.
        """
        self.set_value(var, value)

    def __getitem__(self, var):
        """
        Return a reference to a program variable from this function.
        
        This allows variables between functions to be linked together::
        
            func1['var_name'] = func2['other_var_name']
            
        In the example above, the two local variables would be assigned to the 
        same program variable whenever func1 and func2 are attached to the same 
        program.
        """
        return VariableReference(self, var)

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
    
    @staticmethod
    def add_to_namespace(ns, name, value):
        """
        Add *value* to the namespace *ns*, using *name* if possible, or 
        modifying *name* if needed to ensure a unique name. 
        The final chosen name is returned.
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
        ns[name] = value
        return name
    
    @staticmethod
    def shorten(name):
        """
        Make a name 31 characters or less. (longer names are not allowed in 
        GLSL)
        """
        if len(name) < 32:
            return name
        
        #name = name.translate(None, 'aeiou')
        #if len(name) < 32:
            #TODO: check for '__'
            #return name

        chars = string.ascii_uppercase
        rand = ''.join([random.choice(chars) for i in range(10)])
        if name[-20] == '_':
            return rand + name[-20:]
        else:
            return rand + "_" + name[-20:]
        
        
        
    #def _process_template(self, name, vars):
        #"""
        #Return a Function whose code is constructed by the following 
        #rules:
        
        #* $func_name is replaced with the contents of the *name* argument,
          #if it is supplied.
        #* each keyword represents a program variable::
            
              #template_name=('uniform|attribute|varying', type, name)
            
          #The declaration for this variable will be automatically added to 
          #the returned function code, and $template_name will be substituted
          #with *name*.

        #"""
        #var_names = self.template_vars.keys()
        #subs = {self.name[1:]: name} #if name is not None else {}
        #code = ""
        #for var_name, var_spec in kwds.items():
            #vtype, dtype, prog_var_name = var_spec
            #var_names.remove(var_name)
            ##template_var = self.template_vars[var_name] + "_" + var_name
            #subs[var_name] = prog_var_name
            #if var_name in self.template_vars:
                #dtype = self.template_vars[var_name]
                #code += "%s %s %s;\n" % (var_spec[0], dtype, var_spec[1])
            #else:
                #raise KeyError("'%s' is not a template variable. Variables "
                               #"are: %s" % (var_name, self._template_vars.keys()))
        
        #if var_names:
            #raise Exception('Unsubstituted template variables in resolve(%s): %s' % 
                            #(name, var_names))
           
        #try:
            #code += self._template.safe_substitute(**subs)
        #except KeyError as exc:
            #print("--------",self._template)
            #print(self.code)
            #print(kwds)
            #print(subs)
            #raise
        #return Function(code, deps=self._deps[:])

class VariableReference(object):
    """
    References a program variable from a function.
    
    """
    def __init__(self, function, name):
        self.function = function
        self.name = name
        
    @property
    def vtype(self):
        return self.function._program_values[self.name][0]
    
    @property
    def dtype(self):
        return self.function._program_values[self.name][1]
    
class CompileResult(object):
    """
    Stores the results of a call to Function.compile(), including the complete
    code, function name, and variable name assignments.    
    """
    def __init__(self, function, code, name, variables):
        self.function = function
        self.code = code
        self.name = name
        self.variables = variables
    
#class BoundFunction(Function):
    #"""
    #A BoundFunction is a wrapper around a Function that 'binds' zero or more 
    #of the function's input arguments to program variables.
    
    #Arguments:
    #parent_function : Function instance
        #The Function to be wrapped
    #name : str
        #The name of the new GLSL function that wraps *parent_function*
    #**bound_args : tuple
        #The name of each keyword argument must match one of the argument names
        #for *parent_function*. The value is a tuple that specifies a new
        #program variable to declare: 
        #('uniform'|'attribute'|'varying', name)
        #This program variable will be used to supply the value to the
        #corresponding input argument to *parent_function*.

    
    #For example:
    
        #func = Function('''
        #vec4 transform(vec4 pos, mat4 matrix) {
            #return vec4 matrix * pos;
        #}
        #''')
        
        #bound = BoundFunction(func, 
                              #name='my_transform', 
                              #matrix=('uniform', 'my_matrix'))
                              
    #In this example, the BoundFunction *bound* calls the original Function 
    #*func* using a new uniform variable *my_matrix* as the *matrix* argument.
    #When *bound* is included in a ModularProgram, the following code is
    #generated:
    
        #vec4 transform(vec4 pos, mat4 matrix) {
            #return vec4 matrix * pos;
        #}
        
        #uniform mat4 my_matrix;
        #vec4 my_transform(vec4 pos) {
            #return transform(pos, my_matrix);
        #}
    #"""
    #def __init__(self, parent_function, name, bound_args):
        #self._parent = parent_function
        #self._name = name
        #self._bound_arguments = bound_args
        
        #Function.__init__(self)
        #self._deps.append(self._parent)
        #self._set_code(self.generate_function_code())

    #@property
    #def code(self):
        #"""
        #The GLSL code that defines this function.
        #"""
        #if self._code is None:
            #code = self.generate_function_code()
            #self._set_code(code)
        #return self._code
        
    #def generate_function_code(self):
        #code = ""
        
        ## Generate attribute/uniform declarations
        #for bname, varspec in self._bound_arguments.items():
            #vtype, vname = varspec
            #dtype = self._parent.bindings[bname]
            #code += "%s %s %s;\n" % (vtype, dtype, vname)
        #code += "\n"
        
        ## new function signature
        #fn_args = self._parent.args
        #arg_defs = ["%s %s" % x for x in fn_args[:] if x[1] not in self._bound_arguments]
        #new_sig = ", ".join(arg_defs)
        #code += "%s %s(%s) {\n" % (self._parent.rtype, self._name, new_sig)
        
        ## call original function
        #args = []
        #for dtype, argname in fn_args:
            #if argname in self._bound_arguments:
                #args.append(self._bound_arguments[argname][1])
            #else:
                #args.append(argname)
        #ret = "return " if self._parent.rtype is not 'void' else ""
        #code += "    %s%s(%s);\n" % (ret, self._parent.name, ", ".join(args))
        
        #code += "}\n"
        
        #return code
        
    
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
        
    If *chain* is included in a ModularProgram, it will generate the following
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
    def __init__(self, name=None, funcs=()):
        Function.__init__(self)
        self._funcs = list(funcs)
        self._deps = list(funcs)
        self._code = None
        self._update_signature()
        
    @property
    def name(self):
        return "$chain"

    @property
    def signature(self):
        return self.name, self._args, self._rtype
    
    def _update_signature(self):
        funcs = self._funcs
        if len(funcs) > 0:
            self._rtype = funcs[-1].rtype
            self._args = funcs[0].args[:]
        else:
            self._rtype = 'void'
            self._args = []
        #self._bindings = dict([(a[1], a[0]) for a in self.args])
        
    @property
    def code(self):
        """
        The GLSL code that defines this function.
        """
        raise NotImplementedError
        #if self._code is None:
            #code = self._generate_code()
            #self._code = code
        #return self._code

    def append(self, function):
        """ Append a new function to the end of this chain.
        """
        self._funcs.append(function)
        self._deps.append(function)
        self._update_signature()
        self._code = None
        
    def insert(self, index, function):
        """ Insert a new function into the chain at *index*.
        """
        self._funcs.insert(index, function)
        self._deps.insert(index, function)
        self._update_signature()
        self._code = None

    def _generate_code(self, subs, dep_names):
        args = ", ".join(["%s %s" % arg for arg in self.args])
        name = subs[self.name.lstrip('$')]
        code = "%s %s(%s) {\n" % (self.rtype, name, args)
        
        if self.rtype == 'void':
            for fn in self._funcs:
                code += "    %s();\n" % dep_names[fn]
        else:
            code += "    return "
            for fn in self._funcs[::-1]:
                code += "%s(\n           " % dep_names[fn]
            code += "    %s%s;\n" % (self.args[0][1], ')'*len(self._funcs))
        
        code += "}\n"
        return code
        
    def _compile_deps(self, func_name, namespace):
        """
        Compile each dependency, return a dict of {name: dep} pairs and a single
        concatenated code string.
        """
        code = ""
        dep_names = {} # keep track of the names of our dependencies in case
                       # we need to modify the code to match
        for i, dep in enumerate(self.deps):
            #if dep.is_anonymous:
                #name = func_name + "_" + dep.name.lstrip('$') + "_" + str(i)
            #else:
                #name = None
                
            n, c = dep.compile(namespace)
            code += c + "\n"
            dep_names[dep] = n
        
        return dep_names, code
        
#class FunctionTemplate(object):
    #"""
    #Template-based shader function generator. This allows to generate new 
    #Function instances with a custom function name and with any custom
    #program variable names substituted in. This has effectively the same
    #functionality as Function.bind(), but avoids the use of wrapper
    #functions.
    
    #Arguments:
    
    #template : str
        #A template string used to construct Function instances.
        #Uses string.Template formatting style ('$name' substitutions). 
        #Must contain $func_name in place of the function name, and $var_name for 
        #each variable declared in the *var_names* argument.
    #bindings : list
        #List of the variables that must be specified when calling bind(). Each
        #variable is given as "type var_name".
    #deps : list(Function)
        #List of Functions that are required by this function.
        
    #See bind() for more information about the construction of Functions
    #from templates. 

    #Example that converts a vec2 input variable to vec4:
    
        #template = FunctionTemplate('''
            #vec4 $func_name() {
                #return vec4($input, 0, 1);
            #}
        #''', var_names=['input'])
        
        #func = template.bind(name='my_function', 
                             #input=('uniform', 'vec2', 'my_input_uniform'))
                             
    #If we include *func* in a ModularProgram, it will generate the following 
    #code:
    
        #uniform vec2 my_input_uniform;
        #vec4 my_function() {
            #return vec4(my_input_uniform, 0, 1);
        #}
        
    #"""
    #def __init__(self, template, bindings=(), deps=()):
        #self.template = string.Template(Function.clean_code(template))
        #self.deps = deps[:]
        #self._bindings = {}
        #for b in bindings:
            #i = b.index(' ')
            #b = (b[:i], b[i+1:])
            #self._bindings[b[1]] = b[0]
        
        ### Do a fake replacement and parse for function signature
        ###  [removed; don't think this will be necessary..]
        #subs = dict([(n, n) for n in self.bindings.keys() + ['func_name']])
        #code = self.template.substitute(**subs)
        #name, self.args, self.rtype = parsing.parse_function_signature(code)
        #self.name = None

    #@property
    #def bindings(self):
        #return self._bindings.copy()
        



class FragmentFunction(Function):
    """
    Function meant to be used in fragment shaders when some supporting 
    code must also be introduced to a vertex shader chain, usually to
    initialize one or more varyings.
    
    Parameters:
        code : Function code to be used in the fragment shader
        vert_func : Function or FunctionTemplate
            To be included in the vertex shader chain given by *vert_hook*
        link_vars : list of tuples
            Each tuple indicates (type, vertex_var, fragment_var) variables that 
            should be bound to the same varying.
        vert_hook : str
            Name of the vertex shader function chain to which vert_callback 
            should be added. Default is 'vert_post_hook'.
        **kwds : passed to Function.__init__
    
    """
    def __init__(self, code, vertex_func, 
                 link_vars, vert_hook='vert_post_hook', **kwds):
        
        super(FragmentFunction, self).__init__(code, **kwds)
        
        self.vert_func = vertex_func
        self.link_vars = link_vars
        self._vert_hook = vert_hook
        
        # TODO: resurrect this
            #for vname, fname in link_vars:
                #vtype = self.vert_func.bindings.get(vname, None)
                #ftype = self.bindings.get(fname, None)
                #if vtype is None:
                    #raise NameError("Variable name '%s' is not bindable in vertex "
                                    #"shader. Names are: %s" %
                                    #(vname, self.vert_func.bindings.keys()))
                #if ftype is None:
                    #raise NameError("Variable name '%s' is not bindable in fragment"
                                    #" shader. Names are: %s" %
                                    #(fname, self.bindings.keys()))
                #if vtype != ftype:
                    #raise TypeError("Linked variables '%s' and '%s' must have the"
                                    #"same type. (types are %s, %s)" % 
                                    #(vname, fname, vtype, ftype))

    def resolve(self, name, **kwds):
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
            var_type = self.bindings[fname]
            var_name = "%s_%s_%s_var" % (name, vname, fname)
            var = ('varying', var_name)
            vert_vars[vname] = var
            frag_vars[fname] = var
        
        # TODO: this is a little sketchy.. can we always unambiguously decide
        # which variable goes to which function, or should this be made more
        # explicit?
        for bind_name in kwds:
            if bind_name not in frag_vars and bind_name in self.bindings:
                frag_vars[bind_name] = kwds[bind_name]
            elif bind_name in self.vert_func.bindings:
                vert_vars[bind_name] = kwds[bind_name]
            else:
                raise KeyError("The name '%s' is not bindable in %s" %
                               (bind_name, self))
                    
        
        
        # bind both functions
        frag_bound = super(FragmentFunction, self).resolve(name, **frag_vars)
        
        # also likely to be a unique name...
        vert_name = name + "_support"
        vert_bound = self.vert_func.resolve(vert_name, **vert_vars)
        
        frag_bound._callbacks.append((self._vert_hook, vert_bound))
        
        # make it easy to access the vertex support function
        # to assign variables.
        frag_bound.fragment_support = vert_bound
        
        return frag_bound

