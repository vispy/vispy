# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: Siddharth Bhat
# -----------------------------------------------------------------------------

import numpy as np

from . import Visual, TextVisual, CompoundVisual, _BorderVisual
# from .border import _BorderVisual
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

    Parameters
    ----------
     pos : tuple (x, y)
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

    Note
    ----
    This is purely internal.
    Externally, the ColorBarVisual must be used.
    This class was separated out to encapsulate rendering information
    That way, ColorBar simply becomes a CompoundVisual

    See Also
    --------
    vispy.visuals.ColorBarVisual
    """
    def __init__(self, pos, halfdim,
                 cmap,
                 orientation,
                 **kwargs):

        self._cmap = get_colormap(cmap)
        self._pos = pos
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

        x, y = self._pos
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
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos):
        self._pos = pos
        self._update()

    @property
    def halfdim(self):
        return self._halfdim

    @halfdim.setter
    def halfdim(self, halfdim):
        self._halfdim = halfdim

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


class ColorBarVisual(CompoundVisual):
    """Visual subclass displaying a colorbar

    Parameters
    ----------
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

    size : (major_axis_length, minor_axis_length)
        lengths with respect to the major and minor axes.
        The minor axis is the shorter axis, while the major axis is
        the longer axis with respect to the orientation

        For orientations 'top' and 'bottom', the major axis is
        along the length.

        For orientations 'left' and 'right', the major axis is
        along the breadth
    pos : tuple (x, y)
        Position where the colorbar is to be placed with
        respect to the center of the colorbar
    label_str : str
        The label that is to be drawn with the colorbar
        that provides information about the colorbar.
    label_color : str | vispy.color.Color
        The color of the labels. This can either be a
        str as the color's name or an actual instace of a vipy.color.Color
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
    # The padding multiplier that's used to place the text
    # next to the Colorbar. Makes sure the text isn't
    # visually "sticking" to the Colorbar
    text_padding_factor = 1.05

    def __init__(self, cmap, orientation, size,
                 pos=[0, 0],
                 label_str="",
                 label_color='black',
                 clim=(0.0, 1.0),
                 border_width=1.0,
                 border_color="black",
                 **kwargs):

        self._label_str = label_str
        self._label_color = label_color
        self._cmap = get_colormap(cmap)
        self._clim = clim
        self._pos = pos
        self._size = size
        self._orientation = orientation

        self._label = TextVisual(self._label_str, color=self._label_color)

        self._ticks = []
        self._ticks.append(TextVisual(str(self._clim[0]), color=self._label_color))
        self._ticks.append(TextVisual(str(self._clim[1]), color=self._label_color))

        if orientation in ["top", "bottom"]:
            (width, height) = size
        elif orientation in ["left", "right"]:
            (height, width) = size
        else:
            raise _CoreColorBarVisual._get_orientation_error(orientation)

        self._halfdim = (width * 0.5, height * 0.5)

        self._colorbar = _CoreColorBarVisual(pos, self._halfdim,
                                             cmap, orientation)

        self._border = _BorderVisual(pos, self._halfdim,
                                     border_width, border_color)

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
        self._colorbar.halfdim = self._halfdim
        self._border.halfdim = self._halfdim

        self._ticks[0].text = str(self._clim[0])
        self._ticks[1].text = str(self._clim[1])

        self._update_positions()

        self._colorbar._update()
        self._border._update()

    def _update_positions(self):
        """
        updates the positions of the colorbars and labels

        """
        self._colorbar.pos = self._pos
        self._border.pos = self._pos

        if self._orientation == "right" or self._orientation == "left":
            self._label.rotation = -90

        x, y = self._pos
        halfw, halfh = self._halfdim

        label_anchors = \
            ColorBarVisual._get_label_anchors(center=self._pos,
                                              halfdim=self._halfdim,
                                              orientation=self._orientation,
                                              transforms=self.label.transforms)
        self._label.anchors = label_anchors

        ticks_anchors = \
            ColorBarVisual._get_ticks_anchors(center=self._pos,
                                              halfdim=self._halfdim,
                                              orientation=self._orientation,
                                              transforms=self.label.transforms)

        self._ticks[0].anchors = ticks_anchors
        self._ticks[1].anchors = ticks_anchors

        (label_pos, ticks_pos) = \
            ColorBarVisual._calc_positions(center=self._pos,
                                           halfdim=self._halfdim,
                                           border_width=self.border_width,
                                           orientation=self._orientation,
                                           transforms=self.transforms)

        self._label.pos = label_pos
        self._ticks[0].pos = ticks_pos[0]
        self._ticks[1].pos = ticks_pos[1]

    @staticmethod
    def _get_label_anchors(center, halfdim, orientation, transforms):
        visual_to_doc = transforms.get_transform('visual', 'document')

        doc_x = visual_to_doc.map(np.array([1, 0, 0, 0], dtype=np.float32))
        doc_y = visual_to_doc.map(np.array([0, 1, 0, 0], dtype=np.float32))

        if doc_x[0] < 0:
            doc_x *= -1

        if doc_y[1] < 0:
            doc_y *= -1

        # NOTE: these are in document coordinates
        if orientation == "bottom":
            perp_direction = doc_y
        elif orientation == "top":
            perp_direction = -doc_y
        elif orientation == "left":
            perp_direction = -doc_x
        elif orientation == "right":
            perp_direction = doc_x

        perp_direction = np.array(perp_direction, dtype=np.float32)
        perp_direction /= np.linalg.norm(perp_direction)

        # rotate axes by -90 degrees to mimic label's rotation
        if orientation in ["left", "right"]:
            x = perp_direction[0]
            y = perp_direction[1]

            perp_direction[0] = -y
            perp_direction[1] = x

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
    def _get_ticks_anchors(center, halfdim, orientation, transforms):
        visual_to_doc = transforms.get_transform('visual', 'document')

        doc_x = visual_to_doc.map(np.array([1, 0, 0, 0], dtype=np.float32))
        doc_y = visual_to_doc.map(np.array([0, 1, 0, 0], dtype=np.float32))

        if doc_x[0] < 0:
            doc_x *= -1

        if doc_y[1] < 0:
            doc_y *= -1

        # NOTE: these are in document coordinates
        if orientation == "bottom":
            perp_direction = doc_y
        elif orientation == "top":
            perp_direction = -doc_y
        elif orientation == "left":
            perp_direction = -doc_x
        elif orientation == "right":
            perp_direction = doc_x

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

        # doc_widths = visual_to_doc.map(np.array([halfw, halfh, 0, 0],
        #                                         dtype=np.float32))

        doc_x = visual_to_doc.map(np.array([halfw, 0, 0, 0], dtype=np.float32))
        doc_y = visual_to_doc.map(np.array([0, halfh, 0, 0], dtype=np.float32))

        if doc_x[0] < 0:
            doc_x *= -1

        if doc_y[1] < 0:
            doc_y *= -1

        # doc_halfw = np.abs(doc_widths[0])
        # doc_halfh = np.abs(doc_widths[1])

        if orientation == "top":
            doc_perp_vector = -doc_y
        elif orientation == "bottom":
            doc_perp_vector = doc_y
        elif orientation == "left":
            doc_perp_vector = -doc_x
        if orientation == "right":
            doc_perp_vector = doc_x

        perp_len = np.linalg.norm(doc_perp_vector)
        doc_perp_vector /= perp_len
        perp_len += border_width
        perp_len += 5  # pixels
        perp_len *= ColorBarVisual.text_padding_factor
        doc_perp_vector *= perp_len

        doc_center = visual_to_doc.map(np.array([x, y, 0, 0],
                                                dtype=np.float32))
        doc_label_pos = doc_center + doc_perp_vector
        visual_label_pos = doc_to_visual.map(doc_label_pos)[:3]

        # next, calculate tick positions
        if orientation in ["top", "bottom"]:
            doc_ticks_pos = [doc_label_pos - doc_x,
                             doc_label_pos + doc_x]
        else:
            doc_ticks_pos = [doc_label_pos + doc_y,
                             doc_label_pos - doc_y]

        visual_ticks_pos = []
        visual_ticks_pos.append(doc_to_visual.map(doc_ticks_pos[0])[:3])
        visual_ticks_pos.append(doc_to_visual.map(doc_ticks_pos[1])[:3])

        return (visual_label_pos, visual_ticks_pos)

    @property
    def pos(self):
        """ The position of the text anchor in the local coordinate frame
        """
        return self._pos

    @pos.setter
    def pos(self, pos):
        self._pos = pos
        self._update_positions()

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
        self._update()

    @property
    def label(self):
        """ The vispy.visuals.TextVisual associated with the label
        """
        return self._label

    @label.setter
    def label(self, label):
        self._label = label
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
        self._update()

    @property
    def border_color(self):
        """ The color of the border around the ColorBar in pixels
        """
        return self._border.border_color

    @border_color.setter
    def border_color(self, border_color):
        self._border.border_color = border_color
        self._update()

    @property
    def orientation(self):
        """ The orientation of the ColorBar
        """
        return self._orientation

    @property
    def size(self):
        """ The size of the ColorBar

        Returns
        -------
        size: (major_axis_length, minor_axis_length)
            major and minor axis are defined by the
            orientation of the ColorBar
        """
        (halfw, halfh) = self._halfdim
        if self.orientation in ["top", "bottom"]:
            return (halfw * 2., halfh * 2.)
        else:
            return (halfh * 2., halfw * 2.)

    @size.setter
    def size(self, size):
        if size[0] < size[1]:
            raise ValueError("Major axis must be greater than or equal to "
                             "Minor axis. Given "
                             "Major axis: (%s) < Minor axis (%s)" % (size[0],
                                                                     size[1]))

        if self.orientation in ["top", "bottom"]:
            (width, height) = size
        else:
            (height, width) = size

        if width < 0.:
            raise ValueError("width must be non-negative, not %s " % (width, ))
        elif width == 0.:
            raise ValueError("width must be non-zero, not %s" % (width, ))

        if height < 0.:
            raise ValueError("height must be non-negative, not %s " %
                             (height, ))
        elif height == 0.:
            raise ValueError("height must be non-zero, not %s" % (height, ))

        self._halfdim = (width / 2., height / 2.)
        self._update()
