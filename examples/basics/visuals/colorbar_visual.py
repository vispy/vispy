# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""Using Colorbars with the Canvas"""

from vispy import app
from vispy import gloo
from vispy.visuals.transforms import NullTransform
from vispy.visuals.transforms import TransformSystem

from vispy.visuals import ColorBarVisual
from vispy.color import Color
from vispy.color.colormap import Colormap

# construct a colormap from dark blue to light blue
spectrum = Colormap(["#0288D1", "#B3E5FC"])


def get_horizontal_bar():
        halfdim = 200, 10
        pos = 300, 400

        # construct a horizontally placed color bar
        # using the previously defined `spectrum` colormap
        horizontal = ColorBarVisual(pos, halfdim, label="horizontal-spectrum",
                                    cmap=spectrum)
        horizontal.label.font_size = 16
        horizontal.ticks[0].font_size = 16
        horizontal.ticks[1].font_size = 16

        horizontal.border_width = 5
        horizontal.border_color = Color("#212121")

        return horizontal


def get_vertical_bar():
        pos = 600, 300
        halfdim = 10, 200

        # similar to the previous case, only
        # with a vertical orientation
        # use clim to set the lower and upper values of the colorbar
        # which are drawn as labels on the bottom and top edge
        vertical = ColorBarVisual(pos, halfdim, label="vertical-spectrum",
                                  cmap=spectrum, orientation="vertical")
        vertical.label.font_size = 16
        vertical.ticks[0].font_size = 16
        vertical.ticks[1].font_size = 16

        vertical.border_width = 5
        vertical.border_color = Color("#212121")

        vertical.clim = (300, 500)
        return vertical


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, size=(800, 600), keys="interactive")

        self.horizontal_bar = get_horizontal_bar()
        self.vertical_bar = get_vertical_bar()

        # construct a default transform that does identity scaling
        # and does not translate the coordinates
        self.transform = NullTransform()

        # construct a TransformSystem to encapsulate the previously
        # created transform, and assign it to it
        self.transform_system = TransformSystem(self)
        self.transform_system.visual_to_document = self.transform

        self.show()

    def on_draw(self, event):
        # clear the color buffer
        gloo.clear(color=Color("white"))

        # render the horizontal and vertical bar
        # with the TransformSystem we had created before
        self.horizontal_bar.draw(self.transform_system)
        self.vertical_bar.draw(self.transform_system)

if __name__ == '__main__':
    win = Canvas()
    app.run()
