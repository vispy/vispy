"""
Implementation of a function object for re-using and composing
GLSL snippets. See the docstring of Function for details.

Details
-------

Each function object keeps track of a dict of Expression objects to
replace template variables with. When composing the final code, the
dependencies are collected recursively and the replacements are applied
on the code of each function object, using the expressions associated
with that object. In effect, expressions are local to the Function
object on which they are set. Expression can be applied after composing
the Function object.

The function class is considered a friend class of the Expression
classes. It uses the _dependencies() and _injection() methods, and for
Variable also the _rename() and _definition().

Things to consider / work out
-----------------------------

* There should be a way to easily set values to varyings. Maybe we
  just need a convention for a a post-hook and a pre-hook or
    something.
* ``code = SomeFunction.new()`` or ``code = Function(SomeFunction)``?
  Both work actually. new() seems nice and short, but maybe the latter
  is more Pythonic.
    
"""

from ...util.ordereddict import OrderedDict
from ...ext.six import string_types
from . import parsing

VARIABLE_TYPES = ('constant', 'uniform', 'attribute', 'varying', 'inout')


class Function(object):
    """ Representation of a GLSL function
    
    This is the class to be used for re-using and composing GLSL snippets.
    
    Each Function consists of a GLSL snippet in the form of a function.
    The code may have template variables that start with the dollar
    sign. These stubs can be replaced with expressions using the index
    operation. Expressions can be calls to other functions, variables
    (constant, uniform, attribute, varying, inout) or plain code.
    
    The signature of a function can be set by calling the Function
    object, arguments can be any of the expressions mentioned above.
    If the signature is already specified in the template code, that
    signature is used.
    
    To get the final source code, simply convert the Function object
    to str (or print it). 
    
    Example
    -------
        
        # ... omitted deinition of FragShaderTemplate and ScaleTransform
        
        # Always create new Function objects to ensure they are 'fresh'.
        code = FragShaderTemplate.new()
        trans1 = ScaleTransform.new()
        trans2 = ScaleTransform.new()
        position = Position.new()
        
        # Compose the different components
        code['position'] = position()  # Set a call to a function
        code['position'] = trans1(trans2(position())  # Functions with args 
        code['some_stub'] = 'vec2(3.0, 1.0)'  # Verbatim code
        code['offset'] = 'uniform float offset'  # a variable
        code['offset'] = 'uniform float offset', 3.0  # a variable with data
        position['position'] = 'attribute vec3 a_position', VertexBuffer()
        
        # You can actually change any code you want, but use this with care!
        code.replace('= color;', '= vec4(color.rgb, 0.5)')
        
        # Updating variables
        code['offset'].value = 4.0
        position['position'].value.set_data(...)
        
        # Note that the Function object itself is agnostic about the
        # value of a variable. It only provides a simple way to
        # associate data with it. Somewhere down the line, you could do:
        for var in code.get_variables():
            program[var.name] = var.value
    """
    
    def __init__(self, code):
        
        # Get and strip code
        if isinstance(code, Function):
            code = code._code
        self._code = code.strip()
        
        # Get some information derived from the code
        self._signature = parsing.parse_function_signature(self._code)
        self._name = self._oname = self._signature[0]
        self._template_vars = self._parse_template_vars()
        
        # Expressions replace template variables (also our dependencies)
        self._expressions = OrderedDict()
        
        # Verbatim string replacements
        self._replacements = OrderedDict()
        
        # Prepare: get name, inject CALL_TEMPLATE, set replacements for
        # uniforms/attributes
        #self._prepare(name)
    
    def __setitem__(self, key, val):
        """ Setting of replacements through a dict-like syntax.
        
        Each replacement can be:
        * verbatim code: ``fun1['foo'] = '3.14159'``
        * a FunctionCall: ``fun1['foo'] = fun2()``
        * a Variable: ``fun1['foo'] = 'uniform vec3 u_ray'``
        """
        
        # Check key
        if not isinstance(key, string_types):
            raise ValueError('In `function[key]` key must be a string.')
        elif key not in self._template_vars:
            raise ValueError('Invalid template variable %r' % key)
        
        # Ensure val is an expression
        val = _convert_to_expression(val, altname=key)
        self._expressions[key] = val
    
    def __getitem__(self, key):
        """ Return a reference to a program variable from this function.

        This allows variables between functions to be linked together::

            func1['var_name'] = func2['other_var_name']

        In the example above, the two local variables would be assigned to the
        same program variable whenever func1 and func2 are attached to the same
        program.
        """
        
        # Check key
        if not isinstance(key, string_types):
            raise ValueError('In `function[key]` key must be a string.')
        elif key not in self._template_vars:
            raise ValueError('Invalid template variable %r' % key)
        
        # Return
        return self._expressions[key]
    
    def __call__(self, *args):
        """ Set the signature for this function and return an FunctionCall
        object. Each argument can be verbatim code or a FunctionCall object.
        """
        # Ensure all expressions
        args = [_convert_to_expression(a) for a in args]
        # Return FunctionCall object
        return FunctionCall(self, args)
    
    def __repr__(self):
        return "<Function '%s' at 0x%x>" % (self.name, id(self))
    
    def __str__(self):
        return self._compile()
    
    ## Public API methods
    
    def new(self):
        """ Make a copy of this Function object, discarting currently set 
        expressions and replacements.
        """
        return Function(self._code)
    
    @property
    def name(self):
        """ The function name. The name may be mangled in the final code
        to avoid name clashes.
        """
        return self._name
    
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
        self._replacements[str1] = str2
    
    def get_variables(self):
        """ Get a list of all variable objects defined in the current
        program.
        """
        deps = self._dependencies()
        return [dep for dep in deps.keys() if isinstance(dep, Variable)]
    
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
            template_vars.add(var)
        return template_vars
    
    def _rename(self, name):
        """ Set the name to be applied when compiling this function.
        """
        self._name = name
        
    def _get_replaced_code(self):
        """ Return code, with new name, expressions, and replacements applied.
        """
        code = self._code
        # Modify name
        code = code.replace(self._oname+'(', self._name+'(')
        # Apply plain replacements
        for key, val in self._replacements.items():
            code = code.replace(key, val)
        # Apply template replacements 
        for key, val in self._expressions.items():
            if isinstance(val, FunctionCall):
                # when signature is specified, use that one instead
                code = code.replace('$'+key+'(', val.function.name+'(')
            code = code.replace('$'+key, val._injection())
        return code
    
    def _dependencies(self):
        """ Get the dependencies (Functions and Variables) for this expression.
        """
        deps = OrderedDict()
        for dep in self._expressions.values():
            deps.update(dep._dependencies())
        return deps
    
    def _definition(self):
        ret = self._signature[2]
        sig = [s[0] for s in self._signature[1]]
        return '%s %s(%s);' % (ret, self.name, ', '.join(sig))
    
    def _compile(self):
        """ Apply the replacements and add code for dependencies.
        Return new code string.
        """
        # Init
        deps = self._dependencies()
        code = '#VERSION 120\n'  # (or not)
        code += '// Code generated by vispy.scene.shaders.Function\n\n'
        # Mangle names of dependencies where necessaty. Objects only
        # gets renamed if there are > 1 objects with that name. We use
        # dep._oname and dep._rename() here.
        depset = set(deps.keys())
        names = {}
        for dep in depset:
            others = names.setdefault(dep._oname, [])
            if others:
                nr = len(others) + 1
                dep._rename(dep._oname + '_' + str(nr))
                others[0]._rename(others[0]._oname + '_1')
            others.append(dep)
        # Add variable definitions
        for dep in deps:
            if isinstance(dep, Variable):
                code += dep._definition() + '\n'
        code += '\n'
        # Add function definitions
        for dep in deps:
            if isinstance(dep, Function):
                code += dep._definition() + '\n'
        code += '\n'
        # Add our code
        code += self._get_replaced_code()
        # Add code for dependencies
        for dep in deps:
            if isinstance(dep, Function):
                code += '\n\n'
                code += dep._get_replaced_code()
        # Done
        return code.rstrip() + '\n'


class Expression(object):
    """ Base class for things that template variables can be replaced with.
    """
    
    def _dependencies(self):
        """ Get the dependencies (Function and Variable objects) for this
        expression.
        """
        raise NotImplementedError()
    
    def _injection(self):
        """ Get the piece of code that is to be replaced at the template
        variable.
        """
        raise NotImplementedError()


class TextExpression(Expression):
    """ Representation of a piece of verbatim code
    """
    
    def __init__(self, text):
        self._text = text

    def __repr__(self):
        return "<Expression %r at 0x%x>" % (self._text, id(self))
    
    def _dependencies(self):
        return OrderedDict()
    
    def _injection(self):
        return self._text


class Variable(Expression):
    """ Representation of global shader variable
    
    These can include: constant, uniform, attribute, varying, inout

    Created by Function.__getitem__
    """
    
    def __init__(self, spec, value=None, altname=None):
        # Unravel spec
        if not isinstance(spec, string_types):
            raise ValueError('Variable should be declared using a string')
        if not any([spec.startswith(vtype) for vtype in VARIABLE_TYPES]):
            raise ValueError('Variable spec should start with %r, nor %r' % 
                             (VARIABLE_TYPES, spec.split(' ')[0]))
        
        # Parse spec
        if spec.count(' ') == 1:
            # Only vtype and dtype specified, use altname
            self._vtype, self._dtype = spec.split(' ')
            self._name = altname
        elif spec.count(' ') == 2:
            # vtype, dtype and name specified, ignore altname
            self._vtype, self._dtype, self._name = spec.split(' ')
        else:
            raise ValueError('Invalid value for Variable: %r' % spec)
        if not self._name:
            raise ValueError('Variable must have a name.')
        
        # Further init
        self._oname = self._name
        self._state_counter = 0
        self._value = value
        assert self._vtype in VARIABLE_TYPES

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        """ The value associated with this variable. This class is
        agnostic about this value, it only provides a simple mechanism
        to associate data with a Variable object.
        """
        return self._value
        
    @value.setter
    def value(self, value):
        self._value = value
        self._state_counter += 1

    @property
    def state_id(self):
        """Return a unique ID that changes whenever the state of the Variable
        has changed. This allows ModularProgram to quickly determine whether
        the value has changed since it was last used."""
        return id(self), self._state_counter

    def __repr__(self):
        return ("<Variable %r at 0x%x>" % (self._definition()[:-1], id(self)))
    
    def _dependencies(self):
        d = OrderedDict()
        d[self] = None
        return d
    
    def _injection(self):
        return self._name
    
    def _rename(self, name):
        # If this is a varying, set name based on id of object so
        # the variable can be used accross different programs
        if self._vtype == 'varying':
            name = '%s_%x' % (self._oname, id(self))
        self._name = name
        #self._spec = self._spec[0], self._spec[1], name
    
    def _definition(self):
        # Used by Function to put at top of shader code
        return '%s %s %s;' % (self._vtype, self._dtype, self.name)


class FunctionCall(Expression):
    """ Representation of a call to a function
    
    Essentially this is container for a Function along with its
    signature. Objects of this class generally live very short; they
    serve only as a message. The signature is either incorporated in
    the next FunctionCall or in the replacement at a function.
    """
    
    def __init__(self, function, signature):
        self._function = function
        self._signature = signature
    
    def __repr__(self):
        return '<FunctionCall %r for %r at 0x%x>' % (
               self._injection(), self.function, id(self))
    
    @property
    def function(self):
        return self._function
    
    def _dependencies(self):
        d = OrderedDict()
        # Add "our" function and its dependencies
        d[self.function] = None
        d.update(self.function._dependencies())
        # Add dependencies of each or our arguments
        for arg in self._signature:
            d.update(arg._dependencies())
        return d
    
    def _injection(self):
        str_args = [arg._injection() for arg in self._signature]
        sig = ', '.join(str_args)
        return '%s(%s)' % (self.function.name, sig)


def _convert_to_expression(val, altname=None):
    """ Convert input to an expression. If an expression is given, it
    is left unchanged. An error is raised if an Expression could not
    be returned.
    """
    if isinstance(val, Expression):
        return val
    elif isinstance(val, string_types):
        try:
            return Variable(val, altname=altname)
        except ValueError:
            return TextExpression(val)
    elif isinstance(val, tuple):
        if len(val) == 2:
            return Variable(val[0], val[1], altname=altname)
    elif isinstance(val, Function):
        # Be friendly for people who forget to call a function
        raise ValueError('A Function is not an expression, it\'s "call" is.')
    # Else ...
    raise ValueError('Cannot convert to Expression %r' % val)
