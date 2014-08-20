# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import numpy as np

from . import gl
from .globject import GLObject
from .wrappers import _check_conversion
from ..util import logger


GL_SAMPLER_3D = 35679


def _check_pyopengl_3D():
    """Helper to ensure users have OpenGL for 3D texture support (for now)"""
    try:
        import OpenGL.GL as _gl
    except ImportError:
        raise ImportError('PyOpenGL is required for 3D texture support')
    return _gl


def glTexImage3D(target, level, internalformat, format, type, pixels):
    # Import from PyOpenGL
    _gl = _check_pyopengl_3D()
    border = 0
    assert isinstance(pixels, (tuple, list))  # the only way we use this now
    depth, height, width = pixels
    _gl.glTexImage3D(target, level, internalformat,
                     width, height, depth, border, format, type, None)


def glTexSubImage3D(target, level, xoffset, yoffset, zoffset,
                    format, type, pixels):
    # Import from PyOpenGL
    _gl = _check_pyopengl_3D()
    depth, height, width = pixels.shape[:3]
    _gl.glTexSubImage3D(target, level, xoffset, yoffset, zoffset,
                        width, height, depth, format, type, pixels)


def _check_value(value, valid_dict):
    """Helper for checking interpolation and wrapping"""
    if not isinstance(value, (tuple, list)):
        value = [value] * 2
    if len(value) != 2:
        raise ValueError('value must be a single value, or a 2-element list')
    return tuple(_check_conversion(v, valid_dict) for v in value)


# ----------------------------------------------------------- Texture class ---
class BaseTexture(GLObject):
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
    format : str | ENUM
        The format of the texture: 'luminance', 'alpha', 'luminance_alpha',
        'rgb', or 'rgba' (or ENUMs GL_LUMINANCE, ALPHA, GL_LUMINANCE_ALPHA,
        or GL_RGB, GL_RGBA). If not given the format is chosen automatically
        based on the number of channels. When the data has one channel,
        'luminance' is assumed.
    """
    _ndim = 2

    _formats = {
        1: gl.GL_LUMINANCE,  # or ALPHA,
        2: gl.GL_LUMINANCE_ALPHA,
        3: gl.GL_RGB,
        4: gl.GL_RGBA
    }

    _inv_formats = {
        gl.GL_LUMINANCE: 1,
        gl.GL_ALPHA: 1,
        gl.GL_LUMINANCE_ALPHA: 2,
        gl.GL_RGB: 3,
        gl.GL_RGBA: 4
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
                 target=None, offset=None, store=True, resizeable=True,
                 format=None):
        GLObject.__init__(self)
        self._data = None
        self._base = base
        self._store = store
        self._copy = False  # flag to indicate that a copy is made
        self._target = target
        self._offset = offset
        self._pending_data = []
        self._resizeable = resizeable
        self._valid = True
        self._views = []

        # Extra stages that are handled in _activate()
        self._need_resize = False
        self._need_parameterization = True
        if base is None:
            self.interpolation = 'nearest'
            self.wrapping = 'clamp_to_edge'

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
            data = self._normalize_shape(data)
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
            shape = shape or ()
            self._shape = self._normalize_shape(shape)
            self._dtype = dtype
            if self._store:
                self._data = np.zeros(self._shape, dtype=self._dtype)
        else:
            raise ValueError("Either data or dtype must be given")

        if offset is None:
            self._offset = (0,) * len(self._shape)
        else:
            self._offset = offset

        # Check dtype
        if hasattr(self._dtype, 'fields') and self._dtype.fields:
            raise ValueError("Texture dtype cannot be structured")

        self._gtype = BaseTexture._types.get(np.dtype(self.dtype), None)
        if self._gtype is None:
            raise ValueError("Type not allowed for texture")

        # Get and check format
        valid_dict = {'luminance': gl.GL_LUMINANCE,
                      'alpha': gl.GL_ALPHA,
                      'luminance_alpha': gl.GL_LUMINANCE_ALPHA,
                      'rgb': gl.GL_RGB,
                      'rgba': gl.GL_RGBA}
        counts = BaseTexture._inv_formats
        if format is None:
            if len(self.shape) == 0:
                raise ValueError('format must be provided if data and shape '
                                 'are both None')
            format = BaseTexture._formats.get(self.shape[-1], None)
            if format is None:
                raise ValueError("Cannot convert data to texture")
            self._format = format
        else:
            # check to make sure it's a valid entry
            out_format = _check_conversion(format, valid_dict)
            # check to make sure that our shape does not conflict with the type
            if len(self.shape) > 0 and self.shape[-1] != counts[out_format]:
                raise ValueError('format %s size %s mismatch with input shape '
                                 '%s' % (format, counts[out_format],
                                         self.shape[-1]))
            self._format = out_format

    def _normalize_shape(self, data_or_shape):
        # Get data and shape from input
        if isinstance(data_or_shape, np.ndarray):
            data = data_or_shape
            shape = data.shape
        else:
            assert isinstance(data_or_shape, tuple)
            data = None
            shape = data_or_shape
        # Check and correct
        if shape:
            if len(shape) < self._ndim:
                raise ValueError("Too few dimensions for texture")
            elif len(shape) > self._ndim + 1:
                raise ValueError("Too many dimensions for texture")
            elif len(shape) == self._ndim:
                shape = shape + (1,)
            else:  # if len(shape) == self._ndim + 1:
                if shape[-1] > 4:
                    raise ValueError("Too many channels for texture")
        # Return
        return data.reshape(shape) if data is not None else shape

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
        value = self._wrapping
        return value[0] if value[0] == value[1] else value

    @wrapping.setter
    def wrapping(self, value):
        """ Texture wrapping mode """
        if self.base is not None:
            raise ValueError("Cannot set wrapping on texture view")
        valid_dict = {'repeat': gl.GL_REPEAT,
                      'clamp_to_edge': gl.GL_CLAMP_TO_EDGE,
                      'mirrored_repeat': gl.GL_MIRRORED_REPEAT}
        self._wrapping = _check_value(value, valid_dict)
        self._need_parameterization = True

    @property
    def interpolation(self):
        """ Texture interpolation for minification and magnification. """
        if self.base is not None:
            return self.base.interpolation
        value = self._interpolation
        return value[0] if value[0] == value[1] else value

    @interpolation.setter
    def interpolation(self, value):
        """ Texture interpolation for minication and magnification. """
        if self.base is not None:
            raise ValueError("Cannot set interpolation on texture view")
        valid_dict = {'nearest': gl.GL_NEAREST,
                      'linear': gl.GL_LINEAR}
        self._interpolation = _check_value(value, valid_dict)
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
        shape = self._normalize_shape(shape)

        if not self._resizeable:
            raise RuntimeError("Texture is not resizeable")

        if self._base is not None:
            raise RuntimeError("Texture view is not resizeable")

        if len(shape) != len(self.shape):
            raise ValueError("New shape has wrong number of dimensions")

        if shape == self.shape:
            return

        # Reset format if size of last dimension differs
        if shape[-1] != self.shape[-1]:
            format = BaseTexture._formats.get(shape[-1], None)
            if format is None:
                raise ValueError("Cannot determine texture format from shape")
            self._format = format

        # Invalidate any view on this texture
        for view in self._views:
            view._valid = False
        self._views = []

        self._pending_data = []
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
            raise ValueError("This texture view has been invalidated")

        if self.base is not None:
            self.base.set_data(data, offset=self.offset, copy=copy)
            return

        # Force using the same data type. We could probably allow it,
        # but with the views and data storage, this is rather complex.
        if data.dtype != self.dtype:
            raise ValueError('Cannot set texture data with another dtype.')

        # Copy if needed, check/normalize shape
        data = np.array(data, copy=copy)
        data = self._normalize_shape(data)

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

        if self._store:
            pass
            # todo: @nico should we not update self._data?
            # but we need to keep the offset into account.

        self._pending_data.append((data, offset))

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
        size = np.prod(shape) if len(shape) > 0 else 1

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
        gl.glTexParameterf(self._target, gl.GL_TEXTURE_MIN_FILTER,
                           self._interpolation[0])
        gl.glTexParameterf(self._target, gl.GL_TEXTURE_MAG_FILTER,
                           self._interpolation[1])
        gl.glTexParameterf(self._target, gl.GL_TEXTURE_WRAP_S,
                           self._wrapping[0])
        gl.glTexParameterf(self._target, gl.GL_TEXTURE_WRAP_T,
                           self._wrapping[1])

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

        # We let base texture to handle all operations
        if self.base is not None:
            return

        # Resize if necessary
        if self._need_resize:
            self._resize()
            self._need_resize = False

        # Reparameterize if necessary
        if self._need_parameterization:
            self._parameterize()
            self._need_parameterization = False

        # Update pending data if necessary
        if self._pending_data:
            logger.debug("GPU: Updating texture (%d pending operation(s))" %
                         len(self._pending_data))
            self._update_data()

    def _deactivate(self):
        """ Deactivate texture on GPU """
        logger.debug("GPU: Deactivate texture")
        gl.glBindTexture(self._target, 0)

    # Taken from pygly
    def _get_alignment(self, width):
        """Determines a textures byte alignment.

        If the width isn't a power of 2
        we need to adjust the byte alignment of the image.
        The image height is unimportant

        www.opengl.org/wiki/Common_Mistakes#Texture_upload_and_pixel_reads
        """
        # we know the alignment is appropriate
        # if we can divide the width by the
        # alignment cleanly
        # valid alignments are 1,2,4 and 8
        # put 4 first, since it's the default
        alignments = [4, 8, 2, 1]
        for alignment in alignments:
            if width % alignment == 0:
                return alignment

    def __repr__(self):
        return "<%s shape=%r dtype=%r format=%r target=%r at 0x%x>" % (
            self.__class__.__name__,
            self._shape, self._dtype, self._format, self._target,
            id(self))


# --------------------------------------------------------- Texture2D class ---
class Texture2D(BaseTexture):
    """ Two dimensional texture

    Parameters
    ----------

    data : ndarray
        Texture data (optional), shaped as HxW.
    shape : tuple of integers
        Texture shape (optional), with shape HxW.
    dtype : dtype
        Texture data type (optional)
    store : bool
        Specify whether this object stores a reference to the data,
        allowing the data to be updated regardless of striding. Note
        that modifying the data after passing it here might result in
        undesired behavior, unless a copy is given. Default True.
    format : str | ENUM
        The format of the texture: 'luminance', 'alpha', 'luminance_alpha',
        'rgb', or 'rgba' (or ENUMs GL_LUMINANCE, ALPHA, GL_LUMINANCE_ALPHA,
        or GL_RGB, GL_RGBA). If not given the format is chosen automatically
        based on the number of channels. When the data has one channel,
        'luminance' is assumed.
    """
    _ndim = 2

    def __init__(self, data=None, shape=None, dtype=None, store=True,
                 format=None, **kwargs):

        # We don't want these parameters to be seen from outside (because they
        # are only used internally)
        offset = kwargs.get("offset", None)
        base = kwargs.get("base", None)
        resizeable = kwargs.get("resizeable", True)
        BaseTexture.__init__(self, data=data, shape=shape, dtype=dtype,
                             base=base, resizeable=resizeable, store=store,
                             target=gl.GL_TEXTURE_2D, offset=offset,
                             format=format)

    @property
    def height(self):
        """ Texture height """
        return self._shape[0]

    @property
    def width(self):
        """ Texture width """
        return self._shape[1]

    @property
    def glsl_type(self):
        """ GLSL declaration strings required for a variable to hold this data.
        """
        return 'uniform', 'sampler2D'

    def _resize(self):
        """ Texture resize on GPU """
        logger.debug("GPU: Resizing texture(%sx%s)" %
                     (self.width, self.height))
        shape = self.height, self.width
        gl.glTexImage2D(self.target, 0, self._format, self._format,
                        self._gtype, shape)

    def _update_data(self):
        """ Texture update on GPU """
        # Update data
        while self._pending_data:
            data, offset = self._pending_data.pop(0)
            x = y = 0
            if offset is not None:
                y, x = offset[0], offset[1]
            # Set alignment (width is nbytes_per_pixel * npixels_per_line)
            alignment = self._get_alignment(data.shape[-2]*data.shape[-1])
            if alignment != 4:
                gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, alignment)
            gl.glTexSubImage2D(self.target, 0, x, y, self._format,
                               self._gtype, data)
            if alignment != 4:
                gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 4)


# --------------------------------------------------------- Texture3D class ---
class Texture3D(BaseTexture):
    """ Three dimensional texture

    Parameters
    ----------
    data : ndarray
        Texture data (optional), shaped as DxHxW.
    shape : tuple of integers
        Texture shape (optional) DxHxW.
    dtype : dtype
        Texture data type (optional)
    store : bool
        Specify whether this object stores a reference to the data,
        allowing the data to be updated regardless of striding. Note
        that modifying the data after passing it here might result in
        undesired behavior, unless a copy is given. Default True.
    format : str | ENUM
        The format of the texture: 'luminance', 'alpha', 'luminance_alpha',
        'rgb', or 'rgba' (or ENUMs GL_LUMINANCE, ALPHA, GL_LUMINANCE_ALPHA,
        or GL_RGB, GL_RGBA). If not given the format is chosen automatically
        based on the number of channels. When the data has one channel,
        'luminance' is assumed.
    """
    _ndim = 3

    def __init__(self, data=None, shape=None, dtype=None, store=True,
                 format=None, **kwargs):

        # Import from PyOpenGL
        _gl = _check_pyopengl_3D()

        # We don't want these parameters to be seen from outside (because they
        # are only used internally)
        offset = kwargs.get("offset", None)
        base = kwargs.get("base", None)
        resizeable = kwargs.get("resizeable", True)
        BaseTexture.__init__(self, data=data, shape=shape, dtype=dtype,
                             base=base, resizeable=resizeable, store=store,
                             target=_gl.GL_TEXTURE_3D, offset=offset,
                             format=format)

    @property
    def width(self):
        """ Texture width """
        return self._shape[2]

    @property
    def height(self):
        """ Texture height """
        return self._shape[1]

    @property
    def depth(self):
        """ Texture depth """
        return self._shape[0]

    @property
    def glsl_type(self):
        """ GLSL declaration strings required for a variable to hold this data.
        """
        return 'uniform', 'sampler3D'

    def _resize(self):
        """ Texture resize on GPU """
        logger.debug("GPU: Resizing texture(%sx%sx%s)" %
                     (self.depth, self.height, self.width))
        glTexImage3D(self.target, 0, self._format, self._format,
                     self._gtype, (self.depth, self.height, self.width))

    def _update_data(self):
        """ Texture update on GPU """
        while self._pending_data:
            data, offset = self._pending_data.pop(0)
            z = y = x = 0
            if offset is not None:
                z, y, x = offset[0], offset[1], offset[2]
            # Set alignment (width is nbytes_per_pixel * npixels_per_line)
            alignment = self._get_alignment(data.shape[-3] *
                                            data.shape[-2] * data.shape[-1])
            if alignment != 4:
                gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, alignment)
            glTexSubImage3D(self.target, 0, x, y, z, self._format,
                            self._gtype, data)
            if alignment != 4:
                gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 4)


# ------------------------------------------------------ TextureAtlas class ---
class TextureAtlas(Texture2D):
    """Group multiple small data regions into a larger texture.

    The algorithm is based on the article by Jukka Jylänki : "A Thousand Ways
    to Pack the Bin - A Practical Approach to Two-Dimensional Rectangle Bin
    Packing", February 27, 2010. More precisely, this is an implementation of
    the Skyline Bottom-Left algorithm based on C++ sources provided by Jukka
    Jylänki at: http://clb.demon.fi/files/RectangleBinPack/.

    Parameters
    ----------
    shape : tuple of int
        Texture width and height (optional).

    Notes
    -----
    This creates a 2D texture that holds 1D float32 data.
    An example of simple access:

        >>> atlas = TextureAtlas()
        >>> bounds = atlas.get_free_region(20, 30)
        >>> atlas.set_region(bounds, np.random.rand(20, 30).T)
    """
    def __init__(self, shape=(1024, 1024)):
        shape = np.array(shape, int)
        assert shape.ndim == 1 and shape.size == 2
        shape = tuple(2 ** (np.log2(shape) + 0.5).astype(int)) + (3,)
        self._atlas_nodes = [(0, 0, shape[1])]
        data = np.zeros(shape, np.float32)
        super(TextureAtlas, self).__init__(data)
        self.interpolation = 'linear'
        self.wrapping = 'clamp_to_edge'

    def get_free_region(self, width, height):
        """Get a free region of given size and allocate it

        Parameters
        ----------
        width : int
            Width of region to allocate
        height : int
            Height of region to allocate

        Returns
        -------
        bounds : tuple | None
            A newly allocated region as (x, y, w, h) or None
            (if failed).
        """
        best_height = best_width = np.inf
        best_index = -1
        for i in range(len(self._atlas_nodes)):
            y = self._fit(i, width, height)
            if y >= 0:
                node = self._atlas_nodes[i]
                if (y+height < best_height or
                        (y+height == best_height and node[2] < best_width)):
                    best_height = y+height
                    best_index = i
                    best_width = node[2]
                    region = node[0], y, width, height
        if best_index == -1:
            return None

        node = region[0], region[1] + height, width
        self._atlas_nodes.insert(best_index, node)
        i = best_index+1
        while i < len(self._atlas_nodes):
            node = self._atlas_nodes[i]
            prev_node = self._atlas_nodes[i-1]
            if node[0] < prev_node[0]+prev_node[2]:
                shrink = prev_node[0]+prev_node[2] - node[0]
                x, y, w = self._atlas_nodes[i]
                self._atlas_nodes[i] = x+shrink, y, w-shrink
                if self._atlas_nodes[i][2] <= 0:
                    del self._atlas_nodes[i]
                    i -= 1
                else:
                    break
            else:
                break
            i += 1

        # Merge nodes
        i = 0
        while i < len(self._atlas_nodes)-1:
            node = self._atlas_nodes[i]
            next_node = self._atlas_nodes[i+1]
            if node[1] == next_node[1]:
                self._atlas_nodes[i] = node[0], node[1], node[2]+next_node[2]
                del self._atlas_nodes[i+1]
            else:
                i += 1

        return region

    def _fit(self, index, width, height):
        """Test if region (width, height) fit into self._atlas_nodes[index]"""
        node = self._atlas_nodes[index]
        x, y = node[0], node[1]
        width_left = width
        if x+width > self.shape[1]:
            return -1
        i = index
        while width_left > 0:
            node = self._atlas_nodes[i]
            y = max(y, node[1])
            if y+height > self.shape[0]:
                return -1
            width_left -= node[2]
            i += 1
        return y
