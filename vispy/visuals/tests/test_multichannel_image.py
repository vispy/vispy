#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the MultiChannelImageVisual."""

from vispy.scene.visuals import MultiChannelImage

import numpy as np
from vispy.testing import TestingCanvas, run_tests_if_main, requires_application


@requires_application()
def test_multiband_visual():
    size = (400, 600)
    with TestingCanvas(size=size) as c:
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


run_tests_if_main()
