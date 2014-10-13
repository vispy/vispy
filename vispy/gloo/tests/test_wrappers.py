# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import numpy as np
from numpy.testing import assert_array_equal, assert_allclose
from nose.tools import assert_true, assert_equal, assert_raises

from vispy import gloo
from vispy.gloo import gl
from vispy.app import Canvas
from vispy.testing import requires_application, run_tests_if_main
from vispy.gloo import read_pixels


def assert_cmd_raises(E, fun, *args, **kwargs):
    gloo.flush()  # no error here
    fun(*args, **kwargs)
    assert_raises(E, gloo.flush)


@requires_application()
def test_wrappers():
    """Test gloo wrappers"""
    with Canvas():
        gl.use_gl('desktop debug')
        gloo.clear('#112233')  # make it so that there's something non-zero
        # check presets
        assert_raises(ValueError, gloo.set_state, preset='foo')
        for state in gloo.get_state_presets().keys():
            gloo.set_state(state)
        assert_raises(ValueError, gloo.set_blend_color, (0., 0.))  # bad color
        assert_raises(TypeError, gloo.set_hint, 1, 2)  # need strs
        # this doesn't exist in ES 2.0 namespace
        assert_cmd_raises(ValueError, gloo.set_hint, 'fog_hint', 'nicest')
        # test bad enum
        assert_raises(RuntimeError, gloo.set_line_width, -1)

        # check read_pixels
        x = gloo.read_pixels()
        assert_true(isinstance(x, np.ndarray))
        assert_true(isinstance(gloo.read_pixels((0, 0, 1, 1)), np.ndarray))
        assert_raises(ValueError, gloo.read_pixels, (0, 0, 1))  # bad port
        y = gloo.read_pixels(alpha=False, out_type=np.ubyte)
        assert_equal(y.shape, x.shape[:2] + (3,))
        assert_array_equal(x[..., :3], y)
        y = gloo.read_pixels(out_type='float')
        assert_allclose(x/255., y)

        # now let's (indirectly) check our set_* functions
        viewport = (0, 0, 1, 1)
        blend_color = (0., 0., 0.)
        _funs = dict(viewport=viewport,  # checked
                     hint=('generate_mipmap_hint', 'nicest'),
                     depth_range=(1., 2.),
                     front_face='cw',  # checked
                     cull_face='front',
                     line_width=1.,
                     polygon_offset=(1., 1.),
                     blend_func=('zero', 'one'),
                     blend_color=blend_color,
                     blend_equation='func_add',
                     scissor=(0, 0, 1, 1),
                     stencil_func=('never', 1, 2, 'back'),
                     stencil_mask=4,
                     stencil_op=('zero', 'zero', 'zero', 'back'),
                     depth_func='greater',
                     depth_mask=True,
                     color_mask=(True, True, True, True),
                     sample_coverage=(0.5, True))
        gloo.set_state(**_funs)
        gloo.clear((1., 1., 1., 1.), 0.5, 1)
        gloo.flush()
        gloo.finish()
        # check some results
        assert_array_equal(gl.glGetParameter(gl.GL_VIEWPORT), viewport)
        assert_equal(gl.glGetParameter(gl.GL_FRONT_FACE), gl.GL_CW)
        assert_equal(gl.glGetParameter(gl.GL_BLEND_COLOR), blend_color + (1,))


@requires_application()
def test_read_pixels():
    """Test read_pixels to ensure that the image is not flipped"""
    # Create vertices
    vPosition = np.array([[-1, 1], [0, 1],  # For drawing a square to top left
                          [-1, 0], [0, 0]], np.float32)

    VERT_SHADER = """ // simple vertex shader
    attribute vec2 a_position;
    void main (void) {
        gl_Position = vec4(a_position, 0., 1.0);
    }
    """

    FRAG_SHADER = """ // simple fragment shader
    void main()
    {
        gl_FragColor = vec4(1,1,1,1);
    }
    """

    with Canvas() as c:
        gloo.set_viewport(0, 0, *c.size)
        c._program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        c._program['a_position'] = gloo.VertexBuffer(vPosition)
        gloo.clear(color='black')
        c._program.draw('triangle_strip')

        # Check if the return of read_pixels is the same as our drawing
        img = read_pixels(alpha=False)
        assert_equal(img.shape[:2], c.size[::-1])
        top_left = sum(img[0, 0])
        assert_true(top_left > 0)  # Should be > 0 (255*4)
        # Sum of the pixels in top right + bottom left + bottom right corners
        corners = sum(img[0, -1] + img[-1, 0] + img[-1, -1])
        assert_true(corners == 0)  # Should be all 0
        gloo.flush()
        gloo.finish()


run_tests_if_main()
