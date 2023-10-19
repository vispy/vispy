# -*- coding: utf-8 -*-
from unittest import mock

from vispy.scene import Image, PanZoomCamera
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main, IS_CI)
from vispy.testing.image_tester import assert_image_approved, downsample

import numpy as np
import pytest

from vispy.testing.rendered_array_tester import compare_render, max_for_dtype


@requires_application()
@pytest.mark.parametrize('is_3d', [True, False])
def test_image(is_3d):
    """Test image visual"""
    size = (100, 50)
    with TestingCanvas(size=size, bgcolor='w') as c:
        image = Image(cmap='grays', clim=[0, 1], parent=c.scene)
        shape = (size[1]-10, size[0]-10) + ((3,) if is_3d else ())
        np.random.seed(379823)
        data = np.random.rand(*shape)
        image.set_data(data)
        assert_image_approved(c.render(), "visuals/image%s.png" %
                              ("_rgb" if is_3d else "_mono"))

        # change to auto clims after first draw
        image.clim = "auto"
        assert_image_approved(c.render(), "visuals/image%s.png" %
                              ("_rgb" if is_3d else "_mono"))


@requires_application()
@pytest.mark.parametrize('gamma', [None, -0.5, "0.5"])
def test_bad_init_gamma(gamma):
    """Test creating an Image with a bad gamma value."""
    with TestingCanvas(size=(100, 50)) as c:
        pytest.raises((TypeError, ValueError), Image, gamma=gamma, parent=c.scene)


def _make_test_data(shape, input_dtype):
    data = np.random.random_sample(shape)
    if data.ndim == 3 and data.shape[-1] == 4:
        # RGBA - make alpha fully opaque
        data[..., -1] = 1.0
    max_val = max_for_dtype(input_dtype)
    if max_val != 1:
        data *= max_val
    data = data.astype(input_dtype)
    return data


def _set_image_data(image, data, should_fail):
    if should_fail:
        pytest.raises(ValueError, image.set_data, data)
        return
    image.set_data(data)


def _get_orig_and_new_clims(input_dtype):
    new_clim = (0.3, 0.8)
    max_val = max_for_dtype(input_dtype)
    if np.issubdtype(input_dtype, np.integer):
        new_clim = (int(new_clim[0] * max_val), int(new_clim[1] * max_val))
    return (0, max_val), new_clim


@requires_application()
@pytest.mark.parametrize('data_on_init', [False, True])
@pytest.mark.parametrize('clim_on_init', [False, True])
@pytest.mark.parametrize('num_channels', [0, 1, 3, 4])
@pytest.mark.parametrize('texture_format', [None, '__dtype__', 'auto'])
@pytest.mark.parametrize('input_dtype', [np.uint8, np.uint16, np.float32, np.float64])
def test_image_clims_and_gamma(input_dtype, texture_format, num_channels,
                               clim_on_init, data_on_init):
    """Test image visual with clims and gamma on shader."""
    size = (80, 80)
    if texture_format == '__dtype__':
        texture_format = input_dtype
    shape = size + (num_channels,) if num_channels > 0 else size
    np.random.seed(0)
    data = _make_test_data(shape, input_dtype)
    orig_clim, new_clim = _get_orig_and_new_clims(input_dtype)
    # 16-bit integers and above seem to have precision loss when scaled on the CPU
    is_16int_cpu_scaled = (np.dtype(input_dtype).itemsize >= 2 and
                           np.issubdtype(input_dtype, np.integer) and
                           texture_format is None)
    clim_atol = 2 if is_16int_cpu_scaled else 1
    gamma_atol = 3 if is_16int_cpu_scaled else 2

    kwargs = {}
    if clim_on_init:
        kwargs['clim'] = orig_clim
    if data_on_init:
        kwargs['data'] = data
    # default is RGBA, anything except auto requires reformat
    set_data_fails = (num_channels != 4 and
                      texture_format is not None and
                      texture_format != 'auto')

    with TestingCanvas(size=size[::-1], bgcolor="w") as c:
        image = Image(cmap='grays', texture_format=texture_format,
                      parent=c.scene, **kwargs)
        if not data_on_init:
            _set_image_data(image, data, set_data_fails)
            if set_data_fails:
                return
        rendered = c.render()
        _dtype = rendered.dtype
        shape_ratio = rendered.shape[0] // data.shape[0]
        rendered1 = downsample(rendered, shape_ratio, axis=(0, 1)).astype(_dtype)
        compare_render(data, rendered1)

        # adjust color limits
        image.clim = new_clim
        rendered2 = downsample(c.render(), shape_ratio, axis=(0, 1)).astype(_dtype)
        scaled_data = (np.clip(data, new_clim[0], new_clim[1]) - new_clim[0]) / (new_clim[1] - new_clim[0])
        compare_render(scaled_data, rendered2, rendered1, atol=clim_atol)

        # adjust gamma
        image.gamma = 2
        rendered3 = downsample(c.render(), shape_ratio, axis=(0, 1)).astype(_dtype)
        compare_render(scaled_data ** 2, rendered3, rendered2, atol=gamma_atol)


@pytest.mark.xfail(IS_CI, reason="CI environments sometimes treat NaN as 0")
@requires_application()
@pytest.mark.parametrize('texture_format', [None, 'auto'])
def test_image_nan_single_band(texture_format):
    size = (40, 40)
    data = np.ones((40, 40))
    data[:5, :5] = np.nan
    data[:5, -5:] = 0

    expected = (np.ones((40, 40, 4)) * 255).astype(np.uint8)
    # black square
    expected[:5, -5:, :3] = 0
    if texture_format is None:
        # CPU scaling's NaNs get converted to 0s
        expected[:5, :5, :3] = 0
    else:
        # GPU receives NaNs
        # nan - transparent square
        expected[:5, :5, 0] = 0
        expected[:5, :5, 1] = 255  # match the 'green' background
        expected[:5, :5, 2] = 0

    with TestingCanvas(size=size[::-1], bgcolor=(0, 1, 0)) as c:
        Image(data, cmap='grays',
              texture_format=texture_format, parent=c.scene)
        rendered = c.render()
        np.testing.assert_allclose(rendered, expected)


@requires_application()
@pytest.mark.parametrize('num_bands', [3, 4])
@pytest.mark.parametrize('texture_format', [None, 'auto'])
def test_image_nan_rgb(texture_format, num_bands):
    size = (40, 40)
    data = np.ones((40, 40, num_bands))
    data[:5, :5, :3] = np.nan  # upper left - RGB all NaN
    data[:5, 20:25, 0] = np.nan  # upper middle - R NaN
    data[:5, -5:, :3] = 0  # upper right - opaque RGB black square
    data[-5:, -5:, :] = np.nan  # lower right RGBA all NaN
    if num_bands == 4:
        data[-5:, :5, 3] = np.nan  # lower left - Alpha NaN

    expected = (np.ones((40, 40, 4)) * 255).astype(np.uint8)
    # upper left - NaN goes to opaque black
    expected[:5, :5, :3] = 0
    # upper middle -> NaN R goes to 0
    expected[:5, 20:25, 0] = 0
    # upper right - opaque RGB black square
    expected[:5, -5:, :3] = 0
    # lower right - NaN RGB/A goes to 0
    # RGBA case - we see the green background behind the image
    expected[-5:, -5:, 0] = 0
    expected[-5:, -5:, 2] = 0
    if num_bands == 3:
        # RGB case - opaque black because Alpha defaults 1
        expected[-5:, -5:, 1] = 0
    # lower left - NaN Alpha goes to 0
    if num_bands == 4:
        # see the green background behind the image
        expected[-5:, :5, 0] = 0
        expected[-5:, :5, 2] = 0

    with TestingCanvas(size=size[::-1], bgcolor=(0, 1, 0)) as c:
        Image(data, cmap='grays',
              texture_format=texture_format, parent=c.scene)
        rendered = c.render()
        np.testing.assert_allclose(rendered, expected)


@requires_application()
@pytest.mark.parametrize('num_channels', [0, 1, 3, 4])
@pytest.mark.parametrize('texture_format', [None, 'auto'])
def test_image_equal_clims(texture_format, num_channels):
    """Test image visual with equal clims."""
    size = (40, 40)
    input_dtype = np.uint8
    shape = size + (num_channels,) if num_channels > 0 else size
    np.random.seed(0)
    data = _make_test_data(shape, input_dtype)
    with TestingCanvas(size=size[::-1], bgcolor="w") as c:
        Image(data, cmap='viridis',
              texture_format=texture_format,
              clim=(128.0, 128.0),
              parent=c.scene)
        rendered = c.render()[..., :3]

        if num_channels >= 3:
            # RGBs don't have colormaps
            assert rendered.sum() == 0
            return

        # not all black
        assert rendered.sum() != 0
        # not all white
        assert rendered.sum() != 255 * rendered.size
        # should be all the same value
        r_unique = np.unique(rendered[..., 0])
        g_unique = np.unique(rendered[..., 1])
        b_unique = np.unique(rendered[..., 2])
        assert r_unique.size == 1
        assert g_unique.size == 1
        assert b_unique.size == 1


@requires_application()
def test_image_vertex_updates():
    """Test image visual coordinates are only built when needed."""
    size = (40, 40)
    with TestingCanvas(size=size, bgcolor="w") as c:
        shape = size + (3,)
        np.random.seed(0)
        image = Image(cmap='grays', clim=[0, 1], parent=c.scene)
        with mock.patch.object(
                image, '_build_vertex_data',
                wraps=image._build_vertex_data) as build_vertex_mock:
            data = np.random.rand(*shape)
            image.set_data(data)
            c.render()
            build_vertex_mock.assert_called_once()
            build_vertex_mock.reset_mock()  # reset the count to 0

            # rendering again shouldn't cause vertex coordinates to be built
            c.render()
            build_vertex_mock.assert_not_called()

            # changing to data of the same shape shouldn't cause it
            data = np.zeros_like(data)
            image.set_data(data)
            c.render()
            build_vertex_mock.assert_not_called()

            # changing to another shape should
            data = data[:-5, :-5]
            image.set_data(data)
            c.render()
            build_vertex_mock.assert_called_once()


@requires_application()
@pytest.mark.parametrize(
    ("dtype", "init_clim"),
    [
        (np.float32, "auto"),
        (np.float32, (0, 5)),
        (np.uint8, "auto"),
        (np.uint8, (0, 5)),
    ]
)
def test_change_clim_float(dtype, init_clim):
    """Test that with an image of floats, clim is correctly set from the first try.

    See https://github.com/vispy/vispy/pull/2245.
    """
    size = (40, 40)
    np.random.seed(0)
    data = (np.random.rand(*size) * 100).astype(dtype)

    with TestingCanvas(size=size[::-1], bgcolor="w") as c:
        image = Image(data=data, clim=init_clim, parent=c.scene)

        # needed to properly initialize the canvas
        c.render()

        image.clim = 0, 10
        rendered1 = c.render()
        # set clim to same values
        image.clim = 0, 10
        rendered2 = c.render()

        assert np.allclose(rendered1, rendered2)


@requires_application()
def test_image_interpolation():
    """Test different interpolations"""
    size = (81, 81)
    data = np.array([[0, 1]], dtype=int)
    left = (40, 0)
    right = (40, 80)
    center_left = (40, 39)
    center = (40, 40)
    center_right = (40, 41)
    white = (255, 255, 255, 255)
    black = (0, 0, 0, 255)
    gray = (128, 128, 128, 255)

    with TestingCanvas(size=size[::-1], bgcolor="w") as c:
        view = c.central_widget.add_view(border_width=0)
        view.camera = PanZoomCamera((0, 0, 2, 1))
        image = Image(data=data, cmap='grays',
                      parent=view.scene)

        # needed to properly initialize the canvas
        render = c.render()

        image.interpolation = 'nearest'
        render = c.render()
        assert np.allclose(render[left], black)
        assert np.allclose(render[right], white)
        assert np.allclose(render[center_left], black)
        assert np.allclose(render[center_right], white)

        image.interpolation = 'bilinear'
        render = c.render()
        assert np.allclose(render[left], black)
        assert np.allclose(render[right], white)
        assert np.allclose(render[center], gray, atol=5)  # we just want gray, this is not quantitative

        image.interpolation = 'custom'
        image.custom_kernel = np.array([[0]])  # no sampling
        render = c.render()
        assert np.allclose(render[left], black)
        assert np.allclose(render[right], black)
        assert np.allclose(render[center], black)

        image.custom_kernel = np.array([[1]])  # same as linear
        render = c.render()
        assert np.allclose(render[left], black)
        assert np.allclose(render[right], white)
        assert np.allclose(render[center], gray, atol=5)  # we just want gray, this is not quantitative


@requires_application()
def test_image_set_data_different_dtype():
    size = (80, 80)
    data = np.array([[0, 127]], dtype=np.int8)
    left = (40, 10)
    right = (40, 70)
    white = (255, 255, 255, 255)
    black = (0, 0, 0, 255)

    with TestingCanvas(size=size[::-1], bgcolor="w") as c:
        view = c.central_widget.add_view()
        view.camera = PanZoomCamera((0, 0, 2, 1))
        image = Image(data=data, cmap='grays', clim=[0, 127],
                      parent=view.scene)

        render = c.render()
        assert np.allclose(render[left], black)
        assert np.allclose(render[right], white)

        # same data as float should change nothing
        image.set_data(data.astype(np.float32))
        render = c.render()
        assert np.allclose(render[left], black)
        assert np.allclose(render[right], white)

        # something inverted, different dtype
        new_data = np.array([[127, 0]], dtype=np.float16)
        image.set_data(new_data)
        render = c.render()
        assert np.allclose(render[left], white)
        assert np.allclose(render[right], black)

        # out of bounds should clip (2000 > 127)
        new_data = np.array([[0, 2000]], dtype=np.float64)
        image.set_data(new_data)
        render = c.render()
        assert np.allclose(render[left], black)
        assert np.allclose(render[right], white)


run_tests_if_main()
