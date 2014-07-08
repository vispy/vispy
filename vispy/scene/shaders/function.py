# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division
import string

from . import parsing
from ...util.event import EmitterGroup, Event
from ...ext.six import string_types


class ShaderObject(object):
    """
    Base class for objects that may appear in a GLSL shader (functions and
    variables). This class defines the interface used by ModularProgram to
    compile multiple objects together into a single program.
    """
    def __init__(self):
        self.events = EmitterGroup(source=self, update=Event)

    @property
    def is_anonymous(self):
        """
        Indicates whether this object may be assigned a new name.
        """
        raise NotImplementedError

    @property
    def name(self):
        """
        The name of this object. If this object is anonymous, then the name
        is only used as a suggestion when compiling a program.
        """
        raise NotImplementedError

    @property
    def dependencies(self):
        """
        A collection of objects that must be defined before this object.
        """
        raise NotImplementedError

    def compile(self, object_names):
        """
        Return complete GLSL code needed to implement this object in a program.

        *object_names* is a dict that maps ShaderObjects to the names
        they have been assigned in a program. The generated code must make
        use of these names when referring to other objects, as well as for
        determining its own name.

        """
        raise NotImplementedError

    def update(self):
        """
        Inform the object (and all listeners of events.update) that this
        object has changed.
        """
        self.events.update()


class Variable(ShaderObject):
    """
    References a program variable from a function.

    Created by Function.__getitem__
    """
    def __init__(self, function, name, spec=None, anonymous=False):
        self._state_counter = 0
        super(Variable, self).__init__()
        self.function = function
        self._name = name  # local name within the function
        self._spec = None  # (vtype, dtype, value)
        if spec is not None:
            self.spec = spec
        self.anonymous = anonymous  # if True, variable may be renamed.

    @property
    def is_anonymous(self):
        return self.anonymous

    @property
    def name(self):
        return self._name

    @property
    def dependencies(self):
        return ()

    def compile(self, obj_names):
        name = obj_names.get(self, self.name)
        if not self.is_anonymous and name != self.name:
            raise Exception("Cannot compile %s with name %s; variable "
                            "is not anonymous." % (self, name))
        return "%s %s %s;" % (self.vtype, self.dtype, name)

    @property
    def vtype(self):
        if self.spec is None:
            raise Exception("%s has not been assigned; cannot "
                            "determine vtype." % self)
        return self.spec[0]

    @property
    def dtype(self):
        if self.spec is None:
            raise Exception("%s has not been assigned; cannot "
                            "determine dtype." % self)
        return self.spec[1]

    @property
    def value(self):
        if self.spec is None:
            raise Exception("%s has not been assigned; cannot "
                            "determine value." % self)
        return self.spec[2]

    @property
    def spec(self):
        return self._spec
    
    @spec.setter
    def spec(self, s):
        self._spec = s
        self._state_counter += 1
        
    @property
    def state_id(self):
        """Return a unique ID that changes whenever the state of the Variable
        has changed. This allows ModularProgram to quickly determine whether
        the value has changed since it was last used."""
        return id(self), self._state_counter

    def __repr__(self):
        return ("<Variable '%s' on %s (%d)>" %
                (self.name, self.function.name, id(self)))


class Function(ShaderObject):
    """
    This class represents a single function in GLSL. Its *code* property
    contains the entire GLSL code of the function as well as any program
    variable declarations it depends on. Functions also have a list
    of dependencies, which are other Functions that must be included
    in the program because they are called from this function.

    A ModularProgram generates its code by concatenating the *code* property
    of multiple Functions and their dependencies; each function is
    included exactly once, even if it is depended upon multiple times.

    The function code may contain $template_variables in place of the function
    name or in place of uniform/attribute/varyings. In this case, the function
    or variable may be assigned a new name when it is compiled with a
    ModularProgram to ensure uniqueness.

    Parameters:
        code : str
            The GLSL code for this Function.
        deps : [list of Functions]
            All functions which may be called by this Function.
    """
    def __init__(self, code=None, deps=()):
        super(Function, self).__init__()
        if code is not None and not isinstance(code, string_types):
            raise ValueError("code argument must be string or None (got %s)"
                             % type(code))
        self._code = code
        self._deps = deps
        self._signature = None
        self._anonymous = None

        # Variable instance assigned to each program variable.
        self._variables = {}  # {'local_var_name': Variable}

        # Set of program variables defined in the program code
        # TODO: not implemented yet; for now all program variables are
        # implemented as template variables.
        #self._program_vars = None

        # Set of template variables used in the program code
        # (excluding the function name)
        self._template_vars = None

        # List of (hook_name, function) pairs indicating functions that must
        # be installed on a particular hook to provide support for this
        # function.
        # TODO: Might remove this. It was previously used by FragmentFunction,
        # which is now out of service.
        self._callbacks = []

        # Cache of string.Template(self.code)
        self._str_template = None

    @property
    def code(self):
        """
        The GLSL code that defines this function. Does not include
        dependencies, program variables, hooks, etc.
        """
        return self._code

    @property
    def name(self):
        """
        Function name as given in the code.
        """
        return self.signature[0]

    @property
    def is_anonymous(self):
        """ Indicates whether this is an anonymous function (the function name
        begins with "$". Anonymous functions may be renamed when included in a
        ModularProgram."""
        return self._anonymous

    @property
    def dependencies(self):
        """List of all Functions and Variables required by this
        Function."""
        deps = list(self._deps)
        for k in self.template_vars:
            deps.append(self[k])
        return deps

    @property
    def args(self):
        """
        List of input arguments in the function signature::

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
        Set of all template variables in the code, excluding the function
        name.
        """
        if self._template_vars is None:
            self._parse_template_vars()
        return self._template_vars

    #@property
    #def program_vars(self):
        #"""
        #dict of program variables declared statically by this code.
        #{var_name: (vtype, dtype)}
        #"""
        #if self._program_vars is None:
        #    self._parse_program_vars()
        #return self._program_vars

    @property
    def function_deps(self):
        """
        List of Functions required by this function.
        """
        return self._deps

    # TODO: remove or resurrect?
    #@property
    #def callbacks(self):
        #"""
        #List of (hook, function) pairs.

        #When this function is added to a program, each pair will cause
        #program.add_callback(hook, function) to be called.
        #"""
        #return self._callbacks

    @property
    def _template(self):
        # string.Template instance used to compile code with new function /
        # variable names.
        if self._str_template is None:
            self._str_template = \
                string.Template(Function.clean_code(self.code))
        return self._str_template

    def _parse_signature(self):
        # Search code for function signature and template variables
        name, args, rtype = parsing.parse_function_signature(self.code)
        anon = name.startswith('$')
        if anon:
            name = name[1:]
        self._anonymous = anon

        self._signature = (name, args, rtype)

    def _parse_template_vars(self):
        # find all template variables in self.code, excluding the function
        # name.
        self._template_vars = set()
        for var in parsing.find_template_variables(self.code):
            var = var.lstrip('$')
            if var == self.name:
                continue
            self._template_vars.add(var)

    #def _parse_program_vars(self):
        ## should find all statically-defined program variables and populate
        ## self._program_vars
        #raise NotImplementedError

    def compile(self, obj_names):
        """
        Generate the final code for this function (excluding dependencies)
        using the given name and object name mappings.
        """
        name = obj_names.get(self, self.name)
        subs = {}
        if self.is_anonymous:
            subs[self.name] = name
        elif name != self.name:
            raise Exception("Cannot compile non-anonymous function %s with "
                            "new name %s." % (self, name))

        for name in self.template_vars:
            var = self[name]
            try:
                subs[name] = obj_names[var]
            except KeyError:
                raise Exception("Cannot compile function %s; Variable %s has "
                                "no name assignment." % (self, var))

        try:
            code = self._template.substitute(**subs)
            return self.clean_code(code)
        except KeyError as err:
            raise KeyError("Must specify variable $%s in substitution" %
                           err.args[0])

    def wrap(self, name=None, **kwds):
        """
        Create a wrapper function that calls this function with any of its
        arguments filled in ..

        """
        raise NotImplementedError

    def __setitem__(self, name, spec):
        """
        Set the value of a variable declared in this function's code.
        Any ModularProgram that depends on this function will automatically
        apply the variable when it is activated.

        Must provide a complete specification of the variable. Examples:

            function['position_a'] = ('attribute', 'vec4', VertexBuffer(...))
            function['color_u'] = ('uniform', 'vec4', (1, 0, 0, 1))
            function['color_v'] = ('varying', 'vec4')

        Note that *name* refers to the locally defined variable name; this may
        be represented by a program variable of a different name when the
        Function is compiled.

        It is also possible to assign one variable to another to ensure
        they refer to the same program variable:

            vert_func['color_ouptut'] = ('varying', 'vec4')
            frag_func['color_input'] = vert_func['color_ouptut']
        """
        if name in self.template_vars:
            anon = True
        elif name in self.program_vars:
            anon = False
        else:
            raise NameError("Variable '%s' does not exist in this function."
                            % name)

        if isinstance(spec, ShaderObject):
            if name in self._variables:
                if self._variables[name] is spec:
                    return
                raise Exception("Cannot assign variable to %s; already "
                                "assigned to %s."
                                % (spec, self._variables[name]))
            self._variables[name] = spec
        else:
            if name in self._variables:
                self._variables[name].spec = spec
            else:
                ref = Variable(self, name, spec, anonymous=anon)
                self._variables[name] = ref

    def __getitem__(self, name):
        """
        Return a reference to a program variable from this function.

        This allows variables between functions to be linked together::

            func1['var_name'] = func2['other_var_name']

        In the example above, the two local variables would be assigned to the
        same program variable whenever func1 and func2 are attached to the same
        program.
        """
        # create empty reference if needed
        if name not in self._variables:
            self._variables[name] = Variable(self, name)
        return self._variables[name]

    def __repr__(self):
        return "<%s %s %d>" % (self.__class__.__name__, self.name, id(self))

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


class FunctionChain(Function):
    """
    Function subclass that generates GLSL code to call a list of Functions
    in order. Functions may be called independently, or composed such that the
    output of each function provides the input to the next.

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
    def __init__(self, name=None, funcs=(), anonymous=True):
        Function.__init__(self, code=None, deps=list(funcs))
        self._funcs = list(funcs)
        self._name = name or "chain"
        self._update_signature()
        self._anonymous = anonymous

    @property
    def name(self):
        return self._name

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

        This property is disabled for FunctionChain; the code may only
        be accessed by calling compile().
        """
        raise NotImplementedError

    @property
    def template_vars(self):
        return {}

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

    def remove(self, function):
        """ Remove a function from the chain.
        """
        self._funcs.remove(function)
        self._deps.remove(function)
        self._update_signature()

    def compile(self, obj_names):
        name = obj_names.get(self, self.name)
        if not self.is_anonymous and name != self.name:
            raise Exception("Cannot compile %s with name %s; function is not "
                            "anonymous." % (self, name))
            #name = subs[self.name.lstrip('$')]
        #else:
            #name = self.name

        args = ", ".join(["%s %s" % arg for arg in self.args])
        code = "%s %s(%s) {\n" % (self.rtype, name, args)

        #if self.rtype == 'void':
        #    for fn in self._funcs:
        #        code += "    %s();\n" % obj_names[fn]
        #else:
        #    code += "    return "
        #    for fn in self._funcs[::-1]:
        #        code += "%s(\n           " % obj_names[fn]
        #    code += "    %s%s;\n" % (self.args[0][1], ')'*len(self._funcs))
        result_index = 0
        if len(self.args) == 0:
            last_rtype = 'void'
            last_result = ''
        else:
            last_rtype, last_result = self.args[0][:2]

        for fn in self._funcs:
            # Use previous return value as an argument to the next function
            if last_rtype == 'void':
                args = ''
            else:
                args = last_result
                if len(fn.args) != 1 or last_rtype != fn.args[0][0]:
                    raise Exception("Cannot chain output '%s' of function to "
                                    "input of '%s'" %
                                    (last_rtype, fn.signature))
            last_rtype = fn.rtype

            # Store the return value of this function
            if fn.rtype == 'void':
                set_str = ''
            else:
                result_index += 1
                result = 'result_%d' % result_index
                set_str = '%s %s = ' % (fn.rtype, result)
                last_result = result

            code += "    %s%s(%s);\n" % (set_str, obj_names[fn], args)

        # return the last function's output
        if self.rtype != 'void':
            code += "    return result_%d;\n" % result_index

        code += "}\n"
        return code
