# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import sys

import numpy as np

from . import gl
from . globject import GLObject
from ..util import logger


# ------------------------------------------------------------ Buffer class ---
class Buffer(GLObject):
    """ Generic GPU buffer.

    A generic buffer is an interface used to upload data to a GPU array buffer
    (gl.GL_ARRAY_BUFFER or gl.GL_ELEMENT_ARRAY_BUFFER). It keeps track of
    buffer size but does not have any CPU storage. You can consider it as
    write-only.

    The `set_data` is a deferred operation: you can call it even if an OpenGL
    context is not available. The `update` function is responsible to upload
    pending data to GPU memory and requires an active GL context.

    The Buffer class only deals with data in terms of bytes; it is not
    aware of data type or element size.

    Parameters
    ----------
    target : GLenum
        gl.GL_ARRAY_BUFFER or gl.GL_ELEMENT_ARRAY_BUFFER
    data : ndarray
        Buffer data
    nbytes : int
        Buffer byte size
    """

    def __init__(self, data=None, target=gl.GL_ARRAY_BUFFER, nbytes=None):

        GLObject.__init__(self)
        self._views = []
        self._valid = True

        # For ATI bug
        self._bufferSubDataOk = False

        # Store and check target
        if target not in (gl.GL_ARRAY_BUFFER, gl.GL_ELEMENT_ARRAY_BUFFER):
            raise ValueError("Invalid target for buffer object")
        self._target = target

        # Bytesize of buffer in GPU memory
        self._buffer_size = None
        # Bytesize of buffer in CPU memory
        self._nbytes = 0

        # Buffer usage (GL_STATIC_DRAW, G_STREAM_DRAW or GL_DYNAMIC_DRAW)
        self._usage = gl.GL_DYNAMIC_DRAW

        # Set data
        self._pending_data = []
        if data is not None:
            if nbytes is not None:
                raise ValueError("Cannot specify both data and nbytes.")
            self.set_data(data, copy=False)
        elif nbytes is not None:
            self._nbytes = nbytes
        
    @property
    def nbytes(self):
        """ Buffer byte size """

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
            self._pending_data = []
        self._pending_data.append((data, nbytes, offset))

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

        # We can discard any other pending operations here.
        self._pending_data = [(data, nbytes, 0)]

    def resize_bytes(self, size):
        """ Resize this buffer (deferred operation). 
        
        Parameters
        ----------
        size : int
            New buffer size in bytes.
        """
        self._nbytes = size
        self._pending_data = []
        # Invalidate any view on this buffer
        for view in self._views:
            view._valid = False
        self._views = []

    def _create(self):
        """ Create buffer on GPU """

        logger.debug("GPU: Creating buffer")
        self._handle = gl.glCreateBuffer()

    def _delete(self):
        """ Delete buffer from GPU """

        logger.debug("GPU: Deleting buffer")
        gl.glDeleteBuffer(self._handle)

    def _resize_bytes(self):
        """ """

        logger.debug("GPU: Resizing buffer(%d bytes)" % self._nbytes)
        gl.glBufferData(self._target, self._nbytes, self._usage)
        self._buffer_size = self._nbytes

    def _activate(self):
        """ Bind the buffer to some target """

        logger.debug("GPU: Activating buffer")
        gl.glBindBuffer(self._target, self._handle)
        
        # Resize if necessary
        if self._buffer_size != self._nbytes:
            self._resize_bytes()
        
        # Update pending data if necessary
        if self._pending_data:
            logger.debug("GPU: Updating buffer (%d pending operation(s))" %
                         len(self._pending_data))
            self._update_data()
    
    def _deactivate(self):
        """ Unbind the current bound buffer """

        logger.debug("GPU: Deactivating buffer")
        gl.glBindBuffer(self._target, 0)

    def _update_data(self):
        """ Upload all pending data to GPU. """

        # Update data
        while self._pending_data:
            data, nbytes, offset = self._pending_data.pop(0)

            # Determine whether to check errors to try handling the ATI bug
            check_ati_bug = ((not self._bufferSubDataOk) and
                             (gl.current_backend is gl.desktop) and
                             sys.platform.startswith('win'))

            # flush any pending errors
            if check_ati_bug:
                gl.check_error('periodic check')

            try:
                gl.glBufferSubData(self._target, offset, data)
                if check_ati_bug:
                    gl.check_error('glBufferSubData')
                self._bufferSubDataOk = True  # glBufferSubData seems to work
            except Exception:
                # This might be due to a driver error (seen on ATI), issue #64.
                # We try to detect this, and if we can use glBufferData instead
                if offset == 0 and nbytes == self._nbytes:
                    gl.glBufferData(self._target, data, self._usage)
                    logger.debug("Using glBufferData instead of " +
                                 "glBufferSubData (known ATI bug).")
                else:
                    raise


# -------------------------------------------------------- DataBuffer class ---
class DataBuffer(Buffer):
    """ GPU data buffer that is aware of data type and elements size

    Parameters
    ----------

    target : GLENUM
        gl.GL_ARRAY_BUFFER or gl.GL_ELEMENT_ARRAY_BUFFER
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
    store : bool
        Specify whether this object stores a reference to the data,
        allowing the data to be updated regardless of striding. Note
        that modifying the data after passing it here might result in
        undesired behavior, unless a copy is given. Default True.
    """

    def __init__(self, data=None, dtype=None, target=gl.GL_ARRAY_BUFFER,
                 size=0, store=True):
        self._data = None
        self._store = store
        self._copied = False  # flag to indicate that a copy is made
        self._size = size  # number of elements in buffer

        # Convert data to array+dtype if needed
        if data is not None:
            if dtype is not None:
                data = np.array(data, dtype=dtype, copy=False)
            else:
                data = np.array(data, copy=False)

        # Create buffer from dtype and size
        elif dtype is not None:
            self._dtype = np.dtype(dtype)
            self._size = size
            self._stride = self._dtype.itemsize
            self._itemsize = self._dtype.itemsize
            self._nbytes = self._size * self._itemsize
            if self._store:
                self._data = np.empty(self._size, dtype=self._dtype)
            # else:
            #    self.set_data(data,copy=True)

        # We need a minimum amount of information
        else:
            raise ValueError("data/dtype/base cannot be all set to None")
        
        Buffer.__init__(self, data=data, target=target)

    @property
    def target(self):
        """ OpenGL type of object. """

        return self._target

    def _prepare_data(self, data, **kwds):
        if len(kwds) > 0:
            raise ValueError("Unexpected keyword arguments: %r" %
                             list(kwds.keys()))
        # Subclasses override this
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
        
        # Handle storage
        if self._store:
            if not data.flags["C_CONTIGUOUS"]:
                logger.warning("Copying discontiguous data as CPU storage")
                self._copied = True
                data = data.copy()
            self._data = data.ravel()  # Makes a copy if not contiguous
        # Store meta data (AFTER flattening, or stride would be wrong)
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
    def data(self):
        """ Buffer CPU storage """

        return self._data

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
        
        if self._data is not None and self._store: 
            if self._data.size != self._size:
                self._data = np.resize(self._data, self._size)
        else:
            self._data = None

    def __getitem__(self, key):
        """ Create a view on this buffer. """

        view = DataBufferView(self, key)
        self._views.append(view)
        return view

    def __setitem__(self, key, data):
        """ Set data (deferred operation) """

        # Setting a whole field of the buffer: only allowed if we have CPU
        # storage. Note this case (key is str) only happen with base buffer
        if isinstance(key, str):
            if self._data is None:
                raise ValueError(
                    """Cannot set non contiguous """
                    """data on buffer without CPU storage""")

            # WARNING: do we check data size
            #          or do we let numpy raises an error ?
            self._data[key] = data
            self.set_data(self._data, copy=False)
            return

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

        # Buffer is a base buffer and we have CPU storage
        if self.data is not None:
            # WARNING: do we check data size
            #          or do we let numpy raises an error ?
            self.data[key] = data
            offset = start  # * self.itemsize
            self.set_subdata(data=self.data[start:stop],
                             offset=offset, copy=False)

        # Buffer is a base buffer but we do not have CPU storage
        # If 'key' points to a contiguous chunk of buffer, it's ok
        elif step == 1:
            offset = start  # * self.itemsize

            # Make sure data is an array
            if not isinstance(data, np.ndarray):
                data = np.array(data, dtype=self.dtype, copy=False)

            # Make sure data is big enough
            if data.size != stop - start:
                data = np.resize(data, stop - start)

            self.set_subdata(data=data, offset=offset, copy=True)

        # All the above fails, we raise an error
        else:
            raise ValueError(
                "Cannot set non contiguous data on buffer without CPU storage")


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
    
    It is gnerally not necessary to instantiate this class manually; use 
    ``base_buffer[key]`` instead.
    """

    def __init__(self, base, key):
        self._base = base
        self._key = key
        self._target = base.target
        self._stride = base.stride

        if isinstance(key, str):
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
    def handle(self):
        """ Name of this object on the GPU """

        return self._base.handle

    @property
    def target(self):
        """ OpenGL type of object. """

        return self._base.target

    def activate(self):
        """ Activate the object on GPU """

        self._base.activate()

    def deactivate(self):
        """ Deactivate the object on GPU """

        self._base.deactivate()

    def set_data(self, data, copy=False):
        raise ValueError("Cannot set_data on buffer view; only set_subdata is "
                         "allowed.")

    @property
    def dtype(self):
        """ Buffer dtype """

        return self._dtype

    @property
    def offset(self):
        """ Buffer offset (in bytes) relative to base """

        return self._offset

    @property
    def stride(self):
        """ Stride of data in memory """

        return self._stride

    @property
    def base(self):
        """Buffer base if this buffer is a view on another buffer. """

        return self._base

    @property
    def size(self):
        """ Number of elements in the buffer """
        return self._size

    @property
    def data(self):
        """ Buffer CPU storage """

        return self.base.data

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
        raise TypeError("Cannot resize buffer view.")

    def __getitem__(self, key):
        """ Create a view on this buffer. """

        raise ValueError("Can only access data from a base buffer")

    def __setitem__(self, key, data):
        """ Set data (deferred operation) """

        if not self._valid:
            raise ValueError("This buffer view has been invalidated")

        if isinstance(key, str):
            raise ValueError(
                "Cannot set a specific field on a non-base buffer")

        elif key == Ellipsis and self.base is not None:
            # WARNING: do we check data size
            #          or do we let numpy raises an error ?
            self.base[self._key] = data
            return
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
            start, stop = 0, self.size
        else:
            raise TypeError("Buffer indices must be integers or strings")

        # Set data on base buffer
        base = self.base
        # Base buffer has CPU storage
        if base.data is not None:
            # WARNING: do we check data size
            #          or do we let numpy raises an error ?
            base.data[key] = data
            offset = start * base.itemsize
            data = base.data[start:stop]
            base.set_subdata(data=data, offset=offset, copy=False)
        # Base buffer has no CPU storage, we cannot do operation
        else:
            raise ValueError(
                """Cannot set non contiguous data """
                """on buffer without CPU storage""")

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
    store : bool
        Specify whether this object stores a reference to the data,
        allowing the data to be updated regardless of striding. Note
        that modifying the data after passing it here might result in
        undesired behavior, unless a copy is given. Default True.
    """

    def __init__(self, data=None, dtype=None, size=0, store=True):

        if isinstance(data, (list, tuple)):
            data = np.array(data, np.float32)

        if dtype is not None:
            dtype = np.dtype(dtype)
            if dtype.isbuiltin:
                dtype = np.dtype([('f0', dtype, 1)])

        DataBuffer.__init__(self, data=data, dtype=dtype, size=size,
                            target=gl.GL_ARRAY_BUFFER,
                            store=store)

        # Check base type and count for each dtype fields (if buffer is a base)
        for name in self.dtype.names:
            btype = self.dtype[name].base
            if len(self.dtype[name].shape):
                count = 1
                s = self.dtype[name].shape
                for i in range(len(s)):
                    count *= s[i]
                #count = reduce(mul, self.dtype[name].shape)
            else:
                count = 1
            if btype not in [np.int8,  np.uint8,  np.float16,
                             np.int16, np.uint16, np.float32]:
                msg = ("Data basetype %r not allowed for Buffer/%s" 
                       % (btype, name))
                raise TypeError(msg)
            elif count not in [1, 2, 3, 4]:
                msg = ("Data basecount %s not allowed for Buffer/%s"
                       % (count, name))
                raise TypeError(msg)

    def _prepare_data(self, data, convert=False):
        # Build a structured view of the data if:
        #  -> it is not already a structured array
        #  -> shape if 1-D or last dimension is 1,2,3 or 4
        if data.dtype.isbuiltin:
            if convert is True and data.dtype is not np.float32:
                data = data.astype(np.float32)
            c = data.shape[-1]
            if data.ndim == 1 or (data.ndim == 2 and c == 1):
                data.shape = (data.size,)  # necessary in case (N,1) array
                data = data.view(dtype=[('f0', data.dtype.base, 1)])
            elif c in [1, 2, 3, 4]:
                if not data.flags['C_CONTIGUOUS']:
                    logger.warning("Copying discontiguous data for struct "
                                   "dtype")
                    data = data.copy()
                data = data.view(dtype=[('f0', data.dtype.base, c)])
            else:
                data = data.view(dtype=[('f0', data.dtype.base, 1)])
        return data


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
    store : bool
        Specify whether this object stores a reference to the data,
        allowing the data to be updated regardless of striding. Note
        that modifying the data after passing it here might result in
        undesired behavior, unless a copy is given. Default True.
    """

    def __init__(self, data=None, dtype=np.uint32, size=0, store=True):

        if dtype and not np.dtype(dtype).isbuiltin:
            raise TypeError("Element buffer dtype cannot be structured")

        if isinstance(data, np.ndarray):
            pass
        elif dtype not in [np.uint8, np.uint16, np.uint32]:
            raise TypeError("Data type not allowed for IndexBuffer")

        DataBuffer.__init__(self, data=data, dtype=dtype, size=size,
                            target=gl.GL_ELEMENT_ARRAY_BUFFER,
                            store=store)

    def _prepare_data(self, data, convert=False):
        if not data.dtype.isbuiltin:
            raise TypeError("Element buffer dtype cannot be structured")
        else:
            if convert is True and data.dtype is not np.uint32:
                data = data.astype(np.uint32)
        return data
