# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import numpy as np
from ...ext.six import string_types
from .shader_object import ShaderObject

VARIABLE_TYPES = ('const', 'uniform', 'attribute', 'varying', 'inout')


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
        a varying using syntax ``Function[varying] = attr``.
        """
        assert self._dtype is not None or hasattr(var, 'dtype')
        self._link = var
        self.changed()
