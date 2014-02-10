# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
""" Definition of VertexBuffer, ElemenBuffer and client buffer classes. """

from __future__ import division

import numpy as np

from ..util import is_string, logger
from . import gl
from . import GLObject


# ------------------------------------------------------------ Buffer class ---
class Buffer(GLObject):

    """ Interface to upload buffer data to the GPU. This class is shape
    and dtype agnostic and considers the arrays as byte data.

    In general, you will want to use the VertexBuffer or ElementBuffer.

    Parameters
    ----------
    target : GLENUM
        gl.GL_ARRAY_BUFFER or gl.GL_ELEMENT_ARRAY_BUFFER
    data : ndarray
        The data to set. Optional.
    """

    def __init__(self, target, data=None):
        """ Initialize buffer into default state. """

        GLObject.__init__(self)

        # Store and check target
        if target not in (gl.GL_ARRAY_BUFFER, gl.GL_ELEMENT_ARRAY_BUFFER):
            raise ValueError("Invalid target for buffer object.")
        self._target = target

        # Total bytes consumed by the elements of the buffer
        self._nbytes = 0

        # Indicate if a resize has been requested
        self._need_resize = False

        # Buffer usage (GL_STATIC_DRAW, G_STREAM_DRAW or GL_DYNAMIC_DRAW)
        self._usage = gl.GL_DYNAMIC_DRAW

        # Set data
        self._pending_data = []
        if data is not None:
            self.set_data(data)

    def set_nbytes(self, nbytes):
        """ Set how many bytes should be available for the buffer.
        """
        nbytes = int(nbytes)

        # Set new bytes
        if self._nbytes != nbytes:
            self._nbytes = int(nbytes)
            self._need_resize = True

        # Clear pending subdata
        self._pending_data = []

    def set_data(self, data):
        """ Set the bytes data. This accepts a numpy array,
        but the data is not checked for dtype or shape.

        Parameters
        ----------
        data : ndarray
            The data to set.
        """

        # Check data is a numpy array
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")

        # Set shape if necessary
        self.set_nbytes(data.nbytes)

        # Set pending!
        nbytes = data.nbytes
        self._pending_data.append((data, nbytes, 0))
        self._need_update = True

    def set_subdata(self, offset, data):
        """ Update a region of the buffer.

        Parameters
        ----------
        offset : int
            The offset (in bytes) at which to set the given data.
        data : ndarray
            The data to set.

        """

        # Check some size has been allocated
        if not self._nbytes:
            raise RuntimeError(
                "Cannot set subdata if there is no space allocated.")

        # Check data is a numpy array
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")

        # Get offset and nbytes
        offset = int(offset)
        nbytes = data.nbytes

        # Check
        if offset < 0:
            raise ValueError("Offset must be > 0.")
        if (offset + nbytes) > self._nbytes:
            raise ValueError("Offseted data is too big for buffer.")

        # Set pending!
        self._pending_data.append((data, nbytes, offset))
        self._need_update = True

    @property
    def nbytes(self):
        """ The buffer size (in bytes). """
        return self._nbytes

    def _create(self):
        """ Create buffer on GPU """
        if not self._handle:
            self._handle = gl.glGenBuffers(1)

    def _delete(self):
        """ Delete buffer from GPU """
        gl.glDeleteBuffers(1, [self._handle])

    def _activate(self):
        """ Bind the buffer to some target """
        gl.glBindBuffer(self._target, self._handle)

    def _deactivate(self):
        """Unbind the current bound buffer"""
        gl.glBindBuffer(self._target, 0)

    def _update(self):
        """Upload all pending data to GPU"""

        # Bind buffer now
        gl.glBindBuffer(self._target, self._handle)

        # Allocate new size if necessary
        if self._need_resize:
            # This will only allocate the buffer on GPU
            # WARNING: we should check if this operation is ok
            gl.glBufferData(self._target, self._nbytes, None, self._usage)
            logger.debug("Creating a new buffer (%d) of %d bytes"
                         % (self._handle, self._nbytes))
            self._need_resize = False

        # Upload data
        while self._pending_data:
            data, nbytes, offset = self._pending_data.pop(0)
            logger.debug("Uploading %d bytes at offset %d to buffer (%d)"
                         % (nbytes, offset, self._handle))
            try:
                gl.glBufferSubData(self._target, offset, nbytes, data)
            except Exception as error:
                # This might be due to a driver error (seen on ATI), issue #64.
                # We try to detect this, and if we can use glBufferData instead
                if (hasattr(error, 'err') and
                        error.err == gl.GL_INVALID_VALUE and
                        offset == 0 and nbytes == self._nbytes):
                    gl.glBufferData(self._target, nbytes, data, self._usage)
                else:
                    raise


# ------------------------------------------------------ DataBuffer class ---
class DataBuffer(Buffer):

    """ Interface to upload buffer data to the GPU. This class is based
    on :class:`buffer.Buffer`, and adds awareness of shape, dtype and striding.

    In general, you will want to use the VertexBuffer or ElementBuffer.

    Parameters
    ----------
    target : GLENUM
        gl.GL_ARRAY_BUFFER or gl.GL_ELEMENT_ARRAY_BUFFER
    data : ndarray or dtype
        The data to set. See docs of VertexBuffer and ElementBuffer for
        details.

    """

    def __init__(self, target, data):
        """ Initialize the buffer """
        Buffer.__init__(self, target)

        # Default offset is 0, only really used for View
        self._offset = 0

        # Allow smart initialziatin
        if is_string(data):
            data = np.dtype(data)  # with a string, e.g. "float32"
        elif isinstance(data, tuple):
            data = np.dtype([data])  # With a tuple, e.g. ('a', np.float32, 3)
        elif isinstance(data, list):
            data = np.dtype(data)  # With a list of the above tuples
        elif isinstance(data, type) and issubclass(data, np.generic):
            data = np.dtype(data)  # With e.g. np.float32

        # Initialize
        if isinstance(data, np.ndarray):
            # Fix dtype, vsize, stride. Initialize count
            array_info = self._parse_array(data)
            self._dtype, self._vsize, self._stride, self._count = array_info
            # Set data now
            if not isinstance(self, (ClientVertexBuffer, ClientElementBuffer)):
                self.set_data(data)
        elif isinstance(data, np.dtype):
            # Fix dtype, vsize, stride. Initialize count
            self._dtype, self._vsize, self._stride = self._parse_dtype(data)
            self._count = 0
        else:
            raise ValueError("DataBuffer needs array or dtype to initialize.")

        # Check data type
        if self.dtype.fields:
            for name in self.dtype.names:
                dtype = self.dtype[name].base
                if dtype.name not in self.DTYPE2GTYPE:
                    raise TypeError("Data type not allowed for %s: %s" %
                                    (self.__class__.__name__, dtype.name))
        else:
            if self.dtype.name not in self.DTYPE2GTYPE:
                raise TypeError("Data type not allowed for %s: %s" %
                                (self.__class__.__name__, self.dtype.name))

    def _parse_array(self, data):
        """ Return (dtype, vsize, stride, count), given an array.
        NEED OVERLOADING
        """
        raise NotImplementedError()

    def _parse_dtype(self, dtype):
        """ Return (dtype, vsize, stride), given a dtype.
        NEED OVERLOADING
        """
        raise NotImplementedError()

    @property
    def dtype(self):
        """ The buffer data type. """
        return self._dtype

    @property
    def vsize(self):
        """ The vector size of each vertex in the buffer. This can be
        1, 2, 3 or 4, corresponding with float, vec2, vec3, vec4. """
        return self._vsize

    @property
    def stride(self):
        """ The number of bytes separating two elements. """
        return self._stride

    @property
    def count(self):
        """ The number of vertices in the buffer. """
        return self._count

    @property
    def offset(self):
        """ The byte offset in the buffer. """
        return self._offset

    def __setitem__(self, key, data):
        """ Set data (deferred operation) """

        # Deal with slices that have None or negatives in them
        if isinstance(key, slice):
            start = key.start or 0
            if start < 0:
                start = self._stride + start
            step = key.step or 1
            assert step > 0
            stop = key.stop or self._stride
            if stop < 0:
                stop = self._stride + stop

        # Check ellipsis (... notation)
        if key == Ellipsis:
            start = 0
            nbytes = data.nbytes
        # If key is not a slice
        elif not isinstance(key, slice) or step > 1:
            raise ValueError("Can only set contiguous block of data.")
        # Else we're happy
        else:
            nbytes = (stop - start) * self._stride

        # Check we have the right amount of data
        if data.nbytes < nbytes:
            raise ValueError("Not enough data.")
        elif data.nbytes > nbytes:
            raise ValueError("Too much data.")

        # WARNING: Do we check data type here or do we cast the data to the
        # same internal dtype ? This would make a silent copy of the data which
        # can be problematic in some cases.
        if data.dtype != self.dtype:
            data = data.astype(self.dtype)  # astype() always makes a copy
        # Set
        self.set_subdata(start, data)

    def __getitem__(self, key):
        """ Create a view on this buffer. """

        if not is_string(key):
            raise ValueError("Can only get access to a named field")

        # Get dtype, e.g. ('x', '<f4', 2)  so it has the vsize!
        dtype = self._dtype[key]  # not .base!
        offset = self._dtype.fields[key][1]

        return VertexBufferView(dtype, base=self, offset=offset)

    def set_count(self, count):
        """ Set the number of vertices for this buffer. This will
        allocate data and discard any pending subdata.

        Parameters
        ----------
        count : int
            The new size of the buffer; the number of vertices.

        """

        # Set count
        self._count = int(count)

        # Update bytes
        nbytes = self._count * self._stride
        self.set_nbytes(nbytes)

    def set_data(self, data):
        """ Set the data for this buffer. Any pending data is discarted.
        The dtype and vsize of this buffer should be respected.

        Parameters
        ----------
        data : np.ndarray
            The data to upload.

        """

        # Check data is a numpy array
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")

        # If data is a structure array with a unique field
        # we get this unique field as data
        while data.dtype.fields and len(data.dtype.fields) == 1:
            data = data[data.dtype.names[0]]

        # Get props of the given data
        dtype, vsize, stride, count = self._parse_array(data)

        # Check dtype and vsize to see whether it is a match
        if dtype != self.dtype:
            raise ValueError('Given data must match dtype of the buffer.')
        elif vsize != self.vsize:
            raise ValueError('Given data must match vsize of the buffer.')

        # Update count
        self.set_count(count)

        # Update stride for this newly given data
        self._stride = stride

        # Update data
        Buffer.set_data(self, data)

    def set_subdata(self, offset, data):
        """ Set subdata. The dtype and vsize of this buffer should be
        respected. And the data must fit in the current buffer.

        Parameters
        ----------
        offset : int
            The offset (in vertex indices) to set the data for.
        data : np.ndarray
            The data to update.
        """

        # If data is a structure array with a unique field
        # we get this unique field as data
        while data.dtype.fields and len(data.dtype.fields) == 1:
            data = data[data.dtype.names[0]]

        # Get props of the given data and check whether it's a match
        dtype, vsize, stride, count = self._parse_array(data)
        if dtype != self.dtype:
            raise ValueError('Given data must match dtype of the buffer.')
        elif vsize != self.vsize:
            raise ValueError('Given data must match vsize of the buffer.')
        elif stride != self.stride:
            raise ValueError('Given data must match stride of the buffer.')

        # Test whether it fits
        if offset < 0:
            raise ValueError('Offset in set_subdata should be >= 0.')
        elif offset + count > self.count:
            raise ValueError('Offset + data does not fit in this buffer.')

        # Turn attribute-offset into a byte offset
        offset = int(offset)
        byte_offset = offset * self._stride

        # Upload
        Buffer.set_subdata(self, byte_offset, data)


# ------------------------------------------------------ ElementBuffer class --
class ElementBuffer(DataBuffer):

    """ The ElementBuffer allows to specify which element of a
    VertexBuffer are to be used in a shader program.
    Inherits :class:`buffer.DataBuffer`.

    The given data must be of unsigned integer type. The shape of the
    data is ignored; each element in the array is simply considered a
    vertex index.

    Parameters
    ----------
    data : ndarray or dtype
        Specify the data, or the type of the data. The dtype can also
        be something that evaluates to a dtype, such as a 'uint32' or
        np.uint8.
    client : bool
        Should be given as a keyword argument. If True, a
        ClientElementBuffer is used instead, which is a lightweight
        wrapper class for storing element data in CPU memory.

    Example
    -------
    indices = np.zeros(100, dtype=np.uint16)
    buffer = ElementBuffer(indices)
    program = Program(...)

    program.draw(gl.GL_TRIANGLES, indices)
    ...
    """

    # We need a DTYPE->GL map for the element buffer. Used in program.draw()
    DTYPE2GTYPE = {'uint8': gl.GL_UNSIGNED_BYTE,
                   'uint16': gl.GL_UNSIGNED_SHORT,
                   'uint32': gl.GL_UNSIGNED_INT,
                   }

    def __new__(cls, *args, **kwargs):
        if cls is ElementBuffer and kwargs.get('client', False):
            # __init__ will be called
            return object.__new__(ClientElementBuffer)
        else:
            return object.__new__(cls)  # __init__ will be called

    def __init__(self, data, client=False):
        DataBuffer.__init__(self, gl.GL_ELEMENT_ARRAY_BUFFER, data)

    def _parse_array(self, data):
        """ Return (dtype, vsize, stride, count), given an array.
        """

        # Check data
        if data.dtype.fields:
            raise ValueError(
                'ElementBuffer does not support structured arrays.')

        # Set dtype, vsize and stride
        dtype, vsize, stride = self._parse_dtype(data.dtype)

        # Count is simply the size
        count = data.size

        return dtype, vsize, stride, count

    def _parse_dtype(self, dtype):
        """ Return (dtype, vsize, stride), given a dtype.
        """

        # Check data
        if dtype.fields:
            raise ValueError(
                'ElementBuffer does not support structured dtype.')

        # Get base dtype, this will turn ('x', '<f4', 3) into np.float32
        dtype_ = dtype.base

        # vsize is one, the ElementBuffer contains indices, which are scalars
        vsize = 1

        # Get stride
        stride = dtype.itemsize * vsize  # == dtype.itemsize

        return dtype_, vsize, stride


# ------------------------------------------------------ VertexBuffer class ---
class VertexBuffer(DataBuffer):

    """ The VertexBuffer represents any kind of vertex data, and can also
    represent an array-of-structures approach.
    Inherits :class:`buffer.DataBuffer`.

    The shape of the given data is interpreted in the following way:
    If a normal array of one dimension is given, the vector-size (vsize)
    is considered 1. Otherwise, data.shape[-1] is considered the vsize,
    and the other dimensions are "collapsed" to get the vertex count.
    If the data is a structured array, the number of elements in each
    item is used as the vector-size (vsize).

    Parameters
    ----------
    data : ndarray or dtype
        Specify the data, or the type of the data. The dtype can also
        be something that evaluates to a dtype, such as a 'uint32' or
        np.uint8. If a structured array or dtype is given, and there
        are more than 1 elements in the structure, this buffer is a
        "structured" buffer. The corresponding items can be obtained
        by indexing this buffer using their name. In most cases
        one can use program.set_vars(structured_buffer) to map the
        item names to their GLSL attribute names automatically.
    client : bool
        Should be given as a keyword argument. If True, a
        ClientVertexBuffer is used instead, which is a lightweight
        wrapper class for storing vertex data in CPU memory.

    Example
    -------
    dtype = np.dtype( [ ('position', np.float32, 3),
                        ('texcoord', np.float32, 2),
                        ('color',    np.float32, 4) ] )
    data = np.zeros(100, dtype=dtype)

    program = Program(...)

    program.set_vars(VertexBuffer(data))
    """

    # Note that we do not actually use this, except the keys to test
    # whether a data type is allowed; we parse the gtype from the
    # attribute data.
    DTYPE2GTYPE = {'int8': gl.GL_BYTE,
                   'uint8': gl.GL_UNSIGNED_BYTE,
                   'uint16': gl.GL_UNSIGNED_SHORT,
                   'int16': gl.GL_SHORT,
                   'float32': gl.GL_FLOAT,
                   'float16': gl.ext.GL_HALF_FLOAT,
                   }

    def __new__(cls, *args, **kwargs):
        if cls is VertexBuffer and kwargs.get('client', False):
            # __init__ will be called
            return object.__new__(ClientVertexBuffer)
        else:
            return object.__new__(cls)  # __init__ will be called

    def __init__(self, data, client=False):
        DataBuffer.__init__(self, gl.GL_ARRAY_BUFFER, data)

    def _parse_array(self, data):
        """ Return (dtype, vsize, stride, count), given an array.
        """

        # If data is a structure array with a unique field
        # we get this unique field as data
        while data.dtype.fields and len(data.dtype.fields) == 1:
            data = data[data.dtype.names[0]]

        # Set dtype, vsize and stride
        dtype, vsize, stride = self._parse_dtype(data.dtype)

        # Determine count and vsize
        if dtype.fields:
            # Structured array, vsize is already set
            # Count is simply the number of elements in the base array
            count = data.size

        else:
            # Normal array, we reset vsize using the data

            if data.ndim <= 1:
                # We take it the vector size is 1
                vsize = 1
                # Count is simply the number of elements.
                count = data.size
            else:
                # Vector size is last dimension
                vsize = data.shape[-1]
                # Count is product of all dimensions except last
                count = int(np.prod(data.shape[:-1]))

        # Set stride
        if data.base is None:
            # There is no base. PyOpenGL will upload our data as-is,
            # so we use strides of the numpy array. This occurs in most
            # situations, but also if we do VertexBuffer(data) where
            # data is a structured array.
            stride = data.strides[0]
        else:
            # There is a base, PyOpenGL will make a local copy before
            # uploading the data. Therefore data.strides[0] will be
            # incorrect; we need to calcualate the stride that the local
            # copy will have. This can differ fron data.strides[0] when
            # we do e.g. VertexBuffer( data['a_position'] ).
            stride = dtype.itemsize * vsize

        # Done
        return dtype, vsize, stride, count

    def _parse_dtype(self, dtype):
        """ Return (dtype, vsize, stride), given a dtype.
        """

        # If dtype is a structure with a unique field
        # we get this unique field as dtype
        while dtype.fields and len(dtype.fields) == 1:
            dtype = dtype[dtype.names[0]]

        # Get base dtype, this will turn ('x', '<f4', 3) into np.float32
        dtype_ = dtype.base

        # Determine count and vsize
        if dtype.fields:
            # Structured array: Vector size is 1: one element of this
            # structured dtype per vertex
            vsize = 1
            # Or ... We set the sun of all vsizes
            # No! because "stride = data.itemsize * vsize" will then fail!
            #shapes = [dtype[name].shape for name in dtype.names]
            #sizes = [int(np.prod(s)) for s in shapes]
            #vsize = sum(sizes)

        elif dtype.shape:
            # e.g. ('x', '<f4', 3):
            # Vector size is simply the number of elements in the dtype
            vsize = int(np.prod(dtype.shape))

        else:
            # Plain dtype, assume scalar value
            vsize = 1

        # Get stride. Note that this will always be overriden by _parse_array
        stride = dtype.itemsize * vsize

        return dtype_, vsize, stride


# ------------------------------------------------------ VertexBuffer class ---
class VertexBufferView(VertexBuffer):

    """ A VertexBufferView is a view on a VertexBuffer. It cannot be
    used to set shape or data. You generally do not use this class
    directly, but create an instance of this class by indexing in a
    structured VertexBuffer.
    """

    def __init__(self, dtype, base, offset):
        """ Initialize the view """
        assert isinstance(dtype, np.dtype)
        VertexBuffer.__init__(self, dtype)

        self._base = base
        self._offset = int(offset)
        self._stride = base.stride  # Override this

    def set_count(self, *args, **kwargs):
        raise RuntimeError(
            'Cannot set count on a %s.' %
            self.__class__.__name__)

    def set_data(self, *args, **kwargs):
        raise RuntimeError(
            'Cannot set data on a %s.' %
            self.__class__.__name__)

    def set_subdata(self, *args, **kwargs):
        raise RuntimeError(
            'Cannot set subdata on a %s.' %
            self.__class__.__name__)

    @property
    def handle(self):
        # Handle on base buffer. (avoid showing up in docs)
        self._handle = self._base._handle
        return self._handle

    @property
    def stride(self):
        """ Byte number separating two elements. """
        self._stride = self._base.stride
        return self._stride

    @property
    def count(self):
        """ Number of vertices in the buffer. """
        self._count = self._base.count
        return self._count

    @property
    def base(self):
        """ Vertex buffer base of this view. """
        return self._base

    def _create(self):
        """ Create buffer on GPU """
        self._base._create()
        self._handle = self._base._handle

    def _delete(self):
        """ Delete base buffer from GPU. """
        self._base.delete()

    def _activate(self):
        """ Bind the base buffer to some target """
        self._base.activate()

    def _deactivate(self):
        """ Unbind the base buffer """
        self._base.deactivate()

    def _update(self):
        """ Update base buffer. """
        pass  # base._update is called from base.activate


# ------------------------------------------------ ClientVertexBuffer class ---
class ClientVertexBuffer(VertexBuffer):

    """
    A client buffer is a buffer that only exists (permanently) on the CPU. It
    cannot be modified nor uploaded into a GPU buffer. It merely serves as
    passing direct data during a drawing operations.

    Note this kind of buffer is in general inefficient since data is
    uploaded at each draw.
    """

    def __init__(self, data, client=True):
        """ Initialize the buffer. """
        if not isinstance(data, np.ndarray):
            raise ValueError('ClientVertexBuffer needs a numpy array.')
        VertexBuffer.__init__(self, data)
        self._data = data

    @property
    def data(self):
        """ Buffer data. """
        return self._data

    def set_count(self, *args, **kwargs):
        raise RuntimeError(
            'Cannot set count on a %s.' %
            self.__class__.__name__)

    def set_data(self, *args, **kwargs):
        raise RuntimeError(
            'Cannot set data on a %s.' %
            self.__class__.__name__)

    def set_subdata(self, *args, **kwargs):
        raise RuntimeError(
            'Cannot set subdata on a %s.' %
            self.__class__.__name__)

    def __getitem__(self, key):
        pass

    def __setitem__(self, key, data):
        pass

    def _create(self):
        pass

    def _delete(self):
        pass

    def _activate(self):
        pass

    def _deactivate(self):
        pass

    def _update(self):
        pass


# ----------------------------------------------- ClientElementBuffer class ---
class ClientElementBuffer(ElementBuffer):

    """
    A client buffer is a buffer that only exists (permanently) on the CPU. It
    cannot be modified nor uploaded into a GPU buffer. It merely serves as
    passing direct data during a drawing operations.

    Note this kind of buffer is in general inefficient since data is
    uploaded at each draw.
    """

    def __init__(self, data, client=True):
        """ Initialize the buffer. """
        if not isinstance(data, np.ndarray):
            raise ValueError('ClientElementBuffer needs a numpy array.')
        ElementBuffer.__init__(self, data)
        self._data = data

    @property
    def data(self):
        """ Buffer data. """
        return self._data

    def set_count(self, *args, **kwargs):
        raise RuntimeError(
            'Cannot set count on a %s.' %
            self.__class__.__name__)

    def set_data(self, *args, **kwargs):
        raise RuntimeError(
            'Cannot set data on a %s.' %
            self.__class__.__name__)

    def set_subdata(self, *args, **kwargs):
        raise RuntimeError(
            'Cannot set subdata on a %s.' %
            self.__class__.__name__)

    def __getitem__(self, key):
        pass

    def __setitem__(self, key, data):
        pass

    def _create(self):
        pass

    def _delete(self):
        pass

    def _activate(self):
        pass

    def _deactivate(self):
        pass

    def _update(self):
        pass
