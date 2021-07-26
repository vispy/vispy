# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import sys

import numpy as np
from numpy.testing import assert_allclose
import pytest

from vispy.app import Canvas
from vispy.gloo import (Texture2D, Texture3D, Program, FrameBuffer,
                        RenderBuffer, set_viewport, clear)
from vispy.gloo.util import draw_texture, _screenshot
from vispy.testing import (requires_application, has_pyopengl,
                           run_tests_if_main,
                           assert_raises, assert_equal, IS_TRAVIS_CI)


@requires_application()
def test_use_textures():
    """Test using textures and FBO"""
    assert_raises(ValueError, Texture2D, np.zeros((2, 2, 3), np.float32),
                  format='rgba')  # format and data size mismatch


@requires_application()
def test_use_framebuffer():
    """Test drawing to a framebuffer"""
    shape = (100, 300)  # for some reason Windows wants a tall window...
    data = np.random.rand(*shape).astype(np.float32)
    use_shape = shape + (3,)
    with Canvas(size=shape[::-1]) as c:
        c.app.process_events()
        c.set_current()
        if c.app.backend_name.lower() == 'pyqt5':
            # PyQt5 on OSX for some reason sets this to 1024x768...
            c.size = shape[::-1]
        c.app.process_events()
        orig_tex = Texture2D(data)
        fbo_tex = Texture2D(use_shape, format='rgb')
        rbo = RenderBuffer(shape, 'color')
        fbo = FrameBuffer(color=fbo_tex)
        c.context.glir.set_verbose(True)
        assert c.size == shape[::-1]
        c.set_current()
        set_viewport((0, 0) + c.size)
        with fbo:
            draw_texture(orig_tex)
        draw_texture(fbo_tex)
        out_tex = _screenshot()[::-1, :, 0].astype(np.float32)
        assert out_tex.shape == c.size[::-1]
        assert_raises(TypeError, FrameBuffer.color_buffer.fset, fbo, 1.)
        assert_raises(TypeError, FrameBuffer.depth_buffer.fset, fbo, 1.)
        assert_raises(TypeError, FrameBuffer.stencil_buffer.fset, fbo, 1.)
        fbo.color_buffer = rbo
        fbo.depth_buffer = RenderBuffer(shape)
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
    with Canvas(size=(100, 100)) as c:
        if not has_pyopengl():
            t = Texture3D(data)
            assert_raises(ImportError, t.glir.flush, c.context.shared.parser)
            return
        program = Program(VERT_SHADER, FRAG_SHADER)
        program['a_pos'] = [[-1., -1.], [1., -1.], [-1., 1.], [1., 1.]]
        tex = Texture3D(data, interpolation='nearest')
        assert_equal(tex.width, w)
        assert_equal(tex.height, h)
        assert_equal(tex.depth, d)
        program['u_texture'] = tex
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


@pytest.mark.xfail(IS_TRAVIS_CI and 'darwin' in sys.platform,
                   reason='Travis OSX causes segmentation fault on this test for an unknown reason.')
@requires_application()
def test_use_uniforms():
    """Test using uniform arrays"""
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
    varying vec2 v_pos;
    uniform vec3 u_color[2];

    void main()
    {
        gl_FragColor = vec4((u_color[0] + u_color[1]) / 2., 1.);
    }
    """
    shape = (500, 500)
    with Canvas(size=shape) as c:
        c.set_current()
        c.context.glir.set_verbose(True)
        assert_equal(c.size, shape[::-1])
        shape = (3, 3)
        set_viewport((0, 0) + shape)
        program = Program(VERT_SHADER, FRAG_SHADER)
        program['a_pos'] = [[-1., -1.], [1., -1.], [-1., 1.], [1., 1.]]
        program['u_color'] = np.ones((2, 3))
        c.context.clear('k')
        c.set_current()
        program.draw('triangle_strip')
        out = _screenshot()
        assert_allclose(out[:, :, 0] / 255., np.ones(shape), atol=1. / 255.)

        # now set one element
        program['u_color[1]'] = np.zeros(3, np.float32)
        c.context.clear('k')
        program.draw('triangle_strip')
        out = _screenshot()
        assert_allclose(out[:, :, 0] / 255., 127.5 / 255. * np.ones(shape),
                        atol=1. / 255.)

        # and the other
        assert_raises(ValueError, program.__setitem__, 'u_color',
                      np.zeros(3, np.float32))
        program['u_color'] = np.zeros((2, 3), np.float32)
        program['u_color[0]'] = np.ones(3, np.float32)
        c.context.clear((0.33,) * 3)
        program.draw('triangle_strip')
        out = _screenshot()
        assert_allclose(out[:, :, 0] / 255., 127.5 / 255. * np.ones(shape),
                        atol=1. / 255.)

run_tests_if_main()
