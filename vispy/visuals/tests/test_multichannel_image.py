#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the MultiChannelImageVisual."""

from vispy.scene.visuals import MultiChannelImage

import numpy as np
from vispy.testing import TestingCanvas, run_tests_if_main, requires_application


@requires_application()
def test_rgb_multiband_visual():
    size = (400, 600)
    with TestingCanvas(size=size[::-1]) as c:
        r_data = np.random.rand(*size)
        g_data = np.random.rand(*size)
        b_data = np.random.rand(*size)
        image = MultiChannelImage(
            [r_data, None, None],
            parent=c.scene)

        # Assign only R
        result = c.render()
        r_result = result[..., 0]
        g_result = result[..., 1]
        b_result = result[..., 2]
        assert not np.allclose(r_result, 0)
        np.testing.assert_allclose(g_result, 0)
        np.testing.assert_allclose(b_result, 0)

        # Add B
        image.set_data([r_data, None, b_data])
        image.clim = ("auto", "auto", "auto")
        result = c.render()
        r_result = result[..., 0]
        g_result = result[..., 1]
        b_result = result[..., 2]
        assert not np.allclose(r_result, 0)
        np.testing.assert_allclose(g_result, 0)
        assert not np.allclose(b_result, 0)

        # Unset R, add G
        image.set_data([None, g_data, b_data])
        image.clim = ("auto", "auto", "auto")
        result = c.render()
        r_result = result[..., 0]
        g_result = result[..., 1]
        b_result = result[..., 2]
        np.testing.assert_allclose(r_result, 0)
        assert not np.allclose(g_result, 0)
        assert not np.allclose(b_result, 0)


@requires_application()
def test_la_multiband_visual():
    size = (400, 600)
    with TestingCanvas(size=size[::-1]) as c:
        l_data = np.random.rand(*size).astype(np.float32)
        a_data = np.random.rand(*size).astype(np.float32)
        image = MultiChannelImage(
            [l_data, None],
            # [l_data, a_data],
            clim=((0.0, 1.0), (0.0, 1.0)),
            parent=c.scene)

        # Assign only L
        result = c.render()
        r_result = result[..., 0]
        g_result = result[..., 1]
        b_result = result[..., 2]
        a_result = result[..., 3]
        assert not np.allclose(r_result, 0)
        np.testing.assert_allclose(g_result, r_result)
        np.testing.assert_allclose(b_result, r_result)
        np.testing.assert_allclose(a_result, 255)

        # Add A
        image.set_data([l_data, a_data])
        image.clim = ("auto", "auto")
        result = c.render()
        old_r_result = r_result
        r_result = result[..., 0]
        g_result = result[..., 1]
        b_result = result[..., 2]
        a_result = result[..., 3]
        assert not np.allclose(r_result, 0)
        np.testing.assert_allclose(g_result, r_result)
        np.testing.assert_allclose(b_result, r_result)
        assert not np.allclose(a_result, 0)
        # the rendered result should always have full alpha
        # we need to compare the end result to the old result
        np.testing.assert_allclose(a_result, 255)
        assert not np.allclose(r_result, old_r_result)

        # Unset L and A - fully transparent
        image.set_data([None, None])
        image.clim = ("auto", "auto")
        result = c.render()
        r_result = result[..., 0]
        g_result = result[..., 1]
        b_result = result[..., 2]
        a_result = result[..., 3]
        # the rendered result will always have full alpha
        np.testing.assert_allclose(r_result, 0)
        np.testing.assert_allclose(g_result, 0)
        np.testing.assert_allclose(b_result, 0)
        np.testing.assert_allclose(a_result, 255)


run_tests_if_main()
