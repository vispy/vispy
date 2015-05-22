# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from ..gloo import set_state, Texture2D
from ..color import get_colormap
from .shaders import ModularProgram, Function, FunctionChain
from .transforms import NullTransform
from .visual import Visual
from ..ext.six import string_types


VERT_SHADER = """
attribute vec2 a_position;
attribute vec2 a_texcoord;
varying vec2 v_texcoord;

void main() {
    v_texcoord = a_texcoord;
    gl_Position = $transform(vec4(a_position, 0., 1.));
}
"""

FRAG_SHADER = """
uniform sampler2D u_texture;
varying vec2 v_texcoord;

void main()
{
    vec2 texcoord = $map_uv_to_tex(vec4(v_texcoord, 0, 1)).xy;
    if(texcoord.x < 0.0 || texcoord.x > 1.0 ||
       texcoord.y < 0.0 || texcoord.y > 1.0) {
        discard;
    }
    gl_FragColor = $color_transform(texture2D(u_texture, texcoord));
}
"""  # noqa

_null_color_transform = 'vec4 pass(vec4 color) { return color; }'
_c2l = 'float cmap(vec4 color) { return (color.r + color.g + color.b) / 3.; }'


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
    **kwargs : dict
        Keyword arguments to pass to `Visual`.

    Notes
    -----
    The colormap functionality through ``cmap`` and ``clim`` are only used
    if the data are 2D.
    """
    def __init__(self, data=None, method='auto', grid=(10, 10),
                 cmap='cubehelix', clim='auto', **kwargs):
        super(ImageVisual, self).__init__(**kwargs)
        self._program = ModularProgram(VERT_SHADER, FRAG_SHADER)
        self.clim = clim
        self.cmap = cmap

        self._data = None

        self._texture = None
        self._interpolation = 'nearest'
        if data is not None:
            self.set_data(data)

        self._method = method
        self._method_used = None
        self._grid = grid
        self._need_vertex_update = True

    def set_data(self, image):
        """Set the data

        Parameters
        ----------
        image : array-like
            The image data.
        """
        data = np.asarray(image)
        if self._data is None or self._data.shape != data.shape:
            self._need_vertex_update = True
        self._data = data
        self._texture = None

    @property
    def clim(self):
        return (self._clim if isinstance(self._clim, string_types) else
                tuple(self._clim))

    @clim.setter
    def clim(self, clim):
        if isinstance(clim, string_types):
            if clim != 'auto':
                raise ValueError('clim must be "auto" if a string')
        else:
            clim = np.array(clim, float)
            if clim.shape != (2,):
                raise ValueError('clim must have two elements')
        self._clim = clim
        self._need_vertex_update = True
        self.update()

    @property
    def cmap(self):
        return self._cmap

    @cmap.setter
    def cmap(self, cmap):
        self._cmap = get_colormap(cmap)
        self.update()

    @property
    def method(self):
        return self._method
    
    @method.setter
    def method(self, m):
        if self._method != m:
            self._method = m
            self._need_vertex_update = True
            self.update()

    @property
    def size(self):
        return self._data.shape[:2][::-1]

    def _build_vertex_data(self, transforms):
        method = self._method
        grid = self._grid
        if method == 'auto':
            if transforms.get_full_transform().Linear:
                method = 'subdivide'
                grid = (1, 1)
            else:
                method = 'impostor'
        self._method_used = method

        # TODO: subdivision and impostor modes should be handled by new
        # components?
        if method == 'subdivide':
            # quads cover area of image as closely as possible
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
            
            # vertex shader provides correct texture coordinates
            self._program.frag['map_uv_to_tex'] = NullTransform()
        
        elif method == 'impostor':
            # quad covers entire view; frag. shader will deal with image shape
            vertices = np.array([[-1, -1], [1, -1], [1, 1],
                                 [-1, -1], [1, 1], [-1, 1]],
                                dtype=np.float32)
            tex_coords = vertices

            # vertex shader provides ND coordinates; 
            # fragment shader maps to texture coordinates
            self._program.vert['transform'] = NullTransform()
            self._raycast_func = Function('''
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
                    return vec4(p3.xy / $image_size, 0, 1);
                }
            ''')
            self._raycast_func['image_size'] = self.size
            self._program.frag['map_uv_to_tex'] = self._raycast_func
        
        else:
            raise ValueError("Unknown image draw method '%s'" % method)
        
        self._program['a_position'] = vertices.astype(np.float32)
        self._program['a_texcoord'] = tex_coords.astype(np.float32)
        self._need_vertex_update = False

    def _build_texture(self):
        data = self._data
        if data.dtype == np.float64:
            data = data.astype(np.float32)

        if data.ndim == 2 or data.shape[2] == 1:
            # deal with clim on CPU b/c of texture depth limits :(
            # can eventually do this by simulating 32-bit float... maybe
            clim = self._clim
            if isinstance(clim, string_types) and clim == 'auto':
                clim = np.min(data), np.max(data)
            clim = np.asarray(clim, dtype=np.float32)
            data = data - clim[0]  # not inplace so we don't modify orig data
            if clim[1] - clim[0] > 0:
                data /= clim[1] - clim[0]
            else:
                data[:] = 1 if data[0, 0] != 0 else 0
            fun = FunctionChain(None, [Function(_c2l),
                                       Function(self.cmap.glsl_map)])
            self._clim = np.array(clim)
        else:
            fun = Function(_null_color_transform)
        self._program.frag['color_transform'] = fun
        self._texture = Texture2D(data, interpolation=self._interpolation)
        self._program['u_texture'] = self._texture

    def bounds(self, mode, axis):
        """Get the bounds

        Parameters
        ----------
        mode : str
            Describes the type of boundary requested. Can be "visual", "data",
            or "mouse".
        axis : 0, 1, 2
            The axis along which to measure the bounding values, in
            x-y-z order.
        """
        if axis > 1:
            return (0, 0)
        else:
            return (0, self.size[axis])

    def draw(self, transforms):
        """Draw the visual

        Parameters
        ----------
        transforms : instance of TransformSystem
            The transforms to use.
        """
        if self._data is None:
            return

        set_state(cull_face=False)

        # upload texture is needed
        if self._texture is None:
            self._build_texture()

        # rebuild vertex buffers if needed
        if self._need_vertex_update:
            self._build_vertex_data(transforms)

        # update transform
        method = self._method_used
        if method == 'subdivide':
            self._program.vert['transform'] = transforms.get_full_transform()
        else:
            self._raycast_func['transform'] = \
                transforms.get_full_transform().inverse

        self._program.draw('triangles')
