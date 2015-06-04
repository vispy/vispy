# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""Using Colorbars with the Canvas"""

from vispy import app
from vispy import gloo
from vispy.visuals.transforms import STTransform, TransformSystem
from vispy.visuals import ColorBarVisual
from vispy.color import Color
from vispy.color.colormap import Colormap


spectrum = Colormap([(1., 0., 0., 1.), (0., 0., 1., 1.)])


def get_horizontal_bar():
        halfdim = 100, 10
        pos = 200, 400

        return ColorBarVisual(pos, halfdim, label="spectrun", cmap=spectrum)


def get_vertical_bar():
        pos = 400, 300
        halfdim = 10, 100

        return ColorBarVisual(pos, halfdim, label="spectrum", cmap=spectrum,
                              orientation="vertical")


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, size=(800, 600), keys="interactive")

        self.horizontal_bar = get_horizontal_bar()
        self.vertical_bar = get_vertical_bar()

        self.transform = STTransform(scale=(1, 1), translate=(0, 0))
        self.transform_system = TransformSystem(self)
        self.transform_system.visual_to_document = self.transform

        self.show()

    def on_draw(self, event):
        gloo.clear(color=Color("gray"))

        self.horizontal_bar.draw(self.transform_system)
        self.vertical_bar.draw(self.transform_system)


win = Canvas()
app.run()
