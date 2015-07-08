# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""Using Colorbars with the Canvas with the Mandlebrot set"""

from vispy import app
from vispy import gloo
from vispy.visuals.transforms import (NullTransform, STTransform,
                                      TransformSystem)

from vispy.visuals import ColorBarVisual, ImageVisual
from vispy.color import Color, get_colormap

import numpy as np


MAX_AMPLITUDE = 2
MAX_ITERATIONS = 30

colormap = get_colormap("RdBu")


def get_num_escape_turns(x, y):
    """Returns the number of iterations it took to escape
       as normalized values.
       Parameters
       ----------

       x: float
        the x coordinates of the point

       y: float
        the y coordinates of the point

       Returns
       -------
       float: [0, 1]
       * 0 if it took 0 iterations to escape
       * 1 if did not escape in MAX_ITERATIONS iterations
       * a linearly interpolated number between 0 and 1 if the point took
         anywhere between 0 to MAX_ITERATIONS to escape

    """
    c = complex(x, y)
    z = complex(0, 0)

    num_iterations = 0
    while np.absolute(z) < MAX_AMPLITUDE and num_iterations < MAX_ITERATIONS:
        z = (z ** 2) + c
        num_iterations += 1

    return float(num_iterations) / float(MAX_ITERATIONS)


def get_mandlebrot_escape_values(width, height):
    """Constructs the Mandlebro set for a grid of dimensions (width, height)

    Parameters
    ----------
    width: int
        width of the resulting grid
    height: int
        height of the resulting grid

    Returns
    -------
    A grid of floating point values containing the output of
    get_num_escape_turns function for each point
    """
    x_vals = np.linspace(-3, 2, width)
    y_vals = np.linspace(-1.5, 1.5, height)

    grid = np.meshgrid(x_vals, y_vals)

    v_get_num_escape_turns = np.vectorize(get_num_escape_turns)
    return v_get_num_escape_turns(*grid).astype(np.float)


def get_vertical_bar():
    """
    Constructs the vertical bar that represents the
    color values for the Mandlebrot set

    Returns
    -------
    A vispy.visual.ColorBarVisual object that represents the
    data of the Mandlebrot set
    """
    pos = 100, 300
    halfdim = 10, 200

    # similar to the previous case, only
    # with a vertical orientation
    # use clim to set the lower and upper values of the colorbar
    # which are drawn as labels on the bottom and top edge
    vertical = ColorBarVisual(pos, halfdim,
                              label_str="no. of iterations to escape",
                              cmap=colormap, orientation="left")

    vertical.label.font_size = 20
    vertical.label.color = "white"

    vertical.clim = (0, MAX_ITERATIONS)

    vertical.ticks[0].font_size = 20
    vertical.ticks[1].font_size = 20
    vertical.ticks[0].color = "white"
    vertical.ticks[1].color = "white"

    vertical.border_width = 2
    vertical.border_color = Color("#222222")

    return vertical


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, size=(800, 600), keys="interactive")

        img_data = get_mandlebrot_escape_values(600, 400)
        self.image = ImageVisual(img_data,  cmap=colormap)

        image_transform = STTransform(scale=(1.3, 1.3), translate=(100, 0))
        self.image_transform_sys = TransformSystem(self)
        self.image_transform_sys.visual_to_document = image_transform

        self.vertical_bar = get_vertical_bar()

        # construct a default transform that does identity scaling
        # and does not translate the coordinates
        colorbar_transform = NullTransform()
        self.colorbar_transform_sys = TransformSystem(self)
        self.colorbar_transform_sys.visual_to_document = colorbar_transform

        self.show()


    def on_resize(self, event):
        # Set canvas viewport and reconfigure visual transforms to match.
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)

        self.image.transforms.configure(canvas=self, viewport=vp)
        self.vertical_bar.transforms.configure(canvas=self, viewport=vp)


    def on_draw(self, event):
        # clear the color buffer
        gloo.clear(color=colormap[0.0])

        self.image.draw()

        # render the horizontal and vertical bar
        # with the TransformSystem we had created before
        # self.horizontal_bar.draw(self.colorbar_transform_sys)
        self.vertical_bar.draw()

if __name__ == '__main__':
    win = Canvas()
    app.run()
