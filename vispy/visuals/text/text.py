# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

##############################################################################
# Load font into texture

from __future__ import division


import numpy as np
from copy import deepcopy
import sys

from ._sdf_gpu import SDFRendererGPU
from ._sdf_cpu import _calc_distance_field
from ...gloo import (TextureAtlas, IndexBuffer, VertexBuffer)
from ...gloo import context
from ...gloo.wrappers import _check_valid
from ...util.fonts import _load_glyph
from ..transforms import STTransform
from ...color import ColorArray
from ..visual import Visual
from ...io import load_spatial_filters


class TextureFont(object):
    """Gather a set of glyphs relative to a given font name and size

    This currently stores characters in a `TextureAtlas` object which uses
    a 2D RGB texture to store unsigned 8-bit integer data. In the future this
    could be changed to a ``GL_R8`` texture instead of RGB when OpenGL ES
    3.0+ is standard. Since VisPy tries to stay compatible with OpenGL ES 2.0
    we are using an ``RGB`` texture. Using a single channel texture should
    improve performance by requiring less data to be sent to the GPU and to
    remote backends (jupyter notebook).

    Parameters
    ----------
    font : dict
        Dict with entries "face", "size", "bold", "italic".
    renderer : instance of SDFRenderer
        SDF renderer to use.

    """

    def __init__(self, font, renderer):
        self._atlas = TextureAtlas(dtype=np.uint8)
        self._atlas.wrapping = 'clamp_to_edge'
        self._kernel, _ = load_spatial_filters()
        self._renderer = renderer
        self._font = deepcopy(font)
        self._font['size'] = 256  # use high resolution point size for SDF
        self._lowres_size = 64  # end at this point size for storage
        assert (self._font['size'] % self._lowres_size) == 0
        # spread/border at the high-res for SDF calculation; must be chosen
        # relative to fragment_insert.glsl multiplication factor to ensure we
        # get to zero at the edges of characters
        # This is also used in SDFRendererCPU, so changing this needs to
        # propagate at least 2 other places.
        self._spread = 32
        assert self._spread % self.ratio == 0
        self._glyphs = {}

    @property
    def ratio(self):
        """Ratio of the initial high-res to final stored low-res glyph"""
        return self._font['size'] // self._lowres_size

    @property
    def slop(self):
        """Extra space along each glyph edge due to SDF borders"""
        return self._spread // self.ratio

    def __getitem__(self, char):
        if not (isinstance(char, str) and len(char) == 1):
            raise TypeError('index must be a 1-character string')
        if char not in self._glyphs:
            self._load_char(char)
        return self._glyphs[char]

    def _load_char(self, char):
        """Build and store a glyph corresponding to an individual character

        Parameters
        ----------
        char : str
            A single character to be represented.
        """
        assert isinstance(char, str) and len(char) == 1
        assert char not in self._glyphs
        # load new glyph data from font
        _load_glyph(self._font, char, self._glyphs)
        # put new glyph into the texture
        glyph = self._glyphs[char]
        bitmap = glyph['bitmap']

        # convert to padded array
        data = np.zeros((bitmap.shape[0] + 2*self._spread,
                         bitmap.shape[1] + 2*self._spread), np.uint8)
        data[self._spread:-self._spread, self._spread:-self._spread] = bitmap

        # Store, while scaling down to proper size
        height = data.shape[0] // self.ratio
        width = data.shape[1] // self.ratio
        region = self._atlas.get_free_region(width + 2, height + 2)
        if region is None:
            raise RuntimeError('Cannot store glyph')
        x, y, w, h = region
        x, y, w, h = x + 1, y + 1, w - 2, h - 2

        self._renderer.render_to_texture(data, self._atlas, (x, y), (w, h))
        u0 = x / float(self._atlas.shape[1])
        v0 = y / float(self._atlas.shape[0])
        u1 = (x+w) / float(self._atlas.shape[1])
        v1 = (y+h) / float(self._atlas.shape[0])
        texcoords = (u0, v0, u1, v1)
        glyph.update(dict(size=(w, h), texcoords=texcoords))


class FontManager(object):
    """Helper to create TextureFont instances and reuse them when possible"""

    # XXX: should store a font-manager on each context,
    # or let TextureFont use a TextureAtlas for each context
    def __init__(self, method='cpu'):
        self._fonts = {}
        if not isinstance(method, str) or \
                method not in ('cpu', 'gpu'):
            raise ValueError('method must be "cpu" or "gpu", got %s (%s)'
                             % (method, type(method)))
        if method == 'cpu':
            self._renderer = SDFRendererCPU()
        else:  # method == 'gpu':
            self._renderer = SDFRendererGPU()

    def get_font(self, face, bold=False, italic=False):
        """Get a font described by face and size"""
        key = '%s-%s-%s' % (face, bold, italic)
        if key not in self._fonts:
            font = dict(face=face, bold=bold, italic=italic)
            self._fonts[key] = TextureFont(font, self._renderer)
        return self._fonts[key]


##############################################################################
# The visual

_VERTEX_SHADER = """
    attribute float a_rotation;  // rotation in rad
    attribute vec2 a_position; // in point units
    attribute vec2 a_texcoord;
    attribute vec3 a_pos;  // anchor position
    varying vec2 v_texcoord;
    varying vec4 v_color;

    void main(void) {
        // Eventually "rot" should be handled by SRTTransform or so...
        mat4 rot = mat4(cos(a_rotation), -sin(a_rotation), 0, 0,
                        sin(a_rotation), cos(a_rotation), 0, 0,
                        0, 0, 1, 0, 0, 0, 0, 1);
        vec4 pos = $transform(vec4(a_pos, 1.0)) +
                   vec4($text_scale(rot * vec4(a_position, 0.0, 1.0)).xyz, 0.0);
        gl_Position = pos;
        v_texcoord = a_texcoord;
        v_color = $color;
    }
    """

_FRAGMENT_SHADER = """
    // Extensions for WebGL
    #extension GL_OES_standard_derivatives : enable
    #extension GL_OES_element_index_uint : enable
    #include "misc/spatial-filters.frag"
    // Adapted from glumpy with permission
    const float M_SQRT1_2 = 0.707106781186547524400844362104849039;

    uniform sampler2D u_font_atlas;
    uniform vec2 u_font_atlas_shape;
    varying vec4 v_color;
    uniform float u_npix;

    varying vec2 v_texcoord;
    const float center = 0.5;

    float contour(in float d, in float w)
    {
        return smoothstep(center - w, center + w, d);
    }

    float sample(sampler2D texture, vec2 uv, float w)
    {
        return contour(texture2D(texture, uv).r, w);
    }

    void main(void) {
        vec2 uv = v_texcoord.xy;
        vec4 rgb;

        // Use interpolation at high font sizes
        if(u_npix >= 50.0)
            rgb = CatRom2D(u_font_atlas, u_font_atlas_shape, uv);
        else
            rgb = texture2D(u_font_atlas, uv);
        float distance = rgb.r;

        // GLSL's fwidth = abs(dFdx(uv)) + abs(dFdy(uv))
        float width = 0.5 * fwidth(distance);  // sharpens a bit

        // Regular SDF
        float alpha = contour(distance, width);

        if (u_npix < 30.) {
            // Supersample, 4 extra points
            // Half of 1/sqrt2; you can play with this
            float dscale = 0.5 * M_SQRT1_2;
            vec2 duv = dscale * (dFdx(v_texcoord) + dFdy(v_texcoord));
            vec4 box = vec4(v_texcoord-duv, v_texcoord+duv);
            float asum = sample(u_font_atlas, box.xy, width)
                       + sample(u_font_atlas, box.zw, width)
                       + sample(u_font_atlas, box.xw, width)
                       + sample(u_font_atlas, box.zy, width);
            // weighted average, with 4 extra points having 0.5 weight
            // each, so 1 + 0.5*4 = 3 is the divisor
            alpha = (alpha + 0.5 * asum) / 3.0;
        }

        if (alpha <= 0) discard;

        gl_FragColor = vec4(v_color.rgb, v_color.a * alpha);
    }
    """


def _text_to_vbo(text, font, anchor_x, anchor_y, lowres_size):
    """Convert text characters to VBO"""
    # Necessary to flush commands before requesting current viewport because
    # There may be a set_viewport command waiting in the queue.
    # TODO: would be nicer if each canvas just remembers and manages its own
    # viewport, rather than relying on the context for this.
    canvas = context.get_current_canvas()
    canvas.context.flush_commands()

    text_vtype = np.dtype([('a_position', np.float32, 2),
                           ('a_texcoord', np.float32, 2)])
    vertices = np.zeros(len(text) * 4, dtype=text_vtype)
    prev = None
    width = height = ascender = descender = 0
    ratio, slop = 1. / font.ratio, font.slop
    x_off = -slop
    # Need to make sure we have a unicode string here (Py2.7 mis-interprets
    # characters like "•" otherwise)
    if sys.version[0] == '2' and isinstance(text, str):
        text = text.decode('utf-8')
    # Need to store the original viewport, because the font[char] will
    # trigger SDF rendering, which changes our viewport
    # todo: get rid of call to glGetParameter!

    # Also analyse chars with large ascender and descender, otherwise the
    # vertical alignment can be very inconsistent
    for char in 'hy':
        glyph = font[char]
        y0 = glyph['offset'][1] * ratio + slop
        y1 = y0 - glyph['size'][1]
        ascender = max(ascender, y0 - slop)
        descender = min(descender, y1 + slop)
        height = max(height, glyph['size'][1] - 2*slop)

    # Get/set the fonts whitespace length and line height (size of this ok?)
    glyph = font[' ']
    spacewidth = glyph['advance'] * ratio
    lineheight = height * 1.5

    # Added escape sequences characters: {unicode:offset,...}
    #   ord('\a') = 7
    #   ord('\b') = 8
    #   ord('\f') = 12
    #   ord('\n') = 10  => linebreak
    #   ord('\r') = 13
    #   ord('\t') = 9   => tab, set equal 4 whitespaces?
    #   ord('\v') = 11  => vertical tab, set equal 4 linebreaks?
    # If text coordinate offset > 0 -> it applies to x-direction
    # If text coordinate offset < 0 -> it applies to y-direction
    esc_seq = {7: 0, 8: 0, 9: -4, 10: 1, 11: 4, 12: 0, 13: 0}

    # Keep track of y_offset to set lines at right position
    y_offset = 0

    # When a line break occur, record the vertices index value
    vi_marker = 0
    ii_offset = 0  # Offset since certain characters won't be drawn

    # The running tracker of characters vertex index
    vi = 0

    orig_viewport = canvas.context.get_viewport()
    for ii, char in enumerate(text):
        if ord(char) in esc_seq:
            if esc_seq[ord(char)] < 0:
                # Add offset in x-direction
                x_off += abs(esc_seq[ord(char)]) * spacewidth
                width += abs(esc_seq[ord(char)]) * spacewidth
            elif esc_seq[ord(char)] > 0:
                # Add offset in y-direction and reset things in x-direction
                dx = dy = 0
                if anchor_x == 'right':
                    dx = -width
                elif anchor_x == 'center':
                    dx = -width / 2.
                vertices['a_position'][vi_marker:vi+4] += (dx, dy)
                vi_marker = vi+4
                ii_offset -= 1
                # Reset variables that affects x-direction positioning
                x_off = -slop
                width = 0
                # Add offset in y-direction
                y_offset += esc_seq[ord(char)] * lineheight
        else:
            # For ordinary characters, normal procedure
            glyph = font[char]
            kerning = glyph['kerning'].get(prev, 0.) * ratio
            x0 = x_off + glyph['offset'][0] * ratio + kerning
            y0 = glyph['offset'][1] * ratio + slop - y_offset
            x1 = x0 + glyph['size'][0]
            y1 = y0 - glyph['size'][1]
            u0, v0, u1, v1 = glyph['texcoords']
            position = [[x0, y0], [x0, y1], [x1, y1], [x1, y0]]
            texcoords = [[u0, v0], [u0, v1], [u1, v1], [u1, v0]]
            vi = (ii + ii_offset) * 4
            vertices['a_position'][vi:vi+4] = position
            vertices['a_texcoord'][vi:vi+4] = texcoords
            x_move = glyph['advance'] * ratio + kerning
            x_off += x_move
            ascender = max(ascender, y0 - slop)
            descender = min(descender, y1 + slop)
            width += x_move
            height = max(height, glyph['size'][1] - 2*slop)
            prev = char

    if orig_viewport is not None:
        canvas.context.set_viewport(*orig_viewport)

    dx = dy = 0
    if anchor_y == 'top':
        dy = -descender
    elif anchor_y in ('center', 'middle'):
        dy = (-descender - ascender) / 2
    elif anchor_y == 'bottom':
        dy = -ascender
    if anchor_x == 'right':
        dx = -width
    elif anchor_x == 'center':
        dx = -width / 2.

    # If any linebreaks occured in text, we only want to translate characters
    # in the last line in text (those after the vi_marker)
    vertices['a_position'][0:vi_marker] += (0, dy)
    vertices['a_position'][vi_marker:] += (dx, dy)
    vertices['a_position'] /= lowres_size

    return vertices


class TextVisual(Visual):
    """Visual that displays text

    Parameters
    ----------
    text : str | list of str
        Text to display. Can also be a list of strings.
        Note: support for list of str might be removed soon
        in favor of text collections.
    color : instance of Color
        Color to use.
    bold : bool
        Bold face.
    italic : bool
        Italic face.
    face : str
        Font face to use.
    font_size : float
        Point size to use.
    pos : tuple | list of tuple
        Position (x, y) or (x, y, z) of the text.
        Can also be a list of tuple if `text` is a list.
    rotation : float
        Rotation (in degrees) of the text clockwise.
    anchor_x : str
        Horizontal text anchor.
    anchor_y : str
        Vertical text anchor.
    method : str
        Rendering method for text characters. Either 'cpu' (default) or
        'gpu'. The 'cpu' method should perform better on remote backends.
        The 'gpu' method should produce higher quality results.
    font_manager : object | None
        Font manager to use (can be shared if the GLContext is shared).
    depth_test : bool
        Whether to apply depth testing. Default False. If False, the text
        behaves like an overlay that does not get hidden behind other
        visuals in the scene.
    """

    _shaders = {
        'vertex': _VERTEX_SHADER,
        'fragment': _FRAGMENT_SHADER,
    }

    def __init__(self, text=None, color='black', bold=False,
                 italic=False, face='OpenSans', font_size=12, pos=[0, 0, 0],
                 rotation=0., anchor_x='center', anchor_y='center',
                 method='cpu', font_manager=None, depth_test=False):
        Visual.__init__(self, vcode=self._shaders['vertex'], fcode=self._shaders['fragment'])
        # Check input
        valid_keys = ('top', 'center', 'middle', 'baseline', 'bottom')
        _check_valid('anchor_y', anchor_y, valid_keys)
        valid_keys = ('left', 'center', 'right')
        _check_valid('anchor_x', anchor_x, valid_keys)
        # Init font handling stuff
        # _font_manager is a temporary solution to use global mananger
        self._font_manager = font_manager or FontManager(method=method)
        self._face = face
        self._bold = bold
        self._italic = italic
        self._update_font()
        self._vertices = None
        self._color_vbo = None
        self._anchors = (anchor_x, anchor_y)
        # Init text properties
        self.color = color
        self.text = text
        self.font_size = font_size
        self.pos = pos
        self.rotation = rotation
        self._text_scale = STTransform()
        self._draw_mode = 'triangles'
        self.set_gl_state(blend=True, depth_test=depth_test, cull_face=False,
                          blend_func=('src_alpha', 'one_minus_src_alpha'))
        self.freeze()

    @property
    def text(self):
        """The text string"""
        return self._text

    @text.setter
    def text(self, text):
        if isinstance(text, list):
            assert all(isinstance(t, str) for t in text)
        if text is None:
            text = []
        self._text = text
        self._vertices = None
        self._pos_changed = True  # need to update this as well
        self._color_changed = True
        self.update()

    @property
    def anchors(self):
        return self._anchors

    @anchors.setter
    def anchors(self, a):
        self._anchors = a
        self._vertices = None
        self._pos_changed = True
        self.update()

    @property
    def font_size(self):
        """The font size (in points) of the text"""
        return self._font_size

    @font_size.setter
    def font_size(self, size):
        self._font_size = max(0.0, float(size))
        self.update()

    @property
    def color(self):
        """The color of the text"""
        return self._color

    @color.setter
    def color(self, color):
        self._color = ColorArray(color)
        self._color_changed = True
        self.update()

    @property
    def rotation(self):
        """The rotation of the text (clockwise, in degrees)"""
        return self._rotation * 180. / np.pi

    @rotation.setter
    def rotation(self, rotation):
        self._rotation = np.asarray(rotation) * np.pi / 180.
        self._pos_changed = True
        self.update()

    @property
    def pos(self):
        """The position of the text anchor in the local coordinate frame"""
        return self._pos

    @pos.setter
    def pos(self, pos):
        pos = np.atleast_2d(pos).astype(np.float32)
        if pos.shape[1] == 2:
            pos = np.concatenate((pos, np.zeros((pos.shape[0], 1),
                                                np.float32)), axis=1)
        elif pos.shape[1] != 3:
            raise ValueError('pos must have 2 or 3 elements')
        elif pos.shape[0] == 0:
            raise ValueError('at least one position must be given')
        self._pos = pos
        self._pos_changed = True
        self.update()

    def _prepare_draw(self, view):
        # attributes / uniforms are not available until program is built
        if len(self.text) == 0:
            return False
        if self._vertices is None:
            text = self.text
            if isinstance(text, str):
                text = [text]
            n_char = sum(len(t) for t in text)
            # we delay creating vertices because it requires a context,
            # which may or may not exist when the object is initialized
            self._vertices = np.concatenate([
                _text_to_vbo(t, self._font, self._anchors[0], self._anchors[1],
                             self._font._lowres_size) for t in text])
            self._vertices = VertexBuffer(self._vertices)
            idx = (np.array([0, 1, 2, 0, 2, 3], np.uint32) +
                   np.arange(0, 4*n_char, 4, dtype=np.uint32)[:, np.newaxis])
            self._index_buffer = IndexBuffer(idx.ravel())
            self.shared_program.bind(self._vertices)
            # This is necessary to reset the GL drawing state after generating
            # SDF textures. A better way would be to enable the state to be
            # pushed/popped by the context.
            self._configure_gl_state()
        if self._pos_changed:
            # now we promote pos to the proper shape (attribute)
            text = self.text
            if not isinstance(text, str):
                repeats = [4 * len(t) for t in text]
                text = ''.join(text)
            else:
                repeats = [4 * len(text)]
            n_text = len(repeats)
            pos = self.pos
            # Rotation
            _rot = self._rotation
            if isinstance(_rot, (int, float)):
                _rot = np.full((pos.shape[0],), self._rotation)
            _rot = np.asarray(_rot)
            if _rot.shape[0] < n_text:
                _rep = [1] * (len(_rot) - 1) + [n_text - len(_rot) + 1]
                _rot = np.repeat(_rot, _rep, axis=0)
            _rot = np.repeat(_rot[:n_text], repeats, axis=0)
            self.shared_program['a_rotation'] = _rot.astype(np.float32)
            # Position
            if pos.shape[0] < n_text:
                _rep = [1] * (len(pos) - 1) + [n_text - len(pos) + 1]
                pos = np.repeat(pos, _rep, axis=0)
            pos = np.repeat(pos[:n_text], repeats, axis=0)
            assert pos.shape[0] == self._vertices.size == len(_rot)
            self.shared_program['a_pos'] = pos
            self._pos_changed = False
        if self._color_changed:
            # now we promote color to the proper shape (varying)
            text = self.text
            if not isinstance(text, str):
                repeats = [4 * len(t) for t in text]
                text = ''.join(text)
            else:
                repeats = [4 * len(text)]
            n_text = len(repeats)
            color = self.color.rgba
            if color.shape[0] < n_text:
                color = np.repeat(color,
                                  [1]*(len(color)-1) + [n_text-len(color)+1],
                                  axis=0)
            color = np.repeat(color[:n_text], repeats, axis=0)
            assert color.shape[0] == self._vertices.size
            self._color_vbo = VertexBuffer(color)
            self.shared_program.vert['color'] = self._color_vbo
            self._color_changed = False

        transforms = self.transforms
        n_pix = (self._font_size / 72.) * transforms.dpi  # logical pix
        tr = transforms.get_transform('document', 'render')
        px_scale = (tr.map((1, 0)) - tr.map((0, 1)))[:2]
        self._text_scale.scale = px_scale * n_pix
        self.shared_program.vert['text_scale'] = self._text_scale
        self.shared_program['u_npix'] = n_pix
        self.shared_program['u_kernel'] = self._font._kernel
        self.shared_program['u_color'] = self._color.rgba
        self.shared_program['u_font_atlas'] = self._font._atlas
        self.shared_program['u_font_atlas_shape'] = self._font._atlas.shape[:2]

    def _prepare_transforms(self, view):
        self._pos_changed = True
        # Note that we access `view_program` instead of `shared_program`
        # because we do not want this function assigned to other views.
        tr = view.transforms.get_transform()
        view.view_program.vert['transform'] = tr  # .simplified()

    def _compute_bounds(self, axis, view):
        return self._pos[:, axis].min(), self._pos[:, axis].max()

    @property
    def face(self):
        return self._face

    @face.setter
    def face(self, value):
        self._face = value
        self._update_font()

    @property
    def bold(self):
        return self._bold

    @bold.setter
    def bold(self, value):
        self._bold = value
        self._update_font()

    @property
    def italic(self):
        return self._italic

    @italic.setter
    def italic(self, value):
        self._italic = value
        self._update_font()

    def _update_font(self):
        self._font = self._font_manager.get_font(self._face, self._bold, self._italic)
        self.update()


class SDFRendererCPU(object):
    """Render SDFs using the CPU."""

    # This should probably live in _sdf_cpu.pyx, but doing so makes
    # debugging substantially more annoying
    def render_to_texture(self, data, texture, offset, size):
        sdf = (data / 255).astype(np.float32)  # from ubyte -> float
        h, w = sdf.shape
        tex_w, tex_h = size
        _calc_distance_field(sdf, w, h, 32)
        # This tweaking gets us a result more similar to the GPU SDFs,
        # for which the text rendering code was optimized
        sdf = 2 * sdf - 1.
        sdf = np.sign(sdf) * np.abs(sdf) ** 0.75 / 2. + 0.5
        # Downsample using NumPy (because we can't guarantee SciPy)
        xp = (np.arange(w) + 0.5) / float(w)
        x = (np.arange(tex_w) + 0.5) / float(tex_w)
        bitmap = np.array([np.interp(x, xp, ss) for ss in sdf])
        xp = (np.arange(h) + 0.5) / float(h)
        x = (np.arange(tex_h) + 0.5) / float(tex_h)
        bitmap = np.array([np.interp(x, xp, ss) for ss in bitmap.T]).T
        assert bitmap.shape[::-1] == size
        # convert to uint8
        bitmap = (bitmap * 255).astype(np.uint8)
        # convert single channel to RGB by repeating
        bitmap = np.tile(bitmap[..., np.newaxis],
                         (1, 1, 3))
        texture[offset[1]:offset[1] + size[1],
                offset[0]:offset[0] + size[0], :] = bitmap
