# -*- coding: utf-8 -*-

import pytest
import numpy as np
from vispy import scene

from vispy.testing import (TestingCanvas, requires_application,
                           run_tests_if_main, requires_pyopengl,
                           raises)
from vispy.testing.image_tester import assert_image_approved, downsample
from vispy.testing.rendered_array_tester import compare_render, max_for_dtype


@requires_pyopengl()
def test_volume():
    vol = np.zeros((20, 20, 20), 'float32')
    vol[8:16, 8:16, :] = 1.0

    # Create
    V = scene.visuals.Volume(vol)
    assert V.clim == (0, 1)
    assert V.method == 'mip'
    assert V.interpolation == 'linear'

    # Set wrong data
    with raises(ValueError):
        V.set_data(np.zeros((20, 20), 'float32'))

    # Clim
    V.set_data(vol, (0.5, 0.8))
    assert V.clim == (0.5, 0.8)
    with raises(ValueError):
        V.set_data((0.5, 0.8, 1.0))

    # Method
    V.method = 'iso'
    assert V.method == 'iso'

    # Interpolation
    V.interpolation = 'nearest'
    assert V.interpolation == 'nearest'

    # Step size
    V.relative_step_size = 1.1
    assert V.relative_step_size == 1.1
    # Disallow 0 step size to avoid GPU stalling
    with raises(ValueError):
        V.relative_step_size = 0


@requires_pyopengl()
@requires_application()
def test_volume_draw():
    with TestingCanvas(bgcolor='k', size=(100, 100)) as c:
        v = c.central_widget.add_view()
        v.camera = 'turntable'
        v.camera.fov = 70
        # Create
        np.random.seed(2376)
        vol = np.random.normal(size=(20, 20, 20), loc=0.5, scale=0.2)
        vol[8:16, 8:16, :] += 1.0
        scene.visuals.Volume(vol, parent=v.scene)  # noqa
        v.camera.set_range()
        assert_image_approved(c.render(), 'visuals/volume.png')


@requires_pyopengl()
@requires_application()
# @pytest.mark.parametrize('data_on_init', [False, True])
# @pytest.mark.parametrize('clim_on_init', [False, True])
# @pytest.mark.parametrize('num_channels', [0, 1, 3, 4])
@pytest.mark.parametrize('texture_format', [None, '__dtype__', 'auto'])
# @pytest.mark.parametrize('input_dtype', [np.uint8, np.uint16, np.float32, np.float64])
# @pytest.mark.parametrize('texture_format', [None, np.float32, np.uint8, 'auto'])
def test_volume_clims_and_gamma(texture_format):
    """Test volume visual with clims and gamma on shader.

    Test is parameterized based on ``texture_format`` and should produce
    relatively the same results for each format.

    Currently just using np.ones since the angle of view made more complicated samples
    challenging, but this confirms gamma and clims works in the shader.
    The VolumeVisual defaults to the "grays" colormap so although we compare
    data using RGBA arrays, each R/G/B channel should be the same.

    """
    size = (40, 40)
    input_dtype = np.float64
    if texture_format == '__dtype__':
        texture_format = input_dtype
    np.random.seed(0)  # make tests the same every time
    data = _make_test_data(size[:1] * 3, input_dtype)
    with TestingCanvas(size=size, bgcolor="k") as c:
        v = c.central_widget.add_view(border_width=0)
        volume = scene.visuals.Volume(
            data,
            clim=(0, 1),
            interpolation='nearest',
            parent=v.scene,
            method='mip',
            texture_format=texture_format,
        )
        v.camera = 'arcball'
        v.camera.fov = 0
        v.camera.scale_factor = 40.0
        # for some reason the x dimension has to be a little bit off center
        # or else the render doesn't match the data
        v.camera.center = (19.6, 19.5, 19.5)

        rendered = c.render()
        _dtype = rendered.dtype
        shape_ratio = rendered.shape[0] // data.shape[0]
        rendered1 = downsample(rendered, shape_ratio, axis=(0, 1)).astype(_dtype)
        predicted = data.max(axis=1)
        compare_render(predicted, rendered1)

        # adjust contrast limits
        new_clim = (0.3, 0.8)
        volume.clim = new_clim
        rendered2 = downsample(c.render(), shape_ratio, axis=(0, 1)).astype(_dtype)
        scaled_data = np.clip((data - new_clim[0]) / np.diff(new_clim)[0], 0, 1)
        predicted = scaled_data.max(axis=1)
        compare_render(predicted, rendered2, previous_render=rendered)

        # adjust gamma
        volume.gamma = 1.5
        rendered3 = downsample(c.render(), shape_ratio, axis=(0, 1)).astype(_dtype)
        predicted = (scaled_data ** volume.gamma).max(axis=1)
        compare_render(predicted, rendered3, previous_render=rendered2)


def _make_test_data(shape, input_dtype):
    one_third = shape[0] // 3
    two_third = 2 * one_third
    data = np.zeros(shape, dtype=np.float64)
    # 0.00 | 1.00 | 0.00
    # 0.50 | 0.00 | 0.25
    # 0.00 | 0.00 | 0.00
    data[:, :one_third, one_third:two_third] = 1.0
    data[:, one_third:two_third, :one_third] = 0.5
    data[:, one_third:two_third, two_third:] = 0.25
    max_val = max_for_dtype(input_dtype)
    if max_val != 1:
        data *= max_val
    data = data.astype(input_dtype)
    return data


@requires_pyopengl()
def test_set_data_does_not_change_input():
    # Create volume
    V = scene.visuals.Volume(np.zeros((20, 20, 20)))

    # calling Volume.set_data() should NOT alter the values of the input array
    # regardless of data type
    vol = np.random.randint(0, 200, (20, 20, 20))
    for dtype in ['uint8', 'int16', 'uint16', 'float32', 'float64']:
        vol_copy = np.array(vol, dtype=dtype, copy=True)
        # setting clim so that normalization would otherwise change the data
        V.set_data(vol_copy, clim=(0, 200))
        assert np.allclose(vol, vol_copy)

    # for those using float32 who want to avoid the copy operation,
    # using set_data() with `copy=False` should be expected to alter the data.
    vol2 = np.array(vol, dtype='float32', copy=True)
    assert np.allclose(vol, vol2)
    V.set_data(vol2, clim=(0, 200), copy=False)
    assert not np.allclose(vol, vol2)


run_tests_if_main()
