# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""Using Colorbars with the Canvas to demo different types"""

from vispy import app
from vispy import gloo
from vispy.visuals import ColorBarVisual
from vispy.color import get_colormap
from vispy.color import Color

# from vispy.visuals.transforms import NullTransform
# from vispy.visuals.transforms.transform_system import TransformSystem

colormap = get_colormap("ice")


def style_colorbar(colorbar):
    colorbar.label.font_size = 18
    colorbar.label.color = "black"

    colorbar.clim = (0, 10)

    colorbar.ticks[0].font_size = 14
    colorbar.ticks[1].font_size = 14
    colorbar.ticks[0].color = "black"
    colorbar.ticks[1].color = "black"

    colorbar.border_width = 10
    colorbar.border_color = "red"

    return colorbar


def get_left_orientation_bar():
    pos = 50, 300
    halfdim = 10, 200

    colorbar = ColorBarVisual(pos, halfdim,
                              label_str="orientation left",
                              cmap=colormap, orientation="left")

    return style_colorbar(colorbar)


def get_right_orientation_bar():
    pos = 200, 300
    halfdim = 10, 200

    colorbar = ColorBarVisual(pos, halfdim,
                              label_str="orientation right",
                              cmap=colormap, orientation="right")

    return style_colorbar(colorbar)


def get_top_orientation_bar():
    pos = 600, 400
    halfdim = 150, 10

    colorbar = ColorBarVisual(pos, halfdim,
                              label_str="orientation top",
                              cmap=colormap, orientation="top")

    return style_colorbar(colorbar)


def get_bottom_orientation_bar():
    pos = 600, 150
    halfdim = 150, 10

    colorbar = ColorBarVisual(pos, halfdim,
                              label_str="orientation bottom",
                              cmap=colormap, orientation="bottom")

    return style_colorbar(colorbar)


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, size=(800, 600), keys="interactive")

        self.bars = []
        self.bars.append(get_left_orientation_bar())
        self.bars.append(get_right_orientation_bar())
        self.bars.append(get_top_orientation_bar())
        self.bars.append(get_bottom_orientation_bar())

        # construct a default transform that does identity scaling
        # and does not translate the coordinates
        # transform = NullTransform()
        # self.transform_sys = TransformSystem(self)
        # self.transform_sys.visual_to_document = transform

        self.show()

    def on_resize(self, event):
        # Set canvas viewport and reconfigure visual transforms to match.
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)

        for bar in self.bars:
            bar.transforms.configure(canvas=self, viewport=vp)

    def on_draw(self, event):
        # clear the color buffer
        gloo.clear(color="white")

        for bar in self.bars:
            bar.draw()

if __name__ == '__main__':
    win = Canvas()
    app.run()
