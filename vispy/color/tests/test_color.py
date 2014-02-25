# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
from nose.tools import assert_equal, assert_raises, assert_true
from numpy.testing import assert_array_equal

from vispy.color import Color, get_color_names
from vispy.util import use_log_level


def test_color_interpretation():
    """Test basic color interpretation API"""
    # test useful ways of single color init
    r = Color('r')
    print(r)  # test repr
    assert_equal(r, Color('#ff0000'))
    assert_equal(r, Color('red'))
    assert_equal(r, Color('red', alpha=1.0))
    assert_equal(Color((1, 0, 0, 0.1)), Color('red', alpha=0.1))

    # warnings and errors
    assert_raises(ValueError, Color, '#ffii00')  # non-hex
    assert_raises(ValueError, Color, '#ff000')  # too short
    with use_log_level('warning', record=True) as w:
        c = Color([2., 0., 0.])  # val > 1
        assert_true(np.all(c.rgb <= 1))
        c = Color([-1., 0., 0.])  # val < 0
        assert_true(np.all(c.rgb >= 0))
        assert_equal(len(w), 2)  # caught warnings
    # make sure our color dict works
    for key in get_color_names():
        assert_true(Color(key))
    assert_raises(ValueError, Color, 'foo')  # unknown color error
    assert_array_equal(r.rgb[0], (1., 0., 0.))
    assert_array_equal(r.rgba[0], (1., 0., 0., 1.))
    assert_array_equal(r.RGBA[0], (255, 0, 0, 255))

    # multiple colors
    rgb = Color(list('rgb'))
    print(rgb)  # multi repr
    assert_array_equal(rgb, Color(np.eye(3)))
    # complex/annoying case
    rgb = Color(['r', (0, 1, 0), '#0000ff'])
    assert_array_equal(rgb, Color(np.eye(3)))
    assert_raises(RuntimeError, Color, ['r', np.eye(3)])  # can't nest


def test_color_conversion():
    """Test color conversions"""
    pass
