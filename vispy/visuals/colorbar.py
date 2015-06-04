# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: Siddharth Bhat
# -----------------------------------------------------------------------------

from . import Visual, TextVisual
from .shaders import ModularProgram, Function
from ..color import get_colormap

import numpy as np

VERT_SHADER = """
attribute vec2 a_position;
attribute vec2 a_texcoord;
varying vec2 v_texcoord;

void main() {
    v_texcoord = a_texcoord;
    gl_Position = $transform(vec4(a_position, 0, 1));
}
"""  # noqa

FRAG_SHADER_HORIZONTAL = """
varying vec2 v_texcoord;

void main()
{   
    vec4 mapped_color = $color_transform(v_texcoord.x);
    gl_FragColor = mapped_color;
}
"""  # noqa

FRAG_SHADER_VERTICAL = """
varying vec2 v_texcoord;
 
void main()
{      
    // we get the texcoords inverted (with respect to the colormap)
    // so let's invert it to make sure that the colorbar renders correctly 
    vec4 mapped_color = $color_transform(1.0 - v_texcoord.y);
    gl_FragColor = mapped_color;
}
"""  # noqa

# TODO:
# * assumes horizontal. allow vertical
# * draw border around rectangle
# * allow border width setting (this will require points in
# pixel coordinates, how do I do that?)
# * actually obey clim
# * write docs for color bar


class ColorBarVisual(Visual):
    """Visual subclass displaying a colorbar

    Parameters
    ----------

    center_pos : tuple (x, y)
        Position where the colorbar is to be placed with
        respect to the center of the colorbar
    halfdim : tuple (half_width, half_height)
        Half the dimensions of the colorbar measured
        from the center. That way, the total dimensions
        of the colorbar is (x - half_width) to (x + half_width)
        and (y - half_height) to (y + half_height)
    label : string
        The label that is to be drawn with the colorbar
        that provides information about the colorbar.
    cmap : str | ColorMap
        either the name of the ColorMap to be used from the standard
        set of names (refer to `vispy.color.get_colormap`),
        or a custom ColorMap object.

        The ColorMap is used to apply a gradient on the colorbar.
    clim : tuple (min, max)
        the minimum and maximum values of the data that
        is given to the colorbar. This is used to draw the scale
        on the side of the colorbar.
    orientation : {'horizontal', 'vertical'}
        the orientation of the colorbar, used for coloring

            * 'horizontal': the color is applied from left to right,
              with minimum corresponding to left and maximum to right
            * 'vertical': the color is applied from bottom to top,
              with mimumum corresponding to bottom and maximum to top
    """

    def __init__(self, center_pos, halfdim,
                 label,
                 cmap,
                 clim=(0.0, 1.0),
                 orientation="horizontal",
                 **kwargs):

        super(ColorBarVisual, self).__init__(**kwargs)

        self._cmap = get_colormap(cmap)
        self._clim = clim

        x, y = center_pos
        halfw, halfh = halfdim

        vertices = np.array([[x - halfw, y - halfh],
                            [x + halfw, y - halfh],
                            [x + halfw, y + halfh],
                             # tri 2
                            [x - halfw, y - halfh],
                            [x + halfw, y + halfh],
                            [x - halfw, y + halfh]],
                            dtype=np.float32)

        tex_coords = np.array([[0, 0], [1, 0], [1, 1],
                              [0, 0], [1, 1], [0, 1]],
                              dtype=np.float32)

        if orientation == "horizontal":
            self._program = ModularProgram(VERT_SHADER, FRAG_SHADER_HORIZONTAL)

        elif orientation == "vertical":
            self._program = ModularProgram(VERT_SHADER, FRAG_SHADER_VERTICAL)

        else:
            raise ValueError("orientation must"
                             " be \'horizontal\' or \'vertical\'."
                             " given: %s" % orientation)

        self._program.frag['color_transform'] = Function(self._cmap.glsl_map)
        self._program['a_position'] = vertices.astype(np.float32)
        self._program['a_texcoord'] = tex_coords.astype(np.float32)

        if orientation == "horizontal":
            text_x, text_y = x, y + halfh * 1.2
            self._label = TextVisual(label, pos=(text_x, text_y))

            begin_tick_pos = x - halfw, text_y
            end_tick_pos = x + halfw, text_y

            self._ticks = TextVisual([str(clim[0]), str(clim[1])],
                                     pos=[begin_tick_pos, end_tick_pos])
        elif orientation == "vertical":
            text_x, text_y = x + halfw * 1.2, y
            self._label = TextVisual(label, pos=(text_x, text_y), rotation=-90)

            begin_tick_pos = text_x, y - halfh
            end_tick_pos = text_x, y + halfh

            self._ticks = TextVisual([str(clim[0]), str(clim[1])],
                                     pos=[begin_tick_pos, end_tick_pos],
                                     rotation=-90)

    @property
    def cmap(self):
        return self._cmap

    @cmap.setter
    def cmap(self, cmap):
        self._cmap = get_colormap(cmap)
        self._program.frag['color_transform'] = Function(self._cmap.glsl_map)

    @property
    def clim(self):
        return self._clim

    @clim.setter
    def clim(self, clim):
        self._clim = clim
        # TODO: regenerate the ticks here

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label

    def draw(self, transforms):
        self._program.vert['transform'] = transforms.get_full_transform()
        self._program.draw('triangles')

        # self._label.draw(transforms)
        # self._ticks.draw(transforms)
