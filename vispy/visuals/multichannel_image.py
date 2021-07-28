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
    default_shape = (10, 10)  # if no data is provided, create a texture of NaNs

    def __init__(self, data, **texture_kwargs):
        # data to send to texture when not being used
        self._fill_arr = np.full(self.default_shape, np.float32(np.nan),
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


_texture_lookup_template = """
    vec4 texture_lookup(vec2 texcoord) {{
        if(texcoord.x < 0.0 || texcoord.x > 1.0 ||
        texcoord.y < 0.0 || texcoord.y > 1.0) {{
            discard;
        }}
        vec4 val;
        val.r = {r_lookup};
        val.g = {g_lookup};
        val.b = {b_lookup};
        val.a = {a_lookup};
        return val;
    }}"""

_apply_clim = """
    vec4 apply_clim(vec4 color) {
        color.r = $clim_channel_r(color.r);
        color.g = $clim_channel_g(color.g);
        color.b = $clim_channel_b(color.b);
        color.a = $clim_channel_a(color);
        return color;
    }
"""
_clim_channel = """
    float clim_channel(float color) {
        // If NaN, set to minimum clim value
        // http://stackoverflow.com/questions/11810158/how-to-deal-with-nan-or-inf-in-opengl-es-2-0-shaders
        color = !(color <= 0.0 || 0.0 <= color) ? min($clim.x, $clim.y) : color;
        color = clamp(color , min($clim.x, $clim.y), max($clim.x, $clim.y));
        color = (color - $clim.x) / ($clim.y - $clim.x);
        return max(color, 0.0);
    }
"""
# Special handling of alpha channel so that NaN values map to max value (fully opaque)
_clim_channel_alpha = """
    float clim_channel_alpha(vec4 color) {
        float alpha;
        // If all the pixels are NaN make it completely transparent
        // http://stackoverflow.com/questions/11810158/how-to-deal-with-nan-or-inf-in-opengl-es-2-0-shaders
        if (
            !(color.r <= 0.0 || 0.0 <= color.r) &&
            !(color.g <= 0.0 || 0.0 <= color.g) &&
            !(color.b <= 0.0 || 0.0 <= color.b)) {
            return 0.0;
        }
        
        if (!(color.a <= 0.0 || 0.0 <= color.a)) {
            return 1.0;
        }
        alpha = clamp(color.a , min($clim.x, $clim.y), max($clim.x, $clim.y));
        alpha = (alpha - $clim.x) / ($clim.y - $clim.x);
        return max(alpha, 0.0);
    }
"""
_clim_noop = """
    float clim_channel_alpha(vec4 color) {
        // If all the pixels are NaN make it completely transparent
        // http://stackoverflow.com/questions/11810158/how-to-deal-with-nan-or-inf-in-opengl-es-2-0-shaders
        if (
            !(color.r <= 0.0 || 0.0 <= color.r) &&
            !(color.g <= 0.0 || 0.0 <= color.g) &&
            !(color.b <= 0.0 || 0.0 <= color.b)) {
            return 0;
        }
        return color.a;
    }
"""

_apply_gamma = """
    vec4 apply_gamma(vec4 color) {
        color.r = $gamma_channel_r(color.r);
        color.g = $gamma_channel_g(color.g);
        color.b = $gamma_channel_b(color.b);
        color.a = $gamma_channel_a(color.a);
        return color;
    }
"""
_gamma_channel = """
    float gamma_channel(float color) {
        return pow(color, $gamma);
    }
"""
_gamma_noop = """
    float gamma_channel_alpha(float color) {
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
        A 2, 3, or 4 element list of numpy arrays with 2 dimensions where the
        arrays are sorted by (R, G, B, A) order. In the case of 2 elements,
        the default behavior is to use the inputs as Luminance (grayscale)
        and Alpha (transparency control) bands. In the case of 3 and 4
        elements the inputs represent R, G, B, and A (if provided). The
        inputs will be stored separately on the GPU and then put together
        to make a single image. The list can contain ``None`` meaning there
        is no value for this channel currently, but it may be filled in
        later. In this case the underlying GPU storage is still allocated,
        but pre-filled with NaNs. Note that each channel may have different
        shapes. Also note that the number of channels can not change after
        creation (ex. providing 2 arrays then later providing 3).
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
            return [self._texture.default_shape]
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
        if isinstance(clims, str) or (len(clims) == 2 and not isinstance(clims[0], (tuple, list, str))):
            clims = [clims] * self.num_channels
        if len(clims) != self.num_channels:
            raise ValueError("List of color limits must have the same number "
                             f"of elements as creation: {self.num_channels}")
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
            clim_names = ('clim_r', 'clim_g', 'clim_b', 'clim_a')
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

        texture_lookup_str = self._format_texture_lookup_shader()
        self._data_lookup_fn = Function(texture_lookup_str)
        self.shared_program.frag['get_data'] = self._data_lookup_fn
        if self._texture.interpolation != texture_interpolation:
            self._texture.interpolation = texture_interpolation

        self._assign_lookup_textures()
        self._need_interpolation_update = False

    def _format_texture_lookup_shader(self):
        lookup_funcs = {}
        func_names = [f"{chan}_lookup" for chan in "rgba"]
        for num_chan, func_name in zip(range(self.num_channels), func_names):
            lookup_funcs[func_name] = f"texture2D($texture_{num_chan}, texcoord).r"
        if self.num_channels == 2:
            r_lookup = g_lookup = b_lookup = "texture2D($texture_1, texcoord).r"
            a_lookup = "texture2D($texture_2, texcoord).r"
        elif self.num_channels >= 3:
            r_lookup = "texture2D($texture_1, texcoord).r"
            g_lookup = "texture2D($texture_2, texcoord).r"
            b_lookup = "texture2D($texture_3, texcoord).r"
            a_lookup = "1.0"
        if self.num_channels == 4:
            a_lookup = "texture2D($texture_4, texcoord).r"
        texture_lookup_str = _texture_lookup_template.format(
            r_lookup=r_lookup,
            g_lookup=g_lookup,
            b_lookup=b_lookup,
            a_lookup=a_lookup,
        )
        return texture_lookup_str

    def _assign_lookup_textures(self):
        texture_names = [f"texture_{chan_num}" for chan_num in range(1, 5)]
        for tex_name, tex in zip(texture_names, self._texture.textures):
            self._data_lookup_fn[tex_name] = tex

    def _build_color_transform(self):
        # LA/RGB/RGBA image data (no colormap)
        fclim = Function(_apply_clim)
        fgamma = Function(_apply_gamma)
        fun = FunctionChain(None, [Function(_null_color_transform), fclim, fgamma])
        textures = self._texture.textures
        gammas = self.gamma
        if self.num_channels == 2:
            textures = [textures[0], textures[0], textures[0], textures[1]]
            gammas = [gammas[0], gammas[0], gammas[0], gammas[1]]
        for chan, gamma, tex in zip("rgba", gammas, textures):
            clim_fun = Function(_clim_channel if chan != "a" else _clim_channel_alpha)
            clim_fun['clim'] = tex.clim_normalized
            fclim[f"clim_channel_{chan}"] = clim_fun
            gamma_fun = Function(_gamma_channel)
            gamma_fun['gamma'] = gamma
            fgamma[f"gamma_channel_{chan}"] = gamma_fun
        if self.num_channels not in [2, 4]:
            clim_fun = Function(_clim_noop)
            fclim['clim_channel_a'] = clim_fun
            gamma_fun = Function(_gamma_noop)
            fgamma['gamma_channel_a'] = gamma_fun
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
