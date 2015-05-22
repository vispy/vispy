# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from ..ext.six import string_types
from .wrappers import read_pixels


def _screenshot(viewport=None, alpha=True):
    """ Take a screenshot using glReadPixels. Not sure where to put this
    yet, so a private function for now. Used in make.py.

    Parameters
    ----------
    viewport : array-like | None
        4-element list of x, y, w, h parameters. If None (default),
        the current GL viewport will be queried and used.
    alpha : bool
        If True (default), the returned array has 4 elements (RGBA).
        Otherwise, it has 3 (RGB)

    Returns
    -------
    pixels : array
        3D array of pixels in np.uint8 format
    """
    # gl.glReadBuffer(gl.GL_BACK)  Not avaliable in ES 2.0
    return read_pixels(viewport, alpha)


KEYWORDS = set(['active', 'asm', 'cast', 'class', 'common', 'default',
                'double', 'dvec2', 'dvec3', 'dvec4', 'enum', 'extern',
                'external', 'filter', 'fixed', 'flat', 'fvec2', 'fvec3',
                'fvec4', 'goto', 'half', 'hvec2', 'hvec3', 'hvec4', 'iimage1D',
                'iimage1DArray', 'iimage2D', 'iimage2DArray', 'iimage3D',
                'iimageBuffer', 'iimageCube', 'image1D', 'image1DArray',
                'image1DArrayShadow', 'image1DShadow', 'image2D',
                'image2DArray', 'image2DArrayShadow', 'image2DShadow',
                'image3D', 'imageBuffer', 'imageCube', 'inline', 'input',
                'interface', 'long', 'namespace', 'noinline', 'output',
                'packed', 'partition', 'public', 'row_major', 'sampler1D',
                'sampler1DShadow', 'sampler2DRect', 'sampler2DRectShadow',
                'sampler2DShadow', 'sampler3D', 'sampler3DRect', 'short',
                'sizeof', 'static', 'superp', 'switch', 'template', 'this',
                'typedef', 'uimage1D', 'uimage1DArray', 'uimage2D',
                'uimage2DArray', 'uimage3D', 'uimageBuffer', 'uimageCube',
                'union', 'unsigned', 'using', 'volatile'])


def check_variable(name):
    """
    Return None if *name* is expected to be a valid variable name in any GLSL
    version. Otherwise, return a string describing the problem.
    """
    # Limit imposed by glGetActive* in pyopengl
    if len(name) > 31:
        return ("Variable names >31 characters may not function on some "
                "systems.")

    return check_identifier(name)


def check_identifier(name):
    if '__' in name:
        return "Identifiers may not contain double-underscores."
    
    if name[:3] == 'gl_' or name[:3] == 'GL_':
        return "Identifiers may not begin with gl_ or GL_."

    if name in KEYWORDS:
        return "Identifier is a reserved keyword."


def check_enum(enum, name=None, valid=None):
    """ Get lowercase string representation of enum.
    """
    name = name or 'enum'
    # Try to convert
    res = None
    if isinstance(enum, int):
        if hasattr(enum, 'name') and enum.name.startswith('GL_'):
            res = enum.name[3:].lower()
    elif isinstance(enum, string_types):
        res = enum.lower()
    # Check
    if res is None:
        raise ValueError('Could not determine string represenatation for'
                         'enum %r' % enum)
    elif valid and res not in valid:
        raise ValueError('Value of %s must be one of %r, not %r' % 
                         (name, valid, enum))
    return res


vert_draw = """
attribute vec2 a_position;
attribute vec2 a_texcoord;
varying vec2 v_uv;

void main(void) {
    v_uv = a_texcoord.xy;
    gl_Position = vec4(a_position, 0, 1);
}
"""

frag_draw = """
uniform sampler2D u_texture;
varying vec2 v_uv;

void main(void) {
    gl_FragColor = texture2D(u_texture, v_uv).rgba;
}
"""


def draw_texture(tex):
    """Draw a 2D texture to the current viewport

    Parameters
    ----------
    tex : instance of Texture2D
        The texture to draw.
    """
    from .program import Program
    program = Program(vert_draw, frag_draw)
    program['u_texture'] = tex
    program['a_position'] = [[-1., -1.], [-1., 1.], [1., -1.], [1., 1.]]
    program['a_texcoord'] = [[0., 1.], [0., 0.], [1., 1.], [1., 0.]]
    program.draw('triangle_strip')
