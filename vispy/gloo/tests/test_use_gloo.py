# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import numpy as np
from numpy.testing import assert_allclose
from nose.tools import assert_raises

from vispy.app import Canvas
from vispy.gloo import (Texture2D, Texture3D, Program, FrameBuffer,
                        set_viewport)
from vispy.gloo.util import draw_texture, _screenshot
from vispy.testing import requires_application, has_pyopengl


@requires_application()
def test_use_textures():
    """Test using textures and FBO"""
    assert_raises(ValueError, Texture2D, np.zeros((2, 2, 3), np.float32),
                  format='rgba')  # format and data size mismatch


@requires_application()
def test_use_framebuffer():
    """Test drawing to a framebuffer"""
    shape = (100, 100)
    data = np.random.rand(*shape).astype(np.float32)
    orig_tex = Texture2D(data)
    fbo_tex = Texture2D(shape=shape+(3,), dtype=np.ubyte, format='rgb')
    fbo = FrameBuffer(color=fbo_tex)
    with Canvas(size=(100, 100)) as c:
        with fbo:
            set_viewport(0, 0, *c.size)
            draw_texture(orig_tex)
        draw_texture(fbo_tex)
        out = _screenshot()[::-1, :, 0].astype(np.float32)
    assert_allclose(data * 255., out, atol=1)


@requires_application()
def test_use_texture3D():
    """Test using a 3D texture"""
    data = np.zeros((5, 6, 7), np.float32)
    if not has_pyopengl():
        assert_raises(ImportError, Texture3D(data))
        return

    assert_raises(ValueError, Texture3D, np.zeros((1, 1, 1, 5), np.float32))

    VERT_SHADER = """
    attribute vec2 a_pos;
    varying vec2 v_pos;

    void main (void)
    {
        v_pos = a_pos;
        gl_Position = vec4(a_pos, 0., 1.);
    }
    """

    FRAG_SHADER = """
    uniform sampler3D u_texture;
    varying vec2 v_pos;
    void main()
    {
        gl_FragColor = texture3D(u_texture, vec3(0., v_pos));
    }
    """
    program = Program(VERT_SHADER, FRAG_SHADER)
    program['a_pos'] = [[0., 0.], [0., 1.], [1., 0.], [1., 1.]]
    program['u_texture'] = Texture3D(data)
    with Canvas(size=(100, 100)):
        # program.draw()  # XXX This should work?
        pass
