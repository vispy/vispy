# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""Using Colorbars with the Canvas with the Mandlebrot set"""

from vispy import app
from vispy import gloo
from vispy.visuals.transforms import STTransform

from vispy.visuals import ColorBarVisual, ImageVisual
from vispy.color import Color, get_colormap


import numpy as np


ESCAPE_MAGNITUDE = 2
MIN_MAGNITUDE = 0.002
MAX_ITERATIONS = 50

colormap = get_colormap("hot")


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
    z = complex(x, y)

    num_iterations = 0

    while (MIN_MAGNITUDE < np.absolute(z) < ESCAPE_MAGNITUDE and
           num_iterations < MAX_ITERATIONS):
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
    return v_get_num_escape_turns(*grid).astype(np.float32)


def get_vertical_bar(pos, size):
    """
    Constructs the vertical bar that represents the
    color values for the Mandlebrot set

    Returns
    -------
    A vispy.visual.ColorBarVisual object that represents the
    data of the Mandlebrot set
    """
    vertical = ColorBarVisual(pos=pos,
                              size=size,
                              label="iterations to escape",
                              cmap=colormap, orientation="left")

    vertical.label.font_size = 15
    vertical.label.color = "white"

    vertical.clim = (0, MAX_ITERATIONS)

    vertical.ticks[0].font_size = 10
    vertical.ticks[1].font_size = 10
    vertical.ticks[0].color = "white"
    vertical.ticks[1].color = "white"

    vertical.border_width = 1
    vertical.border_color = Color("#ababab")

    return vertical


class Canvas(app.Canvas):
    def __init__(self):
        # dimensions of generated image
        img_dim = np.array([700, 500])
        # position of colorbar
        colorbar_pos = np.array([100, 300])
        # size of the colorbar, measured as (major, minor)
        colorbar_size = np.array([400, 20])
        # position of the generated image
        image_pos = np.array([200, 80])

        app.Canvas.__init__(self, size=(800, 600), keys="interactive")

        img_data = get_mandlebrot_escape_values(img_dim[0], img_dim[1])
        self.image = ImageVisual(img_data, cmap=colormap)

        self.image.transform = \
            STTransform(scale=1.1,
                        translate=image_pos)

        self.vertical_bar = get_vertical_bar(colorbar_pos, colorbar_size)

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
