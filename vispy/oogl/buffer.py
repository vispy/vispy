# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
""" Definition of Vertex Buffer Object class """

from __future__ import print_function, division, absolute_import

import sys
import numpy as np
from vispy import gl
from vispy.util.six import string_types
from . import GLObject
from . import ext_available


class BufferError(RuntimeError):
    """ Raised when something goes wrong that depens on state that was set 
    earlier (due to deferred loading).
    """
    pass


# ------------------------------------------------------------ Buffer class ---
class Buffer(GLObject):
    """The Buffer class is a raw interface to upload some data to the GPU.
    It is data agnostic and doesn't check any data type.

    Note that it is possible to only upload subdata to the GPU without ever
    uploading the full buffer. In such case, you have to first set the size of
    the buffer.
    """


    # ---------------------------------
    def __init__(self, target, data=None):
        """ Initialize buffer into default state. """

        GLObject.__init__(self)
        
        # Store and check target
        if target not in (gl.GL_ARRAY_BUFFER, gl.GL_ELEMENT_ARRAY_BUFFER):
            raise ValueError("Invalid target for buffer object.")
        self._target = target
        
        # Bytesize of buffer in GPU memory
        self._size = 0

        # Buffer usage (one of GL_STATIC_DRAW, G_STREAM_DRAW or GL_DYNAMIC_DRAW)
        self._usage = gl.GL_DYNAMIC_DRAW
        
        # Set data
        self._pending_data = []
        if data is not None:
            self.set_data(data)

    
    # ---------------------------------
    def _get_size(self):
        """ Get buffer bytesize """

        return self._size

    size = property(_get_size,
                    doc = "Buffer byte size")


    # ---------------------------------
    def set_size(self, size):
        """ Set buffer bytesize (invalidates all pending operations) """

        self._pending_data = []
        self._size = size
    

    # ---------------------------------
    def set_data(self, data, count=-1, offset=0):
        """ Set data or subdata (deferred operations)  """

        # Check some size has been allocated
        if self.size == 0:
            raise ValueError("Buffer size is null.")

        # Check data is a numpy array
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")

        # If count is not specified, we assume the whole data is to be uploaded
        if count == -1:
            count = data.nbytes

        # If the whole buffer is to be written, we clear any pending data
        # operations since this will be overwritten anyway.
        if count == data.nbytes:
            if offset == 0:
                self._pending_data = []
            else:
                raise ValueError("Data is too big for buffer.")

        # Check if we have enough space
        if (offset+count) > self.size:
            raise ValueError("Offseted data is too big for buffer.")

        # Ok, we should be safe now
        self._pending_data.append( (data, count, offset) )
        self._need_update = True

   
    def _create(self):
        """ Create buffer on GPU """
        self._handle = gl.glGenBuffers(1)
    
    
    def _delete(self):
        """ Delete buffer from GPU """
        gl.glDeleteBuffers(1 , [self._handle])
        
    
    def _activate(self):
        """ Bind the buffer to some target """
        gl.glBindBuffer(self._target, self._handle)
    
    
    def _deactivate(self):
        """ UnBind the buffer to some target """
        gl.glBindBuffer(self._target, 0)

    
    # ---------------------------------
    def _update(self):
        """ Upload all pending data to GPU. """
        
        # Has the buffer been already created ?
        if not self._valid:
            self._create()

        # Bind buffer now 
        gl.glBindBuffer(self._target, self._handle)

        # Check if size has been changed and allocate new size if necessary
        size = gl.glGetBufferParameteriv(self._target, gl.GL_BUFFER_SIZE)
        if size != self._size:
            # This will only allocate the buffer on GPU
            gl.glBufferData(self._target, self._size, None, self._usage)

        # Upload data
        while self._pending_data:
            data, count, offset = self._pending_data.pop(0)
            gl.glBufferSubData(self._target, offset, count, data)

        # Sanity measure    
        gl.glBindBuffer(self._target, 0)
    
   


# -----------------------------------------------------------------------------
class IndexableVertexBufferMixin(object):
    def __getitem__(self, index):
        
        if isinstance(index, string_types):
            # Try to get field info
            if not isinstance(self._type, dict):
                raise RuntimeError('Cannot index by name in this VertexBuffer.')
            try:
                fieldinfo = self._type[index]
            except KeyError:
                raise ValueError('Invalid field name for this VertexBuffer.')
            # Get view params
            new_offset = fieldinfo[2] + self._offset
            new_stride = self._stride
            # Type and shape
            new_type = fieldinfo[0]
            new_shape0 = self._shape[0]
            new_shape1 = fieldinfo[1]  # number of elements
        elif isinstance(index, slice):
            # Get defaults
            start = (index.start or 0)
            step = (index.step or 1)
            stop = index.stop or self._shape[0]
            assert start >= 0
            assert step >= 1
            assert stop > 0
            # Get view params
            new_offset = start*self._stride + self._offset
            new_stride = step*self._stride
            # Type and shape
            new_type = self._type
            new_shape0 = (stop-start) // step
            new_shape1 = self._shape[1]
        else:
            raise ValueError('Invalid parameter for getting a view on a VertexBuffer.')
        
        # Get buffer that new view will be based on: us, or our buffer
        if isinstance(self, VertexBufferView):
            buffer = self._buffer
        else:
            buffer = self
        
        # Create new VertexBufferView based on our own buffer
        return VertexBufferView(buffer, 
                (new_shape0, new_shape1), new_type, new_offset, new_stride)
    
    
    def __len__(self):
        return self.shape[0]
    


class ClientArray(object):
    """ Representation of attribute that that is stored on the client side,
    i.e. in CPU memory. Note that in general a VertexBufferis is
    recommended since it is more efficient. However, there may be corner
    cases when one wants to directly use a numpy array. 
    
    This class is a very thin wrapper on a numpy array and primarily 
    functions as signal mechanism.
    """
    
    def __init__(self, data):
        assert isinstance(data, np.ndarray)
        self._data = data
    
    @property
    def data(self):
        """ The underlying numpy array.
        """
        return self._data
    
    def __len__(self):
        return len(self._data)



class VertexBuffer(Buffer, IndexableVertexBufferMixin):
    """ Representation of vertex buffer object of type GL_ARRAY_BUFFER,
    which can be used to store vertex data. Inherits from Buffer.
    
    To use a VertexBuffer, set it as a member of
    a_shader_program.attributes.
    """
    # When enabled,  pointer in gl.glVertexAttribPointer becomes an offset
    
    # Data types that OpenGL ES 2.0 can understand
    DTYPES =  { 'uint8':gl.GL_UNSIGNED_BYTE,    'int8':gl.GL_BYTE,
                'uint16':gl.GL_UNSIGNED_SHORT,  'int16':gl.GL_SHORT, 
                'float32':gl.GL_FLOAT, 
                'float16': gl.ext.GL_HALF_FLOAT }
                # GL_FIXED?
    
    
    def __init__(self, data=None, buffer=None):
        Buffer.__init__(self, gl.GL_ARRAY_BUFFER)
        
        # View parameters, in bytes. 
        # Stride is set corresponding to element size in set_data/
        self._offset = 0
        self._stride = 0
        
        # Data parameters
        self._shape = None
        self._type = None
        
        # Set data?
        if data is not None:
            self.set_size(data.nbytes)
            self.set_data(data)
    
    
    # ---------------------------------
    def set_data(self, data, count=-1, offset=0):

        """ Set vertex attribute data, or a part of it. If the data
        matches the current size of the buffer, the data is updated
        faster.
        
        The data can be (and is recommended to be) a numpy array with
        dtype fields, one for each vertex attribute. In that way, the
        buffer represents an "array of structures" topology wich is
        good for performance. 
        
        VertexBufferView instances can be created that are associated 
        with the same undelying Buffer. This can be done by slicing 
        or by indexing using the appropriate field name. VertexBufferView
        instances can themselves be sliced/indexed as well.
        
        Parameters
        ----------
        data : numpy array
            The data to set. 
        offset : int
            The offset, to update part of the buffer. Optional.
        
        """
        
        # Check data
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")
        
        if data.dtype.fields:
            # Data with multiple fields
            fields = unravel_dtype_fields(data.dtype)
            for name, fieldinfo in fields.items():
                if fieldinfo[0] not in self.DTYPES:
                    raise TypeError("Field %s type %s not supported by VertexBuffer." % (name, fieldinfo[0]))
                if fieldinfo[1] not in (1,2,3,4):
                    raise TypeError("Field %s size=%d; not supported by VertexBuffer." % (name, fieldinfo[1]))
            # Set type and shape
            self._type = fields
            self._shape = data.size, 1
        
        else:
            # Plain data
            tuple_count = 1
            assert data.ndim in (1,2)
            if data.ndim == 2:
                assert data.shape[1] in (1,2,3,4)
                tuple_count = data.shape[1]
            # Convert if necessary
            if not data.dtype.name in self.DTYPES:
                data = data.astype(np.float32)  
            # Set type and shape
            self._type = data.dtype.name
            self._shape = data.shape[0], tuple_count
        
        # Check offset
        if self._offset:
            offset = (offset or 0) + self._offset
        
        # Set data in buffer
        self._stride = data.dtype.itemsize * self._shape[1]
        Buffer.set_data(self, data, offset=offset)
    
    
    
    @property
    def type(self):
        """ The name of the dtype of the data. If the data is a numpy array
        with fields, this yields a list of field specifiers.
        """
        return self._type
    
    
    @property
    def shape(self):
        """ The shape of the data that this VertexBuffer represents. This 
        is always a 2-element tuple (size, vector_size).
        """
        return self._shape
    


class VertexBufferView(IndexableVertexBufferMixin):
    """ A view on a VertexBuffer. This allows having multiple
    attributes on the same VBO. Each with their own offset,
    strides, type and shape.
    
    Do not use this class directly, but index a VertexBuffer to create one.
    """
    
    def __init__(self, buffer, shape, type, offset, stride):
        # Set buffer
        assert isinstance(buffer, VertexBuffer)
        self._buffer = buffer
        
        # Data parameters
        self._shape = shape
        self._type = type
        
        # View parameters, in bytes. 
        self._offset = offset
        self._stride = stride
    
    
    @property
    def buffer(self):
        """ The VertexBuffer that this object is a view of.
        """
        return self._buffer
    
    
    @property
    def type(self):
        """ The name of the dtype of the data. If the data is a numpy array
        with fields, this yields a list of field specifiers.
        """
        return self._type
    
    
    @property
    def shape(self):
        """ The shape of the data that this VertexBuffer represents. This 
        is always a 2-element tuple (size, vector_size).
        """
        return self._shape
    
    
    @property
    def view_params(self):
        """ A tuple with (offset, stride), specifying the slice in
        the Buffer object, in bytes.
        """
        return self._offset, self._stride



class ElementBuffer(Buffer):
    """ Representation of vertex buffer object of type GL_ELEMENT_ARRAY_BUFFER,
    which can be used to store indices to vertex data. Inherits from Buffer.
    
    To use an ElementBuffer, enable it before drawing.
    When enabled, the indices pointer in glDrawElements becomes a byte offset.
    """
    
    # Data types that OpenGL ES 2.0 can understand
    DTYPES =  { 'uint8': gl.GL_UNSIGNED_BYTE, 
                'uint16': gl.GL_UNSIGNED_SHORT,
                'uint32': gl.GL_UNSIGNED_INT, # Needs extension
            }
    
    
    def __init__(self, data=None):
        Buffer.__init__(self, gl.GL_ELEMENT_ARRAY_BUFFER)
        
        # Data parameters
        self._shape = None
        self._type = None
        
        # Set data?
        if data is not None:
            self.set_size(data.nbytes)
            self.set_data(data)
    
    
    # ---------------------------------
    def set_data(self, data, count=-1, offset=0):
        """ Set vertex element data, or a part of it. If the data
        matches the current size of the buffer, the data is updated
        faster.
        
        Parameters
        ----------
        data : numpy array
            The data to set. 
        offset : int
            The offset, to update part of the buffer. Optional.
        
        """
        
        # Check data
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")
        
        # Plain data
        tuple_count = 1
        assert data.ndim in (1,2)
        if data.ndim == 2:
            assert data.shape[1] in (1,2,3,4)
            tuple_count = data.shape[1]
        # Check type
        gltype = self.DTYPES.get(data.dtype.name, None)
        if gltype is None:
            raise ValueError('Unsupported data type for ElementBuffer.')
        elif gltype == gl.GL_UNSIGNED_INT and not ext_available('element_index_uint'):
            raise ValueError('element_index_uint extension needed for uint32 ElementBuffer.')
        
        # Set type and shape
        self._type = data.dtype.name
        self._shape = data.shape[0], tuple_count
        
        # Set data in buffer
        Buffer.set_data(self, data, offset=offset)
    
    
    @property
    def type(self):
        """ The name of the dtype of the data. If the data is a numpy array
        with fields, this yields a list of field specifiers.
        """
        return self._type
    
    
    @property
    def count(self):
        """ The number of indices that this ElementBuffer represents.
        """
        return self._shape[0] * self._shape[1]



def unravel_dtype_fields(dtype):
    """ Create a dictionary of names to tuples, one for each field in
    the given dtype: (dtypename, size, offset)
    """
    fields = {}
    for name in dtype.fields:
        type, offset = dtype.fields[name]
        if type.subdtype:
            thisdtype, shape = type.subdtype
        else:
            thisdtype, shape = type, (1,)
        assert len(shape) == 1
        fields[name] = thisdtype.name, shape[0], offset, 
    return fields
