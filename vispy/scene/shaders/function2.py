"""
Classses representing GLSL objects (functions, variables, etc) that may be
composed together to create complete shaders. 
See the docstring of Function for details.

Details
-------

A complete GLSL program is composed of ShaderObjects, each of which may be used
inline as an expression, and some of which include a definition that must be
included on the final code. ShaderObjects kepp track of a hierarchy of
dependencies so that all necessary code is included at compile time, and
changes made to any object may be propagated to the root of the hierarchy to 
trigger a recompile.
"""

import time
import re
import numpy as np

from ...util.ordereddict import OrderedDict
from ...util.event import EventEmitter
from ...util import logger
from ...ext.six import string_types
from . import parsing
from .compiler import Compiler

VARIABLE_TYPES = ('const', 'uniform', 'attribute', 'varying', 'inout')


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
                    
        if isinstance(obj, ShaderObject):
            if isinstance(obj, Variable) and obj.name is None:
                obj.name = ref
        elif isinstance(obj, string_types):
            obj = TextExpression(obj)
        else:
            obj = Variable(ref, obj)
        
        return obj
        
    
    def __init__(self):
        # emitted when any part of the code for this object has changed,
        # including dependencies.
        self.changed = EventEmitter(source=self, type="code_change")
        
        # objects that must be declared before this object's definition.
        # {obj: refcount}
        self._deps = {}
        
    @property
    def name(self):
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
    
    def dependencies(self):
        """ Return all dependencies required to use this object. The last item 
        in the list is *self*.
        """
        alldeps = []
        for dep in self._deps:
            alldeps.extend(dep.dependencies())
        alldeps.append(self)
        return alldeps
        
    def add_dep(self, dep):
        """ Increment the reference count for *dep*. If this is a new 
        dependency, then connect to its *changed* event.
        """
        if dep in self._deps:
            self._deps[dep] += 1
        else:
            self._deps[dep] = 1
            dep.changed.connect(self._dep_changed)

    def remove_dep(self, dep):
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
        self.changed()
    

class Function(ShaderObject):
    """ Representation of a GLSL function
    
    Objects of this class can be used for re-using and composing GLSL
    snippets. Each Function consists of a GLSL snippet in the form of
    a function. The code may have template variables that start with
    the dollar sign. These stubs can be replaced with expressions using
    the index operation. Expressions can be plain text or any ShaderObject
    that defines an expression() method.
    
    Example
    -------
    
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

        #
        # Three ways to assign to template variables:
        #
        # 1) Assign verbatim code
        vert_code['xoffset'] = '(3.0 / 3.1415)'

        # 2) Assign a value (this creates a new uniform or attribute)
        vert_code['yoffset'] = 5.0

        # 3) Assign a function call expression
        pos_var = 'attribute vec4 a_position'
        vert_code['pos'] = trans1(trans2(pos_var))  

        # Transforms also need their variables set
        trans1['scale'] = 0.5
        trans2['scale'] = (1.0, 0.5, 1.0, 1.0)

        # You can actually change any code you want, but use this with care!
        vert_code.replace('gl_Position.y', 'gl_Position.z')

        # Finally, you can set special variables explicitly. This generates
        # a new statement at the end of the vert_code function.
        vert_code['gl_PointSize'] = 10.
    
    
    If we use ``str(vert_code)`` we get::

        uniform float scale;
        vec4 transform_scale(vec4 pos){
            return pos * scale;
        }

        uniform vec4 scale_1;
        vec4 transform_scale_1(vec4 pos){
            return pos * scale_1;
        }

        uniform float gl_PointSize;
        uniform float yoffset;
        void main() {
            gl_Position = transform_scale(transform_scale_1(attribute vec4 a_position));
            gl_Position.x += (3.0 / 3.1415);
            gl_Position.z += yoffset;

            gl_PointSize = gl_PointSize;
        }
    
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
        code['scale'] = scale_func  # No need to specify args
    
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
    varyings is to use the following method:
        
        // This is how to link
        vert_code.link(frag_code)
        
        // Pass attribute data to the fragment shader
        frag_code['color'] = 'varying vec3 v_color'
        variable = frag_code['color']
        vert_code[variable] = 'attribute vec3 a_color'
    
    """
    
    def __init__(self, code):
        super(Function, self).__init__()
        
        # Get and strip code
        if isinstance(code, Function):
            code = code._code
        elif not isinstance(code, string_types):
            raise ValueError('Function needs a string or Function.')
        self._code = self._clean_code(code)
        
        # Get some information derived from the code
        try:
            self._signature = parsing.parse_function_signature(self._code)
        except Exception as err:
            raise ValueError('Invalid code: ' + str(err))
        self._name = self._signature[0]
        self._template_vars = self._parse_template_vars()
        
        ## Expressions replace template variables (also our dependencies)
        self._expressions = OrderedDict()
        
        # Verbatim string replacements
        self._replacements = OrderedDict()
        
        ## Stuff to do at the end
        self._post_hooks = OrderedDict()
        
        # Toplevel vertex/fragment shader funtctions can be linked
        #self._linked = None
        
        # flags to be able to indicate whether code has changed
        #self._last_changed = time.time()
        #self._last_compiled = 0.0 
    
    def __setitem__(self, key, val):
        """ Setting of replacements through a dict-like syntax.
        
        Each replacement can be:
        * verbatim code: ``fun1['foo'] = '3.14159'``
        * a FunctionCall: ``fun1['foo'] = fun2()``
        * a Variable: ``fun1['foo'] = 'uniform vec3 u_ray'``
        """
        if isinstance(key, Variable): 
            if key.vtype == 'varying':
                if self.name != 'main':
                    raise Exception("Varying assignment only alowed in 'main' "
                                    "function.")
                storage = self._post_hooks
            else:
                raise TypeError("Variable assignment only allowed for "
                                "varyings, not %s" % key.vtype)
        elif isinstance(key, string_types):
            if any(map(key.startswith, 
                       ('gl_PointSize', 'gl_Position', 'gl_FragColor'))):
                storage = self._post_hooks
            elif key in self._template_vars:
                storage = self._expressions
            else:
                raise KeyError('Invalid template variable %r' % key)
        else:
            raise TypeError('In `function[key]` key must be a string or '
                            'varying.')

        
        if storage.get(key) == val:
            # values already match; bail out now
            return
        
        # Remove old references, if any
        oldval = storage.pop(key, None)
        if oldval is not None:
            for obj in (key, oldval):
                if isinstance(obj, ShaderObject):
                    self.remove_dep(obj)
                
        # Add new references
        if val is not None:
            val = ShaderObject.create(val, ref=key)
                
            if isinstance(key, Varying):
                # tell this varying to inherit properties from 
                # its source attribute / expression.
                key.link(val)
                
            storage[key] = val
            for obj in (key, val):
                if isinstance(obj, ShaderObject):
                    self.add_dep(obj)

        # In case of verbatim text, we might have added new template vars
        if isinstance(val, TextExpression):
            for var in parsing.find_template_variables(val.expression()):
                if var not in self._template_vars:
                    self._template_vars.add(var.lstrip('$'))
        
        self.changed()
    
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
        
        if key not in self._template_vars:
            raise KeyError('Invalid template variable %r' % key) 
        else:
            raise KeyError('No value known for key %r' % key)
    
    def __call__(self, *args):
        """ Set the signature for this function and return an FunctionCall
        object. Each argument can be verbatim code or a FunctionCall object.
        """
        return FunctionCall(self, args)
    
    def __repr__(self):
        return "<Function '%s' at 0x%x>" % (self.name, id(self))
    
    def __str__(self):
        compiler = Compiler(func=self)
        return compiler.compile()['func']
    
    ## Public API methods
    
    @property
    def name(self):
        """ The function name. The name may be mangled in the final code
        to avoid name clashes.
        """
        return self._name
    
    #def ischanged(self, since=None):
        #""" Whether the code has been modified since the last time it
        #was compiled, or since the given time.
        #"""
        #since = since or self._last_compiled
        #ischanged = True
        #if since > self._last_changed:
            #for dep in self._dependencies(True):
                #if since < dep._last_changed:
                    #break
            #else:
                #ischanged = False
        #return ischanged
    
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
            self.changed()
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
                           (v, self._expressions.keys()))
        
        return code + '\n'
    
    def definition(self, names):
        return self._get_replaced_code(names)

    def expression(self, names):
        return names[self]
    
    def _clean_code(self, code):
        """ Return *code* with indentation and leading/trailing blank lines
        removed. 
        """
        lines = code.strip().split("\n")
        min_indent = 100
        for line in lines:
            if line.strip() != "":
                indent = len(line) - len(line.lstrip())
                min_indent = min(indent, min_indent)
        if min_indent > 0:
            lines = [line[min_indent:] for line in lines]
        code = "\n".join(lines)
        return code


class Variable(ShaderObject):
    """ Representation of global shader variable
    
    These can include: const, uniform, attribute, varying, inout

    Created by Function.__getitem__
    """
    def __init__(self, name, value=None, vtype=None, dtype=None):
        super(Variable, self).__init__()
        
        # allow full definition in first argument
        if ' ' in name:
            vtype, dtype, name = name.split(' ')
            
        if not isinstance(name, string_types + (None,)):
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
        
        assert self._vtype is None or self._vtype in VARIABLE_TYPES

    @property
    def name(self):
        """ The name of this variable.
        """
        return self._name
    
    @name.setter
    def name(self, n):
        if self._name != n:
            self._name = n
            self.changed()
    
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
        self._value = value
        self._state_counter += 1
        if self._type_locked:
            # Don't emit here--this should not result in a code change.
            #self.changed()
            return
        
        if isinstance(value, (tuple, list)):
            vtype = 'uniform'
            dtype = 'vec%d' % len(value)
        elif np.isscalar(value):
            vtype = 'uniform'
            if isinstance(value, (float, np.floating)):
                dtype = 'float'
            elif isinstance(value, (int, np.integer)):
                dtype = 'int'
            else:
                raise TypeError("Unknown data type %r for variable %r" % 
                                (type(value), self))
        elif hasattr(value, 'glsl_type'):
            vtype, dtype = value.glsl_type
        else:
            raise TypeError("Unknown data type %r for variable %r" % 
                            (type(value), self))
            
        # update vtype/dtype and emit changed event if necessary
        changed = False
        if self._dtype != dtype:
            self._dtype = dtype
            changed = True
        if self._vtype != vtype:
            self._vtype = vtype
            changed = True
        if changed:
            self.changed()
    
    @property
    def state_id(self):
        """Return a unique ID that changes whenever the state of the Variable
        has changed. This allows ModularProgram to quickly determine whether
        the value has changed since it was last used."""
        return id(self), self._state_counter

    def __repr__(self):
        return ("<Variable \"%s %s %s\" at 0x%x>" % (self._vtype, self._dtype, 
                                                     self.name, id(self)))
    
    #def _dependencies(self):
        #d = OrderedDict()
        #d[self] = None
        #return d
    
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
        dtype.
        """
        assert self._dtype is not None or hasattr(var, 'dtype')
        self._link = var
        self.changed()


class Expression(ShaderObject):
    def definition(self, names):
        # expressions are declared inline.
        return None
    

class TextExpression(Expression):
    """ Plain GLSL text to insert inline.
    """
    def __init__(self, text):
        super(TextExpression, self).__init__()
        self._text = text
        
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


class FunctionCall(Expression):
    """ Representation of a call to a function
    
    Essentially this is container for a Function along with its
    signature. Objects of this class generally live very short; they
    serve only as a message. The signature is either incorporated in
    the next FunctionCall or in the replacement at a function.
    """
    
    def __init__(self, function, args):
        super(FunctionCall, self).__init__()
        
        if not isinstance(function, Function):
            raise TypeError('FunctionCall needs a Function')
        
        sig_len = len(function._signature[1])
        if len(args) != sig_len:
            raise TypeError('Function %s requires %d arguments (got %d)' %
                            (function.name, sig_len, len(args)))
        
        # Ensure all expressions
        sig = function._signature[1]
        
        self._function = function
        
        # Convert all arguments to ShaderObject, using arg name if possible.
        self._args = [ShaderObject.create(arg, ref=sig[i][1]) 
                      for i,arg in enumerate(args)]
        
        self.add_dep(function)
        for arg in self._args:
            self.add_dep(arg)
    
    def __repr__(self):
        return '<FunctionCall %r for at 0x%x>' % (self.name, id(self))
    
    @property
    def function(self):
        return self._function
    
    @property
    def dtype(self):
        return self._function._signature[0]
    
    def expression(self, names):
        str_args = [arg.expression(names) for arg in self._args]
        args = ', '.join(str_args)
        fname = self.function.expression(names)
        return '%s(%s)' % (fname, args)
    
