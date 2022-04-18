# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
from numpy.testing import assert_array_equal, assert_allclose

from vispy.color import (Color, ColorArray, get_color_names,
                         Colormap,
                         get_color_dict, get_colormap, get_colormaps)
from vispy.visuals.shaders import Function
from vispy.util import use_log_level
from vispy.testing import (run_tests_if_main, assert_equal, assert_raises,
                           assert_true)


def test_color():
    """Basic tests for Color class"""
    x = Color('white')
    assert_array_equal(x.rgba, [1.] * 4)
    assert_array_equal(x.rgb, [1.] * 3)
    assert_array_equal(x.RGBA, [255] * 4)
    assert_array_equal(x.RGB, [255] * 3)
    assert_equal(x.value, 1.)
    assert_equal(x.alpha, 1.)
    x.rgb = [0, 0, 1]
    assert_array_equal(x.hsv, [240, 1, 1])
    assert_equal(x.hex, '#0000ff')
    x.hex = '#00000000'
    assert_array_equal(x.rgba, [0.]*4)


def test_color_array():
    """Basic tests for ColorArray class"""
    x = ColorArray(['r', 'g', 'b'])
    assert_array_equal(x.rgb, np.eye(3))
    # Test ColorArray.__getitem__.
    assert isinstance(x[0], ColorArray)
    assert isinstance(x[:], ColorArray)
    assert_array_equal(x.rgba[:], x[:].rgba)
    assert_array_equal(x.rgba[0], x[0].rgba.squeeze())
    assert_array_equal(x.rgba[1:3], x[1:3].rgba)
    assert_raises(ValueError, x.__getitem__, (0, 1))
    # Test ColorArray.__setitem__.
    x[0] = 0
    assert_array_equal(x.rgba[0, :], np.zeros(4))
    assert_array_equal(x.rgba, x[:].rgba)
    x[1] = 1
    assert_array_equal(x[1].rgba, np.ones((1, 4)))
    x[:] = .5
    assert_array_equal(x.rgba, .5 * np.ones((3, 4)))
    assert_raises(ValueError, x.__setitem__, (0, 1), 0)

    # test hsv color space colors
    x = ColorArray(color_space="hsv", color=[(0, 0, 1),
                                             (0, 0, 0.5), (0, 0, 0)])
    assert_array_equal(x.rgba[0], [1, 1, 1, 1])
    assert_array_equal(x.rgba[1], [0.5, 0.5, 0.5, 1])
    assert_array_equal(x.rgba[2], [0, 0, 0, 1])

    x = ColorArray(color_space="hsv")
    assert_array_equal(x.rgba[0], [0, 0, 0, 1])

    x = ColorArray([Color((0, 0, 0)), Color((1, 1, 1))])
    assert len(x.rgb) == 2
    x = ColorArray([ColorArray((0, 0, 0)), ColorArray((1, 1, 1))])
    assert len(x.rgb) == 2


def test_color_interpretation():
    """Test basic color interpretation API"""
    # test useful ways of single color init
    r = ColorArray('r')
    print(r)  # test repr
    r2 = ColorArray(r)
    assert_equal(r, r2)
    r2.rgb = 0, 0, 0
    assert_equal(r2, ColorArray('black'))
    assert_equal(r, ColorArray('r'))  # modifying new one preserves old
    assert_equal(r, r.copy())
    assert_equal(r, ColorArray('#ff0000'))
    assert_equal(r, ColorArray('#FF0000FF'))
    assert_equal(r, ColorArray('red'))
    assert_equal(r, ColorArray('red', alpha=1.0))
    assert_equal(ColorArray((1, 0, 0, 0.1)), ColorArray('red', alpha=0.1))
    assert_array_equal(r.rgb.ravel(), (1., 0., 0.))
    assert_array_equal(r.rgba.ravel(), (1., 0., 0., 1.))
    assert_array_equal(r.RGBA.ravel(), (255, 0, 0, 255))

    # handling multiple colors
    rgb = ColorArray(list('rgb'))
    print(rgb)  # multi repr
    assert_array_equal(rgb, ColorArray(np.eye(3)))
    # complex/annoying case
    rgb = ColorArray(['r', (0, 1, 0), '#0000ffff'])
    assert_array_equal(rgb, ColorArray(np.eye(3)))
    assert_raises(RuntimeError, ColorArray, ['r', np.eye(3)])  # can't nest

    # getting/setting properties
    r = ColorArray('#ffff')
    assert_equal(r, ColorArray('white'))
    r = ColorArray('#ff000000')
    assert_true('turquoise' in get_color_names())  # make sure our JSON loaded
    assert_equal(r.alpha, 0)
    r.alpha = 1.0
    assert_equal(r, ColorArray('r'))
    r.alpha = 0
    r.rgb = (1, 0, 0)
    assert_equal(r.alpha, 0)
    assert_equal(r.hex, ['#ff0000'])
    r.alpha = 1
    r.hex = '00ff00'
    assert_equal(r, ColorArray('g'))
    assert_array_equal(r.rgb.ravel(), (0., 1., 0.))
    r.RGB = 255, 0, 0
    assert_equal(r, ColorArray('r'))
    assert_array_equal(r.RGB.ravel(), (255, 0, 0))
    r.RGBA = 255, 0, 0, 0
    assert_equal(r, ColorArray('r', alpha=0))
    w = ColorArray()
    w.rgb = ColorArray('r').rgb + ColorArray('g').rgb + ColorArray('b').rgb
    assert_equal(w, ColorArray('white'))
    w = ColorArray('white')
    assert_equal(w, w.darker().lighter())
    assert_equal(w, w.darker(0.1).darker(-0.1))
    w2 = w.darker()
    assert_true(w != w2)
    w.darker(copy=False)
    assert_equal(w, w2)
    with use_log_level('warning', record=True, print_msg=False) as w:
        w = ColorArray('white')
        w.value = 2
        assert_equal(len(w), 1)
    assert_equal(w, ColorArray('white'))

    # warnings and errors
    assert_raises(ValueError, ColorArray, '#ffii00')  # non-hex
    assert_raises(ValueError, ColorArray, '#ff000')  # too short
    assert_raises(ValueError, ColorArray, [0, 0])  # not enough vals
    assert_raises(ValueError, ColorArray, [2, 0, 0])  # val > 1
    assert_raises(ValueError, ColorArray, [-1, 0, 0])  # val < 0
    c = ColorArray([2., 0., 0.], clip=True)  # val > 1
    assert_true(np.all(c.rgb <= 1))
    c = ColorArray([-1., 0., 0.], clip=True)  # val < 0
    assert_true(np.all(c.rgb >= 0))

    # make sure our color dict works
    for key in get_color_names():
        assert_true(ColorArray(key))
    assert_raises(ValueError, ColorArray, 'foo')  # unknown color error

    _color_dict = get_color_dict()
    assert isinstance(_color_dict, dict)
    assert set(_color_dict.keys()) == set(get_color_names())


# Taken from known values
hsv_dict = dict(red=(0, 1, 1),
                lime=(120, 1, 1),
                yellow=(60, 1, 1),
                silver=(0, 0, 0.75),
                olive=(60, 1, 0.5),
                purple=(300, 1, 0.5),
                navy=(240, 1, 0.5))

# Taken from skimage conversions
lab_dict = dict(red=(53.2405879437448, 80.0941668344849, 67.2015369950715),
                lime=(87.7350994883189, -86.1812575110439, 83.1774770684517),
                yellow=(97.1395070397132, -21.5523924360088, 94.4757817840079),
                black=(0., 0., 0.),
                white=(100., 0., 0.),
                gray=(53.5850240, 0., 0.),
                olive=(51.86909754, -12.93002583, 56.67467593))


def test_color_conversion():
    """Test color conversions"""
    # HSV
    # test known values
    test = ColorArray()
    for key in hsv_dict:
        c = ColorArray(key)
        test.hsv = hsv_dict[key]
        assert_allclose(c.RGB, test.RGB, atol=1)
    test.value = 0
    assert_equal(test.value, 0)
    assert_equal(test, ColorArray('black'))
    c = ColorArray('black')
    assert_array_equal(c.hsv.ravel(), (0, 0, 0))
    rng = np.random.RandomState(0)
    for _ in range(50):
        hsv = rng.rand(3)
        hsv[0] *= 360
        hsv[1] = hsv[1] * 0.99 + 0.01  # avoid ugly boundary effects
        hsv[2] = hsv[2] * 0.99 + 0.01
        c.hsv = hsv
        assert_allclose(c.hsv.ravel(), hsv, rtol=1e-4, atol=1e-4)

    # Lab
    test = ColorArray()
    for key in lab_dict:
        c = ColorArray(key)
        test.lab = lab_dict[key]
        assert_allclose(c.rgba, test.rgba, atol=1e-4, rtol=1e-4)
        assert_allclose(test.lab.ravel(), lab_dict[key], atol=1e-4, rtol=1e-4)
    for _ in range(50):
        # boundaries can have ugly rounding errors in some parameters
        rgb = (rng.rand(3)[np.newaxis, :] * 0.9 + 0.05)
        c.rgb = rgb
        lab = c.lab
        c.lab = lab
        assert_allclose(c.lab, lab, atol=1e-4, rtol=1e-4)
        assert_allclose(c.rgb, rgb, atol=1e-4, rtol=1e-4)


def test_colormap_interpolation():
    """Test interpolation routines for colormaps."""
    import vispy.color.colormap as c
    assert_raises(AssertionError, c._glsl_step, [0., 1.],)

    for fun in (c._glsl_step, c._glsl_mix):
        assert_raises(AssertionError, fun, controls=[0.1, 1.],)
        assert_raises(AssertionError, fun, controls=[0., .9],)
        assert_raises(AssertionError, fun, controls=[0.1, .9],)

    # Interpolation tests.
    color_0 = np.array([1., 0., 0.])
    color_1 = np.array([0., 1., 0.])
    color_2 = np.array([0., 0., 1.])

    colors_00 = np.vstack((color_0, color_0))
    colors_01 = np.vstack((color_0, color_1))
    colors_11 = np.vstack((color_1, color_1))
    # colors_012 = np.vstack((color_0, color_1, color_2))
    colors_021 = np.vstack((color_0, color_2, color_1))

    controls_2 = np.array([0., 1.])
    controls_3 = np.array([0., .25, 1.])
    x = np.array([-1., 0., 0.1, 0.4, 0.5, 0.6, 1., 2.])[:, None]

    mixed_2 = c.mix(colors_01, x, controls_2)
    mixed_3 = c.mix(colors_021, x, controls_3)

    for y in mixed_2, mixed_3:
        assert_allclose(y[:2, :], colors_00)
        assert_allclose(y[-2:, :], colors_11)

    assert_allclose(mixed_2[:, -1], np.zeros(len(y)))


def test_colormap_gradient():
    """Test gradient colormaps."""
    cm = Colormap(['r', 'g'])
    assert_allclose(cm[-1].rgba, [[1, 0, 0, 1]])
    assert_allclose(cm[0.].rgba, [[1, 0, 0, 1]])
    assert_allclose(cm[0.5].rgba, [[.5, .5, 0, 1]])
    assert_allclose(cm[1.].rgba, [[0, 1, 0, 1]])

    cm = Colormap(['r', 'g', 'b'])
    assert_allclose(cm[-1].rgba, [[1, 0, 0, 1]])
    assert_allclose(cm[0.].rgba, [[1, 0, 0, 1]])
    assert_allclose(cm[.5].rgba, [[0, 1, 0, 1]])
    assert_allclose(cm[1].rgba, [[0, 0, 1, 1]])
    assert_allclose(cm[2].rgba, [[0, 0, 1, 1]])

    cm = Colormap(['r', 'g', 'b'], [0., 0.1, 1.0])
    assert_allclose(cm[-1].rgba, [[1, 0, 0, 1]])
    assert_allclose(cm[0.].rgba, [[1, 0, 0, 1]])
    assert_allclose(cm[.1].rgba, [[0, 1, 0, 1]])
    assert_allclose(cm[1].rgba, [[0, 0, 1, 1]], 1e-6, 1e-6)
    assert_allclose(cm[2].rgba, [[0, 0, 1, 1]], 1e-6, 1e-6)


def test_colormap_discrete():
    """Test discrete colormaps."""
    cm = Colormap(['r', 'g'], interpolation='zero')
    assert_allclose(cm[-1].rgba, [[1, 0, 0, 1]])
    assert_allclose(cm[0.].rgba, [[1, 0, 0, 1]])
    assert_allclose(cm[0.49].rgba, [[1, 0, 0, 1]])
    assert_allclose(cm[0.51].rgba, [[0, 1, 0, 1]])
    assert_allclose(cm[1.].rgba, [[0, 1, 0, 1]])

    cm = Colormap(['r', 'g', 'b'], interpolation='zero')
    assert_allclose(cm[-1].rgba, [[1, 0, 0, 1]])
    assert_allclose(cm[0.].rgba, [[1, 0, 0, 1]])
    assert_allclose(cm[.32].rgba, [[1, 0, 0, 1]])
    assert_allclose(cm[.34].rgba, [[0, 1, 0, 1]])
    assert_allclose(cm[.66].rgba, [[0, 1, 0, 1]])
    assert_allclose(cm[.67].rgba, [[0, 0, 1, 1]])
    assert_allclose(cm[.99].rgba, [[0, 0, 1, 1]])
    assert_allclose(cm[1].rgba, [[0, 0, 1, 1]])
    assert_allclose(cm[1.1].rgba, [[0, 0, 1, 1]])

    cm = Colormap(['r', 'g', 'b'], [0., 0.1, 0.8, 1.0],
                  interpolation='zero')
    assert_allclose(cm[-1].rgba, [[1, 0, 0, 1]])
    assert_allclose(cm[0.].rgba, [[1, 0, 0, 1]])
    assert_allclose(cm[.099].rgba, [[1, 0, 0, 1]])
    assert_allclose(cm[.101].rgba, [[0, 1, 0, 1]])
    assert_allclose(cm[.799].rgba, [[0, 1, 0, 1]])
    assert_allclose(cm[.801].rgba, [[0, 0, 1, 1]])
    assert_allclose(cm[1].rgba, [[0, 0, 1, 1]], 1e-6, 1e-6)
    assert_allclose(cm[2].rgba, [[0, 0, 1, 1]], 1e-6, 1e-6)


def test_colormap():
    """Test named colormaps."""
    autumn = get_colormap('autumn')
    assert autumn.glsl_map != ""
    assert len(autumn[0.]) == 1
    assert len(autumn[0.5]) == 1
    assert len(autumn[1.]) == 1
    assert len(autumn[[0., 0.5, 1.]]) == 3
    assert len(autumn[np.array([0., 0.5, 1.])]) == 3

    fire = get_colormap('fire')
    assert_array_equal(fire[0].rgba, np.ones((1, 4)))
    assert_array_equal(fire[1].rgba, np.array([[1, 0, 0, 1]]))

    grays = get_colormap('grays')
    assert_array_equal(grays[.5].rgb, np.ones((1, 3)) * .5)

    hot = get_colormap('hot')
    assert_allclose(hot[0].rgba, [[0, 0, 0, 1]], 1e-6, 1e-6)
    assert_allclose(hot[0.5].rgba, [[1, .52272022, 0, 1]], 1e-6, 1e-6)
    assert_allclose(hot[1.].rgba, [[1, 1, 1, 1]], 1e-6, 1e-6)

    # Test the GLSL and Python mapping.
    for name in get_colormaps():
        colormap = get_colormap(name)
        Function(colormap.glsl_map)
        colors = colormap[np.linspace(-2., 2., 50)]
        assert colors.rgba.min() >= 0
        assert colors.rgba.max() <= 1


def test_normalize():
    """Test the _normalize() function."""
    from vispy.color.colormap import _normalize
    for x in (-1, 0., .5, 1., 10., 20):
        assert _normalize(x) == .5
    assert_allclose(_normalize((-1., 0., 1.)), (0., .5, 1.))
    assert_allclose(_normalize((-1., 0., 1.), 0., 1.),
                    (0., 0., 1.))
    assert_allclose(_normalize((-1., 0., 1.), 0., 1., clip=False),
                    (-1., 0., 1.))

    y = _normalize(np.random.randn(100, 5), -10., 10.)
    assert_allclose([y.min(), y.max()], [0.2975, 1-0.2975], 1e-1, 1e-1)


run_tests_if_main()
