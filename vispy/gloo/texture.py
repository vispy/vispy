# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import numpy as np

from . import gl
from .globject import GLObject
from ..util import logger


# ----------------------------------------------------------- Texture class ---
class Texture(GLObject):
    """
    A Texture is used to represent a topological set of scalar values.
    
    Parameters
    ----------

    target : GLEnum
        gl.GL_TEXTURE2D
        gl.GL_TEXTURE_CUBE_MAP
    data : ndarray
        Texture data (optional)
    shape : tuple of integers
        Texture shape (optional)
    dtype : dtype
        Texture data type (optional)
    base : Texture
        Base texture of this texture
    offset : tuple of integers
        Offset of this texture relative to base texture
    store : bool
        Specify whether this object stores a reference to the data,
        allowing the data to be updated regardless of striding. Note
        that modifying the data after passing it here might result in
        undesired behavior, unless a copy is given. Default True.
    resizeable : bool
        Indicates whether texture can be resized
    """

    _formats = {
        1: gl.GL_LUMINANCE,  # or ALPHA,
        2: gl.GL_LUMINANCE_ALPHA,
        3: gl.GL_RGB,
        4: gl.GL_RGBA
    }

    _types = {
        np.dtype(np.int8): gl.GL_BYTE,
        np.dtype(np.uint8): gl.GL_UNSIGNED_BYTE,
        np.dtype(np.int16): gl.GL_SHORT,
        np.dtype(np.uint16): gl.GL_UNSIGNED_SHORT,
        np.dtype(np.int32): gl.GL_INT,
        np.dtype(np.uint32): gl.GL_UNSIGNED_INT,
        # np.dtype(np.float16) : gl.GL_HALF_FLOAT,
        np.dtype(np.float32): gl.GL_FLOAT,
        # np.dtype(np.float64) : gl.GL_DOUBLE
    }

    def __init__(self, data=None, shape=None, dtype=None, base=None, 
                 target=None, offset=None, store=True, resizeable=True):
        GLObject.__init__(self)
        self._data = None
        self._base = base
        self._store = store
        self._copy = False  # flag to indicate that a copy is made
        self._target = target
        self._offset = offset
        self._pending_data = []
        self._resizeable = resizeable
        self._need_resize = False
        self._need_update = False
        self._valid = True
        self._views = []

        self._interpolation = gl.GL_NEAREST, gl.GL_NEAREST
        self._wrapping = gl.GL_CLAMP_TO_EDGE
        self._need_parameterization = True

        # Do we have data to build texture upon ?
        if data is not None:
            self._need_resize = True
            # Handle dtype
            if dtype is not None:
                data = np.array(data, dtype=dtype, copy=False)
            else:
                data = np.array(data, copy=False)
            self._dtype = data.dtype
            # Handle shape
            if shape is not None:
                raise ValueError('Texture needs data or shape, nor both.')
            self._shape = data.shape
            # Handle storage
            if self._store:
                if not data.flags["C_CONTIGUOUS"]:
                    logger.warning("Copying discontiguous data as CPU storage")
                    self._copy = True
                    data = data.copy()
                self._data = data
            # Set data
            self.set_data(data, copy=False)
        elif dtype is not None:
            if shape is not None:
                self._need_resize = True
            self._shape = shape or ()
            self._dtype = dtype
            if self._store:
                self._data = np.empty(self._shape, dtype=self._dtype)
        else:
            raise ValueError("Either data or dtype must be given")

        if offset is None:
            self._offset = (0,) * len(self._shape)
        else:
            self._offset = offset
        
        # Check shape and dtype
        self._check_shape()
        if hasattr(self._dtype, 'fields') and self._dtype.fields:
            raise ValueError("Texture dtype cannot be structured")

        self._gtype = Texture._types.get(np.dtype(self.dtype), None)
        if self._gtype is None:
            raise ValueError("Type not allowed for texture")

    def _check_shape(self):
        pass
    
    @property
    def shape(self):
        """ Texture shape """

        return self._shape

    @property
    def offset(self):
        """ Texture offset """

        return self._offset

    @property
    def dtype(self):
        """ Texture data type """

        return self._dtype

    @property
    def base(self):
        """ Texture base if this texture is a view on another texture """

        return self._base

    @property
    def data(self):
        """ Texture CPU storage """

        return self._data

    @property
    def wrapping(self):
        """ Texture wrapping mode """

        if self.base is not None:
            return self.base.wrapping
        return self._wrapping

    @wrapping.setter
    def wrapping(self, value):
        """ Texture wrapping mode """

        if self.base is not None:
            raise ValueError("Cannot set wrapping on texture view")

        assert value in (gl.GL_REPEAT, gl.GL_CLAMP_TO_EDGE,
                         gl.GL_MIRRORED_REPEAT)
        self._wrapping = value
        self._need_parameterization = True

    @property
    def interpolation(self):
        """ Texture interpolation for minification and magnification. """

        if self.base is not None:
            return self.base.interpolation

        return self._interpolation

    @interpolation.setter
    def interpolation(self, value):
        """ Texture interpolation for minication and magnification. """

        if self.base is not None:
            raise ValueError("Cannot set interpolation on texture view")

        assert value in (gl.GL_NEAREST, gl.GL_LINEAR)
        self._interpolation = value
        self._need_parameterization = True

    def resize(self, shape):
        """ Resize the texture (deferred operation)

        Parameters
        ----------

        shape : tuple of integers
            New texture shape

        Notes
        -----
        This clears any pending operations.
        """

        if not self._resizeable:
            raise RuntimeError("Texture is not resizeable")

        if self._base is not None:
            raise RuntimeError("Texture view is not resizeable")

        if len(shape) != len(self.shape):
            raise ValueError("New shape has wrong number of dimensions")

        if shape == self.shape:
            return

        # Invalidate any view on this texture
        for view in self._views:
            view._valid = False
        self._views = []

        self._pending_data = []
        self._need_update = False
        self._need_resize = True
        self._shape = shape
        if self._data is not None and self._store:
            self._data = np.resize(self._data, self._shape)
        else:
            self._data = None

    def set_data(self, data, offset=None, copy=False):
        """
        Set data (deferred operation)

        Parameters
        ----------

        data : ndarray
            Data to be uploaded
        offset: int or tuple of ints
            Offset in texture where to start copying data
        copy: bool
            Since the operation is deferred, data may change before
            data is actually uploaded to GPU memory.
            Asking explicitly for a copy will prevent this behavior.

        Notes
        -----
        This operation implicitely resizes the texture to the shape of the data
        if given offset is None.
        """

        if self.base is not None and not self._valid:
            raise ValueError("This texture view has been invalited")

        if self.base is not None:
            self.base.set_data(data, offset=self.offset, copy=copy)
            return
        
        data = np.array(data, copy=copy)
        
        # Check data has the right shape
        # if len(data.shape) != len(self.shape):
        #  raise ValueError("Data has wrong shape")

        # Check if resize needed
        if offset is None:
            if data.shape != self.shape:
                self.resize(data.shape)

        if offset is None or offset == (0,) * len(self.shape):
            if data.shape == self.shape:
                self._pending_data = []

            # Convert offset to something usable
            offset = (0,) * len(self.shape)

        # Check if data fits
        for i in range(len(data.shape)):
            if offset[i] + data.shape[i] > self.shape[i]:
                raise ValueError("Data is too large")

        self._pending_data.append((data, offset))
        self._need_update = True

    def __getitem__(self, key):
        """ x.__getitem__(y) <==> x[y] """

        if self.base is not None:
            raise ValueError("Can only access data from a base texture")

        # Make sure key is a tuple
        if isinstance(key, (int, slice)) or key == Ellipsis:
            key = (key,)

        # Default is to access the whole texture
        shape = self.shape
        slices = [slice(0, shape[i]) for i in range(len(shape))]

        # Check last key/Ellipsis to decide on the order
        keys = key[::+1]
        dims = range(0, len(key))
        if key[0] == Ellipsis:
            keys = key[::-1]
            dims = range(len(self.shape) - 1,
                         len(self.shape) - 1 - len(keys), -1)

        # Find exact range for each key
        for k, dim in zip(keys, dims):
            size = self.shape[dim]
            if isinstance(k, int):
                if k < 0:
                    k += size
                if k < 0 or k > size:
                    raise IndexError("Texture assignment index out of range")
                start, stop = k, k + 1
                slices[dim] = slice(start, stop, 1)
            elif isinstance(k, slice):
                start, stop, step = k.indices(size)
                if step != 1:
                    raise ValueError("Cannot access non-contiguous data")
                if stop < start:
                    start, stop = stop, start
                slices[dim] = slice(start, stop, step)
            elif k == Ellipsis:
                pass
            else:
                raise TypeError("Texture indices must be integers")

        offset = tuple([s.start for s in slices])
        shape = tuple([s.stop - s.start for s in slices])
        data = None
        if self.data is not None:
            data = self.data[slices]

        T = self.__class__(dtype=self.dtype, shape=shape,
                           base=self, offset=offset, resizeable=False)
        T._data = data
        self._views.append(T)
        return T

    def __setitem__(self, key, data):
        """ x.__getitem__(y) <==> x[y] """

        if self.base is not None and not self._valid:
            raise ValueError("This texture view has been invalited")

        # Make sure key is a tuple
        if isinstance(key, (int, slice)) or key == Ellipsis:
            key = (key,)

        # Default is to access the whole texture
        shape = self.shape
        slices = [slice(0, shape[i]) for i in range(len(shape))]

        # Check last key/Ellipsis to decide on the order
        keys = key[::+1]
        dims = range(0, len(key))
        if key[0] == Ellipsis:
            keys = key[::-1]
            dims = range(len(self.shape) - 1,
                         len(self.shape) - 1 - len(keys), -1)

        # Find exact range for each key
        for k, dim in zip(keys, dims):
            size = self.shape[dim]
            if isinstance(k, int):
                if k < 0:
                    k += size
                if k < 0 or k > size:
                    raise IndexError("Texture assignment index out of range")
                start, stop = k, k + 1
                slices[dim] = slice(start, stop, 1)
            elif isinstance(k, slice):
                start, stop, step = k.indices(size)
                if step != 1:
                    raise ValueError("Cannot access non-contiguous data")
                if stop < start:
                    start, stop = stop, start
                slices[dim] = slice(start, stop, step)
            elif k == Ellipsis:
                pass
            else:
                raise TypeError("Texture indices must be integers")

        offset = tuple([s.start for s in slices])
        shape = tuple([s.stop - s.start for s in slices])
        size = 1
        for i in range(len(shape)):
            size *= shape[i]
        #size = reduce(mul, shape)

        # We have CPU storage
        if self.data is not None:
            self.data[key] = data
            data = self.data[key]
        else:
            # Make sure data is an array
            if not isinstance(data, np.ndarray):
                data = np.array(data, dtype=self.dtype, copy=False)
            # Make sure data is big enough
            if data.size != size:
                data = np.resize(data, size).reshape(shape)

        # Set data (deferred)
        if self.base is None:
            self.set_data(data=data, offset=offset, copy=False)
        else:
            offset = self.offset + offset
            self.base.set_data(data=data, offset=offset, copy=False)

    def _parameterize(self):
        """ Paramaterize texture """

        if self._need_parameterization:
            self._need_parameterization = False
            if isinstance(self._interpolation, tuple):
                min_filter = self._interpolation[0]
                mag_filter = self._interpolation[1]
            else:
                min_filter = self._interpolation
                mag_filter = self._interpolation
            gl.glTexParameterf(
                self._target, gl.GL_TEXTURE_MIN_FILTER, min_filter)
            gl.glTexParameterf(
                self._target, gl.GL_TEXTURE_MAG_FILTER, mag_filter)

            if isinstance(self._wrapping, tuple):
                wrap_s = self._wrapping[0]
                wrap_t = self._wrapping[1]
            else:
                wrap_s = self._wrapping
                wrap_t = self._wrapping
            gl.glTexParameterf(self._target, gl.GL_TEXTURE_WRAP_S, wrap_s)
            gl.glTexParameterf(self._target, gl.GL_TEXTURE_WRAP_T, wrap_t)

    def _create(self):
        """ Create texture on GPU """

        logger.debug("GPU: Creating texture")
        self._handle = gl.glCreateTexture()

    def _delete(self):
        """ Delete texture from GPU """

        logger.debug("GPU: Deleting texture")
        gl.glDeleteTexture(self._handle)

    def _activate(self):
        """ Activate texture on GPU """

        logger.debug("GPU: Activate texture")
        gl.glBindTexture(self.target, self._handle)
        if self._need_parameterization:
            self._parameterize()
        if self._need_resize:
            self._resize()
            self._need_resize = False

    def _deactivate(self):
        """ Deactivate texture on GPU """

        logger.debug("GPU: Deactivate texture")
        gl.glBindTexture(self._target, 0)


# --------------------------------------------------------- Texture1D class ---
class Texture1D(Texture):
    """ One dimensional texture
    
    Parameters
    ----------

    data : ndarray
        Texture data (optional)
    shape : tuple of integers
        Texture shape (optional)
    dtype : dtype
        Texture data type (optional)
    store : bool
        Specify whether this object stores a reference to the data,
        allowing the data to be updated regardless of striding. Note
        that modifying the data after passing it here might result in
        undesired behavior, unless a copy is given. Default True.
    format : ENUM
        The format of the texture: GL_LUMINANCE, ALPHA, GL_LUMINANCE_ALPHA, 
        or GL_RGB, GL_RGBA. If not given the format is chosen automatically 
        based on the number of channels. When the data has one channel,
        GL_LUMINANCE is assumed.
    
    Notes
    -----
    Under water this is really a 2D texture (1D textures are not
    supported in GL ES 2.0).
    
    """

    def __init__(self, data=None, shape=None, dtype=None, store=True, 
                 format=None, **kwargs):
        
        # We don't want these parameters to be seen from outside (because they
        # are only used internally)
        offset = kwargs.get("offset", None)
        base = kwargs.get("base", None)
        resizeable = kwargs.get("resizeable", True)
        
        Texture.__init__(self, data=data, shape=shape, dtype=dtype,
                         base=base, resizeable=resizeable, store=store,
                         target=gl.GL_TEXTURE_2D, offset=offset)

        # Get and check format
        if format is None:
            self._format = Texture._formats.get(self.shape[-1], None)
        else:
            self._format = format
        if self._format is None:
            raise ValueError("Cannot convert data to texture")

    def _check_shape(self):
        shape = self._shape
        if shape:
            if len(shape) < 1:
                raise ValueError("Too few dimensions for texture")
            elif len(shape) > 2:
                raise ValueError("Too many dimensions for texture")
            elif len(shape) == 1:
                if self._data is not None:
                    self._data = self._data.reshape((shape[0], 1))
                self._shape = (shape[0], 1)
            elif len(shape) == 2:
                if shape[-1] > 4:
                    raise ValueError("Too many channels for texture")
    
    @property
    def width(self):
        """ Texture width """

        return self._shape[0]

    def _resize(self):
        """ Texture resize on GPU """

        logger.debug("GPU: Resizing texture(%s)" % (self.width))
        # gl.glTexImage1D(self.target, 0, self._format, self._format, 
        #                 self._gtype, (self._width,))
        shape = self.height, self.width
        gl.glTexImage2D(self.target, 0, self._format, self._format, 
                        self._gtype, shape)

    def _update(self):
        """ Texture update on GPU """

        # We let base texture to handle all operations
        if self.base is not None:
            return

        logger.debug("GPU: Updating texture (%d pending operation(s))" %
                     len(self._pending_data))

        while self._pending_data:
            data, offset = self._pending_data.pop(0)
            if offset is None:
                x = 0
            else:
                x = offset[0]
            # gl.glTexSubImage1D(self.target, 0, x, self._format, 
            #                    self._gtype, data)
            gl.glTexSubImage2D(self.target, 0, x, self._format, 
                               self._gtype, data)


# --------------------------------------------------------- Texture2D class ---
class Texture2D(Texture):
    """ Two dimensional texture
    
    Parameters
    ----------

    data : ndarray
        Texture data (optional)
    shape : tuple of integers
        Texture shape (optional)
    dtype : dtype
        Texture data type (optional)
    store : bool
        Specify whether this object stores a reference to the data,
        allowing the data to be updated regardless of striding. Note
        that modifying the data after passing it here might result in
        undesired behavior, unless a copy is given. Default True.
    format : ENUM
        The format of the texture: GL_LUMINANCE, ALPHA, GL_LUMINANCE_ALPHA, 
        or GL_RGB, GL_RGBA. If not given the format is chosen automatically 
        based on the number of channels. When the data has one channel,
        GL_LUMINANCE is assumed.
    """

    def __init__(self, data=None, shape=None, dtype=None, store=True, 
                 format=None, **kwargs):

        # We don't want these parameters to be seen from outside (because they
        # are only used internally)
        offset = kwargs.get("offset", None)
        base = kwargs.get("base", None)
        resizeable = kwargs.get("resizeable", True)

        Texture.__init__(self, data=data, shape=shape, dtype=dtype, base=base,
                         resizeable=resizeable, store=store,
                         target=gl.GL_TEXTURE_2D, offset=offset)

        # Get and check format
        if format is None:
            self._format = Texture._formats.get(self.shape[-1], None)
        else:
            self._format = format
        if self._format is None:
            raise ValueError("Cannot convert data to texture")
    
    def _check_shape(self):
        shape = self._shape
        if shape:
            if len(shape) < 2:
                raise ValueError("Too few dimensions for texture")
            elif len(shape) > 3:
                raise ValueError("Too many dimensions for texture")
            elif len(shape) == 2:
                if self._data is not None:
                    self._data = self._data.reshape((shape[0], shape[1], 1))
                self._shape = (shape[0], shape[1], 1)
            elif len(shape) == 3:
                if shape[-1] > 4:
                    raise ValueError("Too many channels for texture")

    @property
    def height(self):
        """ Texture height """

        return self._shape[0]

    @property
    def width(self):
        """ Texture width """

        return self._shape[1]

    def _resize(self):
        """ Texture resize on GPU """

        logger.debug("GPU: Resizing texture(%sx%s)" %
                     (self.width, self.height))
        shape = self.height, self.width
        gl.glTexImage2D(self.target, 0, self._format, self._format, 
                        self._gtype, shape)

    def _update(self):
        """ Texture update on GPU """

        # We let base texture to handle all operations
        if self.base is not None:
            return

        if self._need_resize:
            self._resize()
            self._need_resize = False
        logger.debug("GPU: Updating texture (%d pending operation(s))" %
                     len(self._pending_data))

        while self._pending_data:
            data, offset = self._pending_data.pop(0)
            x, y = 0, 0
            if offset is not None:
                y, x = offset[0], offset[1]
            #width, height = data.shape[1], data.shape[0]
            gl.glTexSubImage2D(self.target, 0, x, y, self._format, 
                               self._gtype, data)

'''
# ---------------------------------------------------- TextureCubeMap class ---
class TextureCubeMap(Texture):
    """ A TextureCubeMap represents a set of 6 2D Textures
    
    Parameters
    ----------

    data : ndarray
        Texture data (optional)
    shape : tuple of integers
        Texture shape (optional)
    dtype : dtype
        Texture data type (optional)
    store : bool
        Specify whether this object stores a reference to the data,
        allowing the data to be updated regardless of striding. Note
        that modifying the data after passing it here might result in
        undesired behavior, unless a copy is given. Default True.
    format : ENUM
        The format of the texture: GL_LUMINANCE, ALPHA, GL_LUMINANCE_ALPHA, 
        or GL_RGB, GL_RGBA. If not given the format is chosen automatically 
        based on the number of channels. When the data has one channel,
        GL_LUMINANCE is assumed.
    """

    def __init__(self, data=None, shape=None, dtype=None, store=True,
                 format=None, **kwargs):
        
        # We don't want these parameters to be seen from outside (because they
        # are only used internally)
        offset = kwargs.get("offset", None)
        base = kwargs.get("base", None)
        resizeable = kwargs.get("resizeable", True)
        
        Texture.__init__(self, data=data, shape=shape, dtype=dtype, base=base,
                         store=store, target=gl.GL_TEXTURE_CUBE_MAP,
                         offset=offset, resizeable=resizeable)

        # Get and check format
        if format is None:
            self._format = Texture._formats.get(self.shape[-1], None)
        else:
            self._format = format
        if self._format is None:
            raise ValueError("Cannot convert data to texture")

        # Create sub-textures
        self._textures = []
        target = gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X
        for i in range(6):
            if data is not None:
                T = Texture2D(data=data[i], base=base,
                              resizeable=False, store=store,
                              target=target + i, offset=offset)
            else:
                T = Texture2D(dtype=dtype, shape=shape[1:], base=base,
                              resizeable=False, store=store,
                              target=target + i, offset=offset)
            self._textures.append(T)
    
    def _check_shape(self):
        shape = self._shape
        if len(shape) < 3:
            raise ValueError("Too few dimensions for texture")
        elif len(shape) > 4:
            raise ValueError("Too many dimensions for texture")
        elif len(shape) == 3:
            if shape[0] != 6:
                raise ValueError("First dimension must be 6 for texture cube")
            if self._data is not None:
                self._data = self._data.reshape((shape[0], shape[1], 
                                                 shape[2], 1))
            self._shape = (shape[0], shape[1], shape[2], 1)
        elif len(shape) == 4:
            if shape[0] != 6:
                raise ValueError("First dimension must be 6 for texture cube")
            if shape[-1] > 4:
                raise ValueError("Too many channels for texture")

    def activate(self):
        """ Activate the object on GPU """

        Texture.activate(self)
        for texture in self._textures:
            texture.activate()

    def _create(self):
        """ Create texture on GPU """

        logger.debug("GPU: Creating texture")

    def _delete(self):
        """ Delete texture from GPU """

        logger.debug("GPU: Deleting texture")

    def _parameterize(self):
        """ Paramaterize texture """

        logger.debug("GPU: Parameterizing texture")

    def _activate(self):
        """ Activate texture on GPU """

        logger.debug("GPU: Activate texture")

    def _deactivate(self):
        """ Deactivate texture on GPU """

        logger.debug("GPU: Deactivate texture")

    def _resize(self):
        """ Texture resize on GPU """

        logger.debug("GPU: Resizing texture(%sx%s)" %
                     (self.width, self.height))

    def _update(self):
        """ Texture upload on GPU """

        logger.debug("GPU: Updating texture (%d pending operation(s))" %
                     len(self._pending_data))


# if __name__ == '__main__':
#    data = np.zeros((6,128,128), dtype=np.uint32)
#    T = TextureCubeMap(data=data)
#    T.activate()
'''
