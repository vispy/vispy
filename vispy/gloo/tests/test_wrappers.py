# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import numpy as np
from numpy.testing import assert_array_equal
from nose.tools import assert_true, assert_equal, assert_raises

from vispy import gloo
from vispy.gloo import gl
from vispy.app import app_opengl_context


def test_wrappers():
    """Test gloo wrappers"""
    with app_opengl_context():
        # check presets
        assert_raises(ValueError, gloo.set_state, preset='foo')
        for state in gloo.get_state_presets().keys():
            gloo.set_state(state)
        assert_raises(ValueError, gloo.set_blend_color, (0., 0.))  # bad color
        assert_raises(TypeError, gloo.set_hint, 1, 2)  # need strs
        assert_raises(TypeError, gloo.get_parameter, 1)  # need str
        # XXX we don't have these in the namespace...?
        assert_raises(ValueError, gloo.set_hint, 'fog_hint', 'nicest')
        # test bad enum
        assert_raises(RuntimeError, gloo.set_line_width, -1)

        # check read_pixels
        assert_true(isinstance(gloo.read_pixels(), np.ndarray))
        assert_true(isinstance(gloo.read_pixels((0, 0, 1, 1)), np.ndarray))
        assert_raises(ValueError, gloo.read_pixels, (0, 0, 1))  # bad port

        # now let's (indirectly) check our set_* functions
        viewport = (0, 0, 1, 1)
        blend_color = (0., 0., 0.)
        _funs = dict(viewport=viewport,  # checked
                     depth_range=(1., 2.),
                     front_face='cw',  # checked
                     cull_face='front',
                     line_width=1.,
                     polygon_offset=(1., 1.),
                     blend_func=('zero', 'one'),
                     blend_func_separate=('zero', 'one', 'zero', 'one'),
                     blend_color=blend_color,
                     blend_equation='func_add',
                     blend_equation_separate=('func_add', 'func_add'),
                     scissor=(0, 0, 1, 1),
                     stencil_func=('never', 1, 2),
                     stencil_func_separate=('back', 'never', 1, 2),
                     stencil_mask=4,
                     stencil_mask_separate=('back', 8),
                     stencil_op=('zero', 'zero', 'zero'),
                     stencil_op_separate=('back', 'incr', 'incr', 'incr'),
                     depth_func='greater',
                     depth_mask=True,
                     color_mask=(True, True, True, True),
                     sample_coverage=(0.5, True))
        gloo.set_state(**_funs)
        gloo.clear((1., 1., 1., 1.), 0.5, 1)
        gloo.flush()
        gloo.finish()
        # check some results
        assert_array_equal(gloo.get_parameter('viewport'), viewport)
        assert_equal(gloo.get_parameter('front_face'), gl.GL_CW)
        assert_equal(gloo.get_parameter('blend_color'), blend_color + (1,))
