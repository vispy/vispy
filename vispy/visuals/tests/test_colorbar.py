# -*- coding: utf-8 -*-

"""
Tests for ColorbarVisual
All images are of size (100,100) to keep a small file size
"""

from vispy.scene import visuals
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved
from pytest import raises


def create_colorbar(center_pos, halfdim, orientation):
    colorbar = visuals.ColorBar(center_pos=center_pos,
                                halfdim=halfdim,
                                orientation=orientation,
                                label_str='label string here',
                                cmap='autumn',
                                border_color='white',
                                border_width=2)

    colorbar.label.color = 'white'
    colorbar.label.font_size = 5

    colorbar.ticks[0].color = 'white'
    colorbar.ticks[0].font_size = 5

    colorbar.ticks[1].color = 'white'
    colorbar.ticks[1].font_size = 5

    return colorbar


@requires_application()
def test_colorbar_draw():
    """Test drawing Colorbar without transform using ColorbarVisual"""
    with TestingCanvas() as c:
        colorbar_top = create_colorbar(center_pos=(50, 50),
                                       halfdim=(30, 2),
                                       orientation='top')

        c.draw_visual(colorbar_top)
        assert_image_approved("screenshot", 'visuals/colorbar/top.png')

        colorbar_bottom = create_colorbar(center_pos=(50, 50),
                                          halfdim=(30, 2),
                                          orientation='bottom')

        c.draw_visual(colorbar_bottom)
        assert_image_approved("screenshot", 'visuals/colorbar/bottom.png')

        colorbar_left = create_colorbar(center_pos=(50, 50),
                                        halfdim=(2, 30),
                                        orientation='left')

        c.draw_visual(colorbar_left)
        assert_image_approved("screenshot", 'visuals/colorbar/left.png')

        colorbar_right = create_colorbar(center_pos=(50, 50),
                                         halfdim=(2, 30),
                                         orientation='right')

        c.draw_visual(colorbar_right)
        assert_image_approved("screenshot", 'visuals/colorbar/right.png')


@requires_application()
def test_reactive_draw():
    """Test reactive RectPolygon attributes"""
    with TestingCanvas() as c:
        colorbar = create_colorbar(center_pos=(50, 50),
                                   halfdim=(30, 2),
                                   orientation='top')
        c.draw_visual(colorbar)

        colorbar.cmap = "ice"
        c.draw_visual(colorbar)
        assert_image_approved("screenshot",
                              'visuals/colorbar/reactive_cmap.png')

        colorbar.clim = (-20, 20)
        c.draw_visual(colorbar)
        assert_image_approved("screenshot",
                              'visuals/colorbar/reactive_clim.png')

        colorbar.label.text = "new label"
        c.draw_visual(colorbar)
        assert_image_approved("screenshot",
                              'visuals/colorbar/reactive_label.png')

        colorbar.ticks[0].color = "red"
        colorbar.ticks[1].color = "blue"
        c.draw_visual(colorbar)
        assert_image_approved("screenshot",
                              'visuals/colorbar/reactive_ticks.png')

        colorbar.border_width = 0
        c.draw_visual(colorbar)
        assert_image_approved("screenshot",
                              'visuals/colorbar/reactive_border_width.png')

        colorbar.border_width = 5
        colorbar.border_color = "red"
        c.draw_visual(colorbar)
        assert_image_approved("screenshot",
                              'visuals/colorbar/reactive_border_color.png')


@requires_application()
def test_attributes():
    """Test if attribute checks are in place"""
    with TestingCanvas():

        # initialize with wrong dimensions for orientations
        with raises(ValueError):
            create_colorbar(center_pos=(50, 50),
                            halfdim=(1, 30),
                            orientation='top')

        with raises(ValueError):
            create_colorbar(center_pos=(50, 50),
                            halfdim=(1, 30),
                            orientation='bottom')

        with raises(ValueError):
            create_colorbar(center_pos=(50, 50),
                            halfdim=(30, 1),
                            orientation='left')

        with raises(ValueError):
            create_colorbar(center_pos=(50, 50),
                            halfdim=(30, 1),
                            orientation='right')

        # set width to 0
        with raises(ValueError):
            create_colorbar(center_pos=(50, 50),
                            halfdim=(0, 1),
                            orientation='right')

        # set height to 0
        with raises(ValueError):
            create_colorbar(center_pos=(50, 50),
                            halfdim=(1, 0),
                            orientation='right')

        # set invalid orientation
        with raises(ValueError):
            create_colorbar(center_pos=(50, 50),
                            halfdim=(30, 2),
                            orientation='top-invalid')

run_tests_if_main()
