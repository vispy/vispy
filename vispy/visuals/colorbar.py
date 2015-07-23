# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: Siddharth Bhat
# -----------------------------------------------------------------------------

import numpy as np

from . import Visual, TextVisual, CompoundVisual, BorderVisual
# from .border import BorderVisual
from .shaders import Function
from ..color import get_colormap

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


class _CoreColorBarVisual(Visual):
    """
    Visual subclass that actually renders the ColorBar.

    Note
    ----
    This is purely internal.
    Externally, the ColorBarVisual must be used.
    This class was separated out to encapsulate rendering information
    That way, ColorBar simply becomes a CompoundVisual
    """
    def __init__(self, center_pos, halfdim,
                 cmap,
                 orientation,
                 **kwargs):

        self._cmap = get_colormap(cmap)
        self._center_pos = center_pos
        self._halfdim = halfdim
        self._orientation = orientation

        # setup the right program shader based on color
        if orientation == "top" or orientation == "bottom":
            # self._program=ModularProgram(VERT_SHADER,FRAG_SHADER_HORIZONTAL)
            Visual.__init__(self, vcode=VERT_SHADER,
                            fcode=FRAG_SHADER_HORIZONTAL, **kwargs)

        elif orientation == "left" or orientation == "right":
            Visual.__init__(self, vcode=VERT_SHADER,
                            fcode=FRAG_SHADER_VERTICAL, **kwargs)

            # self._program = ModularProgram(VERT_SHADER, FRAG_SHADER_VERTICAL)
        else:
            raise _CoreColorBarVisual._get_orientation_error(self._orientation)

        tex_coords = np.array([[0, 0], [1, 0], [1, 1],
                               [0, 0], [1, 1], [0, 1]],
                              dtype=np.float32)

        glsl_map_fn = Function(self._cmap.glsl_map)

        self.shared_program.frag['color_transform'] = glsl_map_fn
        self.shared_program['a_texcoord'] = tex_coords.astype(np.float32)

        self._update()

    def _update(self):
        """Rebuilds the shaders, and repositions the objects
           that are used internally by the ColorBarVisual
        """

        x, y = self._center_pos
        halfw, halfh = self._halfdim

        anchor_x, anchor_y = ColorBarVisual._get_anchors(self._orientation)

        # test that width and height are non-zero
        if halfw <= 0:
            raise ValueError("half-width must be positive and non-zero"
                             ", not %s", halfw)
        if halfh <= 0:
            raise ValueError("half-height must be positive and non-zero"
                             ", not %s", halfh)

        # test that the given width and height is consistent
        # with the orientation
        if (self._orientation == "bottom" or self._orientation == "top"):
                if halfw < halfh:
                    raise ValueError("half-width(%s) < half-height(%s) for"
                                     "%s orientation,"
                                     " expected half-width >= half-height",
                                     (halfw, halfh, self._orientation, ))
        else:  # orientation == left or orientation == right
            if halfw > halfh:
                raise ValueError("half-width(%s) > half-height(%s) for"
                                 "%s orientation,"
                                 " expected half-width <= half-height",
                                 (halfw, halfh, self._orientation, ))

        # Set up the attributes that the shaders require
        vertices = np.array([[x - halfw, y - halfh],
                             [x + halfw, y - halfh],
                             [x + halfw, y + halfh],
                             # tri 2
                             [x - halfw, y - halfh],
                             [x + halfw, y + halfh],
                             [x - halfw, y + halfh]],
                            dtype=np.float32)

        self.shared_program['a_position'] = vertices

    @staticmethod
    def _get_orientation_error(orientation):
            return ValueError("orientation must"
                              " be one of 'top', 'bottom', "
                              "'left', or 'right', "
                              "not '%s'" % (orientation, ))

    @property
    def cmap(self):
        """ The colormap of the Colorbar
        """
        return self._cmap

    @cmap.setter
    def cmap(self, cmap):
        self._cmap = get_colormap(cmap)
        self._program.frag['color_transform'] = Function(self._cmap.glsl_map)

    @staticmethod
    def _prepare_transforms(view):
        # figure out padding by considering the entire transform
        # on the width and height
        program = view.view_program
        total_transform = view.transforms.get_transform()
        program.vert['transform'] = total_transform

    def _prepare_draw(self, view):
        self._draw_mode = "triangles"
        return True

# The padding multiplier that's used to place the text
# next to the Colorbar. Makes sure the text isn't
# visually "sticking" to the Colorbar
_TEXT_PADDING_FACTOR = 1.5


class ColorBarVisual(CompoundVisual):

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
    cmap : str | vispy.color.ColorMap
        Either the name of the ColorMap to be used from the standard
        set of names (refer to `vispy.color.get_colormap`),
        or a custom ColorMap object.
        The ColorMap is used to apply a gradient on the colorbar.
    orientation : {'left', 'right', 'top', 'bottom'}
        The orientation of the colorbar, used for rendering. The
        orientation can be thought of as the position of the label
        relative to the color bar.

        When the orientation is 'left' or 'right', the colorbar is
        vertically placed. When it is 'top' or 'bottom', the colorbar is
        horizontally placed.

            * 'top': the colorbar is horizontal.
              Color is applied from left to right.
              Minimum corresponds to left and maximum to right.
              Label is to the top of the colorbar

            * 'bottom': Same as top, except that
              label is to the bottom of the colorbar

            * 'left': the colorbar is vertical.
              Color is applied from bottom to top.
              Minimum corresponds to bottom and maximum to top.
              Label is to the left of the colorbar

            * 'right': Same as left, except that the
              label is placed to the right of the colorbar
    label_str : str
        The label that is to be drawn with the colorbar
        that provides information about the colorbar.
    clim : tuple (min, max)
        the minimum and maximum values of the data that
        is given to the colorbar. This is used to draw the scale
        on the side of the colorbar.
    border_width : float (in px)
        The width of the border the colormap should have. This measurement
        is given in pixels
    border_color : str | vispy.color.Color
        The color of the border of the colormap. This can either be a
        str as the color's name or an actual instace of a vipy.color.Color
    """

    def __init__(self, center_pos, halfdim,
                 cmap,
                 orientation,
                 label_str="",
                 clim=(0.0, 1.0),
                 border_width=1.0,
                 border_color="black",
                 **kwargs):

        self._label_str = label_str
        self._cmap = get_colormap(cmap)
        self._clim = clim
        self._center_pos = center_pos
        self._halfdim = halfdim
        self._orientation = orientation
        self._text_padding = 0

        anchor_x, anchor_y = ColorBarVisual._get_anchors(self._orientation)
        self._label = TextVisual(text=self._label_str,
                                 anchor_x=anchor_x,
                                 anchor_y=anchor_y)

        self._ticks = []

        self._ticks.append(TextVisual(str(self._clim[0]),
                                      anchor_x=anchor_x,
                                      anchor_y=anchor_y))

        self._ticks.append(TextVisual(str(self._clim[1]),
                                      anchor_x=anchor_x,
                                      anchor_y=anchor_y))

        self._colorbar = _CoreColorBarVisual(center_pos,
                                             halfdim, cmap,
                                             orientation)

        self._border = BorderVisual(center_pos,
                                    halfdim,
                                    border_width,
                                    border_color)

        CompoundVisual.__init__(self, [self._colorbar,
                                       self._border,
                                       self._ticks[0],
                                       self._ticks[1],
                                       self._label,
                                       ])

        self._update()

    def _update(self):
        """Rebuilds the shaders, and repositions the objects
           that are used internally by the ColorBarVisual
        """

        self._colorbar._update()
        self._border._update()

        # create a new label if this is the first time this function
        # is being called. Otherwise, just update the existing bar
        self.label.text = self._label_str

        # if this is the first time we're initializing ever
        # i.e - from the constructor, then create the TextVisual objects
        # otherwise, just change the _text_.
        # this is SUPER IMPORTANT, since the user might have modified the
        # ticks first to have say, a white color. And then he might have
        # edited the ticks.
        # This way, we retain any changes made by the user
        # to the _ticks while still reflecting changes in _clim
        self._ticks[0].text = str(self._clim[0])
        self._ticks[1].text = str(self._clim[1])

        self._update_positions()

    def _update_positions(self):
        """
        updates the positions of the colorbars and labels
        """
        x, y = self._center_pos
        halfw, halfh = self._halfdim

        anchor_x, anchor_y = ColorBarVisual._get_anchors(self._orientation)

        # test that width and height are non-zero
        if halfw <= 0:
            raise ValueError("half-width must be positive and non-zero"
                             ", not %s", halfw)
        if halfh <= 0:
            raise ValueError("half-height must be positive and non-zero"
                             ", not %s", halfh)

        visual_to_doc = self.transforms.get_transform('visual', 'document')
        doc_to_visual = self.transforms.get_transform('document', 'visual')

        center_doc = visual_to_doc.map(np.array([x, y, 0, 1]))

        axis_x = visual_to_doc.map(np.array([halfw, 0, 0, 1]))
        axis_y = visual_to_doc.map(np.array([0, halfh, 0, 1]))

        print("center: %s\naxis_x:%s\naxis_y:%s\n" %
              (center_doc, axis_x, axis_y))

        # Place the labels according to the given orientation
        if self._orientation == "bottom":
            baseline = center_doc + axis_y

            self._label.pos = doc_to_visual.map(baseline)[:-1]
            # TODO, HACK: This should ideally be a single TextVisual
            # However, one TextVisual with multiple strings
            # does not seem to be working as of now. (See #981)
            # https://github.com/vispy/vispy/issues/981
            self._ticks[0].pos = doc_to_visual.map(baseline + axis_x)[:-1]
            self._ticks[1].pos = doc_to_visual.map(baseline - axis_x)[:-1]

        elif self._orientation == "top":
            baseline = center_doc - axis_y

            self._label.pos = doc_to_visual.map(baseline)[:-1]
            self._ticks[0].pos = doc_to_visual.map(baseline - axis_x)[:-1]
            self._ticks[1].pos = doc_to_visual.map(baseline + axis_x)[:-1]

        elif self._orientation == "right":
            text_x = x + halfw
            text_x += self._border.visual_border_width[0]
            text_y = y
            self._label.pos = text_x, text_y
            self._label.rotation = -90

            # TODO, HACK: See comment - ticks on "horizontal" conditional
            self._ticks[0].pos = text_x, y + halfh
            self._ticks[1].pos = text_x, y - halfh
            self._ticks[0].rotation = self.ticks[1].rotation = -90

        elif self._orientation == "left":
            text_x = x - halfw
            text_x -= self._border.visual_border_width[0]
            text_y = y
            self._label.pos = text_x, text_y
            self._label.rotation = -90

            self._ticks[0].pos = text_x, y + halfh
            self._ticks[1].pos = text_x, y - halfh
            self._ticks[0].rotation = self.ticks[1].rotation = -90

        else:
            # raise an error since the orientation is now what was
            # expected
            raise _CoreColorBarVisual._get_orientation_error(self._orientation)

    def _prepare_draw(self, view):
        print ("preparing draw")
        self._update_positions()

    @staticmethod
    def _get_anchors(orientation):
        if orientation == "top":
            return "center", "bottom"

        elif orientation == "bottom":
            return "center", "top"

        elif orientation == "left":
            return "center", "bottom"

        else:  # orientation == "right"
            return "center", "top"

    @property
    def cmap(self):
        """ The colormap of the Colorbar
        """
        return self._colorbar._cmap

    @cmap.setter
    def cmap(self, cmap):
        self._colorbar.cmap = cmap

    @property
    def clim(self):
        """ The data limits of the Colorbar

        Returns
        -------
        clim: tuple(min, max)
        """

        return self._clim

    @clim.setter
    def clim(self, clim):
        self._clim = clim
        # new TextVisuals need to be created
        self._update()

    @property
    def label(self):
        """ The vispy.visuals.TextVisual associated with the label
        """
        return self._label

    @label.setter
    def label(self, label):
        self._label = label
        # position, styling has to be applied
        self._update()

    @property
    def ticks(self):
        """ The vispy.visuals.TextVisual associated with the ticks

        Returns
        -------
        ticks: [vispy.visual.TextVisual]
            The array is of length 2
        """
        return self._ticks

    @ticks.setter
    def ticks(self, ticks):
        self._ticks = ticks
        self._update()

    @property
    def border_width(self):
        """ The width of the border around the ColorBar in pixels
        """
        return self._border.border_width

    @border_width.setter
    def border_width(self, border_width):
        self._border.border_width = border_width
        # positions of text need to be changed accordingly
        self._update()

    @property
    def border_color(self):
        """ The color of the border around the ColorBar in pixels
        """
        return self._border.border_color

    @border_color.setter
    def border_color(self, border_color):
        self._border.border_color = border_color
