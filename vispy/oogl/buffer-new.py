# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
""" Definition of Vertex Buffer class """

from __future__ import print_function, division, absolute_import

import sys
import numpy as np
from vispy import gl
from vispy.util.six import is_string
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

    # ---------------------------------
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


    # ---------------------------------
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
    
    
    # ---------------------------------
    def _set_bytesize(self, bytesize):
        """ Set buffer bytesize (invalidates all pending operations) """

        self._pending_data = []
        self._bytesize = bytesize


    # ---------------------------------    
    def _create(self):
        """ Create buffer on GPU """
        if not self._handle:
            handle = gl.glGenBuffers(1)
            self._handle = handle
            self._valid = True


    # ---------------------------------
    def _delete(self):
        """ Delete buffer from GPU """

        if self._handle:
            gl.glDeleteBuffers(1 , [self._handle])
            self._handle = 0
            self._valid = False
    
    
    # ---------------------------------
    def _activate(self):
        """ Bind the buffer to some target """

        gl.glBindBuffer(self._target, self._handle)
    

    # ---------------------------------
    def _deactivate(self):
        """ Unbind the current bound buffer """

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



# ------------------------------------------------------ VertexBuffer class ---
class VertexBuffer(Buffer):
    """
    """

    # ---------------------------------
    def __init__(self, data=None, dtype=None, count=0, base=None, offset=0):
        """ Initialize the buffer """

        Buffer.__init__(self, gl.GL_ARRAY_BUFFER, data)

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


    # ---------------------------------
    def __setitem__(self, key, data):
        """ """
        # todo: you probably want to cast the data to the same internal dtype

        # Is this buffer a view on another ?
        if self._base is not None:
            raise ValueError("Can set data on buffer views.")
        
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

        self.set_data(data, offset=offset)


    # ---------------------------------
    def __getitem__(self, key):
        """ """

        if not is_string(key):
            raise ValueError("Can only get access to a named field")

        dtype = self._dtype[key]
        offset = self._dtype.fields[key][1]
        return VertexBuffer(dtype=dtype, base=self, offset=offset)


    # ---------------------------------
    def _get_gtype(self):
        """
        """

        bsize = np.prod(self._dtype.shape)
        btype = self._dtype.base

        if btype.fields:
            raise TypeError("Incompatible buffer (structured buffer)")

        if bsize > 4:
            raise TypeError("Incompatible buffer (too many components)")

        gltypes =  { 'np.uint8'   : gl.GL_UNSIGNED_BYTE,
                     'np.int8'    : gl.GL_BYTE,
                     'np.uint16'  : gl.GL_UNSIGNED_SHORT,
                     'np.int16'   : gl.GL_SHORT, 
                     'np.float32' : gl.GL_FLOAT, 
                     'np.float16' : gl.ext.GL_HALF_FLOAT }
        
        if not str(btype) not in gltypes.keys():
            raise TypeError("Incompatible type")

        return btype, bsize



# -----------------------------------------------------------------------------
if __name__ == '__main__':
    
    dtype = np.dtype( [ ('position', np.float32, 3),
                        ('texcoord', np.float32, 2),
                        ('color',    np.float32, 4) ] )
    Z = np.zeros(100, dtype=dtype)

    V = VertexBuffer(Z)
    V_position = V['position']
    V_texcoord = V['texcoord']
    V_color    = V['color']

    for P in (V_position, V_texcoord, V_color):
        print("Offset:",   P._offset)
        print("Itemsize:", P._itemsize)
        print("Itemcount", P._itemcount)
        print("Data type", P._dtype)
        print("Data gtype", P._get_gtype())
        print()

    V[...] = Z
    V[10:20] = Z[10:20]
    V[10:20] = Z[10:19]
    V[10:20] = Z[10:21]
