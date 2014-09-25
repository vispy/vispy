# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np
from os import path as op
from traceback import extract_stack, format_list

# from . import gl  Ha, no more gl here!
from . globject import GLObject
from ..util import logger
from ..ext.six import string_types


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
            self._context.glir.command('SIZE', self._id, nbytes)
        self._context.glir.command('DATA', self._id, offset, data)
    
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
            self._context.glir.command('SIZE', self._id, nbytes)
        
        self._context.glir.command('DATA', self._id, 0, data)
    
    def resize_bytes(self, size):
        """ Resize this buffer (deferred operation). 
        
        Parameters
        ----------
        size : int
            New buffer size in bytes.
        """
        self._nbytes = size
        self._context.glir.command('SIZE', self._id, size)
        # Invalidate any view on this buffer
        for view in self._views:
            view._valid = False
        self._views = []

    def _create(self):
        # Big hack in transition phase
        # variables.py needs the handle :(
        return
        glir = self._context.glir
        try:
            self._handle = glir._parser._objects[self._id]._handle
        except KeyError:
            glir.parse()
            self._handle = glir._parser._objects[self._id]._handle

    def _delete(self):
        pass

    def _resize_bytes(self):
        pass

    def _activate(self):
        return
        # Big hack in transition phase
        # variables.py needs to activate us
        from . import gl
        target = gl.GL_ARRAY_BUFFER
        if isinstance(self, IndexBuffer):
            target = gl.GL_ELEMENT_ARRAY_BUFFER
        gl.glBindBuffer(target, self._handle)
       
    def _deactivate(self):
        return
        from . import gl
        target = gl.GL_ARRAY_BUFFER
        if isinstance(self, IndexBuffer):
            target = gl.GL_ELEMENT_ARRAY_BUFFER
        gl.glBindBuffer(target, 0)
        # todo: remove when Program uses GLIR
    
    def _update_data(self):
        pass


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

    def __init__(self, data=None, dtype=None, size=0):
        self._size = 0  # number of elements in buffer, set in resize_bytes()
        
        # Convert data to array+dtype if needed
        if data is not None:
            nbytes = None
            data_type = data.__class__.__name__
            if dtype is not None:
                data = np.array(data, dtype=dtype, copy=False)
            else:
                data = np.array(data, copy=False)
            # Check whether the given data turned up a sensible array
            if not data.strides:
                raise ValueError("Cannot turn %r ob into a buffer" % data_type)

        # Create buffer from dtype and size
        elif dtype is not None:
            self._dtype = np.dtype(dtype)
            self._stride = self._dtype.itemsize
            self._itemsize = self._dtype.itemsize
            nbytes = size * self._itemsize

        # We need a minimum amount of information
        else:
            raise ValueError("data/dtype/base cannot be all set to None")
        
        Buffer.__init__(self, data=data, nbytes=nbytes)
    
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
        if not isinstance(data, np.ndarray):
            raise ValueError('Data must be a ndarray')
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
    
    It is gnerally not necessary to instantiate this class manually; use 
    ``base_buffer[key]`` instead.
    """

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
    
    # todo: make id a public method? And get rid of handle
    @property
    def _id(self):
        return self._base._id
    
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

        if isinstance(key, string_types):
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
    """
    
    _GLIR_TYPE = 'VERTEXBUFFER'

    def __init__(self, data=None, dtype=None, size=0):

        if isinstance(data, (list, tuple)):
            data = np.array(data, np.float32)

        # Make data structured. This makes things more consistent; our data
        # is always consistent (AK: at least, that is why I *think* this is)
        if dtype is not None:
            dtype = np.dtype(dtype)
            if dtype.isbuiltin:
                dtype = np.dtype([('f0', dtype, 1)])

        DataBuffer.__init__(self, data=data, dtype=dtype, size=size)

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
    
    _GLIR_TYPE = 'INDEXBUFFER'
    
    def __init__(self, data=None, dtype=np.uint32, size=0):

        if dtype and not np.dtype(dtype).isbuiltin:
            raise TypeError("Element buffer dtype cannot be structured")

        if isinstance(data, np.ndarray):
            pass
        elif dtype not in [np.uint8, np.uint16, np.uint32]:
            raise TypeError("Data type not allowed for IndexBuffer")

        DataBuffer.__init__(self, data=data, dtype=dtype, size=size)

    def _prepare_data(self, data, convert=False):
        if not data.dtype.isbuiltin:
            raise TypeError("Element buffer dtype cannot be structured")
        else:
            if convert is True and data.dtype is not np.uint32:
                data = data.astype(np.uint32)
        return data
