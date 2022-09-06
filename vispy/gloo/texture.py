# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import math

import numpy as np
import warnings

from .globject import GLObject
from .util import check_enum


def get_dtype_limits(dtype):
    if np.issubdtype(dtype, np.floating):
        info = np.finfo(dtype)
    else:
        info = np.iinfo(dtype)
    return info.min, info.max


def convert_dtype_and_clip(data, dtype, copy=False):
    """
    cast dtype to a new one, but first clip data to the new dtype's limits if needed
    """
    old_min, old_max = get_dtype_limits(data.dtype)
    new_min, new_max = get_dtype_limits(dtype)
    if new_max >= old_max and new_min <= old_min:
        # no need to clip
        return np.array(data, dtype=dtype, copy=copy)
    else:
        # to reduce copying, we clip into a pre-generated array of the right dtype
        new_data = np.empty_like(data, dtype=dtype)
        np.clip(data, new_min, new_max, out=new_data)
        return new_data


def downcast_to_32bit_if_needed(data, copy=False):
    """Downcast to 32bit dtype if necessary."""
    dtype = np.dtype(data.dtype)
    if dtype.itemsize > 4:
        warnings.warn(
            f"GPUs can't support dtypes bigger than 32-bit, but got '{dtype}'. "
            "Precision will be lost due to downcasting to 32-bit."
        )

    size = min(dtype.itemsize, 4)
    kind = dtype.kind

    new_dtype = np.dtype(f'{kind}{size}')
    return convert_dtype_and_clip(data, new_dtype, copy=copy)


class BaseTexture(GLObject):
    """
    A Texture is used to represent a topological set of scalar values.

    Parameters
    ----------
    data : ndarray | tuple | None
        Texture data in the form of a numpy array (or something that
        can be turned into one). A tuple with the shape of the texture
        can also be given.
    format : str | enum | None
        The format of the texture: 'luminance', 'alpha',
        'luminance_alpha', 'rgb', or 'rgba'. If not given the format
        is chosen automatically based on the number of channels.
        When the data has one channel, 'luminance' is assumed.
    resizable : bool
        Indicates whether texture can be resized. Default True.
    interpolation : str | None
        Interpolation mode, must be one of: 'nearest', 'linear'.
        Default 'nearest'.
    wrapping : str | None
        Wrapping mode, must be one of: 'repeat', 'clamp_to_edge',
        'mirrored_repeat'. Default 'clamp_to_edge'.
    shape : tuple | None
        Optional. A tuple with the shape of the texture. If ``data``
        is also a tuple, it will override the value of ``shape``.
    internalformat : str | None
        Internal format to use.
    resizeable : None
        Deprecated version of `resizable`.
    """

    _ndim = 2

    _formats = {
        1: 'luminance',  # or alpha, or red
        2: 'luminance_alpha',  # or rg
        3: 'rgb',
        4: 'rgba'
    }

    _inv_formats = {
        'luminance': 1,
        'alpha': 1,
        'red': 1,
        'luminance_alpha': 2,
        'rg': 2,
        'rgb': 3,
        'rgba': 4,
        'depth_component': 1,
    }

    # NOTE: non-normalized formats ending with 'i' and 'ui' are currently
    #   disabled as they don't work with the current VisPy implementation.
    #   Attempting to use them along with the additional enums defined in
    #   vispy/gloo/glir.py produces an invalid operation from OpenGL.
    _inv_internalformats = dict([
        (base + suffix, channels)
        for base, channels in [('r', 1), ('rg', 2), ('rgb', 3), ('rgba', 4)]
        for suffix in ['8', '16', '16f', '32f']  # , '8i', '8ui', '32i', '32ui']
    ] + [
        ('luminance', 1),
        ('alpha', 1),
        ('red', 1),
        ('luminance_alpha', 2),
        ('rg', 2),
        ('rgb', 3),
        ('rgba', 4),
        ('depth_component', 1),
    ])

    def __init__(self, data=None, format=None, resizable=True,
                 interpolation=None, wrapping=None, shape=None,
                 internalformat=None, resizeable=None):
        GLObject.__init__(self)
        if resizeable is not None:
            resizable = resizeable
            warnings.warn(
                "resizeable has been deprecated in favor of "
                "resizable and will be removed next release",
                DeprecationWarning,
                stacklevel=2,
            )

        # Init shape and format
        self._resizable = True  # at least while we're in init
        self._shape = tuple([0 for i in range(self._ndim+1)])
        self._format = format
        self._internalformat = internalformat

        # Set texture parameters (before setting data)
        self.interpolation = interpolation or 'nearest'
        self.wrapping = wrapping or 'clamp_to_edge'

        # Set data or shape (shape arg is for backward compat)
        if isinstance(data, tuple):
            shape, data = data, None
        if data is not None:
            if shape is not None:
                raise ValueError('Texture needs data or shape, not both.')
            data = np.array(data, copy=False)
            # So we can test the combination
            self._resize(data.shape, format, internalformat)
            self._set_data(data)
        elif shape is not None:
            self._resize(shape, format, internalformat)
        else:
            raise ValueError("Either data or shape must be given")

        # Set resizable (at end of init)
        self._resizable = bool(resizable)

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
        """Data shape (last dimension indicates number of color channels)"""
        return self._shape

    @property
    def format(self):
        """The texture format (color channels)."""
        return self._format

    @property
    def internalformat(self):
        """The texture internalformat."""
        return self._internalformat

    @property
    def wrapping(self):
        """Texture wrapping mode"""
        value = self._wrapping
        return value[0] if all([v == value[0] for v in value]) else value

    @wrapping.setter
    def wrapping(self, value):
        # Convert
        if isinstance(value, int) or isinstance(value, str):
            value = (value,) * self._ndim
        elif isinstance(value, (tuple, list)):
            if len(value) != self._ndim:
                raise ValueError('Texture wrapping needs 1 or %i values' %
                                 self._ndim)
        else:
            raise ValueError('Invalid value for wrapping: %r' % value)
        # Check and set
        valid = 'repeat', 'clamp_to_edge', 'mirrored_repeat'
        value = tuple([check_enum(value[i], 'tex wrapping', valid)
                       for i in range(self._ndim)])
        self._wrapping = value
        self._glir.command('WRAPPING', self._id, value)

    @property
    def interpolation(self):
        """Texture interpolation for minification and magnification."""
        value = self._interpolation
        return value[0] if value[0] == value[1] else value

    @interpolation.setter
    def interpolation(self, value):
        # Convert
        if isinstance(value, int) or isinstance(value, str):
            value = (value,) * 2
        elif isinstance(value, (tuple, list)):
            if len(value) != 2:
                raise ValueError('Texture interpolation needs 1 or 2 values')
        else:
            raise ValueError('Invalid value for interpolation: %r' % value)
        # Check and set
        valid = 'nearest', 'linear'
        value = (check_enum(value[0], 'tex interpolation', valid),
                 check_enum(value[1], 'tex interpolation', valid))
        self._interpolation = value
        self._glir.command('INTERPOLATION', self._id, *value)

    def resize(self, shape, format=None, internalformat=None):
        """Set the texture size and format

        Parameters
        ----------
        shape : tuple of integers
            New texture shape in zyx order. Optionally, an extra dimention
            may be specified to indicate the number of color channels.
        format : str | enum | None
            The format of the texture: 'luminance', 'alpha',
            'luminance_alpha', 'rgb', or 'rgba'. If not given the format
            is chosen automatically based on the number of channels.
            When the data has one channel, 'luminance' is assumed.
        internalformat : str | enum | None
            The internal (storage) format of the texture: 'luminance',
            'alpha', 'r8', 'r16', 'r16f', 'r32f'; 'luminance_alpha',
            'rg8', 'rg16', 'rg16f', 'rg32f'; 'rgb', 'rgb8', 'rgb16',
            'rgb16f', 'rgb32f'; 'rgba', 'rgba8', 'rgba16', 'rgba16f',
            'rgba32f'.  If None, the internalformat is chosen
            automatically based on the number of channels.  This is a
            hint which may be ignored by the OpenGL implementation.
        """
        return self._resize(shape, format, internalformat)

    def _check_format_change(self, format, num_channels):
        # Determine format
        if format is None:
            format = self._formats[num_channels]
            # Keep current format if channels match
            if self._format and \
                    self._inv_formats[self._format] == self._inv_formats[format]:
                format = self._format
        else:
            format = check_enum(format)

        if format not in self._inv_formats:
            raise ValueError('Invalid texture format: %r.' % format)
        elif num_channels != self._inv_formats[format]:
            raise ValueError('Format does not match with given shape. '
                             '(format expects %d elements, data has %d)' %
                             (self._inv_formats[format], num_channels))
        return format

    def _check_internalformat_change(self, internalformat, num_channels):
        if internalformat is None:
            # Keep current internalformat if channels match
            if self._internalformat and \
               self._inv_internalformats[self._internalformat] == num_channels:
                internalformat = self._internalformat
        else:
            internalformat = check_enum(internalformat)

        if internalformat is None:
            pass
        elif internalformat not in self._inv_internalformats:
            raise ValueError(
                'Invalid texture internalformat: %r. Allowed formats: %r'
                % (internalformat, self._inv_internalformats)
            )
        elif num_channels != self._inv_internalformats[internalformat]:
            raise ValueError('Internalformat does not match with given shape.')
        return internalformat

    def _resize(self, shape, format=None, internalformat=None):
        """Internal method for resize."""
        shape = self._normalize_shape(shape)

        # Check
        if not self._resizable:
            raise RuntimeError("Texture is not resizable")

        format = self._check_format_change(format, shape[-1])
        internalformat = self._check_internalformat_change(internalformat, shape[-1])

        # Store and send GLIR command
        self._shape = shape
        self._format = format
        self._internalformat = internalformat
        self._glir.command('SIZE', self._id, self._shape, self._format,
                           self._internalformat)

    def set_data(self, data, offset=None, copy=False):
        """Set texture data

        Parameters
        ----------
        data : ndarray
            Data to be uploaded
        offset: int | tuple of ints
            Offset in texture where to start copying data
        copy: bool
            Since the operation is deferred, data may change before
            data is actually uploaded to GPU memory. Asking explicitly
            for a copy will prevent this behavior.

        Notes
        -----
        This operation implicitly resizes the texture to the shape of
        the data if given offset is None.
        """
        return self._set_data(data, offset, copy)

    def _set_data(self, data, offset=None, copy=False):
        """Internal method for set_data."""
        # Copy if needed, check/normalize shape
        data = downcast_to_32bit_if_needed(data, copy=copy)
        data = self._normalize_shape(data)

        # Maybe resize to purge DATA commands?
        if offset is None:
            self._resize(data.shape)
        elif all([i == 0 for i in offset]) and data.shape == self._shape:
            self._resize(data.shape)

        # Convert offset to something usable
        offset = offset or tuple([0 for i in range(self._ndim)])
        assert len(offset) == self._ndim

        # Check if data fits
        for i in range(len(data.shape)-1):
            if offset[i] + data.shape[i] > self._shape[i]:
                raise ValueError("Data is too large")

        # Send GLIR command
        self._glir.command('DATA', self._id, offset, data)

    def __setitem__(self, key, data):
        """x.__getitem__(y) <==> x[y]"""
        # Make sure key is a tuple
        if isinstance(key, (int, slice)) or key == Ellipsis:
            key = (key,)

        # Default is to access the whole texture
        shape = self._shape
        slices = [slice(0, shape[i]) for i in range(len(shape))]

        # Check last key/Ellipsis to decide on the order
        keys = key[::+1]
        dims = range(0, len(key))
        if key[0] == Ellipsis:
            keys = key[::-1]
            dims = range(len(self._shape) - 1,
                         len(self._shape) - 1 - len(keys), -1)

        # Find exact range for each key
        for k, dim in zip(keys, dims):
            size = self._shape[dim]
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
                    raise IndexError("Cannot access non-contiguous data")
                if stop < start:
                    start, stop = stop, start
                slices[dim] = slice(start, stop, step)
            elif k == Ellipsis:
                pass
            else:
                raise TypeError("Texture indices must be integers")

        offset = tuple([s.start for s in slices])[:self._ndim]
        shape = tuple([s.stop - s.start for s in slices])
        size = np.prod(shape) if len(shape) > 0 else 1

        # Make sure data is an array
        if not isinstance(data, np.ndarray):
            data = np.array(data, copy=False)
        # Make sure data is big enough
        if data.shape != shape:
            data = np.resize(data, shape)

        # Set data (deferred)
        self._set_data(data=data, offset=offset, copy=False)

    def __repr__(self):
        return "<%s shape=%r format=%r at 0x%x>" % (
            self.__class__.__name__, self._shape, self._format, id(self))


# --------------------------------------------------------- Texture1D class ---
class Texture1D(BaseTexture):
    """One dimensional texture

    Parameters
    ----------
    data : ndarray | tuple | None
        Texture data in the form of a numpy array (or something that
        can be turned into one). A tuple with the shape of the texture
        can also be given.
    format : str | enum | None
        The format of the texture: 'luminance', 'alpha',
        'luminance_alpha', 'rgb', or 'rgba'. If not given the format
        is chosen automatically based on the number of channels.
        When the data has one channel, 'luminance' is assumed.
    resizable : bool
        Indicates whether texture can be resized. Default True.
    interpolation : str | None
        Interpolation mode, must be one of: 'nearest', 'linear'.
        Default 'nearest'.
    wrapping : str | None
        Wrapping mode, must be one of: 'repeat', 'clamp_to_edge',
        'mirrored_repeat'. Default 'clamp_to_edge'.
    shape : tuple | None
        Optional. A tuple with the shape of the texture. If ``data``
        is also a tuple, it will override the value of ``shape``.
    internalformat : str | None
        Internal format to use.
    resizeable : None
        Deprecated version of `resizable`.
    """

    _ndim = 1
    _GLIR_TYPE = 'Texture1D'

    def __init__(self, data=None, format=None, resizable=True,
                 interpolation=None, wrapping=None, shape=None,
                 internalformat=None, resizeable=None):
        BaseTexture.__init__(self, data, format, resizable, interpolation,
                             wrapping, shape, internalformat, resizeable)

    @property
    def width(self):
        """Texture width"""
        return self._shape[0]

    @property
    def glsl_type(self):
        """GLSL declaration strings required for a variable to hold this data."""
        return 'uniform', 'sampler1D'

    @property
    def glsl_sampler_type(self):
        """GLSL type of the sampler."""
        return 'sampler1D'

    @property
    def glsl_sample(self):
        """GLSL function that samples the texture."""
        return 'texture1D'


# --------------------------------------------------------- Texture2D class ---
class Texture2D(BaseTexture):
    """Two dimensional texture

    Parameters
    ----------
    data : ndarray
        Texture data shaped as W, or a tuple with the shape for
        the texture (W).
    format : str | enum | None
        The format of the texture: 'luminance', 'alpha',
        'luminance_alpha', 'rgb', or 'rgba'. If not given the format
        is chosen automatically based on the number of channels.
        When the data has one channel, 'luminance' is assumed.
    resizable : bool
        Indicates whether texture can be resized. Default True.
    interpolation : str
        Interpolation mode, must be one of: 'nearest', 'linear'.
        Default 'nearest'.
    wrapping : str
        Wrapping mode, must be one of: 'repeat', 'clamp_to_edge',
        'mirrored_repeat'. Default 'clamp_to_edge'.
    shape : tuple
        Optional. A tuple with the shape HxW. If ``data``
        is also a tuple, it will override the value of ``shape``.
    internalformat : str | None
        Internal format to use.
    resizeable : None
        Deprecated version of `resizable`.
    """

    _ndim = 2
    _GLIR_TYPE = 'Texture2D'

    def __init__(self, data=None, format=None, resizable=True,
                 interpolation=None, wrapping=None, shape=None,
                 internalformat=None, resizeable=None):
        BaseTexture.__init__(self, data, format, resizable, interpolation,
                             wrapping, shape, internalformat, resizeable)

    @property
    def height(self):
        """Texture height"""
        return self._shape[0]

    @property
    def width(self):
        """Texture width"""
        return self._shape[1]

    @property
    def glsl_type(self):
        """GLSL declaration strings required for a variable to hold this data."""
        return 'uniform', 'sampler2D'

    @property
    def glsl_sampler_type(self):
        """GLSL type of the sampler."""
        return 'sampler2D'

    @property
    def glsl_sample(self):
        """GLSL function that samples the texture."""
        return 'texture2D'


# --------------------------------------------------------- Texture3D class ---
class Texture3D(BaseTexture):
    """Three dimensional texture

    Parameters
    ----------
    data : ndarray | tuple | None
        Texture data in the form of a numpy array (or something that
        can be turned into one). A tuple with the shape of the texture
        can also be given.
    format : str | enum | None
        The format of the texture: 'luminance', 'alpha',
        'luminance_alpha', 'rgb', or 'rgba'. If not given the format
        is chosen automatically based on the number of channels.
        When the data has one channel, 'luminance' is assumed.
    resizable : bool
        Indicates whether texture can be resized. Default True.
    interpolation : str | None
        Interpolation mode, must be one of: 'nearest', 'linear'.
        Default 'nearest'.
    wrapping : str | None
        Wrapping mode, must be one of: 'repeat', 'clamp_to_edge',
        'mirrored_repeat'. Default 'clamp_to_edge'.
    shape : tuple | None
        Optional. A tuple with the shape of the texture. If ``data``
        is also a tuple, it will override the value of ``shape``.
    internalformat : str | None
        Internal format to use.
    resizeable : None
        Deprecated version of `resizable`.
    """

    _ndim = 3
    _GLIR_TYPE = 'Texture3D'

    def __init__(self, data=None, format=None, resizable=True,
                 interpolation=None, wrapping=None, shape=None,
                 internalformat=None, resizeable=None):
        BaseTexture.__init__(self, data, format, resizable, interpolation,
                             wrapping, shape, internalformat, resizeable)

    @property
    def width(self):
        """Texture width"""
        return self._shape[2]

    @property
    def height(self):
        """Texture height"""
        return self._shape[1]

    @property
    def depth(self):
        """Texture depth"""
        return self._shape[0]

    @property
    def glsl_type(self):
        """GLSL declaration strings required for a variable to hold this data."""
        return 'uniform', 'sampler3D'

    @property
    def glsl_sampler_type(self):
        """GLSL type of the sampler."""
        return 'sampler3D'

    @property
    def glsl_sample(self):
        """GLSL function that samples the texture."""
        return 'texture3D'


# --------------------------------------------------------- TextureCube class ---
class TextureCube(BaseTexture):
    """Texture Cube

    Parameters
    ----------
    data : ndarray | tuple | None
        Texture data in the form of a numpy array (or something that
        can be turned into one). A tuple with the shape of the texture
        can also be given.
    format : str | enum | None
        The format of the texture: 'luminance', 'alpha',
        'luminance_alpha', 'rgb', or 'rgba'. If not given the format
        is chosen automatically based on the number of channels.
        When the data has one channel, 'luminance' is assumed.
    resizable : bool
        Indicates whether texture can be resized. Default True.
    interpolation : str | None
        Interpolation mode, must be one of: 'nearest', 'linear'.
        Default 'nearest'.
    wrapping : str | None
        Wrapping mode, must be one of: 'repeat', 'clamp_to_edge',
        'mirrored_repeat'. Default 'clamp_to_edge'.
    shape : tuple | None
        Optional. A tuple with the shape of the texture. If ``data``
        is also a tuple, it will override the value of ``shape``.
    internalformat : str | None
        Internal format to use.
    resizeable : None
        Deprecated version of `resizable`.
    """

    _ndim = 3
    _GLIR_TYPE = 'TextureCube'

    def __init__(self, data=None, format=None, resizable=True,
                 interpolation=None, wrapping=None, shape=None,
                 internalformat=None, resizeable=None):
        BaseTexture.__init__(self, data, format, resizable, interpolation,
                             wrapping, shape, internalformat, resizeable)
        if self._shape[0] != 6:
            raise ValueError("Texture cube require arrays first dimension to be 6 :"
                             " {} was given.".format(self._shape[0]))

    @property
    def height(self):
        """Texture height"""
        return self._shape[1]

    @property
    def width(self):
        """Texture width"""
        return self._shape[2]

    @property
    def depth(self):
        """Texture depth"""
        return self._shape[0]

    @property
    def glsl_type(self):
        """GLSL declaration strings required for a variable to hold this data."""
        return 'uniform', 'samplerCube'

    @property
    def glsl_sampler_type(self):
        """GLSL type of the sampler."""
        return 'samplerCube'

    @property
    def glsl_sample(self):
        """GLSL function that samples the texture."""
        return 'textureCube'


# ------------------------------------------------- TextureEmulated3D class ---
class TextureEmulated3D(Texture2D):
    """Two dimensional texture that is emulating a three dimensional texture

    Parameters
    ----------
    data : ndarray | tuple | None
        Texture data in the form of a numpy array (or something that
        can be turned into one). A tuple with the shape of the texture
        can also be given.
    format : str | enum | None
        The format of the texture: 'luminance', 'alpha',
        'luminance_alpha', 'rgb', or 'rgba'. If not given the format
        is chosen automatically based on the number of channels.
        When the data has one channel, 'luminance' is assumed.
    resizable : bool
        Indicates whether texture can be resized. Default True.
    interpolation : str | None
        Interpolation mode, must be one of: 'nearest', 'linear'.
        Default 'nearest'.
    wrapping : str | None
        Wrapping mode, must be one of: 'repeat', 'clamp_to_edge',
        'mirrored_repeat'. Default 'clamp_to_edge'.
    shape : tuple | None
        Optional. A tuple with the shape of the texture. If ``data``
        is also a tuple, it will override the value of ``shape``.
    internalformat : str | None
        Internal format to use.
    resizeable : None
        Deprecated version of `resizable`.
    """

    # TODO: does GL's nearest use floor or round?
    _glsl_sample_nearest = """
        vec4 sample(sampler2D tex, vec3 texcoord) {
            // Don't let adjacent frames be interpolated into this one
            texcoord.x = min(texcoord.x * $shape.x, $shape.x - 0.5);
            texcoord.x = max(0.5, texcoord.x) / $shape.x;
            texcoord.y = min(texcoord.y * $shape.y, $shape.y - 0.5);
            texcoord.y = max(0.5, texcoord.y) / $shape.y;

            float index = floor(texcoord.z * $shape.z);

            // Do a lookup in the 2D texture
            float u = (mod(index, $r) + texcoord.x) / $r;
            float v = (floor(index / $r) + texcoord.y) / $c;

            return texture2D(tex, vec2(u,v));
        }
    """

    _glsl_sample_linear = """
        vec4 sample(sampler2D tex, vec3 texcoord) {
            // Don't let adjacent frames be interpolated into this one
            texcoord.x = min(texcoord.x * $shape.x, $shape.x - 0.5);
            texcoord.x = max(0.5, texcoord.x) / $shape.x;
            texcoord.y = min(texcoord.y * $shape.y, $shape.y - 0.5);
            texcoord.y = max(0.5, texcoord.y) / $shape.y;

            float z = texcoord.z * $shape.z;
            float zindex1 = floor(z);
            float u1 = (mod(zindex1, $r) + texcoord.x) / $r;
            float v1 = (floor(zindex1 / $r) + texcoord.y) / $c;

            float zindex2 = zindex1 + 1.0;
            float u2 = (mod(zindex2, $r) + texcoord.x) / $r;
            float v2 = (floor(zindex2 / $r) + texcoord.y) / $c;

            vec4 s1 = texture2D(tex, vec2(u1, v1));
            vec4 s2 = texture2D(tex, vec2(u2, v2));

            return s1 * (zindex2 - z) + s2 * (z - zindex1);
        }
    """

    _gl_max_texture_size = 1024  # For now, we just set this manually

    def __init__(self, data=None, format=None, resizable=True,
                 interpolation=None, wrapping=None, shape=None,
                 internalformat=None, resizeable=None):
        from ..visuals.shaders import Function

        self._set_emulated_shape(data)
        Texture2D.__init__(self, self._normalize_emulated_shape(data),
                           format, resizable, interpolation, wrapping,
                           shape, internalformat, resizeable)
        if self.interpolation == 'nearest':
            self._glsl_sample = Function(self.__class__._glsl_sample_nearest)
        else:
            self._glsl_sample = Function(self.__class__._glsl_sample_linear)
        self._update_variables()

    def _set_emulated_shape(self, data_or_shape):
        if isinstance(data_or_shape, np.ndarray):
            self._emulated_shape = data_or_shape.shape
        else:
            assert isinstance(data_or_shape, tuple)
            self._emulated_shape = tuple(data_or_shape)

        depth, width = self._emulated_shape[0], self._emulated_shape[1]
        self._r = TextureEmulated3D._gl_max_texture_size // width
        self._c = depth // self._r
        if math.fmod(depth, self._r):
            self._c += 1

    def _normalize_emulated_shape(self, data_or_shape):
        if isinstance(data_or_shape, np.ndarray):
            new_shape = self._normalize_emulated_shape(data_or_shape.shape)
            new_data = np.empty(new_shape, dtype=data_or_shape.dtype)
            for j in range(self._c):
                for i in range(self._r):
                    i0, i1 = i * self.width, (i+1) * self.width
                    j0, j1 = j * self.height, (j+1) * self.height
                    k = j * self._r + i
                    if k >= self.depth:
                        break
                    new_data[j0:j1, i0:i1] = data_or_shape[k]

            return new_data

        assert isinstance(data_or_shape, tuple)
        return (self._c * self.height, self._r * self.width) + \
            data_or_shape[3:]

    def _update_variables(self):
        self._glsl_sample['shape'] = self.shape[:3][::-1]
        # On Windows with Python 2.7, self._c can end up being a long
        # integer because Numpy array shapes return long integers. This
        # causes issues when setting the gloo variables since these are
        # expected to be native ints, so we cast the integers to ints
        # to avoid this.
        # Newer GLSL compilers do not implicitly cast types so these integers
        # must be converted to floats lastly
        self._glsl_sample['c'] = float(int(self._c))
        self._glsl_sample['r'] = float(int(self._r))

    def set_data(self, data, offset=None, copy=False):
        """Set texture data

        Parameters
        ----------
        data : ndarray
            Data to be uploaded
        offset: int | tuple of ints
            Offset in texture where to start copying data
        copy: bool
            Since the operation is deferred, data may change before
            data is actually uploaded to GPU memory. Asking explicitly
            for a copy will prevent this behavior.

        Notes
        -----
        This operation implicitely resizes the texture to the shape of
        the data if given offset is None.
        """
        self._set_emulated_shape(data)
        Texture2D.set_data(self, self._normalize_emulated_shape(data),
                           offset, copy)
        self._update_variables()

    def resize(self, shape, format=None, internalformat=None):
        """Set the texture size and format

        Parameters
        ----------
        shape : tuple of integers
            New texture shape in zyx order. Optionally, an extra dimention
            may be specified to indicate the number of color channels.
        format : str | enum | None
            The format of the texture: 'luminance', 'alpha',
            'luminance_alpha', 'rgb', or 'rgba'. If not given the format
            is chosen automatically based on the number of channels.
            When the data has one channel, 'luminance' is assumed.
        internalformat : str | enum | None
            The internal (storage) format of the texture: 'luminance',
            'alpha', 'r8', 'r16', 'r16f', 'r32f'; 'luminance_alpha',
            'rg8', 'rg16', 'rg16f', 'rg32f'; 'rgb', 'rgb8', 'rgb16',
            'rgb16f', 'rgb32f'; 'rgba', 'rgba8', 'rgba16', 'rgba16f',
            'rgba32f'.  If None, the internalformat is chosen
            automatically based on the number of channels.  This is a
            hint which may be ignored by the OpenGL implementation.
        """
        self._set_emulated_shape(shape)
        Texture2D.resize(self, self._normalize_emulated_shape(shape),
                         format, internalformat)
        self._update_variables()

    @property
    def shape(self):
        """Data shape (last dimension indicates number of color channels)"""
        return self._emulated_shape

    @property
    def width(self):
        """Texture width"""
        return self._emulated_shape[2]

    @property
    def height(self):
        """Texture height"""
        return self._emulated_shape[1]

    @property
    def depth(self):
        """Texture depth"""
        return self._emulated_shape[0]

    @property
    def glsl_sample(self):
        """GLSL function that samples the texture."""
        return self._glsl_sample


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
        Texture shape (optional).
    dtype : numpy.dtype object
        Texture starting data type (default: float32)

    Notes
    -----
    This creates a 2D texture that holds 1D float32 data.
    An example of simple access:

        >>> atlas = TextureAtlas()
        >>> bounds = atlas.get_free_region(20, 30)
        >>> atlas.set_region(bounds, np.random.rand(20, 30).T)
    """

    def __init__(self, shape=(1024, 1024), dtype=np.float32):
        shape = np.array(shape, int)
        assert shape.ndim == 1 and shape.size == 2
        shape = tuple(2 ** (np.log2(shape) + 0.5).astype(int)) + (3,)
        self._atlas_nodes = [(0, 0, shape[1])]
        data = np.zeros(shape, dtype)
        super(TextureAtlas, self).__init__(data, interpolation='linear',
                                           wrapping='clamp_to_edge')

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
        if x+width > self._shape[1]:
            return -1
        i = index
        while width_left > 0:
            node = self._atlas_nodes[i]
            y = max(y, node[1])
            if y+height > self._shape[0]:
                return -1
            width_left -= node[2]
            i += 1
        return y
