# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
from ...ext.six import string_types
from .shader_object import ShaderObject


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
        from .function import Function
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
