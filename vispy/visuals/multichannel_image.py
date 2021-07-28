# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Image visual constructed from 3 separate image arrays."""

import warnings

import numpy as np
from ..gloo.texture import should_cast_to_f32
from ._scalable_textures import GPUScaledTexture2D
from .image import ImageVisual
from .shaders import Function, FunctionChain


class MultiChannelGPUScaledTexture2D:
    """Wrapper class around individual textures.

    This helper class allows for easier handling of multiple textures that
    represent individual R, G, and B channels of an image.

    """

    _singular_texture_class = GPUScaledTexture2D
    _ndim = 2

    def __init__(self, data, **texture_kwargs):
        # data to send to texture when not being used
        self._fill_arr = np.full((10, 10), np.float32(np.nan),
                                 dtype=np.float32)

        self.num_channels = len(data)
        data = [x if x is not None else self._fill_arr for x in data]
        self._textures = self._create_textures(self.num_channels, data,
                                               **texture_kwargs)

    def _create_textures(self, num_channels, data, **texture_kwargs):
        return [
            self._singular_texture_class(data[i], **texture_kwargs)
            for i in range(num_channels)
        ]

    @property
    def textures(self):
        return self._textures

    @property
    def clim(self):
        """Get color limits used when rendering the image (cmin, cmax)."""
        return tuple(t.clim for t in self._textures)

    def set_clim(self, clims):
        if isinstance(clims, str) or (len(clims) == 2 and not isinstance(clims[0], (tuple, list, str))):
            clims = [clims] * self.num_channels

        need_tex_upload = False
        for tex, clim in zip(self._textures, clims):
            if clim is None or clim[0] is None:
                clim = (0, 0)  # let VisPy decide what to do with unusable clims
            if tex.set_clim(clim):
                need_tex_upload = True
        return need_tex_upload

    @property
    def clim_normalized(self):
        return tuple(tex.clim_normalized for tex in self._textures)

    @property
    def internalformat(self):
        return self._textures[0].internalformat

    @internalformat.setter
    def internalformat(self, value):
        for tex in self._textures:
            tex.internalformat = value

    @property
    def interpolation(self):
        return self._textures[0].interpolation

    @interpolation.setter
    def interpolation(self, value):
        for tex in self._textures:
            tex.interpolation = value

    def check_data_format(self, data_arrays):
        if len(data_arrays) != self.num_channels:
            raise ValueError(f"Expected {self.num_channels} number of channels, got {len(data_arrays)}.")
        for tex, data in zip(self._textures, data_arrays):
            if data is not None:
                tex.check_data_format(data)

    def scale_and_set_data(self, data, offset=None, copy=False):
        """Scale and set data for one or all sub-textures.

        Parameters
        ----------
        data : list | ndarray
            Texture data in the form of a numpy array or as a list of numpy
            arrays. If a list is provided then it must be the same length as
            ``num_channels`` for this texture. If a numpy array is provided
            then ``offset`` should also be provided with the first value
            representing which sub-texture to update. For example,
            ``offset=(1, 0, 0)`` would update the entire the second (index 1)
            sub-texture with an offset of ``(0, 0)``. The list can also contain
            ``None`` to not update the sub-texture at that index.
        offset: tuple | None
            Offset into the texture where to write the provided data. If
            ``None`` then data will be written with no offset (0). If
            provided as a 2-element tuple then that offset will be used
            for all sub-textures. If a 3-element tuple then the first offset
            index represents the sub-texture to update.

        """
        is_multi = isinstance(data, (list, tuple))
        index_provided = offset is not None and len(offset) == self._ndim + 1
        if not is_multi and not index_provided:
            raise ValueError("Setting texture data for a single sub-texture "
                             "requires 'offset' to be passed with the first "
                             "element specifying the sub-texture index.")
        elif is_multi and index_provided:
            warnings.warn("Multiple texture arrays were passed, but so was "
                          "sub-texture index in 'offset'. Ignoring that index.", UserWarning)
            offset = offset[1:]
        if is_multi and len(data) != self.num_channels:
            raise ValueError("Multiple provided arrays must match number of channels. "
                             f"Got {len(data)}, expected {self.num_channels}.")

        if offset is not None and len(offset) == self._ndim + 1:
            tex_indexes = offset[:1]
            offset = offset[1:]
            data = [data]
        else:
            tex_indexes = range(self.num_channels)

        for tex_idx, _data in zip(tex_indexes, data):
            if _data is None:
                _data = self._fill_arr
            self._textures[tex_idx].scale_and_set_data(_data, offset=offset, copy=copy)


_rgb_texture_lookup = """
    vec4 texture_lookup(vec2 texcoord) {
        if(texcoord.x < 0.0 || texcoord.x > 1.0 ||
        texcoord.y < 0.0 || texcoord.y > 1.0) {
            discard;
        }
        vec4 val;
        val.r = texture2D($texture_r, texcoord).r;
        val.g = texture2D($texture_g, texcoord).r;
        val.b = texture2D($texture_b, texcoord).r;
        val.a = 1.0;
        return val;
    }"""

_apply_clim = """
    vec4 apply_clim(vec4 color) {
        // If all the pixels are NaN make it completely transparent
        // http://stackoverflow.com/questions/11810158/how-to-deal-with-nan-or-inf-in-opengl-es-2-0-shaders
        if (
            !(color.r <= 0.0 || 0.0 <= color.r) &&
            !(color.g <= 0.0 || 0.0 <= color.g) &&
            !(color.b <= 0.0 || 0.0 <= color.b)) {
            color.a = 0;
        }
        
        // if color is NaN, set to minimum possible value
        color.r = !(color.r <= 0.0 || 0.0 <= color.r) ? min($clim_r.x, $clim_r.y) : color.r;
        color.g = !(color.g <= 0.0 || 0.0 <= color.g) ? min($clim_g.x, $clim_g.y) : color.g;
        color.b = !(color.b <= 0.0 || 0.0 <= color.b) ? min($clim_b.x, $clim_b.y) : color.b;
        // clamp data to minimum and maximum of clims
        color.r = clamp(color.r, min($clim_r.x, $clim_r.y), max($clim_r.x, $clim_r.y));
        color.g = clamp(color.g, min($clim_g.x, $clim_g.y), max($clim_g.x, $clim_g.y));
        color.b = clamp(color.b, min($clim_b.x, $clim_b.y), max($clim_b.x, $clim_b.y));
        // linearly scale data between clims
        color.r = (color.r - $clim_r.x) / ($clim_r.y - $clim_r.x);
        color.g = (color.g - $clim_g.x) / ($clim_g.y - $clim_g.x);
        color.b = (color.b - $clim_b.x) / ($clim_b.y - $clim_b.x);
        return max(color, 0);
    }
"""

_apply_gamma = """
    vec4 apply_gamma(vec4 color) {
        color.r = pow(color.r, $gamma_r);
        color.g = pow(color.g, $gamma_g);
        color.b = pow(color.b, $gamma_b);
        return color;
    }
"""

_null_color_transform = 'vec4 pass(vec4 color) { return color; }'


class MultiChannelImageVisual(ImageVisual):
    """Visual subclass displaying an image from three separate arrays.

    Note this Visual uses only GPU scaling, unlike the ImageVisual base
    class which allows for CPU or GPU scaling.

    Parameters
    ----------
    data : list
        A 3-element list of numpy arrays with 2 dimensons where the
        arrays are sorted by (R, G, B) order. These will be put together
        to make an RGB image. The list can contain ``None`` meaning there
        is no value for this channel currently, but it may be filled in
        later. In this case the underlying GPU storage is still allocated,
        but pre-filled with NaNs. Note that each channel may have different
        shapes.
    cmap : str | Colormap
        Unused by this Visual, but is still provided to the ImageVisual base
        class.
    clim : str | tuple | list | None
        Limits of each RGB data array. If provided as a string it must be
        "auto" and the limits will be computed on the fly. If a 2-element
        tuple then it will be considered the color limits for all channel
        arrays. If provided as a 3-element list of 2-element tuples then
        they represent the color limits of each channel array.
    gamma : float | list
        Gamma to use during colormap lookup.  Final value will be computed
        ``val**gamma` for each RGB channel array. If provided as a float then
        it will be used for each channel. If provided as a 3-element tuple
        then each value is used for the separate channel arrays. Default is
        1.0 for each channel.
    **kwargs : dict
        Keyword arguments to pass to :class:`~vispy.visuals.ImageVisual`. Note
        that this Visual does not allow for ``texture_format`` to be specified
        and is hardcoded to ``r32f`` internal texture format.

    """

    VERTEX_SHADER = ImageVisual.VERTEX_SHADER
    FRAGMENT_SHADER = ImageVisual.FRAGMENT_SHADER

    def __init__(self, data_arrays, clim='auto', gamma=1.0, **kwargs):
        if kwargs.get("texture_format") is not None:
            raise ValueError("'texture_format' can't be specified with the "
                             "'MultiChannelImageVisual'.")
        kwargs["texture_format"] = "R32F"
        if kwargs.get("cmap") is not None:
            raise ValueError("'cmap' can't be specified with the"
                             "'MultiChannelImageVisual'.")
        kwargs["cmap"] = None
        self.num_channels = len(data_arrays)
        self._verify_num_channels()
        super().__init__(data_arrays, clim=clim, gamma=gamma, **kwargs)

    def _init_texture(self, data_arrays, texture_format):
        if self._interpolation == 'bilinear':
            texture_interpolation = 'linear'
        else:
            texture_interpolation = 'nearest'

        tex = MultiChannelGPUScaledTexture2D(
            data_arrays,
            internalformat=texture_format,
            format="LUMINANCE",
            interpolation=texture_interpolation,
        )
        return tex

    def _verify_num_channels(self):
        if self.num_channels < 2:
            raise ValueError("You must provide 2 or more channels as input.")
        if self.num_channels > 4:
            raise ValueError("Can not handle more than 4 elements.")

    def _get_shapes(self, data_arrays):
        shapes = [x.shape for x in data_arrays if x is not None]
        if not shapes:
            raise ValueError("List of data arrays must contain at least one "
                             "numpy array.")
        return shapes

    def _get_min_shape(self, data_arrays):
        return min(self._get_shapes(data_arrays))

    def _get_max_shape(self, data_arrays):
        return max(self._get_shapes(data_arrays))

    @property
    def size(self):
        """Get size of the image (width, height)."""
        return self._get_max_shape(self._data)[::-1]

    @property
    def clim(self):
        """Get color limits used when rendering the image (cmin, cmax)."""
        return self._texture.clim

    @clim.setter
    def clim(self, clims):
        if isinstance(clims, str) or len(clims) == 2:
            clims = [clims] * self.num_channels
        if self._texture.set_clim(clims):
            self._need_texture_upload = True
        self._update_colortransform_clim()
        self.update()

    def _update_colortransform_clim(self):
        if self._need_colortransform_update:
            # we are going to rebuild anyway so just do it later
            return
        try:
            norm_clims = self._texture.clim_normalized
        except RuntimeError:
            return
        else:
            clim_names = ('clim_r', 'clim_g', 'clim_b')
            # shortcut so we don't have to rebuild the whole color transform
            for clim_name, clim in zip(clim_names, norm_clims):
                # shortcut so we don't have to rebuild the whole color transform
                self.shared_program.frag['color_transform'][1][clim_name] = clim

    @property
    def gamma(self):
        """Get the gamma used when rendering the image."""
        return self._gamma

    @gamma.setter
    def gamma(self, gammas):
        """Set gamma used when rendering the image."""
        if not isinstance(gammas, (list, tuple)):
            gammas = [gammas] * self.num_channels
        if len(gammas) != self.num_channels:
            raise ValueError("List of color limits must have the same number "
                             f"of elements as creation: {self.num_channels}")
        if any(val <= 0 for val in gammas):
            raise ValueError("gamma must be > 0")
        self._gamma = tuple(float(gamma) for gamma in gammas)

        gamma_names = ('gamma_r', 'gamma_g', 'gamma_b', 'gamma_a')
        for gamma_name, gamma in zip(gamma_names, self._gamma):
            # shortcut so we don't have to rebuild the color transform
            if not self._need_colortransform_update:
                self.shared_program.frag['color_transform'][2][gamma_name] = gamma
        self.update()

    @ImageVisual.cmap.setter
    def cmap(self, cmap):
        if cmap is not None:
            raise ValueError("MultiChannelImageVisual does not support a colormap.")
        self._cmap = None

    def _build_interpolation(self):
        # assumes 'nearest' interpolation
        interpolation = self._interpolation
        if interpolation != 'nearest':
            raise NotImplementedError("MultiChannelImageVisual only supports 'nearest' interpolation.")
        texture_interpolation = 'nearest'

        self._data_lookup_fn = Function(_rgb_texture_lookup)
        self.shared_program.frag['get_data'] = self._data_lookup_fn
        if self._texture.interpolation != texture_interpolation:
            self._texture.interpolation = texture_interpolation
        self._data_lookup_fn['texture_r'] = self._texture.textures[0]
        self._data_lookup_fn['texture_g'] = self._texture.textures[1]
        self._data_lookup_fn['texture_b'] = self._texture.textures[2]

        self._need_interpolation_update = False

    def _build_color_transform(self):
        if self.num_channels != 3:
            raise NotImplementedError("MultiChannelimageVisuals only support 3 channels.")
        else:
            # RGB/A image data (no colormap)
            fclim = Function(_apply_clim)
            fgamma = Function(_apply_gamma)
            fun = FunctionChain(None, [Function(_null_color_transform), fclim, fgamma])
        fclim['clim_r'] = self._texture.textures[0].clim_normalized
        fclim['clim_g'] = self._texture.textures[1].clim_normalized
        fclim['clim_b'] = self._texture.textures[2].clim_normalized
        fgamma['gamma_r'] = self.gamma[0]
        fgamma['gamma_g'] = self.gamma[1]
        fgamma['gamma_b'] = self.gamma[2]
        return fun

    def set_data(self, data_arrays):
        """Set the data.

        Parameters
        ----------
        image : array-like
            The image data.
        """
        if len(data_arrays) != self.num_channels:
            raise ValueError("List of data arrays must have the same number "
                             f"of elements as creation: {self.num_channels}")
        if self._data is not None and any(self._shape_differs(x1, x2) for x1, x2 in zip(self._data, data_arrays)):
            self._need_vertex_update = True
        data_arrays = list(self._cast_arrays_if_needed(data_arrays))
        self._texture.check_data_format(data_arrays)
        self._data = data_arrays
        self._need_texture_upload = True

    @staticmethod
    def _cast_arrays_if_needed(data_arrays):
        for data in data_arrays:
            if data is not None and should_cast_to_f32(data.dtype):
                data = data.astype(np.float32)
            yield data

    @staticmethod
    def _shape_differs(arr1, arr2):
        none_change1 = arr1 is not None and arr2 is None
        none_change2 = arr1 is None and arr2 is not None
        shape_change = False
        if arr1 is not None and arr2 is not None:
            shape_change = arr1.shape[:2] != arr2.shape[:2]
        return none_change1 or none_change2 or shape_change

    def _build_texture(self):
        pre_clims = self._texture.clim
        pre_internalformat = self._texture.internalformat
        self._texture.scale_and_set_data(self._data)
        post_clims = self._texture.clim
        post_internalformat = self._texture.internalformat
        # color transform needs rebuilding if the internalformat was changed
        # new color limits need to be assigned if the normalized clims changed
        # otherwise, the original color transform should be fine
        # Note that this assumes that if clim changed, clim_normalized changed
        new_if = post_internalformat != pre_internalformat
        new_cl = post_clims != pre_clims
        if new_if or new_cl:
            self._need_colortransform_update = True
        self._need_texture_upload = False
