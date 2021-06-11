# -*- coding: utf-8 -*-

"""Tests for ColorbarVWidget.

All images are of size (100,100) to keep a small file size

"""

from vispy.scene.widgets import ColorBarWidget
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved


def create_colorbar(pos, orientation, label='label string here'):
    colorbar = ColorBarWidget(pos=pos,
                              orientation=orientation,
                              label=label,
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
def test_colorbar_widget():
    with TestingCanvas() as c:
        colorbar_top = create_colorbar(pos=(50, 50),
                                       label="my label",
                                       orientation='top')

        c.draw_visual(colorbar_top)
        assert_image_approved(c.render(), 'visuals/colorbar/top.png')
        assert colorbar_top.label.text == "my label"


run_tests_if_main()
