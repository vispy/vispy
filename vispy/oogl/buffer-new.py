# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
""" Definition of Vertex Buffer class """

from __future__ import print_function, division, absolute_import

import sys
import numpy as np
from vispy import gl
from vispy.util import is_string
from vispy.oogl import GLObject
from vispy.oogl import ext_available



# ------------------------------------------------------------ Buffer class ---
class Buffer(GLObject):
    """The Buffer class is a raw interface to upload some data to the GPU.
    It is data agnostic and doesn't check any data type.

    Note that it is possible to only upload subdata to the GPU without ever
    uploading the full buffer. In such case, you have to first set the size of
    the buffer. Once the size is set, checks will be made as to not override the
    end of the buffer. If you need more space, set a new size first.
    """


    def __init__(self, target, data=None):
        """ Initialize buffer into default state. """

        GLObject.__init__(self)
        
        # Store and check target
        if target not in (gl.GL_ARRAY_BUFFER, gl.GL_ELEMENT_ARRAY_BUFFER):
            raise ValueError("Invalid target for buffer object.")
        self._target = target
        
        # Bytesize of buffer in GPU memory
        self._bytesize = 0

        # Buffer usage (GL_STATIC_DRAW, G_STREAM_DRAW or GL_DYNAMIC_DRAW)
        self._usage = gl.GL_DYNAMIC_DRAW
        
        # Set data
        self._pending_data = []
        if data is not None:
            if not isinstance(data, np.ndarray):
                raise ValueError("Data should be a numpy array.")
            self._set_bytesize(data.nbytes)
            self.set_data(data)



    def set_data(self, data, offset=0):
        """ Set data or subdata (deferred operations)  """

        # Check some size has been allocated
        if self._bytesize == 0:
            raise ValueError("Buffer size is null.")

        # Check data is a numpy array
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")


        count = data.nbytes

        # If the whole buffer is to be written, we clear any pending data
        # operations since this will be overwritten anyway.
        if count == self._bytesize:
            if offset == 0:
                self._pending_data = []
            else:
                raise ValueError("Data is too big for buffer.")

        # Check if we have enough space
        if (offset+count) > self._bytesize:
            raise ValueError("Offseted data is too big for buffer.")

        # Ok, we should be safe now
        self._pending_data.append( (data, count, offset) )
        self._need_update = True
    
    

    def _set_bytesize(self, bytesize):
        """ Set buffer bytesize (invalidates all pending operations) """

        self._pending_data = []
        self._bytesize = bytesize



    def _create(self):
        """ Create buffer on GPU """
        if not self._handle:
            handle = gl.glGenBuffers(1)
            self._handle = handle
            self._valid = True



    def _delete(self):
        """ Delete buffer from GPU """

        if self._handle:
            gl.glDeleteBuffers(1 , [self._handle])
            self._handle = 0
            self._valid = False
    
    

    def _activate(self):
        """ Bind the buffer to some target """

        gl.glBindBuffer(self._target, self._handle)
    


    def _deactivate(self):
        """ Unbind the current bound buffer """

        gl.glBindBuffer(self._target, 0)

    

    def _update(self):
        """ Upload all pending data to GPU. """
        
        # Has the buffer been already created ?
        if not self._valid:
            self._create()

        # Bind buffer now 
        gl.glBindBuffer(self._target, self._handle)

        # Check if size has been changed and allocate new size if necessary
        bytesize = gl.glGetBufferParameteriv(self._target, gl.GL_BUFFER_SIZE)
        if bytesize != self._bytesize:
            # This will only allocate the buffer on GPU
            gl.glBufferData(self._target, self._bytesize, None, self._usage)

        # Upload data
        while self._pending_data:
            data, count, offset = self._pending_data.pop(0)
            gl.glBufferSubData(self._target, offset, count, data)

        # Sanity measure    
        gl.glBindBuffer(self._target, 0)





# ------------------------------------------------------ DataBuffer class ---
class DataBuffer(Buffer):
    """Data buffer allows to manipulate typed data.  """


    def __init__(self, data=None, dtype=None, count=0, base=None, offset=0, target=0):
        """ Initialize the buffer """

        Buffer.__init__(self, target, data)

        # Check if this buffer is a sub-buffer of another buffer
        if base is not None:
            self._dtype     = dtype
            self._itemsize  = base._itemsize
            self._itemcount = base._itemcount
            self._bytesize  = base._bytesize
            self._offset    = offset

        # Check if dtype is a numpy dtype (after conversion by numpy)
        elif dtype is not None:
            dtype = np.dtype(dtype)
            if isinstance(dtype,np.dtype):
                if count == 0:
                    raise ValueError("Count error (cannot be 0).")
                self._dtype     = dtype
                self._itemsize  = self._dtype.itemsize
                self._itemcount = count
                self._bytesize  = self._itemsize * self._itemcount
                self._offset    = 0
            else:
                raise ValueError("Unknown data type.")

        # Check if data is a numpy array
        elif isinstance(data,np.ndarray):
            self._dtype     = data.dtype
            self._bytesize  = data.nbytes
            self._itemsize  = self._dtype.itemsize
            self._itemcount = data.size
            self._offset    = 0

        # We need at least one (data) or the others (dtype+size)
        else:
            raise ValueError("One of 'data' or 'dtype' must be specified.")

        # Pointer to the base buffer (if any)
        self._base = base


    @property
    def dtype(self):
        """Buffer data type. """
        return self._dtype


    @property
    def itemcount(self):
        """Buffer element count. """
        return self._itemcount


    @property
    def itemsize(self):
        """Buffer element size (in bytes). """
        return self._itemsize


    @property
    def bytesize(self):
        """Buffer size (in bytes) """
        return self._bytesize


    @property
    def offset(self):
        """Buffer offset (in bytes) relative to base. """
        return self._offset


    @property
    def base(self):
        """Buffer base if this buffer is a view on another buffer. """
        return self._dtype


    def __setitem__(self, key, data):
        """Set data (deferred operation) """

        # Is this buffer a view on another ?
        if self._base is not None:
            raise ValueError("Cannot set data on buffer views.")
        
        # Deal with slices that have None or negatives in them
        if isinstance(key, slice):
            start = key.start or 0
            if start < 0:
                start = self._itemsize + start
            step = key.step or 1
            assert step > 0
            stop = key.stop or self._itemsize
            if stop < 0:
                stop = self._itemsize + stop
        
        # Check ellipsis (... notation)
        if key == Ellipsis:
            offset = 0
            count  = data.nbytes
        # If key is not a slice
        elif not isinstance(key, slice) or step > 1:
            raise ValueError("Can only set contiguous block of data.")
        # Else we're happy
        else:
            offset = start * self._itemsize
            count  = (stop - start) * self._itemsize

        # Check we have the right amount of data
        if data.nbytes < count:
            raise ValueError("Not enough data.")
        elif data.nbytes > count:
            raise ValueError("Too much data.")

        # Do we check data type here or do we cast the data to the same
        # internal dtype ? This would make a silent copy of the data which can
        # be problematic in some cases
        self.set_data(data, offset=offset)


    def __getitem__(self, key):
        """ Create a view on this buffer. """

        if not is_string(key):
            raise ValueError("Can only get access to a named field")

        dtype = self._dtype[key]
        offset = self._dtype.fields[key][1]
        return self.__class__(dtype=dtype, base=self, offset=offset)


    def _get_gtype(self):
        """ Get equivalent elementary data type. """

        bsize = np.prod(self._dtype.shape)
        btype = self._dtype.base
        return btype, bsize




# ------------------------------------------------------ VertexBuffer class ---
class VertexBuffer(DataBuffer):
    """Vertex buffer allows to group set of vertices such they can be later used
    in a shader program.

    Example
    -------

    dtype = np.dtype( [ ('position', np.float32, 3),
                        ('texcoord', np.float32, 2),
                        ('color',    np.float32, 4) ] )
    data = np.zeros(100, dtype=dtype)

    buffer = VertexBuffer(data)
    program = Program(...)

    program['position'] = buffer['position']
    program['texcoord'] = buffer['texcoord']
    program['color'] = buffer['color']
    ...
    """


    def __init__(self, data=None, dtype=None, count=0, base=None, offset=0):
        """ Initialize the buffer """

        DataBuffer.__init__(self, data=data, dtype=dtype, count=count,
                            base=base, offset = offset, target = gl.GL_ARRAY_BUFFER)



# ------------------------------------------------------ ElementBuffer class ---
class ElementBuffer(DataBuffer):
    """ElementBuffer allows to specify which element of a VertexBuffer are to be
    used in a shader program.

    Example
    -------

    indices = np.zeros(100, dtype=np.uint16)
    buffer = ElementBuffer(indices)
    program = Program(...)

    program.draw(gl.GL_TRIANGLES, indices)
    ...
    """
    
    def __init__(self, data=None, dtype=None, count=0):
        """ Initialize the buffer """

        DataBuffer.__init__(self, data=data, dtype=dtype, count=count,
                            target = gl.GL_ELEMENT_ARRAY_BUFFER)
        
        btype,bsize = self._get_gtype()

        # Check data type
        if str(btype) not in ('uint8', 'uint16', 'uint32'):
            raise TypeError("An element buffer data type should be one of " +
                            "uint8, uint16 or uint32. ")
        # Check data shape
        if bsize > 1:
            raise TypeError("An element buffer data should be contiguous.")



# ------------------------------------------------------ ImmediateBuffer class ---
class ClientBuffer(DataBuffer):
    """
    A client buffer is a buffer that only exists (permanently) on the CPU. It
    cannot be modified nor uploaded into a GPU buffer.
    
    It merely serves as rapidly passing data during a drawing operations.

    Note this kind of buffer is highly inefficient since data is uploaded at
    each drawing operations.
    """

    def __init__(self, data):
        """ Initialize the buffer. """

        self._value       = True
        self._need_update = True
        self._data        = data

        self._dtype     = data.dtype
        self._itemsize  = data.dtype.itemsize
        self._itemcount = data.size
        self._bytesize  = data.size * data.dtype.itemsize
        self._offset    = 0

    def _set_bytesize(self, bytesize):
        raise TypeError("Operation no allowed this type of buffer")

    def __getitem__(self, key):
        raise TypeError("Operation no allowed this type of buffer")

    def __setitem__(self, key, data):
        raise TypeError("Operation no allowed this type of buffer")

    def _create(self):
        raise TypeError("Operation no allowed this type of buffer")

    def _delete(self):
        raise TypeError("Operation no allowed this type of buffer")

    def _activate(self):
        raise TypeError("Operation no allowed this type of buffer")

    def _deactivate(self):
        raise TypeError("Operation no allowed this type of buffer")

    def _update(self):
        raise TypeError("Operation no allowed this type of buffer")


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    
    dtype = np.dtype( [ ('position', np.float32, 3),
                        ('texcoord', np.float32, 2),
                        ('color',    np.float32, 4) ] )
    data = np.zeros(100, dtype=dtype)
    indices = np.zeros(100, dtype=np.uint8)

    V = VertexBuffer(data)
    V_position = V['position']
    V_texcoord = V['texcoord']
    V_color    = V['color']

    I = ElementBuffer(indices)

    for P in (V_position, V_texcoord, V_color):
        print("Offset:",   P.offset)
        print("Itemsize:", P.itemsize)
        print("Itemcount", P.itemcount)
        print("Data type", P.dtype)
        print("Data gtype", P._get_gtype())
        print()

    V[...] = data
    V[10:20] = data[10:20]
    V[10:20] = data[10:19]
    V[10:20] = data[10:21]
