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


# construct a colormap from red to blue,
# similar to the electromagnetic spectrum
# any default colormap can also be used.
spectrum = Colormap([(1., 0., 0., 1.),
                     (1.0, 1.0, 0.0, 1.0),
                     (0.0, 1.0, 0.0, 1.0),
                    (0., 0., 1., 1.)])


def get_horizontal_bar():
        halfdim = 100, 10
        pos = 200, 400

        # construct a horizontally placed color bar
        # using the previously defined `spectrum` colormap
        return ColorBarVisual(pos, halfdim, label="spectrum", cmap=spectrum)


def get_vertical_bar():
        pos = 400, 300
        halfdim = 10, 100

        # similar to the previous case, only
        # with a vertical orientation
        # use clim to set the lower and upper values of the colorbar
        # which are drawn as labels on the bottom and top edge
        return ColorBarVisual(pos, halfdim, label="spectrum", cmap=spectrum,
                              orientation="vertical", clim=(-100, 100))


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, size=(800, 600), keys="interactive")

        self.horizontal_bar = get_horizontal_bar()
        self.horizontal_bar.label.font_size = 15

        self.vertical_bar = get_vertical_bar()
        self.vertical_bar.label.font_size = 15
        self.vertical_bar.border_width = 5
        self.vertical_bar.border_color = "black"
        self.vertical_bar.clim = (300, 500)

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
