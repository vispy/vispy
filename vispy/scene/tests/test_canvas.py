# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from vispy import gloo, scene
from vispy.testing import requires_application, TestingCanvas
from vispy.visuals.transforms import STTransform

import numpy as np
import pytest


@requires_application()
@pytest.mark.parametrize(
    'blend_func',
    [
        ('src_alpha', 'one_minus_src_alpha', 'one', 'one_minus_src_alpha'),
        ('src_alpha', 'one_minus_src_alpha'),
        None,
    ])
def test_canvas_render(blend_func):
    """Test rendering a canvas to an array.

    Different blending functions are used to test what various Visuals may
    produce without actually using different types of Visuals.

    """
    with TestingCanvas(size=(125, 125), show=True, title='run') as c:
        view = c.central_widget.add_view()

        im1 = np.zeros((100, 100, 4)).astype(np.float32)
        im1[:, :, 0] = 1
        im1[:, :, 3] = 1

        im2 = np.zeros((50, 50, 4)).astype(np.float32)
        im2[:, :, 1] = 1
        im2[:, :, 3] = 0.4

        # Create the image
        image1 = scene.visuals.Image(im1, parent=view.scene)
        image1.transform = STTransform(translate=(20, 20, 0))
        image2 = scene.visuals.Image(im2, parent=view.scene)
        image2.transform = STTransform(translate=(0, 0, -1))
        if blend_func:
            image1.set_gl_state(preset='translucent', blend_func=blend_func)
            image2.set_gl_state(preset='translucent', blend_func=blend_func)

        rgba_result = c.render()
        rgb_result = c.render(alpha=False)

        # the results should be the same except for alpha
        np.testing.assert_allclose(rgba_result[..., :3], rgb_result)
        # the image should have something drawn in it
        assert not np.allclose(rgba_result[..., :3], 0)
        # the alpha should not be completely transparent
        assert not np.allclose(rgba_result[..., 3], 0)
        if blend_func is None or 'one' in blend_func:
            # no transparency
            np.testing.assert_allclose(rgba_result[..., 3], 255)
        else:
            # the alpha should have some transparency
            assert (rgba_result[..., 3] != 255).any()


@requires_application()
def test_picking_basic():
    """Test basic picking behavior.

    Based on https://github.com/vispy/vispy/issues/2107.

    """
    with TestingCanvas(size=(125, 125), show=True, title='run') as c:
        view = c.central_widget.add_view()
        view.margin = 5  # add empty space where there are no visuals
        view.camera = 'panzoom'

        x = np.linspace(0, 400, 100)
        y = np.linspace(0, 200, 100)
        line = scene.Line(np.array((x, y)).T.astype(np.float32))
        line.interactive = True
        view.add(line)
        view.camera.set_range()

        c.render()  # initial basic draw
        for _ in range(2):  # run picking twice to make sure it is repeatable
            # get Visuals on a Canvas point that Line is drawn on
            picked_visuals = c.visuals_at((100, 25))
            assert len(picked_visuals) == 2
            assert any(isinstance(vis, scene.ViewBox) for vis in picked_visuals)
            assert any(isinstance(vis, scene.Line) for vis in picked_visuals)


@requires_application()
@pytest.mark.parametrize(
    'preset',
    [
        'opaque', 'additive', 'translucent',
    ])
def test_blend_presets(preset):
    """Test blending presets render a canvas to an array.

    Different blending presets are used to test that they properly set
    blend equations.

    """
    with TestingCanvas(size=(125, 125), show=True, title='run') as c:
        view = c.central_widget.add_view()
        im1 = np.zeros((100, 100, 4)).astype(np.float32)
        im1[:, :, 1] = 1
        im1[:, :, 3] = .4
        # Create the image
        image1 = scene.visuals.Image(im1, parent=view.scene)
        image1.transform = STTransform(translate=(20, 20, -1))

        gloo.set_state(blend_equation='min')
        image1.set_gl_state(preset)

        rgba_result = c.render()
        assert not np.allclose(rgba_result[..., :3], 0)
