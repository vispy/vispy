# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Primitive 2D image visual class."""

from __future__ import division
import warnings

import numpy as np

from ..gloo import Texture2D, VertexBuffer
from ..color import get_colormap
from .shaders import Function, FunctionChain
from .transforms import NullTransform
from .visual import Visual
from ..io import load_spatial_filters


F64_PRECISION_WARNING = ("GPUs can't support floating point data with more "
                         "than 32-bits, precision will be lost due to "
                         "downcasting to 32-bit float.")


def _should_cast_to_f32(data_dtype):
    data_dtype = np.dtype(data_dtype)
    is_floating = np.issubdtype(data_dtype, np.floating)
    gt_float32 = data_dtype.itemsize > 4
    if is_floating and gt_float32:
        # OpenGL can't support floating point numbers greater than 32-bits
        warnings.warn(F64_PRECISION_WARNING)
        return True
    return False


class _CPUScaledTexture2D(Texture2D):
    """Texture class for smarter scaling decisions.

    This class wraps the logic to normalize data on the CPU before sending
    it to the GPU (the texture). Pre-scaling on the CPU can be helpful in
    cases where OpenGL 2/ES requirements limit the texture storage to an
    8-bit normalized integer internally.

    This class includes optimizations where image data is not re-normalized
    if the previous normalization can still be used to visualize the data
    with the new color limits.

    This class should only be used internally. For similar features where
    scaling occurs on the GPU see
    :class:`vispy.visuals.image._GPU_ScaledTexture2D`.

    """

    def __init__(self, data=None, **texture_kwargs):
        """Initialize texture and normalization limit properties."""
        self._clim = None
        self._data_dtype = getattr(data, 'dtype', None)
        self._data_limits = None

        data = self._create_rep_array(data)
        super().__init__(data, **texture_kwargs)

    @property
    def clim(self):
        """Color limits of the texture's data."""
        return self._clim

    def set_clim(self, clim):
        """Set clim and return if a texture update is needed."""
        need_texture_upload = False
        # NOTE: Color limits are not checked against data type limits
        if isinstance(clim, str):
            if clim != 'auto':
                raise ValueError('clim must be "auto" if a string')
            need_texture_upload = True
            self._clim = clim
        else:
            try:
                cmin, cmax = clim
            except (ValueError, TypeError):
                raise ValueError('clim must have two elements')
            if self._clim_outside_data_limits(cmin, cmax):
                need_texture_upload = True
            self._clim = (cmin, cmax)
        return need_texture_upload

    def _clim_outside_data_limits(self, cmin, cmax):
        if self._data_limits is None:
            return False
        return cmin < self._data_limits[0] or cmax > self._data_limits[1]

    @property
    def clim_normalized(self):
        """Normalize current clims to match texture data inside the shader.

        If data is scaled on the CPU then the texture data will be in the range
        0-1 in the _build_texture() method. Inside the fragment shader the
        final contrast adjustment will be applied based on this normalized
        ``clim``.

        """
        range_min, range_max = self._data_limits
        clim_min, clim_max = self.clim
        clim_min = (clim_min - range_min) / (range_max - range_min)
        clim_max = (clim_max - range_min) / (range_max - range_min)
        return clim_min, clim_max

    @property
    def is_normalized(self):
        """Whether the in-shader representation of this texture is normalized or not.

        Formats ending in 'f' (float), 'ui' (unsigned integral), or 'i'
        (integral) are not normalized in the GPU. Formats ending in "_snorm"
        are normalized on the range [-1, 1] based on the data type of the
        input data (ex. 0-255 for uint8). Formats with no data type suffix are
        normalized on the range [0, 1]. See
        https://www.khronos.org/opengl/wiki/Image_Format for more information.

        This property can be used to determine if input shader variables
        (uniforms, template variables) need to also be normalized. See
        :meth:`~BaseTexture.normalize_value` below.

        """
        if self.internalformat is None:
            return True
        return self.internalformat[-1] not in ('f', 'i')

    def normalize_value(self, val, input_data_dtype):
        """Normalize values to match in-shader representation of this shader.

        Parameters
        ----------
        val : int | float | ndarray
            Value(s) to normalize.
        input_data_dtype : numpy.dtype
            Data type of input data. The assumption is that the provided
            values to be normalized are in the same range as the input
            texture data and must be normalized in the same way.

        """
        if not self.is_normalized:
            return val
        dtype_info = np.iinfo(input_data_dtype)
        dmin = dtype_info.min
        dmax = dtype_info.max
        val = (val - dmin) / (dmax - dmin)
        # XXX: Do we need to handle _snorm differently?
        #  Not currently supported in vispy.
        return val

    @staticmethod
    def _data_num_channels(data):
        if data is not None:
            num_channels = data.shape[-1] if data.ndim == 3 else 1
        else:
            num_channels = 4
        return num_channels

    def _create_rep_array(self, data):
        """Get a representative array with an initial shape.

        Data will be filled in and the texture resized later.

        """
        dtype = getattr(data, 'dtype', np.float32)
        num_channels = self._data_num_channels(data)
        return np.zeros((1, 1, num_channels)).astype(dtype)

    @staticmethod
    def _scale_data_on_cpu(data, clim):
        data = data - clim[0]  # not inplace so we don't modify orig data
        if clim[1] - clim[0] > 0:
            data /= clim[1] - clim[0]
        else:
            data[:] = 1 if data[0, 0] != 0 else 0
        if data.dtype == np.float64:
            data = data.astype(np.float32)
        return data

    def check_data_format(self, data):
        """Check if provided data will cause issues if set later."""
        # this texture type has no limitations
        return

    def _get_auto_rgb_minmax(self, data):
        # assume floating point data is pre-normalized to 0 and 1
        if np.issubdtype(data.dtype, np.floating):
            return 0, 1
        # assume integer RGBs fill the whole data space
        dtype_info = np.iinfo(data.dtype)
        dmin = dtype_info.min
        dmax = dtype_info.max
        return dmin, dmax

    def set_data(self, data, offset=None, copy=False):
        """Upload new data to the GPU, scaling if necessary."""
        self._data_dtype = data.dtype

        clim = self._clim
        is_auto = isinstance(clim, str) and clim == 'auto'
        if data.ndim == 2 or data.shape[2] == 1:
            if is_auto:
                clim = np.min(data), np.max(data)
            clim = (np.float32(clim[0]), np.float32(clim[1]))
            data = self._scale_data_on_cpu(data, clim)
            data_limits = clim
        else:
            data_limits = self._get_auto_rgb_minmax(data)
            if is_auto:
                clim = data_limits

        self._clim = clim
        self._data_limits = data_limits
        ret = super().set_data(data, offset=offset, copy=copy)
        return ret


class _GPUScaledTexture2D(_CPUScaledTexture2D):
    """Texture class for smarter scaling and internalformat decisions.

    This texture class uses internal formats that are not supported by
    strict OpenGL 2/ES drivers without additional extensions. By using
    this texture we upload data to the GPU in a format as close to
    the original data type as possible (32-bit floats on the CPU are 32-bit
    floats on the GPU). No normalization/scaling happens on the CPU and
    all of it happens on the GPU. This should avoid unnecessary data copies
    as well as provide the highest precision for the final visualization.

    The texture format may either be a GL enum string (ex. 'r32f'), a numpy
    dtype object (ex. np.float32), or 'auto' which means the texture will
    try to pick the best format for the provided data. By using 'auto' you
    also give the texture permission to change formats in the future if
    new data is provided with a different data type.

    """

    # dtype -> internalformat
    # 'r' will be replaced (if needed) with rgb or rgba depending on number of bands
    _texture_dtype_format = {
        np.float32: 'r32f',
        np.float64: 'r32f',
        np.uint8: 'r8',
        np.uint16: 'r16',
        # np.uint32: 'r32ui',  # not supported texture format in vispy
        np.int8: 'r8',
        np.int16: 'r16',
        # np.int32: 'r32i',  # not supported texture format in vispy
    }

    def __init__(self, data=None, internalformat=None, **texture_kwargs):
        self._auto_texture_format = False
        self._clim = None
        self._data_dtype = getattr(data, 'dtype', None)

        data = self._create_rep_array(data)
        internalformat = self._get_texture_format_for_data(data, internalformat)
        super().__init__(data, internalformat=internalformat, **texture_kwargs)

    def _handle_auto_texture_format(self, texture_format, data):
        if isinstance(texture_format, str) and texture_format == 'auto':
            if data is None:
                warnings.warn("'texture_format' set to 'auto' but no data "
                              "provided. Falling back to CPU scaling.")
                texture_format = None
            else:
                texture_format = data.dtype.type
                self._auto_texture_format = True
        return texture_format

    def _get_gl_tex_format(self, texture_format, num_channels):
        if texture_format and not isinstance(texture_format, str):
            texture_format = np.dtype(texture_format).type
            if texture_format not in self._texture_dtype_format:
                raise ValueError("Can't determine internal texture format for '{}'".format(texture_format))
            _should_cast_to_f32(texture_format)
            texture_format = self._texture_dtype_format[texture_format]
        # adjust internalformat for format of data (RGBA vs L)
        texture_format = texture_format.replace('r', 'rgba'[:num_channels])
        return texture_format

    def _get_texture_format_for_data(self, data, texture_format):
        if texture_format is not None:
            num_channels = self._data_num_channels(data)
            texture_format = self._handle_auto_texture_format(texture_format, data)
            texture_format = self._get_gl_tex_format(texture_format, num_channels)
        return texture_format

    @property
    def clim(self):
        """Color limits of the texture's data."""
        return self._clim

    def set_clim(self, clim):
        """Set clim and return if a texture update is needed."""
        need_texture_upload = False
        if isinstance(clim, str):
            if clim != 'auto':
                raise ValueError('clim must be "auto" if a string')
            need_texture_upload = True
            self._clim = clim
        else:
            try:
                cmin, cmax = clim
            except (ValueError, TypeError):
                raise ValueError('clim must have two elements')
            self._clim = (cmin, cmax)
        return need_texture_upload

    @property
    def clim_normalized(self):
        """Normalize current clims to match texture data inside the shader.

        Scaling only happens on the GPU so we only normalize
        the color limits when needed (for unsigned normalized integer
        internal formats). Otherwise, for internal formats that are not
        normalized such as floating point (ex. r32f) we can leave the ``clim``
        as is.

        """
        # if the internalformat of the texture is normalized we need to
        # also normalize the clims so they match in-shader
        clim_min = self.normalize_value(self.clim[0], self._data_dtype)
        clim_max = self.normalize_value(self.clim[1], self._data_dtype)
        return clim_min, clim_max

    def _compute_clim(self, data):
        clim = self._clim
        is_auto = isinstance(clim, str) and clim == 'auto'
        if data.ndim == 2 or data.shape[2] == 1:
            if is_auto:
                clim = np.min(data), np.max(data)
            clim = (np.float32(clim[0]), np.float32(clim[1]))
        elif is_auto:
            # assume that RGB data is already scaled (0, 1)
            clim = self._get_auto_rgb_minmax(data)
        return clim

    def _internalformat_will_change(self, data):
        shape_repr = self._create_rep_array(data)
        new_if = self._get_gl_tex_format(data.dtype, shape_repr.shape[-1])
        return new_if != self.internalformat

    def check_data_format(self, data):
        """Check if provided data will cause issues if set later."""
        if self._internalformat_will_change(data) and not self._auto_texture_format:
            raise ValueError("Data being set would cause a format change "
                             "in the texture. This is only allowed when "
                             "'texture_format' is set to 'auto'.")

    def _reformat_if_necessary(self, data):
        if not self._internalformat_will_change(data):
            return
        if self._auto_texture_format:
            shape_repr = self._create_rep_array(data)
            internalformat = self._get_gl_tex_format(data.dtype, shape_repr.shape[-1])
            self._resize(data.shape, internalformat=internalformat)
        else:
            raise RuntimeError("'internalformat' needs to change but "
                               "'texture_format' was not 'auto'.")

    def set_data(self, data, offset=None, copy=False):
        """Upload new data to the GPU, scaling if necessary."""
        self._reformat_if_necessary(data)
        self._data_dtype = np.dtype(data.dtype)
        self._clim = self._compute_clim(data)
        ret = super(_CPUScaledTexture2D, self).set_data(data, offset=offset, copy=copy)
        return ret


VERT_SHADER = """
uniform int method;  // 0=subdivide, 1=impostor
attribute vec2 a_position;
attribute vec2 a_texcoord;
varying vec2 v_texcoord;

void main() {
    v_texcoord = a_texcoord;
    gl_Position = $transform(vec4(a_position, 0., 1.));
}
"""

FRAG_SHADER = """
uniform vec2 image_size;
uniform int method;  // 0=subdivide, 1=impostor
uniform sampler2D u_texture;
varying vec2 v_texcoord;

vec4 map_local_to_tex(vec4 x) {
    // Cast ray from 3D viewport to surface of image
    // (if $transform does not affect z values, then this
    // can be optimized as simply $transform.map(x) )
    vec4 p1 = $transform(x);
    vec4 p2 = $transform(x + vec4(0, 0, 0.5, 0));
    p1 /= p1.w;
    p2 /= p2.w;
    vec4 d = p2 - p1;
    float f = p2.z / d.z;
    vec4 p3 = p2 - d * f;

    // finally map local to texture coords
    return vec4(p3.xy / image_size, 0, 1);
}


void main()
{
    vec2 texcoord;
    if( method == 0 ) {
        texcoord = v_texcoord;
    }
    else {
        // vertex shader outputs clip coordinates;
        // fragment shader maps to texture coordinates
        texcoord = map_local_to_tex(vec4(v_texcoord, 0, 1)).xy;
    }

    gl_FragColor = $color_transform($get_data(texcoord));
}
"""  # noqa

_interpolation_template = """
    #include "misc/spatial-filters.frag"
    vec4 texture_lookup_filtered(vec2 texcoord) {
        if(texcoord.x < 0.0 || texcoord.x > 1.0 ||
        texcoord.y < 0.0 || texcoord.y > 1.0) {
            discard;
        }
        return %s($texture, $shape, texcoord);
    }"""

_texture_lookup = """
    vec4 texture_lookup(vec2 texcoord) {
        if(texcoord.x < 0.0 || texcoord.x > 1.0 ||
        texcoord.y < 0.0 || texcoord.y > 1.0) {
            discard;
        }
        return texture2D($texture, texcoord);
    }"""

_apply_clim_float = """
    float apply_clim(float data) {
        if ($clim.x < $clim.y) {{
            data = clamp(data, $clim.x, $clim.y);
        }} else {{
            data = clamp(data, $clim.y, $clim.x);
        }}
        data = data - $clim.x;
        data = data / ($clim.y - $clim.x);
        return max(data, 0);
    }"""
_apply_clim = """
    vec4 apply_clim(vec4 color) {
        if ($clim.x < $clim.y) {{
            color.rgb = clamp(color.rgb, $clim.x, $clim.y);
        }} else {{
            color.rgb = clamp(color.rgb, $clim.y, $clim.x);
        }}
        color.rgb = color.rgb - $clim.x;
        color.rgb = color.rgb / ($clim.y - $clim.x);
        return max(color, 0);
    }
"""

_apply_gamma_float = """
    float apply_gamma(float data) {
        return pow(data, $gamma);
    }"""
_apply_gamma = """
    vec4 apply_gamma(vec4 color) {
        color.rgb = pow(color.rgb, vec3($gamma));
        return color;
    }
"""

_null_color_transform = 'vec4 pass(vec4 color) { return color; }'
_c2l_red = 'float cmap(vec4 color) { return color.r; }'


class ImageVisual(Visual):
    """Visual subclass displaying an image.

    Parameters
    ----------
    data : ndarray
        ImageVisual data. Can be shape (M, N), (M, N, 3), or (M, N, 4).
    method : str
        Selects method of rendering image in case of non-linear transforms.
        Each method produces similar results, but may trade efficiency
        and accuracy. If the transform is linear, this parameter is ignored
        and a single quad is drawn around the area of the image.

            * 'auto': Automatically select 'impostor' if the image is drawn
              with a nonlinear transform; otherwise select 'subdivide'.
            * 'subdivide': ImageVisual is represented as a grid of triangles
              with texture coordinates linearly mapped.
            * 'impostor': ImageVisual is represented as a quad covering the
              entire view, with texture coordinates determined by the
              transform. This produces the best transformation results, but may
              be slow.

    grid: tuple (rows, cols)
        If method='subdivide', this tuple determines the number of rows and
        columns in the image grid.
    cmap : str | ColorMap
        Colormap to use for luminance images.
    clim : str | tuple
        Limits to use for the colormap. Can be 'auto' to auto-set bounds to
        the min and max of the data.
    gamma : float
        Gamma to use during colormap lookup.  Final color will be cmap(val**gamma).
        by default: 1.
    interpolation : str
        Selects method of image interpolation. Makes use of the two Texture2D
        interpolation methods and the available interpolation methods defined
        in vispy/gloo/glsl/misc/spatial_filters.frag

            * 'nearest': Default, uses 'nearest' with Texture2D interpolation.
            * 'bilinear': uses 'linear' with Texture2D interpolation.
            * 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric', 'bicubic',
                'catrom', 'mitchell', 'spline16', 'spline36', 'gaussian',
                'bessel', 'sinc', 'lanczos', 'blackman'
    texture_format: numpy.dtype | str | None
        How to store data on the GPU. OpenGL allows for many different storage
        formats and schemes for the low-level texture data stored in the GPU.
        Most common is unsigned integers or floating point numbers.
        Unsigned integers are the most widely supported while other formats
        may not be supported on older versions of OpenGL, WebGL
        (without enabling some extensions), or with older GPUs.
        Default value is ``None`` which means data will be scaled on the
        CPU and the result stored in the GPU as an unsigned integer. If a
        numpy dtype object, an internal texture format will be chosen to
        support that dtype and data will *not* be scaled on the CPU. Not all
        dtypes are supported. If a string, then
        it must be one of the OpenGL internalformat strings described in the
        table on this page: https://www.khronos.org/registry/OpenGL-Refpages/gl4/html/glTexImage2D.xhtml
        The name should have `GL_` removed and be lowercase (ex.
        `GL_R32F` becomes ``'r32f'``). Lastly, this can also be the string
        ``'auto'`` which will use the data type of the provided image data
        to determine the internalformat of the texture.
        When this is specified (not ``None``) data is scaled on the
        GPU which allows for faster color limit changes. Additionally, when
        32-bit float data is provided it won't be copied before being
        transferred to the GPU.
    **kwargs : dict
        Keyword arguments to pass to `Visual`.

    Notes
    -----
    The colormap functionality through ``cmap`` and ``clim`` are only used
    if the data are 2D.
    """

    VERTEX_SHADER = VERT_SHADER
    FRAGMENT_SHADER = FRAG_SHADER

    def __init__(self, data=None, method='auto', grid=(1, 1),
                 cmap='viridis', clim='auto', gamma=1.0,
                 interpolation='nearest', texture_format=None, **kwargs):
        """Initialize image properties, texture storage, and interpolation methods."""
        self._data = None
        self._gamma = gamma

        # load 'float packed rgba8' interpolation kernel
        # to load float interpolation kernel use
        # `load_spatial_filters(packed=False)`
        kernel, interpolation_names = load_spatial_filters()

        self._kerneltex = Texture2D(kernel, interpolation='nearest')
        # The unpacking can be debugged by changing "spatial-filters.frag"
        # to have the "unpack" function just return the .r component. That
        # combined with using the below as the _kerneltex allows debugging
        # of the pipeline
        # self._kerneltex = Texture2D(kernel, interpolation='linear',
        #                             internalformat='r32f')

        interpolation_names, interpolation_fun = self._init_interpolation(
            interpolation_names)
        self._interpolation_names = interpolation_names
        self._interpolation_fun = interpolation_fun
        self._interpolation = interpolation
        if self._interpolation not in self._interpolation_names:
            raise ValueError("interpolation must be one of %s" %
                             ', '.join(self._interpolation_names))

        # check texture interpolation
        if self._interpolation == 'bilinear':
            texture_interpolation = 'linear'
        else:
            texture_interpolation = 'nearest'

        self._method = method
        self._grid = grid
        self._need_texture_upload = True
        self._need_vertex_update = True
        self._need_colortransform_update = True
        self._need_interpolation_update = True
        if texture_format is None:
            self._texture = _CPUScaledTexture2D(
                data, interpolation=texture_interpolation)
        else:
            self._texture = _GPUScaledTexture2D(
                data, internalformat=texture_format,
                interpolation=texture_interpolation)
        self._subdiv_position = VertexBuffer()
        self._subdiv_texcoord = VertexBuffer()

        # impostor quad covers entire viewport
        vertices = np.array([[-1, -1], [1, -1], [1, 1],
                             [-1, -1], [1, 1], [-1, 1]],
                            dtype=np.float32)
        self._impostor_coords = VertexBuffer(vertices)
        self._null_tr = NullTransform()

        self._init_view(self)
        super(ImageVisual, self).__init__(vcode=self.VERTEX_SHADER, fcode=self.FRAGMENT_SHADER)
        self.set_gl_state('translucent', cull_face=False)
        self._draw_mode = 'triangles'

        # define _data_lookup_fn as None, will be setup in
        # self._build_interpolation()
        self._data_lookup_fn = None

        self.clim = clim
        self.cmap = cmap
        if data is not None:
            self.set_data(data)
        self.freeze()

    @staticmethod
    def _init_interpolation(interpolation_names):
        # create interpolation shader functions for available
        # interpolations
        fun = [Function(_interpolation_template % n)
               for n in interpolation_names]
        interpolation_names = [n.lower() for n in interpolation_names]

        interpolation_fun = dict(zip(interpolation_names, fun))
        interpolation_names = tuple(sorted(interpolation_names))

        # overwrite "nearest" and "bilinear" spatial-filters
        # with  "hardware" interpolation _data_lookup_fn
        interpolation_fun['nearest'] = Function(_texture_lookup)
        interpolation_fun['bilinear'] = Function(_texture_lookup)
        return interpolation_names, interpolation_fun

    def set_data(self, image):
        """Set the image data.

        Parameters
        ----------
        image : array-like
            The image data.
        texture_format : str or None

        """
        data = np.asarray(image)
        if _should_cast_to_f32(data.dtype):
            data = data.astype(np.float32)
        # can the texture handle this data?
        self._texture.check_data_format(data)
        if self._data is None or self._data.shape[:2] != data.shape[:2]:
            # Only rebuild if the size of the image changed
            self._need_vertex_update = True
        self._data = data
        self._need_texture_upload = True

    def view(self):
        """Get the :class:`vispy.visuals.visual.VisualView` for this visual."""
        v = Visual.view(self)
        self._init_view(v)
        return v

    def _init_view(self, view):
        # Store some extra variables per-view
        view._need_method_update = True
        view._method_used = None

    @property
    def clim(self):
        """Get color limits used when rendering the image (cmin, cmax)."""
        return self._texture.clim

    @clim.setter
    def clim(self, clim):
        if self._texture.set_clim(clim):
            self._need_texture_upload = True
        # shortcut so we don't have to rebuild the whole color transform
        if not self._need_colortransform_update:
            self.shared_program.frag['color_transform'][1]['clim'] = self._texture.clim_normalized
        self.update()

    @property
    def cmap(self):
        """Get the colormap object applied to luminance (single band) data."""
        return self._cmap

    @cmap.setter
    def cmap(self, cmap):
        self._cmap = get_colormap(cmap)
        self._need_colortransform_update = True
        self.update()

    @property
    def gamma(self):
        """Get the gamma used when rendering the image."""
        return self._gamma

    @gamma.setter
    def gamma(self, value):
        """Set gamma used when rendering the image."""
        if value <= 0:
            raise ValueError("gamma must be > 0")
        self._gamma = float(value)
        # shortcut so we don't have to rebuild the color transform
        if not self._need_colortransform_update:
            self.shared_program.frag['color_transform'][2]['gamma'] = self._gamma
        self.update()

    @property
    def method(self):
        """Get rendering method name."""
        return self._method

    @method.setter
    def method(self, m):
        if self._method != m:
            self._method = m
            self._need_vertex_update = True
            self.update()

    @property
    def size(self):
        """Get size of the image (width, height)."""
        return self._data.shape[:2][::-1]

    @property
    def interpolation(self):
        """Get interpolation algorithm name."""
        return self._interpolation

    @interpolation.setter
    def interpolation(self, i):
        if i not in self._interpolation_names:
            raise ValueError("interpolation must be one of %s" %
                             ', '.join(self._interpolation_names))
        if self._interpolation != i:
            self._interpolation = i
            self._need_interpolation_update = True
            self.update()

    @property
    def interpolation_functions(self):
        """Get names of possible interpolation methods."""
        return self._interpolation_names

    # The interpolation code could be transferred to a dedicated filter
    # function in visuals/filters as discussed in #1051
    def _build_interpolation(self):
        """Rebuild the _data_lookup_fn for different interpolations."""
        interpolation = self._interpolation
        self._data_lookup_fn = self._interpolation_fun[interpolation]
        self.shared_program.frag['get_data'] = self._data_lookup_fn

        # only 'bilinear' uses 'linear' texture interpolation
        if interpolation == 'bilinear':
            texture_interpolation = 'linear'
        else:
            # 'nearest' (and also 'bilinear') doesn't use spatial_filters.frag
            # so u_kernel and shape setting is skipped
            texture_interpolation = 'nearest'
            if interpolation != 'nearest':
                self.shared_program['u_kernel'] = self._kerneltex
                self._data_lookup_fn['shape'] = self._data.shape[:2][::-1]

        if self._texture.interpolation != texture_interpolation:
            self._texture.interpolation = texture_interpolation

        self._data_lookup_fn['texture'] = self._texture

        self._need_interpolation_update = False

    def _build_vertex_data(self):
        """Rebuild the vertex buffers for the subdivide method."""
        grid = self._grid
        w = 1.0 / grid[1]
        h = 1.0 / grid[0]

        quad = np.array([[0, 0, 0], [w, 0, 0], [w, h, 0],
                         [0, 0, 0], [w, h, 0], [0, h, 0]],
                        dtype=np.float32)
        quads = np.empty((grid[1], grid[0], 6, 3), dtype=np.float32)
        quads[:] = quad

        mgrid = np.mgrid[0.:grid[1], 0.:grid[0]].transpose(1, 2, 0)
        mgrid = mgrid[:, :, np.newaxis, :]
        mgrid[..., 0] *= w
        mgrid[..., 1] *= h

        quads[..., :2] += mgrid
        tex_coords = quads.reshape(grid[1]*grid[0]*6, 3)
        tex_coords = np.ascontiguousarray(tex_coords[:, :2])
        vertices = tex_coords * self.size

        self._subdiv_position.set_data(vertices.astype('float32'))
        self._subdiv_texcoord.set_data(tex_coords.astype('float32'))
        self._need_vertex_update = False

    def _update_method(self, view):
        """Decide which method to use for *view* and configure it accordingly."""
        method = self._method
        if method == 'auto':
            if view.transforms.get_transform().Linear:
                method = 'subdivide'
            else:
                method = 'impostor'
        view._method_used = method

        if method == 'subdivide':
            view.view_program['method'] = 0
            view.view_program['a_position'] = self._subdiv_position
            view.view_program['a_texcoord'] = self._subdiv_texcoord
        elif method == 'impostor':
            view.view_program['method'] = 1
            view.view_program['a_position'] = self._impostor_coords
            view.view_program['a_texcoord'] = self._impostor_coords
        else:
            raise ValueError("Unknown image draw method '%s'" % method)

        self.shared_program['image_size'] = self.size
        view._need_method_update = False
        self._prepare_transforms(view)

    def _build_texture(self):
        pre_clims = self._texture.clim
        pre_internalformat = self._texture.internalformat
        self._texture.set_data(self._data)
        post_clims = self._texture.clim
        post_internalformat = self._texture.internalformat
        # color transform needs rebuilding if the internalformat was changed
        # new color limits need to be assigned if the normalized clims changed
        # otherwise, the original color transform should be fine
        # Note that this assumes that if clim changed, clim_normalized changed
        new_if = post_internalformat != pre_internalformat
        new_cl = post_clims != pre_clims
        if not new_if and new_cl and not self._need_colortransform_update:
            # shortcut so we don't have to rebuild the whole color transform
            self.shared_program.frag['color_transform'][1]['clim'] = self._texture.clim_normalized
        elif new_if:
            self._need_colortransform_update = True
        self._need_texture_upload = False

    def _compute_bounds(self, axis, view):
        if axis > 1:
            return 0, 0
        else:
            return 0, self.size[axis]

    def _build_color_transform(self):
        if self._data.ndim == 2 or self._data.shape[2] == 1:
            # luminance data
            fclim = Function(_apply_clim_float)
            fgamma = Function(_apply_gamma_float)
            # NOTE: _c2l_red only uses the red component, fancy internalformats
            #   may need to use the other components or a different function chain
            fun = FunctionChain(
                None, [Function(_c2l_red), fclim, fgamma, Function(self.cmap.glsl_map)]
            )
        else:
            # RGB/A image data (no colormap)
            fclim = Function(_apply_clim)
            fgamma = Function(_apply_gamma)
            fun = FunctionChain(None, [Function(_null_color_transform), fclim, fgamma])
        fclim['clim'] = self._texture.clim_normalized
        fgamma['gamma'] = self.gamma
        return fun

    def _prepare_transforms(self, view):
        trs = view.transforms
        prg = view.view_program
        method = view._method_used
        if method == 'subdivide':
            prg.vert['transform'] = trs.get_transform()
            prg.frag['transform'] = self._null_tr
        else:
            prg.vert['transform'] = self._null_tr
            prg.frag['transform'] = trs.get_transform().inverse

    def _prepare_draw(self, view):
        if self._data is None:
            return False

        if self._need_interpolation_update:
            self._build_interpolation()

        if self._need_texture_upload:
            self._build_texture()

        if self._need_colortransform_update:
            prg = view.view_program
            self.shared_program.frag['color_transform'] = self._build_color_transform()
            self._need_colortransform_update = False
            prg['texture2D_LUT'] = self.cmap.texture_lut() \
                if (hasattr(self.cmap, 'texture_lut')) else None

        if self._need_vertex_update:
            self._build_vertex_data()

        if view._need_method_update:
            self._update_method(view)
