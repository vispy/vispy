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
    
    Shader objects have a *declaration* that defines the object in GLSL, an 
    *expression* that is used to reference the object, and a set of 
    *dependencies* that must be declared before the object is used.
    
    Dependencies are tracked hierarchically such that changes to the 
    *expression* of any object will invalidate the *declaration* of its 
    dependents.
    """
    
    # todo: handle name, oname, rename, etc.
    
    def __init__(self):
        # emitted when any part of the code for this object has changed,
        # including dependencies.
        self.changed = EventEmitter(source=self, type="code_change")
        
        # objects that must be declared before this object's declaration.
        # {obj: refcount}
        self._deps = {}
        
    @property
    def name(self):
        return None
        
    def declaration(self, obj_names):
        """ Return the GLSL declaration for this object. Use *obj_names* to
        determine the names of dependencies.
        """
        return None
    
    def expression(self, obj_names):
        """ Return the GLSL expression used to reference this object.
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
        
        # Finally, you can set special variables explicitly
        vert_code['gl_PointSize'] = 'uniform float u_pointsize'
    
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
        #self._expressions = OrderedDict()
        
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
                                "varyings, not %s" % key.type)
        elif isinstance(key, string_types):
            if key[:11] in ['gl_PointSiz', 'gl_Position', 'gl_FragColo']:
                storage = self._post_hooks
            elif key in self._template_vars:
                storage = self._replacements
            else:
                raise KeyError('Invalid template variable %r' % key)
        else:
            raise TypeError('In `function[key]` key must be a string or '
                            'varying.')
        
        # Remove old references, if any
        oldval = storage.pop(key, None)
        if oldval is not None:
            for obj in (key, oldval):
                if isinstance(obj, ShaderObject):
                    self.remove_dep(obj)
                
        # Add new references
        if val is not None:
            if not isinstance(val, string_types + (ShaderObject,)):
                if isinstance(key, Variable):
                    vname = key.name
                else:
                    vname = key
                val = Variable(vname, val)
                
            if isinstance(key, Variable):
                # tell this varying to inherit properties from 
                # its source attribute.
                key.link(val)
                
            storage[key] = val
            for obj in (key, val):
                if isinstance(obj, ShaderObject):
                    self.add_dep(obj)

        # In case of verbatim text, we might have added new template vars
        if isinstance(val, string_types):
            for var in parsing.find_template_variables(val):
                if var not in self._template_vars:
                    # LC: need append here to ensure we don't attempt to 
                    #     replace these placeholders until they have been 
                    #     added to the code.
                    self._template_vars.append(var.lstrip('$'))
        
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
            return self._replacements[key]
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
    
    #def get_variables(self):
        #""" Get a list of all variable objects defined in the current program.
        #When this function is linked, it gets *all* variables.
        #"""
        #deps = self._dependencies(True)
        #return [dep for dep in deps.keys() if isinstance(dep, Variable)]
    
    #def link(self, frag_func):
        #""" Link a vertex and fragment shader
        
        #Both functions need to represent main-functions. When the vertex
        #and fragment shader are linked, the scope for name mangling is
        #shared, and it allows for setting varyings
        #"""
        ## Check 
        #if not isinstance(frag_func, Function):
            #raise ValueError('Can only link to a Function object.')
        #if not self.name == 'main':
            #raise ValueError('Can only link if this is a main-function.')
        #if not frag_func.name == 'main':
            #raise ValueError('Can only link to a main-function.')
        ## Apply
        #vert_func = self
        #vert_func._linked = frag_func, 'vertex'
        #frag_func._linked = vert_func, 'fragment'
        ## After linking we likely need renaming
        #vert_func._last_changed = time.time()
        #frag_func._last_changed = time.time()
    
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
        return list(template_vars)
    
    #def _rename(self, name):
        #""" Set the name to be applied when compiling this function.
        #"""
        #if self.name == 'main':
            #raise ValueError('Cannot rename the main function.')
        #self._name = name
        #self._last_changed = time.time()
        
    def _get_replaced_code(self, names):
        """ Return code, with new name, expressions, and replacements applied.
        """
        code = self._code
        
        # Modify name
        code = code.replace(" " + self.name + "(", " " + names[self] + "(")

        def replace(code, key, val):
            search = r'\$' + key + r'($|[^a-zA-Z0-9_])'
            return re.sub(search, val+r'\1', code)
        
        # Apply string replacements first -- these may contain $placeholders
        for key, val in self._replacements.items():
            if isinstance(val, string_types):
                code = replace(code, key, val)
        
        # Apply post-hooks
        
        # Collect post lines
        post_lines = []
        for key, val in self._post_hooks.items():
            if isinstance(key, Variable):
                key = names[key]
            if isinstance(val, ShaderObject):
                val = val.expression(names)
            line = '\n    %s = %s;' % (key, val)
            post_lines.append(line)
            
        # Apply placeholders for hooks
        post_text = ''.join(post_lines) + '\n'
        code = code.rpartition('}')
        code = code[0] + post_text + code[1] + code[2]
        
        # Apply template variables
        for key, val in self._replacements.items():
            if isinstance(val, ShaderObject):
                val = val.expression(names)
                code = replace(code, key, val)

        # Done
        
        if '$' in code:
            v = parsing.find_template_variables(code)
            logger.warning('Unsubstituted placeholders in code: %s\n'
                           '  replacements made: %s' % 
                           (v, self._replacements.keys()))
        
        return code
    
    #def _dependencies(self, also_linked=False):
        #""" Get the dependencies (Functions and Variables) for this
        #expression.
        #"""
        ## Get list of expressions, taking linking into account
        #expressions1, expressions2 = self._expressions.values(), []
        #if also_linked and self._linked:
            #expressions2 = self._linked[0]._expressions.values()
            #if self._linked[1] == 'fragment':
                #expressions1, expressions2 = expressions2, expressions1
        ## Collect dependencies
        #deps = OrderedDict()
        #for dep in expressions1:
            #deps.update(dep._dependencies())
        #for dep in expressions2:
            #deps.update(dep._dependencies())
        #return deps
    
    #def _definition(self):
        #ret = self._signature[2]
        #sig = [s[0] for s in self._signature[1]]
        #return '%s %s(%s);' % (ret, self.name, ', '.join(sig))
        
        
    def declaration(self, names):
        return self._get_replaced_code(names)

    def expression(self, names):
        return names[self]
    
    #def _mangle_names(self):
        #""" Mangle names of dependencies where necessary. Objects only
        #gets renamed if there are > 1 objects with that name, and if
        #they are not already renamed appropriatly. We use dep._oname
        #and dep._rename() here.
        #"""
        ## Collect all dependencies with the same name
        #deps = self._dependencies(True)
        #names = {}
        #for dep in deps:
            #deps_with_this_name = names.setdefault(dep._oname, [])
            #deps_with_this_name.append(dep)
        ## Mangle names where necessary
        #for name, deps_with_this_name in names.items():
            #nameset = set([dep.name for dep in deps_with_this_name])
            #if len(nameset) > 1:
                #nameset.discard(name)  # if > 1, all must be mangled
            #if len(nameset) != len(deps_with_this_name):
                #for i, dep in enumerate(deps_with_this_name):
                    #dep._rename(dep._oname + '_' + str(i+1))
    
    #def _compile(self):
        #""" Apply the replacements and add code for dependencies.
        #Return new code string.
        #"""
        ## Init
        #code = ''
        #self._mangle_names()
        #deps = self._dependencies()
        ## Write header
        #if self.name == 'main':
            #code += '#version 120\n'  # (or not)
        #code += '// Code generated by vispy.scene.shaders.Function\n\n'
        ## Add variable definitions
        #for dep in deps:
            #if isinstance(dep, Variable):
                #code += dep._definition() + '\n'
        #code += '\n'
        ## Add function definitions
        #for dep in deps:
            #if isinstance(dep, Function):
                #code += dep._definition() + '\n'
        #code += '\n'
        ## Add our code
        #code += self._get_replaced_code()
        ## Add code for dependencies
        #for dep in deps:
            #if isinstance(dep, Function):
                #code += '\n\n'
                #code += dep._get_replaced_code()
        ## Done
        #self._last_compiled = time.time()
        #return code.rstrip() + '\n'

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


#class Expression(ShaderObject):
    #""" Base class for things that template variables can be replaced with.
    #"""
    
    #def _dependencies(self):
        #""" Get the dependencies (Function and Variable objects) for this
        #expression.
        #"""
        #raise NotImplementedError()
    
    #def _injection(self):
        #""" Get the piece of code that is to be replaced at the template
        #variable.
        #"""
        #raise NotImplementedError()


#class TextExpression(Expression):
    #""" Representation of a piece of verbatim code
    #"""
    
    #def __init__(self, text):
        #if not isinstance(text, string_types):
            #raise ValueError('TextExpression needs a string.')
        #super(TextExpression, self).__init__()
        #self._text = text
    
    #def expression(self):
        #""" The text for this expression.
        #"""
        #return self._text
    
    #def __repr__(self):
        #return "<TextExpression %r at 0x%x>" % (self._text, id(self))
    
    ##def _dependencies(self):
        ##return OrderedDict()
    
    ##def _injection(self):
        ##return self._text


class Variable(ShaderObject):
    """ Representation of global shader variable
    
    These can include: const, uniform, attribute, varying, inout

    Created by Function.__getitem__
    """
    def __init__(self, name, value=None, vtype=None, dtype=None):
        super(Variable, self).__init__()
        
        # allow full declaration in first argument
        if ' ' in name:
            vtype, dtype, name = name.split(' ')
        
        self._state_counter = 0
        self._name = name
        self._vtype = vtype
        self._dtype = dtype
        
        # If vtype/dtype were given at init, then we will never
        # try to set these values automatically.
        self._type_locked = self._vtype is not None and self._dtype is not None
            
        self.value = value
        
        assert self._vtype in VARIABLE_TYPES

    @property
    def name(self):
        """ The name of this variable.
        """
        return self._name
    
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
            self.changed()
            return
        
        if isinstance(value, (tuple, list)):
            self._vtype = 'uniform'
            self._dtype = 'vec%d' % len(value)
        elif np.isscalar(value):
            self._vtype = 'uniform'
            if isinstance(value, (float, np.floating)):
                self._dtype = 'float'
            elif isinstance(value, (int, np.integer)):
                self.dtype = 'int'
            else:
                raise TypeError("Unknown data type %r for variable %r" % 
                                (type(value), self))
        elif hasattr(value, 'glsl_type'):
            self._vtype, self._dtype = value.glsl_type
        else:
            raise TypeError("Unknown data type %r for variable %r" % 
                            (type(value), self))
            
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
    
    def _rename(self, name):
        self._name = name
        self._last_changed = time.time()
        self.decl_changed()
        self.expr_changed()
    
    def declaration(self, names):
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
    def declaration(self, names):
        # expressions are declared inline.
        return None


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
            raise ValueError('FunctionCall needs a Function')
        
        sig_len = len(function._signature[1])
        if len(args) != sig_len:
            raise ValueError('Function %s requires %d arguments (got %d)' %
                             (function, sig_len, len(args)))
        
        # Ensure all expressions
        sig = function._signature[1]
        #args = [_convert_to_expression(args[i], altname=sig[i][1]) 
                #for i in range(len(args))]
        
        self._function = function
        self._args = args
        self._expr = None
        
        self.add_dep(function)
        for arg in args:
            if isinstance(arg, ShaderObject):
                self.add_dep(arg)
    
    def __repr__(self):
        return '<FunctionCall %r for at 0x%x>' % (self.name, id(self))
    
    @property
    def function(self):
        return self._function
    
    @property
    def dtype(self):
        return self._function._signature[0]
    
    #def _dependencies(self):
        #d = OrderedDict()
        ## Add "our" function and its dependencies
        #d[self.function] = None
        #d.update(self.function._dependencies())
        ## Add dependencies of each or our arguments
        #for arg in self._signature:
            #d.update(arg._dependencies())
        #return d
    
    def expression(self, names):
        str_args = [arg.expression(names) for arg in self._args]
        args = ', '.join(str_args)
        fname = self.function.expression(names)
        return '%s(%s)' % (fname, args)
    

#def _convert_to_expression(val, altname=None):
    #""" Convert input to an expression. If an expression is given, it
    #is left unchanged. An error is raised if an Expression could not
    #be returned.
    #"""
    #if isinstance(val, Expression):
        #return val
    #elif isinstance(val, string_types):
        #try:
            #return Variable(val, altname=altname)
        #except ValueError:
            #return TextExpression(val)
    #elif isinstance(val, tuple):
        #if len(val) == 2:
            #return Variable(val[0], val[1], altname=altname)
    #elif isinstance(val, Function):
        ## Be friendly for people who forget to call a function
        #raise ValueError('A Function is not an expression, it\'s "call" is.')
    ## Else ...
    #raise ValueError('Cannot convert to Expression: %r' % val)
