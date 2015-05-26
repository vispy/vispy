# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Classses representing GLSL objects (functions, variables, etc) that may be
composed together to create complete shaders. 
See the docstring of Function for details.

Details
-------

A complete GLSL program is composed of ShaderObjects, each of which may be used
inline as an expression, and some of which include a definition that must be
included on the final code. ShaderObjects keep track of a hierarchy of
dependencies so that all necessary code is included at compile time, and
changes made to any object may be propagated to the root of the hierarchy to 
trigger a recompile.
"""

import re
import logging
import numpy as np

from ...util.eq import eq
from ...util import logger
from ...ext.ordereddict import OrderedDict
from ...ext.six import string_types
from . import parsing
from .shader_object import ShaderObject
from .variable import Variable, Varying
from .expression import TextExpression, FunctionCall


class Function(ShaderObject):
    """Representation of a GLSL function
    
    Objects of this class can be used for re-using and composing GLSL
    snippets. Each Function consists of a GLSL snippet in the form of
    a function. The code may have template variables that start with
    the dollar sign. These stubs can be replaced with expressions using
    the index operation. Expressions can be:
    
    * plain text that is inserted verbatim in the code
    * a Function object or a call to a funcion
    * a Variable (or Varying) object
    * float, int, tuple are automatically turned into a uniform Variable
    * a VertexBuffer is automatically turned into an attribute Variable
    
    All functions have implicit "$pre" and "$post" placeholders that may be
    used to insert code at the beginning and end of the function.
    
    Examples
    --------
    This example shows the basic usage of the Function class::

        vert_code_template = Function('''
            void main() {
            gl_Position = $pos;
            gl_Position.x += $xoffset;
            gl_Position.y += $yoffset;
        }''')
        
        scale_transform = Function('''
        vec4 transform_scale(vec4 pos){
            return pos * $scale;
        }''')
        
        # If you get the function from a snippet collection, always
        # create new Function objects to ensure they are 'fresh'.
        vert_code = Function(vert_code_template)
        trans1 = Function(scale_transform)
        trans2 = Function(scale_transform)  # trans2 != trans1
        
        # Three ways to assign to template variables:
        #
        # 1) Assign verbatim code
        vert_code['xoffset'] = '(3.0 / 3.1415)'
        
        # 2) Assign a value (this creates a new uniform or attribute)
        vert_code['yoffset'] = 5.0
        
        # 3) Assign a function call expression
        pos_var = Variable('attribute vec4 a_position')
        vert_code['pos'] = trans1(trans2(pos_var))
        
        # Transforms also need their variables set
        trans1['scale'] = 0.5
        trans2['scale'] = (1.0, 0.5, 1.0, 1.0)
        
        # You can actually change any code you want, but use this with care!
        vert_code.replace('gl_Position.y', 'gl_Position.z')
        
        # Finally, you can set special variables explicitly. This generates
        # a new statement at the end of the vert_code function.
        vert_code['gl_PointSize'] = '10.'
    
    
    If we use ``vert_code.compile()`` we get::

        attribute vec4 a_position;
        uniform float u_yoffset;
        uniform float u_scale_1;
        uniform vec4 u_scale_2;
        uniform float u_pointsize;
        
        vec4 transform_scale_1(vec4 pos){
            return pos * u_scale_1;
        }
        
        vec4 transform_scale_2(vec4 pos){
            return pos * u_scale_2;
        }
        
        void main() {
            gl_Position = transform_scale_1(transform_scale_2(a_position));
            gl_Position.x += (3.0 / 3.1415);
            gl_Position.z += u_yoffset;
        
            gl_PointSize = u_pointsize;
        }
    
    Note how the two scale function resulted in two different functions
    and two uniforms for the scale factors.
    
    Function calls
    --------------
    
    As can be seen above, the arguments with which a function is to be
    called must be specified by calling the Function object. The
    arguments can be any of the expressions mentioned earlier. If the
    signature is already specified in the template code, that function
    itself must be given.
    
        code = Function('''
            void main() {
                vec4 position = $pos;
                gl_Position = $scale(position)
            }
        ''')
        
        # Example of a function call with all possible three expressions
        vert_code['pos'] = func1('3.0', 'uniform float u_param', func2())
        
        # For scale, the sigfnature is already specified
        code['scale'] = scale_func  # Must not specify args
    
    Data for uniform and attribute variables
    ----------------------------------------
    To each variable a value can be associated. In fact, in most cases
    the Function class is smart enough to be able to create a Variable
    object if only the data is given.
    
        code['offset'] = Variable('uniform float offset')  # No data
        code['offset'] = Variable('uniform float offset', 3.0)  # With data
        code['offset'] = 3.0  # -> Uniform Variable
        position['position'] = VertexBuffer()  # -> attribute Variable
        
        # Updating variables
        code['offset'].value = 4.0
        position['position'].value.set_data(...)
    """
    
    def __init__(self, code, dependencies=None):
        super(Function, self).__init__()
        
        # Add depencencies is given. This is to allow people to
        # manually define deps for a function that they use.
        if dependencies is not None:
            for dep in dependencies:
                self._add_dep(dep)
        
        self.code = code
        
        # Expressions replace template variables (also our dependencies)
        self._expressions = OrderedDict()
        
        # Verbatim string replacements
        self._replacements = OrderedDict()
        
        # Stuff to do at the end
        self._assignments = OrderedDict()
        
    def __setitem__(self, key, val):
        """ Setting of replacements through a dict-like syntax.
        
        Each replacement can be:
        * verbatim code: ``fun1['foo'] = '3.14159'``
        * a FunctionCall: ``fun1['foo'] = fun2()``
        * a Variable: ``fun1['foo'] = Variable(...)`` (can be auto-generated)
        """
        # Check the key. Must be Varying, 'gl_X' or a known template variable
        if isinstance(key, Variable): 
            if key.vtype == 'varying':
                if self.name != 'main':
                    raise Exception("Varying assignment only alowed in 'main' "
                                    "function.")
                storage = self._assignments
            else:
                raise TypeError("Variable assignment only allowed for "
                                "varyings, not %s (in %s)"
                                % (key.vtype, self.name))
        elif isinstance(key, string_types):
            if any(map(key.startswith, 
                       ('gl_PointSize', 'gl_Position', 'gl_FragColor'))):
                storage = self._assignments
            elif key in self.template_vars or key in ('pre', 'post'):
                storage = self._expressions
            else:
                raise KeyError('Invalid template variable %r' % key)
        else:
            raise TypeError('In `function[key]` key must be a string or '
                            'varying.')
        
        # If values already match, bail out now
        if eq(storage.get(key), val):
            return

        # If we are only changing the value (and not the dtype) of a uniform,
        # we can set that value and return immediately to avoid triggering a
        # recompile.
        if val is not None and not isinstance(val, Variable):
            # We are setting a value. If there is already a variable set here,
            # try just updating its value.
            variable = storage.get(key, None)
            if isinstance(variable, Variable):
                if np.any(variable.value != val):
                    variable.value = val
                    self.changed(value_changed=True)
                return
            
            # Could not set variable.value directly; instead we will need
            # to create a new ShaderObject
            val = ShaderObject.create(val, ref=key)
            if variable is val:
                # This can happen if ShaderObject.create returns the same 
                # object (such as when setting a Transform).
                return
        
        # Remove old references, if any
        oldval = storage.pop(key, None)
        if oldval is not None:
            for obj in (key, oldval):
                if isinstance(obj, ShaderObject):
                    self._remove_dep(obj)

        # Add new references
        if val is not None:
            if isinstance(key, Varying):
                # tell this varying to inherit properties from 
                # its source attribute / expression.
                key.link(val)
            
            # Store value and dependencies
            storage[key] = val
            for obj in (key, val):
                if isinstance(obj, ShaderObject):
                    self._add_dep(obj)
        
        # In case of verbatim text, we might have added new template vars
        if isinstance(val, TextExpression):
            for var in parsing.find_template_variables(val.expression()):
                if var not in self.template_vars:
                    self.template_vars.add(var.lstrip('$'))
        
        self.changed(code_changed=True, value_changed=True)
        if logger.level <= logging.DEBUG:
            import traceback
            last = traceback.format_list(traceback.extract_stack()[-2:-1])
            logger.debug("Assignment would trigger shader recompile:\n"
                         "Original:\n%r\nReplacement:\n%r\nSource:\n%s", 
                         oldval, val, ''.join(last))
    
    def __getitem__(self, key):
        """ Return a reference to a program variable from this function.

        This allows variables between functions to be linked together::

            func1['var_name'] = func2['other_var_name']

        In the example above, the two local variables would be assigned to the
        same program variable whenever func1 and func2 are attached to the same
        program.
        """
        
        try:
            return self._expressions[key]
        except KeyError:
            pass
        
        try:
            return self._assignments[key]
        except KeyError:
            pass
        
        if key not in self.template_vars:
            raise KeyError('Invalid template variable %r' % key) 
        else:
            raise KeyError('No value known for key %r' % key)
    
    def __call__(self, *args):
        """ Set the signature for this function and return an FunctionCall
        object. Each argument can be verbatim code or a FunctionCall object.
        """
        return FunctionCall(self, args)
    
    ## Public API methods

    @property
    def signature(self):
        if self._signature is None:
            try:
                self._signature = parsing.parse_function_signature(self._code)
            except Exception as err:
                raise ValueError('Invalid code: ' + str(err))
        return self._signature
    
    @property
    def name(self):
        """ The function name. The name may be mangled in the final code
        to avoid name clashes.
        """
        return self.signature[0]

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
        The return type of this function.
        """
        return self.signature[2]
    
    @property
    def code(self):
        """ The template code used to generate the definition for this 
        function.
        """
        return self._code
    
    @code.setter
    def code(self, code):
        # Get and strip code
        if isinstance(code, Function):
            code = code._code
        elif not isinstance(code, string_types):
            raise ValueError('Function needs a string or Function; got %s.' %
                             type(code))
        self._code = self._clean_code(code)

        # (name, args, rval)
        self._signature = None
        
        # $placeholders parsed from the code
        self._template_vars = None
        
        # Create static Variable instances for any global variables declared
        # in the code
        self._static_vars = None
    
    @property
    def template_vars(self):
        if self._template_vars is None:
            self._template_vars = self._parse_template_vars()
        return self._template_vars

    def static_names(self):
        if self._static_vars is None:
            self._static_vars = parsing.find_program_variables(self._code)
        return list(self._static_vars.keys()) + [arg[0] for arg in self.args]

    def replace(self, str1, str2):
        """ Set verbatim code replacement
        
        It is strongly recommended to use function['$foo'] = 'bar' where
        possible because template variables are less likely to changed
        than the code itself in future versions of vispy.
        
        Parameters
        ----------
        str1 : str
            String to replace
        str2 : str
            String to replace str1 with
        """
        if str2 != self._replacements.get(str1, None):
            self._replacements[str1] = str2
            self.changed(code_changed=True)
            #self._last_changed = time.time()
    
    ## Private methods
    
    def _parse_template_vars(self):
        """ find all template variables in self._code, excluding the
        function name. 
        """
        template_vars = set()
        for var in parsing.find_template_variables(self._code):
            var = var.lstrip('$')
            if var == self.name:
                continue
            if var in ('pre', 'post'):
                raise ValueError('GLSL uses reserved template variable $%s' % 
                                 var)
            template_vars.add(var)
        return template_vars
    
    def _get_replaced_code(self, names):
        """ Return code, with new name, expressions, and replacements applied.
        """
        code = self._code
        
        # Modify name
        fname = names[self]
        code = code.replace(" " + self.name + "(", " " + fname + "(")

        # Apply string replacements first -- these may contain $placeholders
        for key, val in self._replacements.items():
            code = code.replace(key, val)
        
        # Apply assignments to the end of the function
        
        # Collect post lines
        post_lines = []
        for key, val in self._assignments.items():
            if isinstance(key, Variable):
                key = names[key]
            if isinstance(val, ShaderObject):
                val = val.expression(names)
            line = '    %s = %s;' % (key, val)
            post_lines.append(line)
            
        # Add a default $post placeholder if needed
        if 'post' in self._expressions:
            post_lines.append('    $post')
            
        # Apply placeholders for hooks
        post_text = '\n'.join(post_lines)
        if post_text:
            post_text = '\n' + post_text + '\n'
        code = code.rpartition('}')
        code = code[0] + post_text + code[1] + code[2]

        # Add a default $pre placeholder if needed
        if 'pre' in self._expressions:
            m = re.search(fname + r'\s*\([^{]*\)\s*{', code)
            if m is None:
                raise RuntimeError("Cound not find beginning of function '%s'" 
                                   % fname) 
            ind = m.span()[1]
            code = code[:ind] + "\n    $pre\n" + code[ind:]
        
        # Apply template variables
        for key, val in self._expressions.items():
            val = val.expression(names)
            search = r'\$' + key + r'($|[^a-zA-Z0-9_])'
            code = re.sub(search, val+r'\1', code)

        # Done
        if '$' in code:
            v = parsing.find_template_variables(code)
            logger.warning('Unsubstituted placeholders in code: %s\n'
                           '  replacements made: %s', 
                           v, list(self._expressions.keys()))
        
        return code + '\n'
    
    def definition(self, names):
        return self._get_replaced_code(names)

    def expression(self, names):
        return names[self]
    
    def _clean_code(self, code):
        """ Return *code* with indentation and leading/trailing blank lines
        removed. 
        """
        lines = code.split("\n")
        min_indent = 100
        for line in lines:
            if line.strip() != "":
                indent = len(line) - len(line.lstrip())
                min_indent = min(indent, min_indent)
        if min_indent > 0:
            lines = [line[min_indent:] for line in lines]
        code = "\n".join(lines)
        return code

    def __repr__(self):
        try:
            args = ', '.join([' '.join(arg) for arg in self.args])
        except Exception:
            return ('<%s (error parsing signature) at 0x%x>' % 
                    (self.__class__.__name__, id(self)))
        return '<%s "%s %s(%s)" at 0x%x>' % (self.__class__.__name__, 
                                             self.rtype,
                                             self.name,
                                             args,
                                             id(self))


class MainFunction(Function):
    """ Subclass of Function that allows multiple functions and variables to 
    be defined in a single code string. The code must contain a main() function
    definition.
    """
    def __init__(self, *args, **kwargs):
        self._chains = {}
        Function.__init__(self, *args, **kwargs)
    
    @property
    def signature(self):
        return ('main', [], 'void')

    def static_names(self):
        if self._static_vars is not None:
            return self._static_vars
        
        # parse static variables
        names = Function.static_names(self)
        
        # parse all function names + argument names
        funcs = parsing.find_functions(self.code)
        for f in funcs:
            if f[0] == 'main':
                continue
            names.append(f[0])
            for arg in f[1]:
                names.append(arg[1])
                
        self._static_vars = names
        return names

    def add_chain(self, var):
        """
        Create a new ChainFunction and attach to $var.
        """
        chain = FunctionChain(var, [])
        self._chains[var] = chain
        self[var] = chain

    def add_callback(self, hook, func):
        self._chains[hook].append(func)
    
    def remove_callback(self, hook, func):
        self._chains[hook].remove(func)


class FunctionChain(Function):
    """Subclass that generates GLSL code to call Function list in order

    Functions may be called independently, or composed such that the
    output of each function provides the input to the next.

    Parameters
    ----------
    name : str
        The name of the generated function
    funcs : list of Functions
        The list of Functions that will be called by the generated GLSL code.

    Examples
    --------
    This creates a function chain:

        >>> func1 = Function('void my_func_1() {}')
        >>> func2 = Function('void my_func_2() {}')
        >>> chain = FunctionChain('my_func_chain', [func1, func2])

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
        # bypass Function.__init__ completely.
        ShaderObject.__init__(self)
        if not (name is None or isinstance(name, string_types)):
            raise TypeError("Name argument must be string or None.")
        self._funcs = []
        self._code = None
        self._name = name or "chain"
        self._args = []
        self._rtype = 'void'
        self.functions = funcs

    @property
    def functions(self):
        return self._funcs[:]

    @functions.setter
    def functions(self, funcs):
        while self._funcs:
            self.remove(self._funcs[0], update=False)
        for f in funcs:
            self.append(f, update=False)
        self._update()

    @property
    def signature(self):
        return self._name, self._args, self._rtype

    def _update(self):
        funcs = self._funcs
        if len(funcs) > 0:
            self._rtype = funcs[-1].rtype
            self._args = funcs[0].args[:]
        else:
            self._rtype = 'void'
            self._args = []
        
        self.changed(code_changed=True)
        
    @property
    def code(self):
        # Code is generated at compile time; hopefully it is not requested
        # before then..
        return None
    
    @code.setter
    def code(self, c):
        raise TypeError("Cannot set code property on FunctionChain.")

    @property
    def template_vars(self):
        return {}

    def append(self, function, update=True):
        """ Append a new function to the end of this chain.
        """
        self._funcs.append(function)
        self._add_dep(function)
        if update:
            self._update()

    def __setitem__(self, index, func):
        self._remove_dep(self._funcs[index])
        self._add_dep(func)
        self._funcs[index] = func
        
        self._update()
    
    def __getitem__(self, k):
        return self.functions[k]
    
    def insert(self, index, function, update=True):
        """ Insert a new function into the chain at *index*.
        """
        self._funcs.insert(index, function)
        self._add_dep(function)
        if update:
            self._update()

    def remove(self, function, update=True):
        """ Remove a function from the chain.
        """
        self._funcs.remove(function)
        self._remove_dep(function)
        if update:
            self._update()

    def definition(self, obj_names):
        name = obj_names[self]

        args = ", ".join(["%s %s" % arg for arg in self.args])
        code = "%s %s(%s) {\n" % (self.rtype, name, args)

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

    def static_names(self):
        return []

    def __repr__(self):
        fn = ",\n                ".join(map(repr, self.functions))
        return "<FunctionChain [%s] at 0x%x>" % (fn, id(self))


class StatementList(ShaderObject):
    """Represents a list of statements. 
    """
    def __init__(self):
        self.items = {}
        self.order = []
        ShaderObject.__init__(self)
        
    def add(self, item, position=5):
        """Add an item to the list unless it is already present.
        
        If the item is an expression, then a semicolon will be appended to it
        in the final compiled code.
        """
        if item in self.items:
            return
        self.items[item] = position
        self._add_dep(item)
        self.order = None
        self.changed(code_changed=True)
        
    def remove(self, item):
        """Remove an item from the list.
        """
        self.items.pop(item)
        self._remove_dep(item)
        self.order = None
        self.changed(code_changed=True)

    def expression(self, obj_names):
        if self.order is None:
            self.order = list(self.items.items())
            self.order.sort(key=lambda x: x[1])
            
        code = ""
        for item, pos in self.order:
            code += item.expression(obj_names) + ';\n'
        return code
