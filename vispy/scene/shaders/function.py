# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
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
import numpy as np

from ...util.event import EventEmitter, Event
from ...util.eq import eq
from ...util import logger
from ...ext.ordereddict import OrderedDict
from ...ext.six import string_types
from . import parsing
from .compiler import Compiler

VARIABLE_TYPES = ('const', 'uniform', 'attribute', 'varying', 'inout')


class ShaderChangeEvent(Event):
    def __init__(self, code_changed=False, value_changed=False, **kwds):
        Event.__init__(self, type='shader_change', **kwds)
        self.code_changed = code_changed
        self.value_changed = value_changed


class ShaderObject(object):
    """ Base class for all objects that may be included in a GLSL program
    (Functions, Variables, Expressions).
    
    Shader objects have a *definition* that defines the object in GLSL, an 
    *expression* that is used to reference the object, and a set of 
    *dependencies* that must be declared before the object is used.
    
    Dependencies are tracked hierarchically such that changes to any object
    will be propagated up the dependency hierarchy to trigger a recompile.
    """
    
    @classmethod
    def create(self, obj, ref=None):
        """ Convert *obj* to a new ShaderObject. If the output is a Variable
        with no name, then set its name using *ref*. 
        """
        if isinstance(ref, Variable):
            ref = ref.name
        elif isinstance(ref, string_types) and ref.startswith('gl_'):
            # gl_ names not allowed for variables
            ref = ref[3:].lower()
        
        if isinstance(obj, ShaderObject):
            if isinstance(obj, Variable) and obj.name is None:
                obj.name = ref
        elif isinstance(obj, string_types):
            obj = TextExpression(obj)
        else:
            obj = Variable(ref, obj)
            # Try prepending the name to indicate attribute, uniform, varying
            if obj.vtype and obj.vtype[0] in 'auv':
                obj.name = obj.vtype[0] + '_' + obj.name 
        
        return obj
    
    def __init__(self):
        # emitted when any part of the code for this object has changed,
        # including dependencies.
        self.changed = EventEmitter(source=self, event_class=ShaderChangeEvent)
        
        # objects that must be declared before this object's definition.
        # {obj: refcount}
        self._deps = OrderedDict()  # OrderedDict for consistent code output
    
    @property
    def name(self):
        """ The name of this shader object.
        """
        return None
        
    def definition(self, obj_names):
        """ Return the GLSL definition for this object. Use *obj_names* to
        determine the names of dependencies.
        """
        return None
    
    def expression(self, obj_names):
        """ Return the GLSL expression used to reference this object inline.
        """
        return obj_names[self]
    
    def dependencies(self, sort=False):
        """ Return all dependencies required to use this object. The last item 
        in the list is *self*.
        """
        alldeps = []
        if sort:
            def key(obj):
                # sort deps such that we get functions, variables, self.
                if not isinstance(obj, Variable):
                    return (0, 0)
                else:
                    return (1, obj.vtype)
            
            deps = sorted(self._deps, key=key)
        else:
            deps = self._deps
        
        for dep in deps:
            alldeps.extend(dep.dependencies(sort=sort))
        alldeps.append(self)
        return alldeps

    def static_names(self):
        """ Return a list of names that are declared in this object's 
        definition (not including the name of the object itself).
        
        These names will be reserved by the compiler when automatically 
        determining object names.
        """
        return []
    
    def _add_dep(self, dep):
        """ Increment the reference count for *dep*. If this is a new 
        dependency, then connect to its *changed* event.
        """
        if dep in self._deps:
            self._deps[dep] += 1
        else:
            self._deps[dep] = 1
            dep.changed.connect(self._dep_changed)

    def _remove_dep(self, dep):
        """ Decrement the reference count for *dep*. If the reference count 
        reaches 0, then the dependency is removed and its *changed* event is
        disconnected.
        """
        refcount = self._deps[dep]
        if refcount == 1:
            self._deps.pop(dep)
            dep.changed.disconnect(self._dep_changed)
        else:
            self._deps[dep] -= 1
        
    def _dep_changed(self, event):
        """ Called when a dependency's expression has changed.
        """
        logger.debug("ShaderObject changed: %r" % event.source)
        self.changed(event)
    
    def compile(self):
        """ Return a compilation of this object and its dependencies. 
        
        Note: this is mainly for debugging purposes; the names in this code
        are not guaranteed to match names in any other compilations. Use
        Compiler directly to ensure consistent naming across multiple objects. 
        """
        compiler = Compiler(obj=self)
        return compiler.compile()['obj']
    
    def __repr__(self):
        if self.name is not None:
            return '<%s "%s" at 0x%x>' % (self.__class__.__name__, 
                                          self.name, id(self))
        else:
            return '<%s at 0x%x>' % (self.__class__.__name__, id(self))


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
        
        # Expressions replace template variables (also our dependencies)
        self._expressions = OrderedDict()
        
        # Verbatim string replacements
        self._replacements = OrderedDict()
        
        # Stuff to do at the end
        self._post_hooks = OrderedDict()
        
        # Create static Variable instances for any global variables declared
        # in the code
        self._static_vars = None
    
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
                storage = self._post_hooks
            else:
                raise TypeError("Variable assignment only allowed for "
                                "varyings, not %s (in %s)"
                                % (key.vtype, self.name))
        elif isinstance(key, string_types):
            if any(map(key.startswith, 
                       ('gl_PointSize', 'gl_Position', 'gl_FragColor'))):
                storage = self._post_hooks
            elif key in self.template_vars:
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
                try:
                    variable.value = val
                    return
                except Exception:
                    # Setting value on existing Variable failed for some
                    # reason; will need to create a new Variable instead. 
                    pass
        
        #print("SET: %s[%s] = %s => %s" % 
        #     (self, key, storage.get(key, None), val))
        
        # Remove old references, if any
        oldval = storage.pop(key, None)
        if oldval is not None:
            for obj in (key, oldval):
                if isinstance(obj, ShaderObject):
                    self._remove_dep(obj)

        # Add new references
        if val is not None:
            val = ShaderObject.create(val, ref=key)
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
            return self._post_hooks[key]
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
            template_vars.add(var)
        return template_vars
    
    def _get_replaced_code(self, names):
        """ Return code, with new name, expressions, and replacements applied.
        """
        code = self._code
        
        # Modify name
        code = code.replace(" " + self.name + "(", " " + names[self] + "(")

        # Apply string replacements first -- these may contain $placeholders
        for key, val in self._replacements.items():
            code = code.replace(key, val)
        
        # Apply post-hooks
        
        # Collect post lines
        post_lines = []
        for key, val in self._post_hooks.items():
            if isinstance(key, Variable):
                key = names[key]
            if isinstance(val, ShaderObject):
                val = val.expression(names)
            line = '    %s = %s;' % (key, val)
            post_lines.append(line)
            
        # Apply placeholders for hooks
        post_text = '\n'.join(post_lines)
        if post_text:
            post_text = '\n' + post_text + '\n'
        code = code.rpartition('}')
        code = code[0] + post_text + code[1] + code[2]
        
        # Apply template variables
        for key, val in self._expressions.items():
            val = val.expression(names)
            search = r'\$' + key + r'($|[^a-zA-Z0-9_])'
            code = re.sub(search, val+r'\1', code)

        # Done
        if '$' in code:
            v = parsing.find_template_variables(code)
            logger.warning('Unsubstituted placeholders in code: %s\n'
                           '  replacements made: %s' % 
                           (v, list(self._expressions.keys())))
        
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
        args = ', '.join([' '.join(arg) for arg in self.args])
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
    def __init__(self, *args, **kwds):
        self._chains = {}
        Function.__init__(self, *args, **kwds)
    
    @property
    def signature(self):
        return ('main', [], 'void')

    def static_names(self):
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


class Variable(ShaderObject):
    """ Representation of global shader variable
    
    Parameters
    ----------
    name : str
        the name of the variable. This string can also contain the full
        definition of the variable, e.g. 'uniform vec2 foo'.
    value : {float, int, tuple, GLObject}
        If given, vtype and dtype are determined automatically. If a
        float/int/tuple is given, the variable is a uniform. If a gloo
        object is given that has a glsl_type property, the variable is
        an attribute and
    vtype : {'const', 'uniform', 'attribute', 'varying', 'inout'}
        The type of variable.
    dtype : str
        The data type of the variable, e.g. 'float', 'vec4', 'mat', etc.
    
    """
    def __init__(self, name, value=None, vtype=None, dtype=None):
        super(Variable, self).__init__()
        
        # allow full definition in first argument
        if ' ' in name:
            fields = name.split(' ')
            if len(fields) == 3:
                vtype, dtype, name = fields
            elif len(fields) == 4 and fields[0] == 'const':
                vtype, dtype, name, value = fields
            else:
                raise ValueError('Variable specifications given by string must'
                                 ' be of the form "vtype dtype name" or '
                                 '"const dtype name value".')
            
        if not (isinstance(name, string_types) or name is None):
            raise TypeError("Variable name must be string or None.")
        
        self._state_counter = 0
        self._name = name
        self._vtype = vtype
        self._dtype = dtype
        self._value = None
        
        # If vtype/dtype were given at init, then we will never
        # try to set these values automatically.
        self._type_locked = self._vtype is not None and self._dtype is not None
            
        if value is not None:
            self.value = value
        
        if self._vtype and self._vtype not in VARIABLE_TYPES:
            raise ValueError('Not a valid vtype: %r' % self._vtype)
    
    @property
    def name(self):
        """ The name of this variable.
        """
        return self._name
    
    @name.setter
    def name(self, n):
        # Settable mostly to allow automatic setting of varying names 
        # See ShaderObject.create()
        if self._name != n:
            self._name = n
            self.changed(code_changed=True)
    
    @property
    def vtype(self):
        """ The type of variable (const, uniform, attribute, varying or inout).
        """
        return self._vtype
    
    @property
    def dtype(self):
        """ The type of data (float, int, vec, mat, ...).
        """
        return self._dtype
    
    @property
    def value(self):
        """ The value associated with this variable.
        """
        return self._value
    
    @value.setter
    def value(self, value):
        if isinstance(value, (tuple, list)) and 1 < len(value) < 5:
            vtype = 'uniform'
            dtype = 'vec%d' % len(value)
        elif isinstance(value, np.ndarray):
            if value.ndim == 1 and (1 < len(value) < 5):
                vtype = 'uniform'
                dtype = 'vec%d' % len(value)
            elif value.ndim == 2 and value.shape in ((2, 2), (3, 3), (4, 4)):
                vtype = 'uniform'
                dtype = 'mat%d' % value.shape[0]                
            else:
                raise ValueError("Cannot make uniform value for %s from array "
                                 "of shape %s." % (self.name, value.shape))
        elif np.isscalar(value):
            vtype = 'uniform'
            if isinstance(value, (float, np.floating)):
                dtype = 'float'
            elif isinstance(value, (int, np.integer)):
                dtype = 'int'
            else:
                raise TypeError("Unknown data type %r for variable %r" % 
                                (type(value), self))
        elif getattr(value, 'glsl_type', None) is not None:
            # Note: hasattr() is broken by design--swallows all exceptions!
            vtype, dtype = value.glsl_type
        else:
            raise TypeError("Unknown data type %r for variable %r" % 
                            (type(value), self))

        self._value = value
        self._state_counter += 1
        
        if self._type_locked:
            if dtype != self._dtype or vtype != self._vtype:
                raise TypeError('Variable is type "%s"; cannot assign value '
                                '%r.' % (self.dtype, value))
            return
            
        # update vtype/dtype and emit changed event if necessary
        changed = False
        if self._dtype != dtype:
            self._dtype = dtype
            changed = True
        if self._vtype != vtype:
            self._vtype = vtype
            changed = True
        if changed:
            self.changed(code_changed=True, value_changed=True)
    
    @property
    def state_id(self):
        """Return a unique ID that changes whenever the state of the Variable
        has changed. This allows ModularProgram to quickly determine whether
        the value has changed since it was last used."""
        return id(self), self._state_counter

    def __repr__(self):
        return ("<%s \"%s %s %s\" at 0x%x>" % (self.__class__.__name__,
                                               self._vtype, self._dtype, 
                                               self.name, id(self)))
    
    def expression(self, names):
        return names[self]
    
    def definition(self, names):
        if self.vtype is None:
            raise RuntimeError("Variable has no vtype: %r" % self)
        if self.dtype is None:
            raise RuntimeError("Variable has no dtype: %r" % self)
        
        name = names[self]
        if self.vtype == 'const':
            return '%s %s %s = %s;' % (self.vtype, self.dtype, name, 
                                       self.value)
        else:
            return '%s %s %s;' % (self.vtype, self.dtype, name)


class Varying(Variable):
    """ Representation of a varying
    
    Varyings can inherit their dtype from another Variable, allowing for
    more flexibility in composing shaders.
    """
    def __init__(self, name, dtype=None):
        self._link = None
        Variable.__init__(self, name, vtype='varying', dtype=dtype)
        
    @property
    def value(self):
        """ The value associated with this variable.
        """
        return self._value
    
    @value.setter
    def value(self, value):
        if value is not None:
            raise TypeError("Cannot assign value directly to varying.")
    
    @property
    def dtype(self):
        if self._dtype is None:
            if self._link is None:
                return None
            else:
                return self._link.dtype
        else:
            return self._dtype

    def link(self, var):
        """ Link this Varying to another object from which it will derive its
        dtype. This method is used internally when assigning an attribute to
        a varying using syntax ``aFunction[varying] = attr``.
        """
        assert self._dtype is not None or hasattr(var, 'dtype')
        self._link = var
        self.changed()


class Expression(ShaderObject):
    """ Base class for expressions (ShaderObjects that do not have a
    definition nor dependencies)
    """
    
    def definition(self, names):
        # expressions are declared inline.
        return None


class TextExpression(Expression):
    """ Plain GLSL text to insert inline
    """
    
    def __init__(self, text):
        super(TextExpression, self).__init__()
        if not isinstance(text, string_types):
            raise TypeError("Argument must be string.")
        self._text = text
    
    def __repr__(self):
        return '<TextExpression %r for at 0x%x>' % (self.text, id(self))
    
    def expression(self, names=None):
        return self._text
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, t):
        self._text = t
        self.changed()

    def __eq__(self, a):
        if isinstance(a, TextExpression):
            return a._text == self._text
        elif isinstance(a, string_types):
            return a == self._text
        else:
            return False
    
    def __hash__(self):
        return self._text.__hash__()


class FunctionCall(Expression):
    """ Representation of a call to a function
    
    Essentially this is container for a Function along with its signature. 
    """
    def __init__(self, function, args):
        super(FunctionCall, self).__init__()
        
        if not isinstance(function, Function):
            raise TypeError('FunctionCall needs a Function')
        
        sig_len = len(function.args)
        if len(args) != sig_len:
            raise TypeError('Function %s requires %d arguments (got %d)' %
                            (function.name, sig_len, len(args)))
        
        # Ensure all expressions
        sig = function.args
        
        self._function = function
        
        # Convert all arguments to ShaderObject, using arg name if possible.
        self._args = [ShaderObject.create(arg, ref=sig[i][1]) 
                      for i, arg in enumerate(args)]
        
        self._add_dep(function)
        for arg in self._args:
            self._add_dep(arg)
    
    def __repr__(self):
        return '<FunctionCall of %r at 0x%x>' % (self.function.name, id(self))
    
    @property
    def function(self):
        return self._function
    
    @property
    def dtype(self):
        return self._function.rtype
    
    def expression(self, names):
        str_args = [arg.expression(names) for arg in self._args]
        args = ', '.join(str_args)
        fname = self.function.expression(names)
        return '%s(%s)' % (fname, args)


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
