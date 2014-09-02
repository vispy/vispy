# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import numpy as np
from numpy.testing import assert_allclose
from nose.tools import assert_raises, assert_equal

from vispy.app import Canvas
from vispy.gloo import (Texture2D, Texture3D, Program, FrameBuffer,
                        ColorBuffer, DepthBuffer, set_viewport, clear)
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
    use_shape = shape + (3,)
    fbo_tex = Texture2D(shape=use_shape, dtype=np.ubyte, format='rgb')
    rbo = ColorBuffer(shape=shape)
    fbo = FrameBuffer(color=fbo_tex)
    with Canvas(size=(100, 100)) as c:
        set_viewport((0, 0) + c.size)
        with fbo:
            draw_texture(orig_tex)
        draw_texture(fbo_tex)
        out_tex = _screenshot()[::-1, :, 0].astype(np.float32)
        assert_raises(TypeError, FrameBuffer.color_buffer.fset, fbo, 1.)
        assert_raises(TypeError, FrameBuffer.depth_buffer.fset, fbo, 1.)
        assert_raises(TypeError, FrameBuffer.stencil_buffer.fset, fbo, 1.)
        fbo.color_buffer = rbo
        fbo.depth_buffer = DepthBuffer(shape)
        fbo.stencil_buffer = None
        print((fbo.color_buffer, fbo.depth_buffer, fbo.stencil_buffer))
        clear(color='black')
        with fbo:
            clear(color='black')
            draw_texture(orig_tex)
            out_rbo = _screenshot()[:, :, 0].astype(np.float32)
    assert_allclose(data * 255., out_tex, atol=1)
    assert_allclose(data * 255., out_rbo, atol=1)


@requires_application()
def test_use_texture3D():
    """Test using a 3D texture"""
    vals = [0, 200, 100, 0, 255, 0, 100]
    d, h, w = len(vals), 3, 5
    data = np.zeros((d, h, w), np.float32)
    if not has_pyopengl():
        assert_raises(ImportError, Texture3D(data))
        return

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
    uniform float i;
    void main()
    {
        gl_FragColor = texture3D(u_texture,
                                 vec3((v_pos.y+1.)/2., (v_pos.x+1.)/2., i));
        gl_FragColor.a = 1.;
    }
    """
    # populate the depth "slices" with different gray colors in the bottom left
    for ii, val in enumerate(vals):
        data[ii, :2, :3] = val / 255.
    program = Program(VERT_SHADER, FRAG_SHADER)
    program['a_pos'] = [[-1., -1.], [1., -1.], [-1., 1.], [1., 1.]]
    tex = Texture3D(data)
    assert_equal(tex.width, w)
    assert_equal(tex.height, h)
    assert_equal(tex.depth, d)
    tex.interpolation = 'nearest'
    program['u_texture'] = tex
    with Canvas(size=(100, 100)):
        for ii, val in enumerate(vals):
            set_viewport(0, 0, w, h)
            clear(color='black')
            iii = (ii + 0.5) / float(d)
            print(ii, iii)
            program['i'] = iii
            program.draw('triangle_strip')
            out = _screenshot()[:, :, 0].astype(int)[::-1]
            expected = np.zeros_like(out)
            expected[:2, :3] = val
            assert_allclose(out, expected, atol=1./255.)
