"""
Implementation of a simple function object for re-using and composing
GLSL snippets. See the docstring of Function for considerations.

There is some example code at the bottom. Just run this script and play
with it!

Details
-------

Each function object keeps track of a dict of replacments and a set
of dependencies. When composing the final code, the dependencies 
are collected recursively and then the replacements are applied
on the code of each function object, using the known replacements
of that object only. In effect, replacements are local to a Function
object, and they can be applied after composing the Function object
together.

To set signatures, the Function object can be called. At that moment,
any dependencies are added and the resulting string signature is stored
on the Function object. Generally, this signature will be used as part
of a replacement string: ``code['$position'] = trans(position())``.
Thus the local storage of the signature string is only temporary to
communicate the signature downstream. In effect, we can reuse a function
without having to worry about signature mixup.

Things to consider / work out
-----------------------------

* Stuff to find names and attriutes/uniforms needs to be made more robust
  using regexp; I am not so good with regexp :(
* There should be a way to easily set values to varyings. Maybe we
  just need a convention for a a post-hook and a pre-hook or
    something.
* ``code = SomeFunction.new()`` or ``code = Function(SomeFunction)``?
  Both work actually. new() seems nice and short, but maybe the latter
  is more Pythonic.
    
    
"""

import re

from ...util.ordereddict import OrderedDict
from ...ext.six import string_types
from . import parsing



class Expression(object):
    """ Base class for things that template variables can be replaced with.
    """
    
    @property
    def dependencies(self):
        """ The dependencies (Function and Variable objects) for this
        expression.
        """
        return self._dependencies()
    
    def _dependencies(self):
        raise NotImplementedError()
    
    @property
    def injection(self):
        """ Get the piece of code that is to be replaced at the template
        variable.
        """
        return self._injection()
    
    def _injection(self):
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
    def __init__(self, name, spec):
        self._state_counter = 0
        self._name = self._oname = name  # local name within the function
        self._spec = spec  # (vtype, dtype, value)
        #if spec is not None:
        #    self.spec = spec
    
#     @property
#     def function(self):
#         return self._function
    
    @property
    def name(self):
        return self._name
    
#     def compile(self, obj_names):
#         name = obj_names.get(self, self.name)
#         if not self.is_anonymous and name != self.name:
#             raise Exception("Cannot compile %s with name %s; variable "
#                             "is not anonymous." % (self, name))
#         return "%s %s %s;" % (self.vtype, self.dtype, name)

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
    
#     @spec.setter
#     def spec(self, s):
#         self._spec = s
#         self._state_counter += 1
        
    @property
    def state_id(self):
        """Return a unique ID that changes whenever the state of the Variable
        has changed. This allows ModularProgram to quickly determine whether
        the value has changed since it was last used."""
        return id(self), self._state_counter

    def __repr__(self):
        return ("<Variable '%s' at 0x%x)>" % (self.name, id(self)))
    
    def _dependencies(self):
        d = OrderedDict()
        d[self] = None
        return d
    
    def _injection(self):
        return self._name
    
    def _rename(self, name):
        self._name = name
        self._spec = self._spec[0], self._spec[1], name


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
        return 'FunctionCall "%s" for %r' % (self.injection, self.function)
    
    @property
    def function(self):
        return self._function
    
    def _dependencies(self):
        d = OrderedDict()
        # Add "our" function and its dependencies
        d[self.function] = None
        d.update(self.function.dependencies)
        # Add dependencies of each or our arguments
        for arg in self._signature:
            d.update(arg.dependencies)
        return d
    
    def _injection(self):
        str_args = [arg.injection for arg in self._signature]
        sig = ', '.join(str_args)
        return '%s(%s)' % (self.function.name, sig)



def _convert_to_expression(val):
    """ Convert input to an expression. If an expression is given, it
    is left unchanged. An error is raised if an Expression could not
    be returned.
    """
    if isinstance(val, Expression):
        return val
    elif isinstance(val, string_types):
        if (val.startswith('constant ') or val.startswith('uniform ') or
            val.startswith('attribute ') or val.startswith('varying ') or
            val.startswith('inout ')):
            if val.count(' ') == 2:
                spec = val.split(' ')
                # todo: Variable should just accept spec!
                return Variable(spec[2], spec)
        return TextExpression(val)
    elif isinstance(val, Function):
        # Be friendly for people who forget to call a function
        raise ValueError('A Function is not an expression, it\'s "call" is.')
    else:
        raise ValueError('Cannot convert to Expression %r' % val)



class Function(object):
    """ Representation of a GLSL function
    
    This is the class to be used for re-using and composing GLSL snippets.
    
    Each Function consists of a GLSL snipped in the form of a GLSL
    function. The code may have stub variables that start with the
    dollar sign by convention. These stubs can be replaced with calls
    to other functions (or with plain source code), using the index
    operation. 
    
    The signature of a function can be set by calling the Function
    object, arguments can be verbatim code or Function objects. Note
    that if the signature is already specified in the template code,
    that signature is used.
    
    To get the final source code, simply convert the Function object
    to str (or print it). In order to further modify a 'finished'
    Function object, firts turn it into a 'fresh' Function via
    ``Function(str(fun))``.
    
    Example
    -------
        
        # ... omitted deinition of FragShaderTemplate and ScaleTransform
        
        # Always create new Function objects to ensure they are 'fresh'.
        # You can also give the function a new name here.
        code = FragShaderTemplate.new()
        trans1 = ScaleTransform.new('trans1')
        trans2 = ScaleTransform.new('trans2')
        position = Position()
        
        # Compose the different components
        code['$position'] = trans1(trans2(position())
        code['$some_stub'] = 'vec2(3.0, 1.0)'
        
        # You can actually change any code you want, but use this with care!
        code['gl_FragColor = color;'] = 'gl_FragColor = vec4(color.rgb, 0.5)'
        
        # By renaming a Function object, the attribute/uniform names are
        # mangled to avoid name conflicts. It is easy to retieve the original
        # names:
        trans1_scale_name = trans1.uniform('u_scale')
        trans2_scale_name = trans1.uniform('u_scale')
        
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
        * a Variable: ``fun1['foo'] = 'uniform vec3 ray'``
        
        """
        
        # Check key
        if not isinstance(key, string_types):
            raise ValueError('In `function[key]` key must be a string.')
        elif key not in self._template_vars:
            raise ValueError('Invalid template variable %r' % key)
        
        # Ensure val is an expression
        val = _convert_to_expression(val)
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
        
        # create empty reference if needed
        #if key not in self._expressions:
        #    self._expressions[name] = Variable(self, key)
        # todo: do we really need delayed setting of variable spec?
        return self._expressions[name]
    
    
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
        """ Make a copy of this Function object, discarting any
        replacements and function signature. 
        
        Optionally the name of the function can be reset. If this is
        done, the attributes and uniform names are mangled with the
        given name as well. Use the uniform() and attribute() methods
        to get the real names.
        
        """
        return Function(self._code)
    
    
    @property
    def name(self):
        """ The function name.
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
    
    
#     def uniform(self, uname):
#         """ Get mangled uniform name given the initial name.
#         """
#         return uname + '__' + self._name
#     
#     
#     def attribute(self, aname):
#         """ Get mangled attribute name given the initial name.
#         """
#         return aname + '__' + self._name
    
    
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
    
#     def _prepare(self, newname=None):
#         """ Get name of function and prepare code a bit to our format.
#         """
#         # Try to get name. This needs to be made more robust!
#         name = ''
#         lines = []
#         for line in self._code.splitlines():
#             if (not name) and '(' in line:
#                 name = line.split(' ',1)[1].split('(')[0].strip()
#                 if newname:
#                     newname = newname.replace('{id}', hex(id(self)))
#                     line = line.replace(name, newname)
#                     name = newname
#             lines.append(line)
#         # Store
#         self._name = name
#         self._code = '\n'.join(lines)
#         # If object is renamed, set replacements for uniforms and attributes
#         # todo: EEK! only do whole worlds, with regexp. 
#         if newname:
#             for line in lines:
#                 #Safer replacing:
#                 #code = re.sub(r"(?<=[^\w])(%s)(?=[^\w])" % symbol, 
#                 #         lambda _: name, code)
#                 if line.startswith('uniform'):
#                     uname = line.split(' ')[2].strip(' ;')
#                     self._expressions[uname] = self.uniform(uname)
#                 elif line.startswith('attribute'):
#                     aname = line.split(' ')[2].strip(' ;')
#                     self._expressions[aname] = self.attribute(aname)
     
    def _rename(self, name):
        """ Set the name to be applied when compiling this function.
        """
        self._name = name
        
    def _get_replaced_code(self):
        """ Return code, with replacements applied.
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
                code = code.replace('$'+key+'(', val.function.name)
            code = code.replace('$'+key, val.injection)
        return code
    
    
    @property
    def dependencies(self):
        """ The dependencies (Functions and Variables) for this expression.
        """
        deps = OrderedDict()
        for dep in self._expressions.values():
            deps.update(dep.dependencies)
        return deps
    
    
    def _compile(self):
        """ Apply the replacements and add code for dependencies.
        Return new code string.
        """
        # todo: we need to prepend the function definitions here
        
        # Init
        deps = self.dependencies
        code = ''
        # Do some renaminmg. Objects only gets renamed if there are > 1
        # objects with that name. We use dep._oname and dep._rename() here.
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
                code += '%s %s %s;\n' % tuple(dep.spec)
        code += '\n'
        # Add function definitions
        for dep in deps:
            if isinstance(dep, Function):
                ret = dep._signature[2]
                sig = [s[0] for s in dep._signature[1]]
                code += '%s %s(%s);\n' % (ret, dep.name, ', '.join(sig))
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
   