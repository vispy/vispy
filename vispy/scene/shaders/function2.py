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

"""

import time

from ...util.ordereddict import OrderedDict
from ...ext.six import string_types
from . import parsing

VARIABLE_TYPES = ('const', 'uniform', 'attribute', 'varying', 'inout')


class Function(object):
    """ Representation of a GLSL function
    
    Objects of this class can be used for re-using and composing GLSL
    snippets. Each Function consists of a GLSL snippet in the form of
    a function. The code may have template variables that start with
    the dollar sign. These stubs can be replaced with expressions using
    the index operation. Expressions can be plain text, variables
    (const, uniform, attribute, varying, inout), or function calls.
    
    Example
    -------
    
    This example shows the basic usage of the Function class.
    
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
        
        # If you get the function from a snipped collection, always
        # create new Function objects to ensure they are 'fresh'.
        vert_code = Function(vert_code_template)
        trans1 = Function(scale_transform)
        trans2 = Function(scale_transform)  # trans2 != trans1
        
        # Three ways to assign to template variables
        vert_code['xoffset'] = '3.0'  # Assign verbatim code
        vert_code['yoffset'] = 'uniform float offset'  # Assign a variable
        pos_var = 'attribute vec4 a_position'
        vert_code['pos'] = trans1(trans2(pos_var))  # Assign a function call
        
        # Transforms also need their variables set
        trans1['scale'] = 'uniform float scale'
        trans2['scale'] = 'uniform float scale'
        
        # You can actually change any code you want, but use this with care!
        vert_code.replace('gl_Position.y', 'gl_Position.z')
        
        # Finally, you can let functions be called at the end
        some_func = Function('void foo(){...}')
        vert_code.post_apply(some_func())
        # Or make some assignments at the end
        vert_code.post_apply('gl_PointSize', 'uniform float u_pointsize')
    
    If we use ``str(vert_code)`` we get:
    
        uniform float offset;
        uniform float scale_1;
        uniform float scale_2;
        attribute vec4 a_position;
        uniform float u_pointsize;
        
        vec4 transform_scale_1(vec4);
        vec4 transform_scale_2(vec4);
        void foo();
        
        void main() {
            gl_Position = transform_scale_1(transform_scale_2(a_position));
            gl_Position.x += 3.0;
            gl_Position.z += offset;
        
            foo();
            gl_PointSize = u_pointsize;
        }
        
        vec4 transform_scale_1(vec4 pos){
            return pos * scale_1;
        }
        
        vec4 transform_scale_2(vec4 pos){
            return pos * scale_2;
        }
        
        void foo(){...}
    
    Note how the two scale function resulted in two different functions
    and two uniforms for the scale factors.
    
    Function calls
    --------------
    
    As can be seen above, the arguments with which a function is to be
    called must be specified by calling the Function object. The
    arguments can be any of the expressions mentioned earlier (plain
    text, variables, or function calls). If the signature is already
    specified in the template code, that signature is used instead.
    
        code = Function('''
            void main() {
                vec4 position = $pos;
                gl_Position = $scale(position)
            }
        ''')
        
        # Example of a function call with all possible three expressions
        vert_code['pos'] = func1('3.0', 'uniform float u_param', func2())
        
        # For scale, the sigfnature is already specified
        code['scale'] = scale_func()  # No need to specify args
    
    Data for uniform and attribute variables
    ----------------------------------------
    To each variable a value can be associated. The Function object
    itself is agnostic about this value; it is only intended to keep
    variable name and data together to make the code that needs to
    process the variables easier.
    
        code['offset'] = 'uniform float offset'  # a variable with no data
        code['offset'] = 'uniform float offset', 3.0  # a variable with data
        position['position'] = 'attribute vec3 a_position', VertexBuffer()
        
        # Updating variables
        code['offset'].value = 4.0
        position['position'].value.set_data(...)
        
        # ... Somewhere later, we get all variables and bind names to value
        for var in code.get_variables():
            program[var.name] = var.value
    
    Linking shaders and specifying varyings
    ---------------------------------------
    By linking a vertex and fragment shader, they share the same name
    scope and variables. The most straightforward way to deal with
    varyings is to use the post_apply() method:
        
        // This is how to link
        vert_code.link(frag_code)
        
        // Pass attribute data to the fragment shader
        frag_code['color'] = 'varying vec3 v_color'
        vert_code.post_apply(frag_code['color'], 'attribute vec3 a_color')
    
    """
    
    def __init__(self, code):
        
        # Get and strip code
        if isinstance(code, Function):
            code = code._code
        elif not isinstance(code, string_types):
            raise ValueError('Function needs a string or Function.')
        self._code = code.strip()
        
        # Get some information derived from the code
        try:
            self._signature = parsing.parse_function_signature(self._code)
        except Exception as err:
            raise ValueError('Invalid code: ' + str(err))
        self._name = self._oname = self._signature[0]
        self._template_vars = self._parse_template_vars()
        
        # Expressions replace template variables (also our dependencies)
        self._expressions = OrderedDict()
        
        # Verbatim string replacements
        self._replacements = OrderedDict()
        
        # Stuff to do at the end
        self._post_hooks = []
        
        # Toplevel vertex/fragment shader funtctions can be linked
        self._linked = None
        
        # flags to be able to indicate whether code has changed
        self._last_changed = time.time()
        self._last_compiled = 0.0 
    
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
        self._last_changed = time.time()
    
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
    
    @property
    def name(self):
        """ The function name. The name may be mangled in the final code
        to avoid name clashes.
        """
        return self._name
    
    def ischanged(self, since=None):
        """ Whether the code has been modified since the last time it
        was compiled, or since the given time.
        """
        since = since or self._last_compiled
        ischanged = True
        if since > self._last_changed:
            for dep in self._dependencies(True):
                if since < dep._last_changed:
                    break
            else:
                ischanged = False
        return ischanged
    
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
        self._last_changed = time.time()
    
    def get_variables(self):
        """ Get a list of all variable objects defined in the current program.
        When this function is linked, it gets *all* variables.
        """
        deps = self._dependencies(True)
        return [dep for dep in deps.keys() if isinstance(dep, Variable)]
    
    def post_apply(self, val1, val2=None):
        """ Assign one variable to another (as in ``val1 = val2``)
        
        This assigment is done at the end of the function.
        """
        if True:
            val1 = _convert_to_expression(val1)
            key1 = 'assign_%x' % id(val1)
            self._expressions[key1] = val1
        if val2:
            val2 = _convert_to_expression(val2)
            key2 = 'assign_%x' % id(val2)
            self._expressions[key2] = val2
        # Add code that these variables can hook into
        if val2:
            self._post_hooks.append('    $%s = $%s;' % (key1, key2))
        else:
            self._post_hooks.append('    $%s;' % key1)
        self._last_changed = time.time()
    
    def link(self, frag_func):
        """ Link a vertex and fragment shader
        
        Both functions need to represent main-functions. When the vertex
        and fragment shader are linked, the scope for name mangling is
        shared, and it allows for setting varyings
        """
        # Check 
        if not isinstance(frag_func, Function):
            raise ValueError('Can only link to a Function object.')
        if not self.name == 'main':
            raise ValueError('Can only link if this is a main-function.')
        if not frag_func.name == 'main':
            raise ValueError('Can only link to a main-function.')
        # Apply
        vert_func = self
        vert_func._linked = frag_func, 'vertex'
        frag_func._linked = vert_func, 'fragment'
        # After linking we likely need renaming
        vert_func._last_changed = time.time()
        frag_func._last_changed = time.time()
    
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
        if self.name == 'main':
            raise ValueError('Cannot rename the main function.')
        self._name = name
        self._last_changed = time.time()
        
    def _get_replaced_code(self):
        """ Return code, with new name, expressions, and replacements applied.
        """
        code = self._code
        # Modify name
        code = code.replace(self._oname+'(', self._name+'(')
        # Apply plain replacements
        for key, val in self._replacements.items():
            code = code.replace(key, val)
        # Apply placeholders for hooks
        post_text = ''
        if self._post_hooks:
            post_text = '\n' + '\n'.join(self._post_hooks) + '\n'
        code = code.rpartition('}')
        code = code[0] + post_text + code[1] + code[2]
        # Apply template replacements 
        for key, val in self._expressions.items():
            if isinstance(val, FunctionCall):
                # When signature is specified, use that one instead
                code = code.replace('$'+key+'(', val.function.name+'(')
            code = code.replace('$'+key, val._injection())
        # Done
        return code
    
    def _dependencies(self, also_linked=False):
        """ Get the dependencies (Functions and Variables) for this
        expression.
        """
        # Get list of expressions, taking linking into account
        expressions1, expressions2 = self._expressions.values(), []
        if also_linked and self._linked:
            expressions2 = self._linked[0]._expressions.values()
            if self._linked[1] == 'fragment':
                expressions1, expressions2 = expressions2, expressions1
        # Collect dependencies
        deps = OrderedDict()
        for dep in expressions1:
            deps.update(dep._dependencies())
        for dep in expressions2:
            deps.update(dep._dependencies())
        return deps
    
    def _definition(self):
        ret = self._signature[2]
        sig = [s[0] for s in self._signature[1]]
        return '%s %s(%s);' % (ret, self.name, ', '.join(sig))
    
    def _mangle_names(self):
        """ Mangle names of dependencies where necessary. Objects only
        gets renamed if there are > 1 objects with that name, and if
        they are not already renamed appropriatly. We use dep._oname
        and dep._rename() here.
        """
        # Collect all dependencies with the same name
        deps = self._dependencies(True)
        names = {}
        for dep in deps:
            deps_with_this_name = names.setdefault(dep._oname, [])
            deps_with_this_name.append(dep)
        # Mangle names where necessary
        for name, deps_with_this_name in names.items():
            nameset = set([dep.name for dep in deps_with_this_name])
            if len(nameset) > 1:
                nameset.discard(name)  # if > 1, all must be mangled
            if len(nameset) != len(deps_with_this_name):
                for i, dep in enumerate(deps_with_this_name):
                    dep._rename(dep._oname + '_' + str(i+1))
    
    def _compile(self):
        """ Apply the replacements and add code for dependencies.
        Return new code string.
        """
        # Init
        code = ''
        self._mangle_names()
        deps = self._dependencies()
        # Write header
        if self.name == 'main':
            code += '#version 120\n'  # (or not)
        code += '// Code generated by vispy.scene.shaders.Function\n\n'
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
        self._last_compiled = time.time()
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
        if not isinstance(text, string_types):
            raise ValueError('TextExpression needs a string.')
        self._text = text

    def __repr__(self):
        return "<TextExpression %r at 0x%x>" % (self._text, id(self))
    
    def _dependencies(self):
        return OrderedDict()
    
    def _injection(self):
        return self._text


class Variable(Expression):
    """ Representation of global shader variable
    
    These can include: const, uniform, attribute, varying, inout

    Created by Function.__getitem__
    """
    
    def __init__(self, spec, value=None, altname=None):
        # Unravel spec
        if not isinstance(spec, string_types):
            raise ValueError('Variable should be declared using a string')
        if not any([spec.startswith(vtype) for vtype in VARIABLE_TYPES]):
            raise ValueError('Variable spec should start with %r, nor %r' % 
                             (VARIABLE_TYPES, spec.split(' ')[0]))
        
        # Init
        self._state_counter = 0
        self._value = value
        self._last_changed = time.time()
        
        # Parse spec
        if spec.count(' ') == 1:
            # Only vtype and dtype specified, use altname
            self._vtype, self._dtype = spec.split(' ')
            self._name = altname
        elif spec.count(' ') == 2:
            # vtype, dtype and name specified, ignore altname
            self._vtype, self._dtype, self._name = spec.split(' ')
        elif spec.startswith('const '):
            # Constant can define its value in the spec
            tmp = spec.split(' ', 3)
            self._vtype, self._dtype, self._name, self._value = tmp
        else:
            raise ValueError('Invalid value for Variable: %r' % spec)
        if not self._name:
            raise ValueError('Variable must have a name.')
        
        # Further init
        self._oname = self._name
        assert self._vtype in VARIABLE_TYPES

    @property
    def name(self):
        """ The (possibly mangled) name of this variable.
        """
        return self._name
    
    @property
    def vtype(self):
        """ The type of variable (const, uniform, attribute, varying or inout).
        """
        return self._vtype
    
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
        self._name = name
        self._last_changed = time.time()
    
    def _definition(self):
        # Used by Function to put at top of shader code
        if self._vtype == 'const':
            return '%s %s %s = %s;' % (self._vtype, self._dtype, self.name, 
                                       self.value)
        else:
            return '%s %s %s;' % (self._vtype, self._dtype, self.name)


class FunctionCall(Expression):
    """ Representation of a call to a function
    
    Essentially this is container for a Function along with its
    signature. Objects of this class generally live very short; they
    serve only as a message. The signature is either incorporated in
    the next FunctionCall or in the replacement at a function.
    """
    
    def __init__(self, function, signature):
        if not isinstance(function, Function):
            raise ValueError('FunctionCall needs a Function')
        self._function = function
        self._signature = signature
    
    def __repr__(self):
        return '<FunctionCall %r for at 0x%x>' % (self._injection(), id(self))
    
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
    raise ValueError('Cannot convert to Expression: %r' % val)
