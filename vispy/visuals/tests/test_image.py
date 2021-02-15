# -*- coding: utf-8 -*-
from unittest import mock

from vispy.scene.visuals import Image
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved, downsample

import numpy as np
import pytest


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


def _make_test_data(shape, input_dtype):
    data = np.random.random_sample(shape)
    if data.ndim == 3 and data.shape[-1] == 4:
        # RGBA - make alpha fully opaque
        data[..., -1] = 1.0
    if input_dtype == np.uint8:
        data *= 255.0
    data = data.astype(input_dtype)
    return data


def _compare_render(orig_data, rendered_data, previous_render=None, atol=1):
    predicted = _make_rgba(orig_data)
    np.testing.assert_allclose(rendered_data, predicted, atol=atol)
    if previous_render is not None:
        # assert not allclose
        pytest.raises(AssertionError, np.testing.assert_allclose,
                      rendered_data, previous_render, atol=10)


def _set_image_data(image, data, should_fail):
    if should_fail:
        pytest.raises(ValueError, image.set_data, data)
        return
    image.set_data(data)


def _get_orig_and_new_clims(input_dtype):
    new_clim = (0.3, 0.8)
    max_val = 255 if input_dtype == np.uint8 else 1.0
    if input_dtype == np.uint8:
        new_clim = (int(new_clim[0] * max_val), int(new_clim[1] * max_val))
    return (0, max_val), new_clim


@requires_application()
@pytest.mark.parametrize('data_on_init', [False, True])
@pytest.mark.parametrize('clim_on_init', [False, True])
@pytest.mark.parametrize('num_channels', [0, 1, 3, 4])
@pytest.mark.parametrize('texture_format', [None, '__dtype__', 'auto'])
@pytest.mark.parametrize('input_dtype', [np.uint8, np.float32, np.float64])
def test_image_clims_and_gamma(input_dtype, texture_format, num_channels,
                               clim_on_init, data_on_init):
    """Test image visual with clims and gamma on shader."""
    size = (40, 40)
    if texture_format == '__dtype__':
        texture_format = input_dtype
    shape = size + (num_channels,) if num_channels > 0 else size
    np.random.seed(0)
    data = _make_test_data(shape, input_dtype)
    orig_clim, new_clim = _get_orig_and_new_clims(input_dtype)

    kwargs = {}
    if clim_on_init:
        kwargs['clim'] = orig_clim
    if data_on_init:
        kwargs['data'] = data
    # default is RGBA, anything except auto requires reformat
    set_data_fails = (num_channels != 4 and
                      texture_format is not None and
                      texture_format != 'auto')

    with TestingCanvas(size=size, bgcolor="w") as c:
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
        _compare_render(data, rendered1)

        # adjust color limits
        image.clim = new_clim
        rendered2 = downsample(c.render(), shape_ratio, axis=(0, 1)).astype(_dtype)
        scaled_data = (np.clip(data, new_clim[0], new_clim[1]) - new_clim[0]) / (new_clim[1] - new_clim[0])
        _compare_render(scaled_data, rendered2, rendered1)

        # adjust gamma
        image.gamma = 2
        rendered3 = downsample(c.render(), shape_ratio, axis=(0, 1)).astype(_dtype)
        _compare_render(scaled_data ** 2, rendered3, rendered2, atol=2)


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


def _make_rgba(data_in):
    max_val = 255 if data_in.dtype == np.uint8 else 1
    if data_in.ndim == 3 and data_in.shape[-1] == 1:
        data_in = data_in.squeeze()

    if data_in.ndim == 2:
        out = np.stack([data_in] * 4, axis=2)
        out[:, :, 3] = max_val
    elif data_in.shape[-1] == 3:
        out = np.concatenate((data_in, np.ones((*data_in.shape[:2], 1)) * max_val), axis=2)
    else:
        out = data_in
    return np.round((out.astype(np.float) * 255 / max_val)).astype(np.uint8)


run_tests_if_main()
