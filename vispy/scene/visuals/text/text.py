# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

##############################################################################
# Load font into texture

import numpy as np
from copy import deepcopy

from ._sdf import SDFRenderer
from ....gloo import TextureAtlas, set_state, IndexBuffer, VertexBuffer
from ....ext.six import string_types
from ....util.fonts import _load_glyph
from ...shaders import ModularProgram
from ..visual import Visual


class TextureFont(object):
    """Gather a set of glyphs relative to a given font name and size

    Parameters
    ----------
    font : dict
        Dict with entries "face", "size", "bold", "italic".
    renderer : instance of SDFRenderer
        SDF renderer to use.
    """
    def __init__(self, font, renderer):
        self._atlas = TextureAtlas()
        self._atlas.wrapping = 'clamp_to_edge'
        self._renderer = renderer
        self._font = deepcopy(font)
        self._font['size'] = 256  # use high resolution point size for SDF
        self._lowres_size = 64  # end at this point size for storage
        assert (self._font['size'] % self._lowres_size) == 0
        # spread/border at the high-res for SDF calculation; must be chosen
        # relative to fragment_insert.glsl multiplication factor to ensure we
        # get to zero at the edges of characters
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
        if not (isinstance(char, string_types) and len(char) == 1):
            raise TypeError('index must be a 1-character string')
        if char not in self._glyphs:
            self._load_char(char)
        return self._glyphs[char]

    def _load_char(self, char):
        """Build and store a glyph corresponding to an individual character

        Parameters:
        -----------
        char : str
            A single character to be represented.
        """
        assert isinstance(char, string_types) and len(char) == 1
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
    def __init__(self):
        self._fonts = {}
        self._renderer = SDFRenderer()

    def get_font(self, face, bold=False, italic=False):
        """Get a font described by face and size"""
        key = '%s-%s-%s' % (face, bold, italic)
        if key not in self._fonts:
            font = dict(face=face, bold=bold, italic=italic)
            self._fonts[key] = TextureFont(font, self._renderer)
        return self._fonts[key]


##############################################################################
# The visual


def _text_to_vbo(text, font, anchor_x, anchor_y, lowres_size):
    """Convert text characters to VBO"""
    text_vtype = np.dtype([('a_position', 'f4', 2),
                           ('a_texcoord', 'f4', 2)])
    vertices = np.zeros(len(text) * 4, dtype=text_vtype)
    prev = None
    width = height = ascender = descender = 0
    ratio, slop = 1. / font.ratio, font.slop
    x_off = -slop
    for ii, char in enumerate(text):
        glyph = font[char]
        kerning = glyph['kerning'].get(prev, 0.) * ratio
        x0 = x_off + glyph['offset'][0] * ratio + kerning
        y0 = glyph['offset'][1] * ratio + slop
        x1 = x0 + glyph['size'][0]
        y1 = y0 - glyph['size'][1]
        u0, v0, u1, v1 = glyph['texcoords']
        position = [[x0, y0], [x0, y1], [x1, y1], [x1, y0]]
        texcoords = [[u0, v0], [u0, v1], [u1, v1], [u1, v0]]
        vi = ii * 4
        vertices['a_position'][vi:vi+4] = position
        vertices['a_texcoord'][vi:vi+4] = texcoords
        x_move = glyph['advance'] * ratio + kerning
        x_off += x_move
        ascender = max(ascender, y0 - slop)
        descender = min(descender, y1 + slop)
        width += x_move
        height = max(height, glyph['size'][1] - 2*slop)
        prev = char

    # Tight bounding box (loose would be width, font.height /.asc / .desc)
    width -= glyph['advance'] * ratio - (glyph['size'][0] - 2*slop)
    dx = dy = 0
    if anchor_y == 'top':
        dy = -ascender
    elif anchor_y in ('center', 'middle'):
        dy = -(height / 2 + descender)
    elif anchor_y == 'bottom':
        dy = -descender
    if anchor_x == 'right':
        dx = -width
    elif anchor_x == 'center':
        dx = -width / 2.
    vertices['a_position'] += (dx, dy)
    vertices['a_position'] /= lowres_size
    return VertexBuffer(vertices)


class Text(Visual):
    """Visual that displays text"""

    VERTEX_SHADER = """
        uniform sampler2D u_font_atlas;
        uniform vec4      u_color;

        attribute vec2  a_position;
        attribute vec2  a_texcoord;

        varying vec2  v_texcoord;
        varying vec4  v_color;

        void main(void) {
            v_color = u_color;
            gl_Position = $transform(vec4(a_position, 0.0, 1.0));
            v_texcoord = a_texcoord;
        }
        """

    FRAGMENT_SHADER = """
        uniform sampler2D u_font_atlas;
        uniform vec4      u_color;

        varying vec2  v_texcoord;
        varying vec4  v_color;
        const float center = 0.5;

        void main(void) {
            vec4 color = v_color;
            vec2 uv = v_texcoord.xy;
            vec4 rgb = texture2D(u_font_atlas, uv);
            float distance = rgb.r;
            float width = fwidth(distance);
            float alpha = smoothstep(center - width, center + width, distance);
            gl_FragColor = vec4(color.rgb, color.a * alpha);
        }
        """

    def __init__(self, text, color=(0., 0., 0., 1.), bold=False,
                 italic=False, face='OpenSans',
                 anchor_x='center', anchor_y='center'):
        assert isinstance(text, string_types)
        assert len(text) > 0
        assert anchor_y in ('top', 'center', 'middle', 'bottom')
        assert anchor_x in ('left', 'center', 'right')
        self._font_manager = FontManager()
        self._font = self._font_manager.get_font(face, bold, italic)
        self._program = ModularProgram(self.VERTEX_SHADER,
                                       self.FRAGMENT_SHADER)
        self._vertices = _text_to_vbo(text, self._font, anchor_x, anchor_y,
                                      self._font._lowres_size)
        self._color = color
        idx = (np.array([0, 1, 2, 0, 2, 3], np.uint32) +
               np.arange(0, 4*len(text), 4, dtype=np.uint32)[:, np.newaxis])
        self._ib = IndexBuffer(idx.ravel())

    def set_options(self):
        """Special function that is used to set the options. Automatically
        called at initialization."""
        set_state(blend=True, depth_test=False,
                  blend_func=('src_alpha', 'one_minus_src_alpha'))

    def draw(self):
        # attributes / uniforms are not available until program is built
        self._program.prepare()  # Force ModularProgram to set shaders
        self._program['u_color'] = self._color
        self._program['u_font_atlas'] = self._font._atlas
        self._program.bind(self._vertices)
        # XXX Don't know why I need this to have it "take", but I do
        set_state(blend=True, depth_test=False,
                  blend_func=('src_alpha', 'one_minus_src_alpha'))
        self._program.draw('triangles', self._ib)
