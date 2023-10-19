# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from vispy.app import Canvas, MouseEvent
from vispy.visuals import ImageVisual
from vispy.testing import requires_application
from vispy.visuals.transforms import STTransform
from vispy import gloo

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
    with Canvas(size=(125, 125), show=True, title='run') as c:
        im1 = np.zeros((100, 100, 4)).astype(np.float32)
        im1[:, :, 0] = 1
        im1[:, :, 3] = 1

        im2 = np.zeros((50, 50, 4)).astype(np.float32)
        im2[:, :, 1] = 1
        im2[:, :, 3] = 0.4

        # Create the image
        image1 = ImageVisual(im1)
        image1.transform = STTransform(translate=(20, 20, 0))
        image1.transforms.configure(canvas=c, viewport=(0, 0, 125, 125))
        image2 = ImageVisual(im2)
        image2.transform = STTransform(translate=(0, 0, -1))
        image2.transforms.configure(canvas=c, viewport=(0, 0, 125, 125))
        if blend_func:
            image1.set_gl_state(preset='translucent', blend_func=blend_func)
            image2.set_gl_state(preset='translucent', blend_func=blend_func)

        @c.events.draw.connect
        def on_draw(ev):
            gloo.clear('black')
            gloo.set_viewport(0, 0, *c.physical_size)
            image1.draw()
            image2.draw()

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
            # this part of this test fails on macOS 12 at the moment
            # see https://github.com/vispy/vispy/pull/2324#issuecomment-1163350672
            assert (rgba_result[..., 3] != 255).any()


@requires_application()
@pytest.mark.parametrize(
    'preset',
    [
        'opaque', 'additive', 'translucent',
    ])
def test_blend_presets(preset):
    """Test blending presets a canvas to an array.

    Different blending presets are used to test that they properly set
    blend equations.

    """
    with Canvas(size=(125, 125), show=True, title='run') as c:
        im1 = np.zeros((100, 100, 4)).astype(np.float32)
        im1[:, :, 1] = 1
        im1[:, :, 3] = .4
        # Create the image
        image1 = ImageVisual(im1)
        image1.transform = STTransform(translate=(20, 20, -1))
        image1.transforms.configure(canvas=c, viewport=(0, 0, 125, 125))
        
        gloo.set_state(blend_equation='min')
        image1.set_gl_state(preset)

        @c.events.draw.connect
        def on_draw(ev):
            gloo.clear('black')
            gloo.set_viewport(0, 0, *c.physical_size)
            image1.draw()
            
        rgba_result = c.render()
        assert not np.allclose(rgba_result[..., :3], 0)


@requires_application()
@pytest.mark.parametrize("mouse_event_type, button, buttons, expected_button, expected_buttons", [
    ('mouse_press', 1, [], 1, [1]),
    ('mouse_release', 1, [1], 1, [1]),
    # left click pressed and held, followed by a right click
    ('mouse_press', 2, [1], 2, [1, 2]),
    ('mouse_release', 2, [1, 2], 2, [1, 2]),
])
def test_mouse_event(mouse_event_type, button, buttons, expected_button, expected_buttons):
    mev = MouseEvent(type=mouse_event_type, button=button, buttons=buttons)
    assert mev.buttons == expected_buttons
    assert mev.button == expected_button
