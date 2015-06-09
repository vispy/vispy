# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: Siddharth Bhat
# -----------------------------------------------------------------------------

from . import Visual, TextVisual
from .shaders import ModularProgram, Function
from ..color import get_colormap, Color

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

VERT_SHADER_BORDER = """
attribute vec2 a_position;
attribute vec2 a_adjust_dir;

void main() {
    vec4 doc_pos = $visual_to_doc(vec4(a_position, 0, 1));

    vec4 doc_x = $visual_to_doc(vec4(a_adjust_dir.x, 0, 0, 0)) -
                $visual_to_doc(vec4(0, 0, 0, 0));

    vec4 doc_y = $visual_to_doc(vec4(0, a_adjust_dir.y, 0, 0)) -
                $visual_to_doc(vec4(0, 0, 0, 0));
    doc_x = normalize(doc_x);
    doc_y = normalize(doc_y);

    // Now doc_x + doc_y points in the direction we need in order to
    // correct the line weight of _both_ segments, but the magnitude of
    // that correction is wrong. To correct it we first need to
    // measure the width that would result from using doc_x + doc_y:
    vec4 proj_y_x = dot(doc_x, doc_y) * doc_x;  // project y onto x
    float cur_width = length(doc_y - proj_y_x);  // measure current weight

    // And now we can adjust vertex position for line width:
    float scaling = $border_width / cur_width;
    gl_Position = $doc_to_render(doc_pos + scaling * (doc_x + doc_y));
}

"""

FRAG_SHADER_BORDER = """
void main() {
    gl_FragColor = $border_color;
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
    cmap : str | vispy.color.ColorMap
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
    border_width : float (in px)
        The width of the border the colormap should have. This measurement
        is given in pixels
    border_color : string | vispy.color.Color
        The color of the border of the colormap. This can either be a
        string as the color's name or an actual instace of a vipy.color.Color
    """

    def __init__(self, center_pos, halfdim,
                 label,
                 cmap,
                 clim=(0.0, 1.0),
                 orientation="horizontal",
                 border_width=1.0,
                 border_color="black",
                 **kwargs):

        super(ColorBarVisual, self).__init__(**kwargs)

        self._cmap = get_colormap(cmap)
        self._clim = clim
        self._center_pos = center_pos
        self._halfdim = halfdim
        self._orientation = orientation
        self._border_width = border_width
        self._border_color = border_color
        self._label = TextVisual(label, anchor_y="top")

        # setup border rendering
        self._border_color = Color(border_color)
        self._border_program = ModularProgram(VERT_SHADER_BORDER,
                                              FRAG_SHADER_BORDER)

        adjust_dir = np.array([[-1, -1], [1, -1], [1, 1],
                              [-1, -1], [1, 1], [-1, 1]],
                              dtype=np.float32)

        self._border_program['a_adjust_dir'] = adjust_dir.astype(np.float32)

        # setup the right program shader based on color
        if orientation == "horizontal":
            self._program = ModularProgram(VERT_SHADER, FRAG_SHADER_HORIZONTAL)

        elif orientation == "vertical":
            self._program = ModularProgram(VERT_SHADER, FRAG_SHADER_VERTICAL)
        else:
            raise ColorBarVisual._get_orientation_error(self._orientation)

        tex_coords = np.array([[0, 0], [1, 0], [1, 1],
                              [0, 0], [1, 1], [0, 1]],
                              dtype=np.float32)

        self._program.frag['color_transform'] = Function(self._cmap.glsl_map)
        self._program['a_texcoord'] = tex_coords.astype(np.float32)

        self.regenerate()

    def regenerate(self):
        x, y = self._center_pos
        halfw, halfh = self._halfdim

        if self._orientation == "horizontal":
            text_x, text_y = x, y + halfh * 1.2 + self.border_width

            self._label.pos = text_x, text_y

            begin_tick_pos = x - halfw, text_y
            end_tick_pos = x + halfw, text_y

            # TODO, HACK: This should ideally be a single TextVisual
            # However, one TextVisual with multiple strings
            # does not seem to be working as of now. (See #981)
            # https://github.com/vispy/vispy/issues/981
            self._ticks = []
            self._ticks.append(TextVisual(str(self._clim[0]),
                               pos=begin_tick_pos,
                               anchor_y="top"))
            self._ticks.append(TextVisual(str(self._clim[1]),
                               pos=end_tick_pos,
                               anchor_y="top"))

        elif self._orientation == "vertical":
            text_x, text_y = x + halfw * 1.2 + self._border_width, y

            self._label.pos = text_x, text_y
            self._label.rotation = -90
            self._label.anchor_y = "top"

            begin_tick_pos = text_x, y + halfh
            end_tick_pos = text_x, y - halfh

            # TODO, HACK: See comment about ticks on "horizontal" conditional
            self._ticks = []
            self._ticks.append(TextVisual(str(self.clim[0]),
                               pos=begin_tick_pos,
                               rotation=-90,
                               anchor_y="top"))
            self._ticks.append(TextVisual(str(self.clim[1]),
                               pos=end_tick_pos,
                               rotation=-90,
                               anchor_y="top"))
        else:
            raise ColorBarVisual._get_orientation_error(self._orientation)

        vertices = np.array([[x - halfw, y - halfh],
                            [x + halfw, y - halfh],
                            [x + halfw, y + halfh],
                             # tri 2
                            [x - halfw, y - halfh],
                            [x + halfw, y + halfh],
                            [x - halfw, y + halfh]],
                            dtype=np.float32)

        self._program['a_position'] = vertices.astype(np.float32)
        self._border_program['a_position'] = vertices.astype(np.float32)

        self._border_program.vert['border_width'] = self._border_width
        self._border_program.frag['border_color'] = self._border_color.rgba

    @staticmethod
    def _get_orientation_error(orientation):
        return ValueError("orientation must"
                          " be \'horizontal\' or \'vertical\'."
                          " given: %s" % orientation)

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
        # new TextVisuals need to be created
        self.regenerate()

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label
        # position, styling has to be applied
        self.regenerate()

    @property
    def ticks(self):
        return self._ticks

    @ticks.setter
    def ticks(self, ticks):
        self._ticks = ticks
        self.regenerate()

    @property
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, border_width):
        self._border_width = border_width
        # positions of text need to be changed accordingly
        self.regenerate()

    @property
    def border_color(self):
        return self._border_color

    @border_color.setter
    def border_color(self, border_color):
        self._border_color = Color(border_color)
        self._border_program.frag['border_color'] = self._border_color.rgba

    def draw(self, transforms):
        """Draw the visual

        Parameters
        ----------
        transforms : instance of TransformSystem
            The transforms to use.
        """

        self._border_program.vert['visual_to_doc'] = \
            transforms.visual_to_document
        self._border_program.vert['doc_to_render'] = (
            transforms.framebuffer_to_render *
            transforms.document_to_framebuffer)
        self._border_program.draw("triangles")

        self._program.vert['transform'] = transforms.get_full_transform()
        self._program.draw('triangles')

        self._label.draw(transforms)

        for tick in self._ticks:
            tick.draw(transforms)
