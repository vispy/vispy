# -*- coding: utf-8 -*-

"""
Tests for ColorbarVisual
All images are of size (100,100) to keep a small file size
"""

from vispy.scene import visuals, transforms
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved
from pytest import raises


def create_colorbar(center_pos, halfdim, orientation):
    colorbar = visuals.ColorBar(
                        center_pos=center_pos,
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
def test_rectangle_draw():
    """Test drawing Colorbar without transform using RectPolygonVisual"""
    with TestingCanvas() as c:
        colorbar_top = create_colorbar(
                        center_pos=(50, 50),
                        halfdim=(30, 2),
                        orientation='top')

        c.draw_visual(colorbar_top)
        assert_image_approved("screenshot", 'visuals/colorbar_top.png')

#         rectpolygon = visuals.Rectangle(pos=(50, 50, 0), height=40.,
#                                         width=80., radius=10., color='red')
#         c.draw_visual(rectpolygon)
#         assert_image_approved("screenshot", 'visuals/rectpolygon2.png')

#         rectpolygon = visuals.Rectangle(pos=(50, 50, 0), height=40.,
#                                         width=80., radius=10., color='red',
#                                         border_color=(0, 1, 1, 1))
#         c.draw_visual(rectpolygon)
#         assert_image_approved("screenshot", 'visuals/rectpolygon3.png')

#         rectpolygon = visuals.Rectangle(pos=(50, 50, 0), height=40.,
#                                         width=80., radius=10.,
#                                         border_color='white')
#         c.draw_visual(rectpolygon)
#         assert_image_approved("screenshot", 'visuals/rectpolygon4.png',
#                               min_corr=0.5)


# @requires_application()
# def test_rectpolygon_draw():
#     """Test drawing transformed rectpolygons using RectPolygonVisual"""
#     with TestingCanvas() as c:
#         rectpolygon = visuals.Rectangle(pos=(0., 0.), height=20.,
#                                         width=20., radius=10., color='blue')
#         rectpolygon.transform = transforms.STTransform(scale=(2.0, 3.0),
#                                                        translate=(50, 50))
#         c.draw_visual(rectpolygon)
#         assert_image_approved("screenshot", 'visuals/rectpolygon6.png')

#         rectpolygon = visuals.Rectangle(pos=(0., 0.), height=20.,
#                                         width=20., radius=10.,
#                                         color='blue', border_color='red')
#         rectpolygon.transform = transforms.STTransform(scale=(2.0, 3.0),
#                                                        translate=(50, 50))
#         c.draw_visual(rectpolygon)
#         assert_image_approved("screenshot", 'visuals/rectpolygon7.png')

#         rectpolygon = visuals.Rectangle(pos=(0., 0.), height=60.,
#                                         width=60., radius=10.,
#                                         border_color='red')
#         rectpolygon.transform = transforms.STTransform(scale=(1.5, 0.5),
#                                                        translate=(50, 50))
#         c.draw_visual(rectpolygon)
#         assert_image_approved("screenshot", 'visuals/rectpolygon8.png',
#                               min_corr=0.5)

#         rectpolygon = visuals.Rectangle(pos=(0., 0.), height=60.,
#                                         width=60., radius=[25, 10, 0, 15],
#                                         color='blue', border_color='red')
#         rectpolygon.transform = transforms.STTransform(scale=(1.5, 0.5),
#                                                        translate=(50, 50))
#         c.draw_visual(rectpolygon)
#         assert_image_approved("screenshot", 'visuals/rectpolygon9.png')


# @requires_application()
# def test_reactive_draw():
#     """Test reactive RectPolygon attributes"""
#     with TestingCanvas() as c:
#         rectpolygon = visuals.Rectangle(pos=(50, 50, 0), height=40.,
#                                         width=80., color='red')
#         c.draw_visual(rectpolygon)

#         rectpolygon.radius = [20., 20, 0., 10.]
#         c.draw_visual(rectpolygon)
#         assert_image_approved("screenshot",
#                               'visuals/reactive_rectpolygon1.png')

#         rectpolygon.pos = (60, 60, 0)
#         c.draw_visual(rectpolygon)
#         assert_image_approved("screenshot",
#                               'visuals/reactive_rectpolygon2.png')

#         rectpolygon.color = 'blue'
#         c.draw_visual(rectpolygon)
#         assert_image_approved("screenshot",
#                               'visuals/reactive_rectpolygon3.png')

#         rectpolygon.border_color = 'yellow'
#         c.draw_visual(rectpolygon)
#         assert_image_approved("screenshot",
#                               'visuals/reactive_rectpolygon4.png')

#         rectpolygon.radius = 10.
#         c.draw_visual(rectpolygon)
#         assert_image_approved("screenshot",
#                               'visuals/reactive_rectpolygon5.png')


# @requires_application()
# def test_attributes():
#     """Test if attribute checks are in place"""
#     with TestingCanvas():
#         rectpolygon = visuals.Rectangle(pos=(50, 50, 0), height=40.,
#                                         width=80., color='red')
#         with raises(ValueError):
#             rectpolygon.height = 0
#         with raises(ValueError):
#             rectpolygon.width = 0
#         with raises(ValueError):
#             rectpolygon.radius = [10, 0, 5]
#         with raises(ValueError):
#             rectpolygon.radius = [10.]
#         with raises(ValueError):
#             rectpolygon.radius = 21.


run_tests_if_main()
