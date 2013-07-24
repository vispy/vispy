# -*- coding: utf-8 -*-
""" Definition of Vertex Buffer Object class.

"""

from __future__ import print_function, division, absolute_import

import sys
import numpy as np

from vispy import gl
from . import GLObject, push_enable, pop_enable, ext_available

if sys.version_info > (3,):
    basestring = str

# Monkey-patch pyopengl to fix a bug in glBufferSubData
_m = sys.modules[gl.glBufferSubData.wrapperFunction.__module__]
_m.long = int


class BaseVertexBuffer(GLObject):
    """ The Vertexbuffer (a.k.a VBO or simply "Buffer") is used to
    store vertex data. It is recommended to use one of the subclasses:
    VertexBuffer or IndexBuffer.
    """
    
    # Data types that OpenGL ES 2.0 can understand
    _TYPEMAP =  {   'uint8':gl.GL_UNSIGNED_BYTE,    'int8':gl.GL_BYTE,
                    'uint16':gl.GL_UNSIGNED_SHORT,  'int16':gl.GL_SHORT, 
                    'float32':gl.GL_FLOAT, 
                    'float16': gl.ext.GL_HALF_FLOAT }
                    # GL_FIXED?
    
    
    def __init__(self, target, data=None):
        
        # Store target (i.e. array buffer of index buffer)
        if target not in [gl.GL_ARRAY_BUFFER, gl.GL_ELEMENT_ARRAY_BUFFER]:
            raise ValueError("Invalid target for vertex buffer object.")
        self._target = target
        
        # Buffer ID (by which OpenGl identifies the texture)
        # 0 means uninitialized, <0 means error.
        self._handle = 0
        
        # Keep track of buffer size
        self._buffer_size = 0
        
        # Set data?
        if data is not None:
            self.set_data(data)
    
    
    def _create(self):
        self._handle = gl.glGenBuffers(1)
    
    def _delete(self):
       gl.glDeleteBuffers([self._handle])
    
    
    def __del__(self):
        self.delete()
    
    
    def set_data(self, data, offset=None):
        """ Set the data for this buffer. This method can be called at any
        time (even if there is no context yet).
        
        If the size of the given data matches the current buffer size, 
        the data is updated in a fast manner.
        
        Parameters
        ----------
        data : numpy array
            The texture data to set.
        offset : int
            The offset, to update part of the texture. Optional.
        """
        
        # Check data
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")
        assert data.ndim == 2
        assert data.shape[1] in (1,2,3,4)
        if not data.dtype.name in self._TYPEMAP:
            data = data.astype(np.float32)
        
        # Reset if there was an error earlier
        if self._handle < 0:
            self._handle = 0
            self._buffer_size = 0
        
        # Check offset
        if offset is not None:
            assert (offset + data.nbytes) <= self._buffer_size
        elif data.nbytes == self._buffer_size:
            # If data is of same size, we can use glBufferSubData
            offset = 0
        
        # Set pending data
        self._pending_data = data, offset
        
        # Also store some properties of the data
        self._buffer_size = data.nbytes
        self._buffer_type = data.dtype.name
        self._buffer_shape = data.shape
    
    
    def _upload(self, data):
        # todo: allow user to control usage (DYNAMIC_DRAW, STATIC_DRAW)
        gl.glBufferData(self._target, data.nbytes, data, gl.GL_DYNAMIC_DRAW)
    
    
    def _update(self, data, offset):
        # Probably faster than upload
        gl.glBufferSubData(self._target, offset, data.nbytes, data)
    
    
    def _enable(self):
        
        # Error last time?
        if self._handle < 0:
            return
        
        # Need to update data?
        if self._pending_data:
            data, offset = self._pending_data
            self._pending_data = None
            if offset is not None:
                # Fast update
                gl.glBindBuffer(self._target, self._handle)
                self._update(data, offset)
            else:
                # Recreate buffer object, just in case
                self.delete()
                self._create()
                # Upload data
                gl.glBindBuffer(self._target, self._handle)
                self._upload(data)
        
        # Bind
        gl.glBindBuffer(self._target, self._handle)
    
    
    def _disable(self):
        gl.glBindBuffer(self._target, 0)



class VertexBuffer(BaseVertexBuffer):
    """ Representation of vertex buffer object of type GL_ARRAY_BUFFER,
    which can be used to store vertex data.
    """
    # When enabled,  pointer in gl.glVertexAttribPointer becomes an offset
    def __init__(self, data=None):
        BaseVertexBuffer.__init__(self, gl.GL_ARRAY_BUFFER, data)


class IndexBuffer(BaseVertexBuffer):
    """ Representation of vertex buffer object of type GL_ELEMENT_ARRAY_BUFFER,
    which can be used to store indices to vertex data.
    When enabled, the indices pointer in glDrawElements becomes a byte offset.
    """
    def __init__(self, data=None):
        BaseVertexBuffer.__init__(self, gl.GL_ELEMENT_ARRAY_BUFFER, data)

