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
            Visual.__init__(self, vcode=VERT_SHADER,
                            fcode=FRAG_SHADER_HORIZONTAL, **kwargs)

        elif orientation == "left" or orientation == "right":
            Visual.__init__(self, vcode=VERT_SHADER,
                            fcode=FRAG_SHADER_VERTICAL, **kwargs)
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

        # test that width and height are non-zero
        if halfw <= 0:
            raise ValueError("half-width must be positive and non-zero"
                             ", not %s" % halfw)
        if halfh <= 0:
            raise ValueError("half-height must be positive and non-zero"
                             ", not %s" % halfh)

        # test that the given width and height is consistent
        # with the orientation
        if (self._orientation == "bottom" or self._orientation == "top"):
                if halfw < halfh:
                    raise ValueError("half-width(%s) < half-height(%s) for"
                                     "%s orientation,"
                                     " expected half-width >= half-height" %
                                     (halfw, halfh, self._orientation, ))
        else:  # orientation == left or orientation == right
            if halfw > halfh:
                raise ValueError("half-width(%s) > half-height(%s) for"
                                 "%s orientation,"
                                 " expected half-width <= half-height" %
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
_TEXT_PADDING_FACTOR = 1.05


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

        self._label = TextVisual(text=self._label_str)

        self._ticks = []

        self._ticks.append(TextVisual(str(self._clim[0])))

        self._ticks.append(TextVisual(str(self._clim[1])))

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

        self.label.text = self._label_str

        self._ticks[0].text = str(self._clim[0])
        self._ticks[1].text = str(self._clim[1])

        self._update_positions()

    def _update_positions(self):
        """
        updates the positions of the colorbars and labels

        """

        if self._orientation == "right" or self._orientation == "left":
            self._label.rotation = -90
            self._ticks[0].rotation = -90
            self._ticks[1].rotation = -90

        x, y = self._center_pos
        halfw, halfh = self._halfdim

        anchors = ColorBarVisual._get_anchors(center=self._center_pos,
                                              halfdim=self._halfdim,
                                              orientation=self._orientation,
                                              transforms=self.label.transforms)
        self._label.anchors = anchors
        self._ticks[0].anchors = anchors
        self._ticks[1].anchors = anchors

        # test that width and height are non-zero
        if halfw <= 0:
            raise ValueError("half-width must be positive and non-zero"
                             ", not %s", halfw)
        if halfh <= 0:
            raise ValueError("half-height must be positive and non-zero"
                             ", not %s", halfh)

        (label_pos, ticks_pos) = \
            ColorBarVisual._calc_positions(center=self._center_pos,
                                           halfdim=self._halfdim,
                                           border_width=self.border_width,
                                           orientation=self._orientation,
                                           transforms=self.transforms)

        self._label.pos = label_pos
        self._ticks[0].pos = ticks_pos[0]
        self._ticks[1].pos = ticks_pos[1]

    def _prepare_draw(self, view):
        # print ("preparing draw")
        self._update_positions()

    @staticmethod
    def _get_anchors(center, halfdim, orientation, transforms):
        if orientation == "bottom":
            perp_direction = [0, -1]
        elif orientation == "top":
            perp_direction = [0, 1]
        # NOTE: we use these as the perp directions for left and right,
        # because the label gets rotated by (-90) degrees at the end.
        elif orientation == "left":
            perp_direction = [0, -1]
        elif orientation == "right":
            perp_direction = [0, 1]

        perp_direction = np.array(perp_direction, dtype=np.float32)
        perp_direction /= np.linalg.norm(perp_direction)
        # use the document (pixel) coord system to set text anchors
        anchors = []
        if perp_direction[0] < 0:
            anchors.append('right')
        elif perp_direction[0] > 0:
            anchors.append('left')
        else:
            anchors.append('center')
        if perp_direction[1] < 0:
            anchors.append('bottom')
        elif perp_direction[1] > 0:
            anchors.append('top')
        else:
            anchors.append('middle')

        return anchors

    @staticmethod
    def _calc_positions(center, halfdim, border_width,
                        orientation, transforms):
        """
        Calculate the text centeritions given the ColorBar
        parameters.

        Note
        ----
        This is static because in principle, this
        function does not need access to the state of the ColorBar
        at all. It's a computation function that computes coordinate
        transforms

        Parameters
        ----------
        center: tuple (x, y)
            Center of the ColorBar
        halfdim: tuple (halfw, halfh)
            Half of the dimensions measured from the center
        border_width: float
            Width of the border of the ColorBar
        orientation: "top" | "bottom" | "left" | "right"
            Position of the label with respect to the ColorBar
        transforms: TransformSystem
            the transforms of the ColorBar
        """
        (x, y) = center
        (halfw, halfh) = halfdim

        visual_to_doc = transforms.get_transform('visual', 'document')
        doc_to_visual = transforms.get_transform('document', 'visual')

        origin_doc = visual_to_doc.map(np.array([0, 0, 0, 1],
                                                dtype=np.float32))
        half_axis_x = visual_to_doc.map(np.array([halfw, 0, 0, 1],
                                                 dtype=np.float32))
        half_axis_y = visual_to_doc.map(np.array([0, halfh, 0, 1],
                                                 dtype=np.float32))

        half_axis_x -= origin_doc
        half_axis_y -= origin_doc

        # -------------------
        #               ^
        #            half_axis_y
        #               v
        #               .(center)
        # <-half_axis_x->
        # --------------------

        # downward y is positive
        if orientation in ["bottom", "top"]:
            perp_axis = half_axis_y
        else:
            perp_axis = half_axis_x

        # scale up the perpendicular by including the
        # border width (we can add it directly) since
        # we are in the document coordinate system
        # plus a text padding factor
        perp_length = np.linalg.norm(perp_axis)
        perp_axis /= perp_length
        perp_length += border_width
        perp_length *= _TEXT_PADDING_FACTOR
        perp_axis *= perp_length

        center = np.array([x, y, 0, 0], dtype=np.float32)
        perp_axis = doc_to_visual.map(perp_axis)

        if orientation == "top":
            baseline_doc = center + perp_axis
        elif orientation == "bottom":
            baseline_doc = center - perp_axis
        elif orientation == "left":
            baseline_doc = center - perp_axis
        elif orientation == "right":
            baseline_doc = center + perp_axis

        label_pos = baseline_doc[:-1]
        half_axis_x = np.array([halfw, 0, 0], dtype=np.float32)
        half_axis_y = np.array([0, halfh, 0], dtype=np.float32)
        if orientation == "top" or orientation == "bottom":
            ticks_pos = [label_pos + half_axis_x,
                         label_pos - half_axis_x]
        else:  # orientation == "top" or orientation == "bottom"
            ticks_pos = [label_pos + half_axis_y,
                         label_pos - half_axis_y]

        return (label_pos, ticks_pos)

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
