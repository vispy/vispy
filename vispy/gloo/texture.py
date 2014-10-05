# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np

from . import gl
from .globject import GLObject
from .wrappers import _check_conversion

GL_SAMPLER_3D = gl.Enum('GL_SAMPLER_3D', 35679)  # needed by Program


def _check_value(value, valid_dict, numel=2):
    """Helper for checking interpolation and wrapping"""
    if not isinstance(value, (tuple, list)):
        value = [value] * numel
    if len(value) != numel:
        raise ValueError('value must be a single value, or a %i-element list' %
                         numel)
    return tuple(_check_conversion(v, valid_dict) for v in value)


# ----------------------------------------------------------- Texture class ---
class BaseTexture(GLObject):
    """
    A Texture is used to represent a topological set of scalar values.

    Parameters
    ----------
    data : ndarray
        Texture data (optional)
    shape : tuple of integers
        Texture shape (optional)
    format : str | enum
        See resize.
    resizeable : bool
        Indicates whether texture can be resized. Default True.
    interpolation : str
        Interpolation mode, must be one of: 'nearest', 'linear'. 
        Default 'nearest'.
    wrapping : str
        Wrapping mode, must be one of: 'repeat', 'clamp_to_edge', 
        'mirrored_repeat'. Default 'clamp_to_edge'.
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

    def __init__(self, data=None, shape=None, format=None, resizeable=True,
                 interpolation=None, wrapping=None):
        GLObject.__init__(self)
        
        # Init shape and format
        self._shape = tuple([0 for i in range(self._ndim+1)])
        self._format = format
        
        # Init more (wrapping and interp are important to set to get an inage)
        self._resizeable = bool(resizeable)
        self.interpolation = interpolation or 'nearest'
        self.wrapping = wrapping or 'clamp_to_edge'
        
        # Set data or shape
        if data is not None:
            if shape is not None:
                raise ValueError('Texture needs data or shape, not both.')
            self.set_data(data)
        elif shape is not None:
            self.resize(shape, format)
        else:
            raise ValueError("Either data or shape must be given")
    
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
        """ Texture shape (last dimension indicates number of color channels)
        """
        return self._shape

    @property
    def format(self):
        """ The texture format (color channels).
        """
        return self._format
    
    @property
    def wrapping(self):
        """ Texture wrapping mode """
        value = self._wrapping
        return value[0] if all([v == value[0] for v in value]) else value

    @wrapping.setter
    def wrapping(self, value):
        valid_dict = {'repeat': gl.GL_REPEAT,
                      'clamp_to_edge': gl.GL_CLAMP_TO_EDGE,
                      'mirrored_repeat': gl.GL_MIRRORED_REPEAT}
        numel = 3 if isinstance(self, Texture3D) else 2
        self._wrapping = _check_value(value, valid_dict, numel)
        self._context.glir.command('WRAPPING', self._id, self._wrapping)

    @property
    def interpolation(self):
        """ Texture interpolation for minification and magnification. """
        value = self._interpolation
        return value[0] if value[0] == value[1] else value

    @interpolation.setter
    def interpolation(self, value):
        valid_dict = {'nearest': gl.GL_NEAREST,
                      'linear': gl.GL_LINEAR}
        self._interpolation = _check_value(value, valid_dict)
        self._context.glir.command('INTERPOLATION', self._id, 
                                   *self._interpolation)
    
    def resize(self, shape, format=None):
        """ Set the texture size and format
        
        Parameters
        ----------
        shape : tuple of integers
            New texture shape in zyx order. Optionally, an extra dimention
            may be specified to indicate the number of color channels.
        format : str | enum
            The format of the texture: 'luminance', 'alpha',
            'luminance_alpha', 'rgb', or 'rgba' (or ENUMs GL_LUMINANCE,
            ALPHA, GL_LUMINANCE_ALPHA, or GL_RGB, GL_RGBA). If not given
            the format is chosen automatically based on the number of
            channels. When the data has one channel, 'luminance' is
            assumed.
        """
        shape = self._normalize_shape(shape)
        
        # Check
        if not self._resizeable:
            raise RuntimeError("Texture is not resizeable")
        if len(shape) != self._ndim + 1:
            raise ValueError("New shape has wrong number of dimensions")
        
        # Determine format
        ambiguous = gl.GL_ALPHA, gl.GL_LUMINANCE
        if format is None:
            format = self._formats.get(shape[-1], None)
            # Keep current format if format is ambiguous
            if format in ambiguous and self._format in ambiguous:
                format = self._format
        if format is None:
            raise ValueError("Cannot determine texture format from shape")
        if shape[-1] != self._inv_formats[format]:
            raise ValueError('Format does not match with given shape.')
        
        # Store and send GLIR command
        self._shape = shape
        self._format = format
        self._context.glir.command('SHAPE', self._id, 
                                   self._shape, self._format)

    def set_data(self, data, offset=None, copy=False):
        """ Set texture data

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
        
        # Copy if needed, check/normalize shape
        data = np.array(data, copy=copy)
        data = self._normalize_shape(data)

        # Check data has the right shape
        if len(data.shape) != self._ndim + 1:
            raise ValueError("Data has wrong shape")

        # Maybe resize to purge DATA commands?
        if offset is None:
            self.resize(data.shape)
        elif all([i == 0 for i in offset]) and data.shape == self.shape:
            self.resize(data.shape)
        
        # Convert offset to something usable
        offset = offset or tuple([0 for i in range(self._ndim)])
        assert len(offset) == self._ndim
        
        # Check if data fits
        for i in range(len(data.shape)-1):
            if offset[i] + data.shape[i] > self.shape[i]:
                raise ValueError("Data is too large")
        
        # Send GLIR command
        self._context.glir.command('DATA', self._id, offset, data)
    
    def __setitem__(self, key, data):
        """ x.__getitem__(y) <==> x[y] """
        
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
        
        # Make sure data is an array
        if not isinstance(data, np.ndarray):
            data = np.array(data, copy=False)
        # Make sure data is big enough
        if data.size != size:
            data = np.resize(data, size).reshape(shape)

        # Set data (deferred)
        self.set_data(data=data, offset=offset, copy=False)
    
    def _create(self):
        pass

    def _delete(self):
        pass

    def _activate(self):
        """ Activate texture on GPU """
        return

    def _deactivate(self):
        """ Deactivate texture on GPU """
        pass

    def __repr__(self):
        return "<%s shape=%r format=%r at 0x%x>" % (
            self.__class__.__name__, self._shape, self._format, id(self))


# --------------------------------------------------------- Texture2D class ---
class Texture2D(BaseTexture):
    """ Two dimensional texture

    Parameters
    ----------

    data : ndarray
        Texture data (optional), shaped as HxW.
    shape : tuple of integers
        Texture shape (optional), with shape HxW.
    format : str | ENUM
        The format of the texture: 'luminance', 'alpha', 'luminance_alpha',
        'rgb', or 'rgba' (or ENUMs GL_LUMINANCE, ALPHA, GL_LUMINANCE_ALPHA,
        or GL_RGB, GL_RGBA). If not given the format is chosen automatically
        based on the number of channels. When the data has one channel,
        'luminance' is assumed.
    """
    _ndim = 2
    _GLIR_TYPE = 'Texture2D'
    
    def __init__(self, data=None, shape=None, format=None, **kwargs):
        BaseTexture.__init__(self, data, shape, format, **kwargs)

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


# --------------------------------------------------------- Texture3D class ---
class Texture3D(BaseTexture):
    """ Three dimensional texture

    Parameters
    ----------
    data : ndarray
        Texture data (optional), shaped as DxHxW.
    shape : tuple of integers
        Texture shape (optional) DxHxW.
    format : str | ENUM
        The format of the texture: 'luminance', 'alpha', 'luminance_alpha',
        'rgb', or 'rgba' (or ENUMs GL_LUMINANCE, ALPHA, GL_LUMINANCE_ALPHA,
        or GL_RGB, GL_RGBA). If not given the format is chosen automatically
        based on the number of channels. When the data has one channel,
        'luminance' is assumed.
    """
    _ndim = 3
    _GLIR_TYPE = 'Texture3D'
    
    def __init__(self, data=None, shape=None, format=None, **kwargs):
        BaseTexture.__init__(self, data, shape, format, **kwargs)

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
