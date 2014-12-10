# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np
from os import path as op
from traceback import extract_stack, format_list

from . globject import GLObject
from ..util import logger
from ..ext.six import string_types


# ------------------------------------------------------------ Buffer class ---
class Buffer(GLObject):
    """ Generic GPU buffer.

    A generic buffer is an interface used to upload data to a GPU array buffer
    (ARRAY_BUFFER or ELEMENT_ARRAY_BUFFER). It keeps track of
    buffer size but does not have any CPU storage. You can consider it as
    write-only.

    The `set_data` is a deferred operation: you can call it even if an OpenGL
    context is not available. The `update` function is responsible to upload
    pending data to GPU memory and requires an active GL context.

    The Buffer class only deals with data in terms of bytes; it is not
    aware of data type or element size.

    Parameters
    ----------
    data : ndarray
        Buffer data
    nbytes : int
        Buffer byte size
    """
    
    def __init__(self, data=None, nbytes=None):
        GLObject.__init__(self)
        self._views = []  # Views on this buffer
        self._valid = True  # To invalidate buffer views
        self._nbytes = 0  # Bytesize in bytes, set in resize_bytes()
        
        # Set data
        if data is not None:
            if nbytes is not None:
                raise ValueError("Cannot specify both data and nbytes.")
            self.set_data(data, copy=False)
        elif nbytes is not None:
            self.resize_bytes(nbytes)
        
    @property
    def nbytes(self):
        """ Buffer size in bytes """

        return self._nbytes
    
    def set_subdata(self, data, offset=0, copy=False):
        """ Set a sub-region of the buffer (deferred operation).
        
        Parameters
        ----------

        data : ndarray
            Data to be uploaded
        offset: int
            Offset in buffer where to start copying data (in bytes)
        copy: bool
            Since the operation is deferred, data may change before
            data is actually uploaded to GPU memory.
            Asking explicitly for a copy will prevent this behavior.
        """
        data = np.array(data, copy=copy)
        nbytes = data.nbytes

        if offset < 0:
            raise ValueError("Offset must be positive")
        elif (offset + nbytes) > self._nbytes:
            raise ValueError("Data does not fit into buffer")

        # If the whole buffer is to be written, we clear any pending data
        # (because they will be overwritten anyway)
        if nbytes == self._nbytes and offset == 0:
            self._glir.command('SIZE', self._id, nbytes)
        self._glir.command('DATA', self._id, offset, data)
    
    def set_data(self, data, copy=False):
        """ Set data in the buffer (deferred operation).
        
        This completely resets the size and contents of the buffer.

        Parameters
        ----------

        data : ndarray
            Data to be uploaded
        copy: bool
            Since the operation is deferred, data may change before
            data is actually uploaded to GPU memory.
            Asking explicitly for a copy will prevent this behavior.
        """
        data = np.array(data, copy=copy)
        nbytes = data.nbytes

        if nbytes != self._nbytes:
            self.resize_bytes(nbytes)
        else:
            # Use SIZE to discard any previous data setting
            self._glir.command('SIZE', self._id, nbytes)
        
        if nbytes:  # Only set data if there *is* data
            self._glir.command('DATA', self._id, 0, data)
    
    def resize_bytes(self, size):
        """ Resize this buffer (deferred operation). 
        
        Parameters
        ----------
        size : int
            New buffer size in bytes.
        """
        self._nbytes = size
        self._glir.command('SIZE', self._id, size)
        # Invalidate any view on this buffer
        for view in self._views:
            view._valid = False
        self._views = []


# -------------------------------------------------------- DataBuffer class ---
class DataBuffer(Buffer):
    """ GPU data buffer that is aware of data type and elements size

    Parameters
    ----------

    data : ndarray
        Buffer data
    dtype : dtype
        Buffer data type
    size : int
        Number of elements in buffer
    base : DataBuffer
        Base buffer of this buffer
    offset : int
        Byte offset of this buffer relative to base buffer
    """

    def __init__(self, data=None):
        self._size = 0  # number of elements in buffer, set in resize_bytes()
        self._dtype = None
        self._stride = 0
        self._itemsize = 0
        Buffer.__init__(self, data)
    
    def _prepare_data(self, data):
        # Needs to be overrriden
        if not isinstance(data, np.ndarray):
            raise TypeError("DataBuffer data must be numpy array.")
        return data

    def set_subdata(self, data, offset=0, copy=False, **kwds):
        data = self._prepare_data(data, **kwds)
        offset = offset * self.itemsize
        Buffer.set_subdata(self, data=data, offset=offset, copy=copy)
    
    def set_data(self, data, copy=False, **kwds):
        """ Set data (deferred operation)

        Parameters
        ----------

        data : ndarray
            Data to be uploaded
        offset: int
            Offset in buffer to start copying data (in number of vertices)
        copy: bool
            Since the operation is deferred, data may change before
            data is actually uploaded to GPU memory.
            Asking explicitly for a copy will prevent this behavior.
        """
        data = self._prepare_data(data, **kwds)
        
        self._dtype = data.dtype
        self._stride = data.strides[-1]
        self._itemsize = self._dtype.itemsize
        Buffer.set_data(self, data=data, copy=copy)

    @property
    def dtype(self):
        """ Buffer dtype """

        return self._dtype

    @property
    def offset(self):
        """ Buffer offset (in bytes) relative to base """

        return 0

    @property
    def stride(self):
        """ Stride of data in memory """

        return self._stride

    @property
    def size(self):
        """ Number of elements in the buffer """
        return self._size

    @property
    def itemsize(self):
        """ The total number of bytes required to store the array data """

        return self._itemsize

    @property
    def glsl_type(self):
        """ GLSL declaration strings required for a variable to hold this data.
        """
        dtshape = self.dtype[0].shape
        n = dtshape[0] if dtshape else 1
        if n > 1:
            dtype = 'vec%d' % n
        else:
            dtype = 'float' if 'f' in self.dtype[0].base.kind else 'int'
        return 'attribute', dtype

    def resize_bytes(self, size):
        """ Resize the buffer (in-place, deferred operation)

        Parameters
        ----------
        size : integer
            New buffer size in bytes

        Notes
        -----
        This clears any pending operations.
        """
        Buffer.resize_bytes(self, size)
        self._size = size // self.itemsize

    def __getitem__(self, key):
        """ Create a view on this buffer. """

        view = DataBufferView(self, key)
        self._views.append(view)
        return view

    def __setitem__(self, key, data):
        """ Set data (deferred operation) """

        # Setting a whole field of the buffer: only allowed if we have CPU
        # storage. Note this case (key is string) only happen with base buffer
        if isinstance(key, string_types):
            raise ValueError("Cannot set non-contiguous data on buffer")
        
        # Setting one or several elements
        elif isinstance(key, int):
            if key < 0:
                key += self.size
            if key < 0 or key > self.size:
                raise IndexError("Buffer assignment index out of range")
            start, stop, step = key, key + 1, 1
        elif isinstance(key, slice):
            start, stop, step = key.indices(self.size)
            if stop < start:
                start, stop = stop, start
        elif key == Ellipsis:
            start, stop, step = 0, self.size, 1
        else:
            raise TypeError("Buffer indices must be integers or strings")

        # Contiguous update?
        if step != 1:
            raise ValueError("Cannot set non-contiguous data on buffer")

        # Make sure data is an array
        if not isinstance(data, np.ndarray):
            data = np.array(data, dtype=self.dtype, copy=False)

        # Make sure data is big enough
        if data.size < stop - start:
            data = np.resize(data, stop - start)
        elif data.size > stop - start:
            raise ValueError('Data too big to fit GPU data.')
        
        # Set data
        offset = start  # * self.itemsize
        self.set_subdata(data=data, offset=offset, copy=True)


class DataBufferView(DataBuffer):
    """ View on a sub-region of a DataBuffer.

    Parameters
    ----------
    base : DataBuffer
        The buffer accessed by this view.
    key : str, int, slice, or Ellpsis
        The index into the base buffer that defines a sub-region of the buffer
        to view. String arguments select a single field from multi-field 
        dtypes, and other allowed types select a subset of rows. 
        
    Notes
    -----
    
    It is generally not necessary to instantiate this class manually; use 
    ``base_buffer[key]`` instead.
    """
    
    # Note that this class is a bit evil: it is a subclass of GLObject,
    # Buffer and DataBuffer, but any of these __init__'s are not called ...
    
    def __init__(self, base, key):
        # Note how this never runs the super's __init__,
        # all attributes must thus be set here ...
        
        self._base = base
        self._key = key
        self._stride = base.stride

        if isinstance(key, string_types):
            self._dtype = base.dtype[key]
            self._offset = base.dtype.fields[key][1]
            self._nbytes = base.size * self._dtype.itemsize
            self._size = base.size
            self._itemsize = self._dtype.itemsize
            return
        
        if isinstance(key, int):
            if key < 0:
                key += base.size
            if key < 0 or key > base.size:
                raise IndexError("Buffer assignment index out of range")
            start, stop, step = key, key + 1, 1
        elif isinstance(key, slice):
            start, stop, step = key.indices(base.size)
            if stop < start:
                start, stop = stop, start
        elif key == Ellipsis:
            start, stop, step = 0, base.size, 1
        else:
            raise TypeError("Buffer indices must be integers or strings")

        if step != 1:
            raise ValueError("Cannot access non-contiguous data")

        self._itemsize = base.itemsize
        self._offset = start * self.itemsize
        self._size = stop - start
        self._dtype = base.dtype
        self._nbytes = self.size * self.itemsize
    
    @property
    def glir(self):
        return self._base.glir
    
    @property
    def id(self):
        return self._base.id
    
    def set_subdata(self, data, offset=0, copy=False, **kwds):
        raise RuntimeError("Cannot set data on buffer view.")
    
    def set_data(self, data, copy=False, **kwds):
        raise RuntimeError("Cannot set data on buffer view.")
    
    @property
    def offset(self):
        """ Buffer offset (in bytes) relative to base """

        return self._offset

    @property
    def base(self):
        """Buffer base if this buffer is a view on another buffer. """
        return self._base
    
    def resize_bytes(self, size):
        raise RuntimeError("Cannot resize buffer view.")

    def __getitem__(self, key):
        raise RuntimeError("Can only access data from a base buffer")

    def __setitem__(self, key, data):
        raise RuntimeError("Cannot set data on Buffer view")

    def __repr__(self):
        return ("<DataBufferView on %r at offset=%d size=%d>" % 
                (self.base, self.offset, self.size))

    
# ------------------------------------------------------ VertexBuffer class ---
class VertexBuffer(DataBuffer):
    """ Buffer for vertex attribute data

    Parameters
    ----------

    data : ndarray
        Buffer data (optional)
    dtype : dtype
        Buffer data type (optional)
    size : int
        Buffer size (optional)
    """
    
    _GLIR_TYPE = 'VertexBuffer'

    def _prepare_data(self, data, convert=False):
        # Build a structured view of the data if:
        #  -> it is not already a structured array
        #  -> shape if 1-D or last dimension is 1,2,3 or 4
        if isinstance(data, list):
            data = np.array(data, dtype=np.float32)
        if not isinstance(data, np.ndarray):
            raise ValueError('Data must be a ndarray (got %s)' % type(data))
        if data.dtype.isbuiltin:
            if convert is True and data.dtype is not np.float32:
                data = data.astype(np.float32)
            c = data.shape[-1]
            if data.ndim == 1 or (data.ndim == 2 and c == 1):
                data.shape = (data.size,)  # necessary in case (N,1) array
                data = data.view(dtype=[('f0', data.dtype.base, 1)])
            elif c in [1, 2, 3, 4]:
                if not data.flags['C_CONTIGUOUS']:
                    logger.warning('Copying discontiguous data for struct '
                                   'dtype:\n%s' % _last_stack_str())
                    data = data.copy()
                data = data.view(dtype=[('f0', data.dtype.base, c)])
            else:
                data = data.view(dtype=[('f0', data.dtype.base, 1)])
        return data


def _last_stack_str():
    """Print stack trace from call that didn't originate from here"""
    stack = extract_stack()
    for s in stack[::-1]:
        if op.join('vispy', 'gloo', 'buffer.py') not in __file__:
            break
    return format_list([s])[0]


# ------------------------------------------------------- IndexBuffer class ---
class IndexBuffer(DataBuffer):
    """ Buffer for index data

    Parameters
    ----------

    data : ndarray
        Buffer data (optional)
    dtype : dtype
        Buffer data type (optional)
    size : int
        Buffer size (optional)
    """
    
    _GLIR_TYPE = 'IndexBuffer'

    def _prepare_data(self, data, convert=False):
        if isinstance(data, list):
            data = np.array(data, dtype=np.uint32)
        if not isinstance(data, np.ndarray):
            raise ValueError('Data must be a ndarray (got %s)' % type(data))
        if not data.dtype.isbuiltin:
            raise TypeError("Element buffer dtype cannot be structured")
        else:
            if convert:
                if data.dtype is not np.uint32:
                    data = data.astype(np.uint32)
            else:
                if data.dtype not in [np.uint32, np.uint16, np.uint8]:
                    raise TypeError("Invalid dtype for IndexBuffer: %r" %
                                    data.dtype)
        return data
