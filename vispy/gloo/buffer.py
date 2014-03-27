# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import numpy as np

from . import gl
from . globject import GLObject
from ..util import logger


# ------------------------------------------------------------ Buffer class ---
class Buffer(GLObject):
    """
    Generic GPU buffer.

    A generic buffer is an interface used to upload data to a GPU array buffer
    (GL_ARRAY_BUFFER or gl.GL_ELEMENT_ARRAY_BUFFER). It keeps tracks of buffer
    size but do not have any CPU storage. You can consider it as write-only.

    The `set_data` is a deferred operation: you can call it even if an OpenGL
    context is not available. The `update` function is responsible to upload
    pending data to GPU memory and requires an active GL context.
    """

    def __init__(self, data=None, target=gl.GL_ARRAY_BUFFER, nbytes=0,
                 resizeable=True):
        """ Initialize buffer

        Parameters
        ----------

        target : GLenum
            gl.GL_ARRAY_BUFFER or gl.GL_ELEMENT_ARRAY_BUFFER

        data : ndarray
            Buffer data

        nbytes : int
            Buffer byte size

        resizeable : boolean
            Indicates whether buffer is resizeable
        """

        GLObject.__init__(self)
        self._need_resize = True
        self._resizeable = resizeable
        self._views = []
        self._valid = True

        # Store and check target
        if target not in (gl.GL_ARRAY_BUFFER, gl.GL_ELEMENT_ARRAY_BUFFER):
            raise ValueError("Invalid target for buffer object")
        self._target = target

        # Bytesize of buffer in GPU memory
        self._nbytes = nbytes

        # Buffer usage (GL_STATIC_DRAW, G_STREAM_DRAW or GL_DYNAMIC_DRAW)
        self._usage = gl.GL_DYNAMIC_DRAW

        # Set data
        self._pending_data = []
        if data is not None:
            data = np.array(data, copy=True)
            self._nbytes = data.nbytes
            self.set_data(data, copy=True)

    @property
    def nbytes(self):
        """ Buffer byte size """

        return self._nbytes

    def set_data(self, data, offset=0, copy=False):
        """ Set data (deferred operation)

        Parameters
        ----------

        data : np.array
            Data to be uploaded

        offset: int
            Offset in buffer where to start copying data

        copy: boolean
            Since the operation is deferred, data may change before
            data is actually uploaded to GPU memory.
            Asking explicitly for a copy will prevent this behavior.
        """

        if not data.flags["C_CONTIGUOUS"]:
            data = np.array(data, copy=True)
        else:
            data = np.array(data, copy=copy)
        nbytes = data.nbytes

        if offset < 0:
            raise ValueError("Offset must be positive")
        elif offset == 0 and nbytes > self._nbytes:
            if not self._resizeable:
                raise ValueError("Data does not fit into buffer")
            else:
                self._nbytes = nbytes
                self._need_resize = True
                # Invalidate any view on this buffer
                for view in self._views:
                    view._valid = False
                self._views = []

        elif (offset + nbytes) > self._nbytes:
            raise ValueError("Data does not fit into buffer")

        # If the whole buffer is to be written, we clear any pending data
        # (because they will be overwritten anyway)
        if nbytes == self._nbytes and offset == 0:
            self._pending_data = []
        self._pending_data.append((data, nbytes, offset))
        self._need_update = True

    def _create(self):
        """ Create buffer on GPU """

        logger.debug("GPU: Creating buffer")
        self._handle = gl.glCreateBuffer()

    def _delete(self):
        """ Delete buffer from GPU """

        logger.debug("GPU: Deleting buffer")
        gl.glDeleteBuffer(self._handle)

    def _resize(self):
        """ """

        logger.debug("GPU: Resizing buffer(%d bytes)" % self._nbytes)
        gl.glBufferData(self._target, self._nbytes, self._usage)
        self._need_resize = False

    def _activate(self):
        """ Bind the buffer to some target """

        logger.debug("GPU: Activating buffer")
        gl.glBindBuffer(self._target, self._handle)

    def _deactivate(self):
        """ Unbind the current bound buffer """

        logger.debug("GPU: Deactivating buffer")
        gl.glBindBuffer(self._target, 0)

    def _update(self):
        """ Upload all pending data to GPU. """

        if self.base is not None:
            return

        if self._need_resize:
            self._resize()
            self._need_resize = False

        logger.debug("GPU: Updating buffer (%d pending operation(s))" %
                     len(self._pending_data))
        while self._pending_data:
            data, nbytes, offset = self._pending_data.pop(0)
            
            # flush any pending errors
            if gl.current_backend is gl.desktop:
                gl.check_error('periodic check')
            
            try:
                gl.glBufferSubData(self._target, offset, data)
                if gl.current_backend is gl.desktop:
                    gl.check_error('glBufferSubData')
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
    """ GPU data buffer """

    def __init__(self, data=None, dtype=None, target=gl.GL_ARRAY_BUFFER,
                 size=0, base=None, offset=0, store=True, copy=False,
                 resizeable=True):
        """
        Initialize the buffer

        Parameters
        ----------

        target : GLENUM
            gl.GL_ARRAY_BUFFER or gl.GL_ELEMENT_ARRAY_BUFFER

        data : ndarray
            Buffer data (optional)

        dtype : np.dtype
           Buffer data type (optional)

        size : int
           Buffer element size

        base : DataBuffer
           Base buffer of this buffer

        offset : int
           Byte offset of this buffer relative to base buffer

        store : boolean
           Indicate whether to use a intermediate CPU storage

        copy : boolean
           Indicate whether to use given data as CPU storage

        resizeable : boolean
            Indicates whether buffer is resizeable
        """

        Buffer.__init__(self, target=target, resizeable=resizeable)
        self._base = base
        self._offset = offset
        self._data = None
        self._store = store
        self._copy = copy
        self._size = size

        # This buffer is a view on another
        if base is not None:
            self._dtype = base.dtype
            if dtype is not None:
                self._dtype = dtype
            self._stride = base.stride
            #self._size = size or base.size

        # Create buffer from data
        elif data is not None:
            if dtype is not None:
                data = np.array(data, dtype=dtype, copy=False)
            else:
                data = np.array(data, copy=False)
            self._dtype = data.dtype
            self._size = data.size
            self._stride = data.strides[-1]
            self._nbytes = data.nbytes
            if self._store:
                if not data.flags["C_CONTIGUOUS"]:
                    if self._copy is False:
                        logger.warning(
                            "Cannot use non contiguous data as CPU storage")
                    self._copy = True
                self._data = np.array(data, copy=self._copy).ravel()
                self.set_data(self._data, copy=False)
            else:
                self.set_data(data, copy=True)

        # Create buffer from dtype and size
        elif dtype is not None:
            self._dtype = np.dtype(dtype)
            self._size = size
            self._stride = self._dtype.itemsize
            if self._store:
                self._data = np.empty(self._size, dtype=self._dtype)
            # else:
            #    self.set_data(data,copy=True)

        # We need a minimum amount of information
        else:
            raise ValueError("data/dtype/base cannot be all set to None")

        self._itemsize = self._dtype.itemsize
        self._nbytes = self._size * self._itemsize

    @property
    def handle(self):
        """ Name of this object on the GPU """

        if self._base:
            return self._base.handle
        else:
            return self._handle

    @property
    def target(self):
        """ OpenGL type of object. """

        if self._base:
            return self._base.target
        else:
            return self._target

    def activate(self):
        """ Activate the object on GPU """

        if self._base is not None:
            self._base.activate()
        else:
            GLObject.activate(self)

    def deactivate(self):
        """ Deactivate the object on GPU """

        if self._base is not None:
            self._base.deactivate()
        else:
            GLObject.deactivate(self)

    def update(self):
        """ Update the object in GPU """

        if self._base is not None:
            self._base.update()
        else:
            GLObject.update(self)

    def set_data(self, data, offset=0, copy=False):
        """ Set data (deferred operation)

        Parameters
        ----------

        data : np.array
            Data to be uploaded

        offset: int
            Offset in buffer where to start copying data

        copy: boolean
            Since the operation is deferred, data may change before
            data is actually uploaded to GPU memory.
            Asking explicitly for a copy will prevent this behavior.
        """
        if self.base is not None:
            raise ValueError("Cannot set data on a non-base buffer")
        else:
            Buffer.set_data(self, data=data, offset=offset, copy=copy)

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

        return self._data

    @property
    def itemsize(self):
        """ The total number of bytes required to store the array data """

        return self._itemsize

    def resize(self, size):
        """ Resize the buffer (in-place, deferred operation)

        Parameters
        ----------

        size : integer
            New buffer size

        Note
        ----

        This clears any pending operations.
        """

        if not self._resizeable:
            raise RuntimeError("Buffer is not resizeable")

        if self._base is not None:
            raise RuntimeError("Buffer view is not resizeable")

        if size == self.size:
            return

        # Invalidate any view on this texture
        for view in self._views:
            view._valid = False
        self._views = []

        self._pending_data = []
        self._need_update = False
        self._need_resize = True
        self._size = size
        if self._data is not None and self._store:
            self._data = np.resize(self._data, self._size)
        else:
            self._data = None

    def __getitem__(self, key):
        """ Create a view on this buffer. """

        if self.base is not None:
            raise ValueError("Can only access data from a base buffer")

        if isinstance(key, str):
            dtype = self.dtype[key]
            offset = self.dtype.fields[key][1]
            target = self.target
            base = self
            V = self.__class__(target=target, dtype=dtype, base=base,
                               size=self.size, offset=offset)
            V._nbytes = self.size * dtype.itemsize
            V._itemsize = dtype.itemsize
            V._key = key
            self._views.append(V)
            return V

        if isinstance(key, int):
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

        if step != 1:
            raise ValueError("Cannot access non-contiguous data")

        if self.data is not None:
            data = self.data[key]
            V = self.__class__(target=self.target, base=self,
                               data=data, size=stop - start,
                               offset=start * self.itemsize, resizeable=False)
        else:
            V = self.__class__(target=self.target, base=self,
                               dtype=self.dtype, size=stop - start,
                               offset=start * self.itemsize, resizeable=False)
        V._key = key
        self._views.append(V)
        return V

    def __setitem__(self, key, data):
        """ Set data (deferred operation) """

        if self.base is not None and not self._valid:
            raise ValueError("This texture view has been invalited")

        # Setting a whole field of the buffer: only allowed if we have CPU
        # storage. Note this case (key is str) only happen with base buffer
        if isinstance(key, str):
            if self.base is not None:
                raise ValueError(
                    "Cannot set a specific field on a non-base buffer")
            if self._data is None:
                raise ValueError(
                    """Cannot set non contiguous """
                    """data on buffer without CPU storage""")

            # WARNING: do we check data size
            #          or do we let numpy raises an error ?
            self._data[key] = data
            self.set_data(self._data, offset=0, copy=False)
            return

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
            start, stop, step = 0, self.size, 1
        else:
            raise TypeError("Buffer indices must be integers or strings")

        # Buffer is a view on a base buffer
        if self.base is not None:
            base = self.base
            # Base buffer has CPU storage
            if base.data is not None:
                # WARNING: do we check data size
                #          or do we let numpy raises an error ?
                base.data[key] = data
                offset = start * base.itemsize
                data = base.data[start:stop]
                base.set_data(data=data, offset=offset, copy=False)
            # Base buffer has no CPU storage, we cannot do operation
            else:
                raise ValueError(
                    """Cannot set non contiguous data """
                    """on buffer without CPU storage""")

        # Buffer is a base buffer and we have CPU storage
        elif self.data is not None:
            # WARNING: do we check data size
            #          or do we let numpy raises an error ?
            self.data[key] = data
            offset = start * self.itemsize
            self.set_data(data=self.data[start:stop],
                          offset=offset, copy=False)

        # Buffer is a base buffer but we do not have CPU storage
        # If 'key' points to a contiguous chunk of buffer, it's ok
        elif step == 1:
            offset = start * self.itemsize

            # Make sure data is an array
            if not isinstance(data, np.ndarray):
                data = np.array(data, dtype=self.dtype, copy=False)

            # Make sure data is big enough
            if data.size != stop - start:
                data = np.resize(data, stop - start)

            self.set_data(data=data, offset=offset, copy=True)

        # All the above fails, we raise an error
        else:
            raise ValueError(
                "Cannot set non contiguous data on buffer without CPU storage")


# ------------------------------------------------------ VertexBuffer class ---
class VertexBuffer(DataBuffer):
    """
    VertexBuffer represents vertex data that can be uploaded to GPU memory.
    """

    def __init__(self, data=None, dtype=None, size=0, store=True,
                 copy=False, resizeable=True, *args, **kwargs):
        """
        Initialize the buffer

        Parameters
        ----------

        data : ndarray
            Buffer data (optional)

        dtype : np.dtype
           Buffer data type (optional)

        size : int
           Buffer size (optional)

        store : boolean
           Indicate whether to use an intermediate CPU storage

        copy : boolean
           Indicate whether to use given data as CPU storage

        resizeable : boolean
            Indicates whether buffer is resizeable
        """

        # We don't want these two parameters to be seen from outside
        # (because they are used internally only)
        offset = kwargs.get("offset", 0)
        base = kwargs.get("base", None)

        # Build a structured view of the data if:
        #  -> it is not already a structured array
        #  -> it is not a view of another buffer
        #  -> shape if 1-D or last dimension is 1,2,3 or 4
        if data is not None and base is None and data.dtype.isbuiltin:
            if len(data.shape) == 1:
                data = data.view(dtype=[('f0', data.dtype.base, 1)])
            elif data.shape[-1] in [1, 2, 3, 4]:
                c = data.shape[-1]
                data = data.view(dtype=[('f0', data.dtype.base, c)])
            else:
                data = data.view(dtype=[('f0', data.dtype.base, 1)])

        elif dtype is not None:
            dtype = np.dtype(dtype)
            if dtype.isbuiltin:
                dtype = np.dtype([('f0', dtype, 1)])

        DataBuffer.__init__(self, data=data, dtype=dtype, size=size, base=base,
                            offset=offset, target=gl.GL_ARRAY_BUFFER,
                            store=store, copy=copy, resizeable=resizeable)

        # Check base type and count for each dtype fields (if buffer is a base)
        if base is None:
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
                    msg = "Data basetype not allowed for Buffer/%s" % name
                    raise TypeError(msg)
                elif count not in [1, 2, 3, 4]:
                    msg = "Data basecount not allowed for Buffer/%s" % name
                    raise TypeError(msg)


# ------------------------------------------------------- IndexBuffer class ---
class IndexBuffer(DataBuffer):
    """
    IndexBuffer represents indices data that can be uploaded to GPU memory.
    """

    def __init__(self, data=None, dtype=np.uint32, size=0, store=True,
                 copy=False, resizeable=True, *args, **kwargs):
        """
        Initialize the buffer

        Parameters
        ----------

        data : ndarray
            Buffer data (optional)

        dtype : np.dtype
           Buffer data type (optional)

        size : int
           Buffer size (optional)

        store : boolean
           Indicate whether to use a intermediate CPU storage

        copy : boolean
           Indicate whether to use given data as CPU storage

        resizeable : boolean
            Indicates whether buffer is resizeable
        """

        # We don't want these two parameters to be seen from outside
        # (because they are used internally only)
        offset = kwargs.get("offset", 0)
        base = kwargs.get("base", None)

        if dtype and not np.dtype(dtype).isbuiltin:
            raise TypeError("Element buffer dtype cannot be structured")

        if isinstance(data, np.ndarray):
            if not data.dtype.isbuiltin:
                raise TypeError("Element buffer dtype cannot be structured")
            else:
                dtype = data.dtype
        elif dtype not in [np.uint8, np.uint16, np.uint32]:
            raise TypeError("Data type not allowed for IndexBuffer")

        DataBuffer.__init__(self, data=data, dtype=dtype, size=size, base=base,
                            offset=offset, target=gl.GL_ELEMENT_ARRAY_BUFFER,
                            store=store, copy=copy, resizeable=resizeable)
