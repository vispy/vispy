# -*- coding: utf-8 -*-

"""
Tests for ColorbarVisual
All images are of size (100,100) to keep a small file size
"""

from vispy.scene import visuals
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main, raises)
from vispy.testing.image_tester import assert_image_approved


def create_colorbar(pos, size, orientation):
    colorbar = visuals.ColorBar(pos=pos,
                                size=size,
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
        colorbar_top = create_colorbar(pos=(50, 50),
                                       size=(60, 4),
                                       orientation='top')

        c.draw_visual(colorbar_top)
        assert_image_approved(c.render(), 'visuals/colorbar/top.png')
        colorbar_top.parent = None

        colorbar_bottom = create_colorbar(pos=(50, 50),
                                          size=(60, 4),
                                          orientation='bottom')

        c.draw_visual(colorbar_bottom)
        assert_image_approved(c.render(), 'visuals/colorbar/bottom.png')
        colorbar_bottom.parent = None

        colorbar_left = create_colorbar(pos=(50, 50),
                                        size=(60, 4),
                                        orientation='left')

        c.draw_visual(colorbar_left)
        assert_image_approved(c.render(), 'visuals/colorbar/left.png')
        colorbar_left.parent = None

        colorbar_right = create_colorbar(pos=(50, 50),
                                         size=(60, 4),
                                         orientation='right')

        c.draw_visual(colorbar_right)
        assert_image_approved(c.render(), 'visuals/colorbar/right.png')


@requires_application()
def test_reactive_draw():
    """Test reactive RectPolygon attributes"""
    with TestingCanvas() as c:
        colorbar = create_colorbar(pos=(50, 50),
                                   size=(60, 4),
                                   orientation='top')
        c.draw_visual(colorbar)

        colorbar.cmap = "ice"
        assert_image_approved(c.render(),
                              'visuals/colorbar/reactive_cmap.png')

        colorbar.clim = (-20, 20)
        assert_image_approved(c.render(),
                              'visuals/colorbar/reactive_clim.png')

        colorbar.label.text = "new label"
        assert_image_approved(c.render(),
                              'visuals/colorbar/reactive_label.png')

        colorbar.ticks[0].color = "red"
        colorbar.ticks[1].color = "blue"
        assert_image_approved(c.render(),
                              'visuals/colorbar/reactive_ticks.png')

        colorbar.border_width = 0
        assert_image_approved(c.render(),
                              'visuals/colorbar/reactive_border_width.png')

        colorbar.border_width = 5
        colorbar.border_color = "red"
        assert_image_approved(c.render(),
                              'visuals/colorbar/reactive_border_color.png')


@requires_application()
def test_attributes():
    """Test if attribute checks are in place"""
    with TestingCanvas():

        # initialize with major axis < minor axis
        with raises(ValueError):
            create_colorbar(pos=(50, 50),
                            size=(1, 30),
                            orientation='top')

        # set major axis to 0
        with raises(ValueError):
            create_colorbar(pos=(50, 50),
                            size=(0, 1),
                            orientation='right')

        # set negative major axis
        with raises(ValueError):
            create_colorbar(pos=(50, 50),
                            size=(-10, 1),
                            orientation='right')

        # set negative minor axis
        with raises(ValueError):
            create_colorbar(pos=(50, 50),
                            size=(1, -10),
                            orientation='right')

        # set minor axis to 0
        with raises(ValueError):
            create_colorbar(pos=(50, 50),
                            size=(1, 0),
                            orientation='right')

        # set invalid orientation
        with raises(ValueError):
            create_colorbar(pos=(50, 50),
                            size=(60, 4),
                            orientation='top-invalid')

run_tests_if_main()
