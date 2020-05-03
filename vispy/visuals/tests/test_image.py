# -*- coding: utf-8 -*-
import numpy as np

from vispy.scene.visuals import Image
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved, downsample


@requires_application()
def test_image():
    """Test image visual"""
    size = (100, 50)
    with TestingCanvas(size=size, bgcolor='w') as c:
        image = Image(cmap='grays', clim=[0, 1], parent=c.scene)
        for three_d in (True, False):
            shape = (size[1]-10, size[0]-10) + ((3,) if three_d else ())
            np.random.seed(379823)
            data = np.random.rand(*shape)
            image.set_data(data)
            assert_image_approved(c.render(), "visuals/image%s.png" %
                                  ("_rgb" if three_d else "_mono"))


@requires_application()
def test_image_clims_and_gamma():
    """Test image visual with clims and gamma on shader."""
    size = (40, 40)
    with TestingCanvas(size=size, bgcolor="w") as c:
        for three_d in (True,):
            shape = size + ((3,) if three_d else ())
            np.random.seed(0)
            image = Image(cmap='grays', clim=[0, 1], parent=c.scene)
            data = np.random.rand(*shape)
            image.set_data(data)
            rendered = c.render()
            _dtype = rendered.dtype
            shape_ratio = rendered.shape[0] // data.shape[0]
            rendered1 = downsample(rendered, shape_ratio, axis=(0, 1)).astype(_dtype)
            predicted = _make_rgba(data)
            assert np.allclose(predicted, rendered1, atol=1)

            # adjust contrast limits
            new_clim = (0.3, 0.8)
            image.clim = new_clim
            rendered2 = downsample(c.render(), shape_ratio, axis=(0, 1)).astype(_dtype)
            scaled_data = np.clip((data - new_clim[0]) / np.diff(new_clim)[0], 0, 1)
            predicted = _make_rgba(scaled_data)
            assert np.allclose(predicted, rendered2, atol=1)
            assert not np.allclose(rendered1, rendered2, atol=10)

            # adjust gamma
            image.gamma = 2
            rendered3 = downsample(c.render(), shape_ratio, axis=(0, 1)).astype(_dtype)
            predicted = _make_rgba(scaled_data ** 2)
            assert np.allclose(
                predicted.astype(np.float), rendered3.astype(np.float), atol=2
            )
            assert not np.allclose(
                rendered2.astype(np.float), rendered3.astype(np.float), atol=10
            )


def _make_rgba(array):
    if array.ndim == 2:
        out = np.stack([array] * 4, axis=2)
        out[:, :, 3] = 1
    else:
        out = np.concatenate((array, np.ones((*array.shape[:2], 1))), axis=2)
    return np.round((out.astype(np.float) * 255)).astype(np.uint8)


run_tests_if_main()
