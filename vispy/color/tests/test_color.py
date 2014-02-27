# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
from nose.tools import assert_equal, assert_raises, assert_true
from numpy.testing import assert_array_equal, assert_allclose

from vispy.color import Color, get_color_names
from vispy.util import use_log_level


def test_color_interpretation():
    """Test basic color interpretation API"""
    # test useful ways of single color init
    r = Color('r')
    print(r)  # test repr
    r2 = Color(r)
    assert_equal(r, r2)
    r2.rgb = 0, 0, 0
    assert_equal(r2, Color('black'))
    assert_equal(r, Color('r'))  # modifying new one preserves old
    assert_equal(r, r.copy())
    assert_equal(r, Color('#ff0000'))
    assert_equal(r, Color('#FF0000FF'))
    assert_equal(r, Color('red'))
    assert_equal(r, Color('red', alpha=1.0))
    assert_equal(Color((1, 0, 0, 0.1)), Color('red', alpha=0.1))
    assert_array_equal(r.rgb.ravel(), (1., 0., 0.))
    assert_array_equal(r.rgba.ravel(), (1., 0., 0., 1.))
    assert_array_equal(r.RGBA.ravel(), (255, 0, 0, 255))

    # handling multiple colors
    rgb = Color(list('rgb'))
    print(rgb)  # multi repr
    assert_array_equal(rgb, Color(np.eye(3)))
    # complex/annoying case
    rgb = Color(['r', (0, 1, 0), '#0000ffff'])
    assert_array_equal(rgb, Color(np.eye(3)))
    assert_raises(RuntimeError, Color, ['r', np.eye(3)])  # can't nest

    # getting/setting properties
    r = Color('#ff000000')
    assert_equal(r.alpha, 0)
    r.alpha = 1.0
    assert_equal(r, Color('r'))
    r.alpha = 0
    r.rgb = (1, 0, 0)
    assert_equal(r.alpha, 0)
    r.alpha = 1
    r.rgb = 0, 1, 0
    assert_equal(r, Color('g'))
    assert_array_equal(r.rgb.ravel(), (0., 1., 0.))
    r.RGB = 255, 0, 0
    assert_equal(r, Color('r'))
    assert_array_equal(r.RGB.ravel(), (255, 0, 0))
    r.RGBA = 255, 0, 0, 0
    assert_equal(r, Color('r', alpha=0))
    w = Color()
    w.rgb = Color('r').rgb + Color('g').rgb + Color('b').rgb
    assert_equal(w, Color('white'))
    w = Color('white')
    w.darken()
    k = Color('black')
    k.lighten()
    assert_equal(w, k)
    with use_log_level('warning', record=True) as w:
        w = Color('white')
        w.value = 2
        assert_equal(len(w), 1)
    assert_equal(w, Color('white'))

    # warnings and errors
    assert_raises(ValueError, Color, '#ffii00')  # non-hex
    assert_raises(ValueError, Color, '#ff000')  # too short
    assert_raises(ValueError, Color, [0, 0])  # not enough vals
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


# Taken from known values
hsv_dict = dict(red=(0, 1, 1),
                lime=(120, 1, 1),
                yellow=(60, 1, 1),
                silver=(0, 0, 0.75),
                olive=(60, 1, 0.5),
                purple=(300, 1, 0.5),
                navy=(240, 1, 0.5))

# Taken from MATLAB script
lab_dict = dict(red=(53.2405879437448, 80.0941668344849, 67.2015369950715),
                lime=(87.7350994883189, -86.1812575110439, 83.1774770684517),
                yellow=(97.1395070397132, -21.5523924360088, 94.4757817840079),
                black=(0., 0., 0.),
                white=(100., 0., 0.),
                gray=(76.1894560083518, 0., 0.),
                olive=(73.9161173021056, -17.1284770202945, 75.0833700744091))


def test_color_conversion():
    """Test color conversions"""
    # HSV
    # test known values
    test = Color()
    for key in hsv_dict:
        c = Color(key)
        test.hsv = hsv_dict[key]
        assert_allclose(c.RGB, test.RGB, atol=1)
    test.value = 0
    assert_equal(test.value, 0)
    assert_equal(test, Color('black'))
    c = Color('black')
    assert_array_equal(c.hsv.ravel(), (0, 0, 0))
    for _ in range(50):
        hsv = np.random.rand(3)
        hsv[0] *= 360
        hsv[1] = hsv[1] * 0.99 + 0.01  # avoid ugly boundary effects
        hsv[2] = hsv[2] * 0.99 + 0.01
        c.hsv = hsv
        assert_allclose(c.hsv.ravel(), hsv)

    # Lab
    test = Color()
    for key in lab_dict:
        c = Color(key)
        test.lab = lab_dict[key]
        assert_allclose(c.rgba, test.rgba, atol=1e-4, rtol=1e-4)
        assert_allclose(test.lab.ravel(), lab_dict[key], atol=1e-4, rtol=1e-4)
    rng = np.random.RandomState(0)
    for _ in range(50):
        # Here we test RGB->Lab->RGB, since Lab->RGB->Lab will not
        # necessarily project to the exact same color for some reason...
        # This is also true in the MATLAB code.
        rgb = rng.rand(3)[np.newaxis, :]
        c.rgb = rgb
        lab = c.lab
        c.lab = lab
        assert_allclose(c.lab, lab, atol=1e-4, rtol=1e-4)
        assert_allclose(c.rgb, rgb, atol=1e-4, rtol=1e-4)
