# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Definition of inputs (uniforms and attributes( for a shader program.

This code is inspired by similar classes from Pygly.

"""

from __future__ import print_function, division, absolute_import

import sys
import weakref
import ctypes

import numpy as np

from vispy import gl
from . import ext_available
from . import Texture, VertexBuffer
from .vbo import VertexBufferView


if sys.version_info > (3,):
    basestring = str


# Note: the ShaderProgram is a friend: it calls private methods of this class.

class BaseInputs(object):
    """ Base proxy class for uniforms, samplers and attributes.
    """
    
    def __init__(self, program):
        self._program_ref = weakref.ref(program)
        self._handles = {}  # Cache of known handles
        self._static = {}  # Static values (set while program not enabled)
    
    
    def __setattr__(self, name, value):
        # Act normal
        object.__setattr__(self, name, value)
        
        # Public attributes are considered  attribute, sampler, sttribute
        if not name.startswith('_'):
            # Get prepared values
            name, value = self._prepare(name, value)
            # Apply or store as static?
            if self._program._enabled:
                self._apply(name, value)
            else:
                self._static[name] = value
    
    
    @property
    def _program(self):
        program = self._program_ref()
        if program is not None:
            return program
        else:
            raise RuntimeError('Reference to program lost.')
    
    
    def _apply_static(self):
        """ Apply static attributes now. Called by the ShaderProgram in the
        _enable method.
        """
        self._prepare_for_drawing()  # Allow subclasses to prepare
        for name, value in self._static.items():
            self._apply(name, value)
    
    
    def _clear_cache(self):
        self._handles = {}
    
    
    def _prepare(self, name, value):
        raise NotImplementedError()
    
    def _apply(self, name, value, enabled):
        raise NotImplementedError()


# todo: tuple means vector, numpy array means matrix?

class UniformInputs(BaseInputs):
    """ Proxy to assign uniform values to a ShaderProgram.
    To use, simply assign values as if it were a dictionary.
    """
    
    _TYPES = { 
        gl.GL_FLOAT:        (gl.glUniform1fv, 1),
        gl.GL_FLOAT_VEC2:   (gl.glUniform2fv, 2),
        gl.GL_FLOAT_VEC3:   (gl.glUniform3fv, 3),
        gl.GL_FLOAT_VEC4:   (gl.glUniform4fv, 4),
        gl.GL_INT:          (gl.glUniform1iv, 1),
        gl.GL_INT_VEC2:     (gl.glUniform2iv, 2),
        gl.GL_INT_VEC3:     (gl.glUniform3iv, 3),
        gl.GL_INT_VEC4:     (gl.glUniform4iv, 4),
        gl.GL_BOOL:         (gl.glUniform1iv, 1),
        gl.GL_BOOL_VEC2:    (gl.glUniform2iv, 2),
        gl.GL_BOOL_VEC3:    (gl.glUniform3iv, 3),
        gl.GL_BOOL_VEC4:    (gl.glUniform4iv, 4),
        gl.GL_FLOAT_MAT2:   (gl.glUniformMatrix2fv, 4),
        gl.GL_FLOAT_MAT3:   (gl.glUniformMatrix3fv, 9),
        gl.GL_FLOAT_MAT4:   (gl.glUniformMatrix4fv, 16),
        gl.GL_SAMPLER_2D:   (gl.glUniform1i, 1),
        gl.GL_SAMPLER_CUBE: (gl.glUniform1i, 1),
        }

    
    def _prepare_for_drawing(self):
        # Reset sampler counter
        self._sampler_count = 0
    
    
    def _prepare(self, name, value):
        """ Set uniform value. The value can be a tuple of floats/ints,
        or a single numpy array. Uniform vectors can be 1,2,3,4 elements.
        Matrices can be 4, 9 or 16 elements.
        """
        
        if isinstance(value, Texture):
            return name, weakref.ref(value)
        elif isinstance(value, np.ndarray):
            pass
        else:
            # Let numpy make it a nice array, and determine the dtype
            value = np.array(value)
        
        # Check size 
        if value.size not in (1,2,3,4, 9, 16):
            raise ValueError("Invalid number of values for uniform")
        
        return name, value
    
    
    def _apply(self, name, value):
        """ Used internally to set the uniform from a cached value.
        """
        
        # Get uniform location
        try:
            loc, type, fun, n = self._handles[name]
        except KeyError:
            # Get location
            loc = gl.glGetUniformLocation(self._program.handle, name.encode('utf-8'))
            # Get type, convert to function + numel
            type, fun, n = 0, None, 0
            if loc >= 0:
                _name, length, type = gl.glGetActiveUniform(self._program.handle, loc)
                fun, n = self._TYPES[type]
            self._handles[name] = loc, type, fun, n
        
        # Our uniform may have been optimized out
        if loc < 0:
            return 
        
        # Get value if it's a weakref
        if isinstance(value, weakref.ReferenceType):
            value = value()
            if value is None:
                return
        
        
        if isinstance(value, Texture):
            # Check if it also a sampler in GLSL
            if type not in (gl.GL_SAMPLER_2D, gl.GL_SAMPLER_CUBE):
                raise RuntimeError('Uniform %s is not a sampler.' % name)
            # Apply
            self._apply_sampler(loc, value)
        else:
            # Check if size matches with that in GLSL
            if value.size != n:
                raise RuntimeError('Uniform %s has %i elements, not %i.' % (name, n, value.size))
            # Apply
            if type in (gl.GL_FLOAT_MAT2, gl.GL_FLOAT_MAT3, gl.GL_FLOAT_MAT4):
                transpose = False 
                fun(loc, 1, transpose, value)
            else:
                fun(loc, 1, value)
    
    
    def _apply_sampler(self, loc, value):
        # Determine unit id 
        unit = self._sampler_count
        self._sampler_count += 1
        # Enable the texture, apply the unit, and bind it to the uniform
        self._program.enable_object(value(unit))
        #gl.glActiveTexture(gl.GL_TEXTURE0 + unit)  # Done in Texture._enable()
        gl.glUniform1i(loc, unit)



class AttributeInputs(BaseInputs):
    """ Proxy to assign attributes (vertex array or VertexBuffer) to a
    ShaderProgram. To use, simply assign values as if it were a dictionary.
    """
    
    def _prepare_for_drawing(self):
        # Reset counter
        self._vertex_count = None
    
    
    def _update_vertex_counter(self, count):
        if count:
            if self._vertex_count is None:
                self._vertex_count = count
            else:
                self._vertex_count = min(self._vertex_count, count)
    
    
    @property
    def vertex_count(self):
        """ The number of vertices to draw.
        """ 
        return self._vertex_count
    
    
    def _prepare(self, name, value):
        """ value can be either a VBO, a clien-array (numpy) or a tuple
        that represents the same value for all vertices.
        """
        if isinstance(value, (int, float)):
            return name, (value,)
        elif isinstance(value, tuple):
            assert len(value) in (1,2,3,4)
            return name, value
        elif isinstance(value, np.ndarray):
            # Check dimensions
            assert value.ndim == 2
            assert value.shape[1] in (1,2,3,4)
            # Ensure it is a type that OpenGL can understand
            if not value.dtype.name in VertexBuffer.DTYPES:
                value = value.astype(np.float32)
            # Return
            return name, weakref.ref(value)
        elif isinstance(value, (VertexBuffer, VertexBufferView)):
            return name, weakref.ref(value)
        else:
            raise ValueError("Vertex attribute must be VertexBuffer or numpy array.")
    
    
    def _apply(self, name, value):
        
        program = self._program
        
        # todo: like uniforms, we should probably query the type here ...
        # Get attribute location
        try:
            loc = self._handles[name]
        except KeyError:
            loc = gl.glGetAttribLocation(program.handle, name.encode('utf-8'))
            self._handles[name] = loc
        
        # Our attribute may have been optimized out
        if loc < 0:
            return 
        
        # Get value if it's a weakref
        if isinstance(value, weakref.ReferenceType):
            value = value()
            if value is None:
                return
        
        
        if isinstance(value, tuple):
            # Global vertex value
            size = 0
            
            # Tell OpenGL to use this value and not the array
            gl.glDisableVertexAttribArray(loc)
            
            # Apply. Note that we checked the size of value in _prepare
            {   1 : gl.glVertexAttrib1f,
                2 : gl.glVertexAttrib2f,
                3 : gl.glVertexAttrib3f,
                4 : gl.glVertexAttrib4f}[len(value)](loc, *value)
        
        elif isinstance(value, np.ndarray):
            # Vertex array (local (non-gpu memory)
            
            self._update_vertex_counter(value.shape[0])
            
            # Prepare
            size = value.shape[1]
            gltype = VertexBuffer.DTYPES[value.dtype.name]
            stride = 0
            
            # Tell OpenGL to use the array and not the glVertexAttrib* value
            gl.glEnableVertexAttribArray(loc)
            
            # Apply (first disable any previous VertexBuffer)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
            gl.glVertexAttribPointer(loc, size, gltype, False, stride, value)
        
        else:
            # Vertex Buffer Object
            
            self._update_vertex_counter(value.shape[0])
            
            # Prepare
            size = value.shape[1]
            gltype = VertexBuffer.DTYPES[value.type]
            offset, stride = value._offset, value._stride  # view_params not on VertexBuffer
            # Make offset a pointer, or it will be interpreted as a small array
            offset = ctypes.c_voidp(offset)
            
            # Tell OpenGL to use the array and not the glVertexAttrib* value
            gl.glEnableVertexAttribArray(loc)
            
            # Apply (enable VBO to associate it with the pointer)
            if isinstance(value, VertexBufferView):
                program.enable_object(value.buffer)
            else:
                program.enable_object(value)
            gl.glVertexAttribPointer(loc, size, gltype, False, stride, offset)
        
    