# -*- coding: utf-8 -*-
""" Definition of shader classes.

This code is inspired by similar classes from Pygly.

"""

from __future__ import print_function, division, absolute_import

import sys

import numpy as np

from vispy import gl
from . import GLObject, push_enable, pop_enable, ext_available

if sys.version_info > (3,):
    basestring = str



class BaseShader(GLObject):
    """ Abstract shader class.
    """
    
    def __init__(self, type, source=None):
        
        # Check and store type
        if type not in [gl.GL_VERTEX_SHADER, gl.GL_FRAGMENT_SHADER]:
            raise ValueError('Type must be vertex or fragment shader.')
        self._type = type
        
        self._handle = 0
        self._compiled = 0  # 0: not compiled, 1: compile tried, 2: compile success 
        self.set_source(source)
    
    
    def _delete(self):
        gl.glDeleteShader(self._handle)
    
    
    def set_source(self, source):
        """ Set the source of the shader.
        """
        self._source = source
        self._compiled = 0  # force recompile 
        # Try to get description from first line
        # EXPERIMENTAL
        self._desciption = self._source.split('\n',1)[0].strip(' \t/*')
    
    
    def add_source(self, source):
        """ Templating, for later.
        """
        raise NotImplemented()
    
    
    def _enable(self):
        
        if self._handle <= 0:
            self._handle = gl.glCreateShader(self._type)
        
        # todo: what should happen if no source is given?
        if not self._source:
            self._compiled = 2
            return
        
        # If shader is compiled, we're done now
        if self._compiled:
            return 
        
        # Set compiled flag. It means that we tried to compile
        self._compiled = 1
        
        # Set source
        gl.glShaderSource(self._handle, self._source)
        
        # Compile the shader
        try:
            gl.glCompileShader(self._handle)
        except Exception as e:
            print( "Error compiling shader %r" % self )
            parse_shader_errors(e.description, self._source)
            raise

        # retrieve the compile status
        if not gl.glGetShaderiv(self._handle, gl.GL_COMPILE_STATUS):
            print( "Error compiling shader %r" % self )
            errors = gl.glGetShaderInfoLog(self._handle)
            parse_shader_errors(errors, self._source)
            raise RuntimeError(errors)
        
        # If we get here, compile is succesful
        self._compiled = 2
    
    
    def _disable(self):
        pass



class VertexShader(BaseShader):
    """ Representation of a vertex shader object. Inherits BaseShader.
    """
    def __init__(self, source=None):
        BaseShader.__init__(self, gl.GL_VERTEX_SHADER, source)
    
    def __repr__(self):
        if self._desciption:
            return "<VertexShader '%s'>" % self._desciption 
        else:
            return "<VertexShader at %s>" % hex(id(self)) 



class FragmentShader(BaseShader):
    """ Representation of a fragment shader object. Inherits BaseShader.
    """
    def __init__(self, source=None):
        BaseShader.__init__(self, gl.GL_FRAGMENT_SHADER, source)
    
    def __repr__(self):
        if self._desciption:
            return "<FragmentShader '%s'>" % self._desciption 
        else:
            return "<FragmentShader at %s>" % hex(id(self)) 
