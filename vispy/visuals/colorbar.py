# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: Siddharth Bhat
# -----------------------------------------------------------------------------

from . import Visual, TextVisual, CompoundVisual
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
    //gl_Position = doc_pos + doc_x + doc_y;
}

"""

FRAG_SHADER_BORDER = """
void main() {
    gl_FragColor = $border_color;
}
"""  # noqa


class _CoreColorBarVisual(Visual):

    def __init__(self, center_pos, halfdim,
                 cmap,
                 orientation,
                 border_width=1.0,
                 border_color="black",
                 **kwargs):

        self._cmap = get_colormap(cmap)
        self._center_pos = center_pos
        self._halfdim = halfdim
        self._orientation = orientation
        self._border_width = border_width
        self._border_color = border_color
        # setup border rendering
        self._border_color = Color(border_color)
        self._border_program = ModularProgram(VERT_SHADER_BORDER,
                                              FRAG_SHADER_BORDER)

        # Direction each vertex should move to correct for line width
        adjust_dir = np.array([
            [0, 0],
            [1, 1],
            [0, 0],
            [-1, 1],
            [0, 0],
            [-1, -1],
            [0, 0],
            [1, -1],
            [0, 0],
            [1, 1],
        ], dtype=np.float32)

        self._border_program['a_adjust_dir'] = adjust_dir.astype(np.float32)

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
            raise ColorBarVisual._get_orientation_error(self._orientation)

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
        if (self._orientation == "bottom" or
           self._orientation == "top"):
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

        border_vertices = np.array([
            [x - halfw, y - halfh],
            [x - halfw, y - halfh],
            [x + halfw, y - halfh],
            [x + halfw, y - halfh],
            [x + halfw, y + halfh],
            [x + halfw, y + halfh],
            [x - halfw, y + halfh],
            [x - halfw, y + halfh],
            [x - halfw, y - halfh],
            [x - halfw, y - halfh],
        ], dtype=np.float32)

        self.shared_program['a_position'] = vertices
        self._border_program['a_position'] = border_vertices

        self._border_program.vert['border_width'] = self._border_width
        self._border_program.frag['border_color'] = self._border_color.rgba

    @staticmethod
    def _get_orientation_error(orientation):
        return ValueError("orientation must"
                          " be 'horizontal' or 'vertical', "
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

    @property
    def border_width(self):
        """ The width of the border around the ColorBar in pixels
        """
        return self._border_width

    @border_width.setter
    def border_width(self, border_width):
        self._border_width = border_width
        # positions of text need to be changed accordingly
        self._update()

    @property
    def border_color(self):
        """ The color of the border around the ColorBar in pixels
        """
        return self._border_color

    @border_color.setter
    def border_color(self, border_color):
        self._border_color = Color(border_color)
        self._border_program.frag['border_color'] = self._border_color.rgba

    @staticmethod
    def _prepare_transforms(view):
        # transfrorm = view.transforms.get_transform()

        program = view.view_program
        border_program = view._border_program

        border_program.vert['visual_to_doc'] = \
            view.transforms.get_transform('visual', 'document')
        border_program.vert['doc_to_render'] = \
            view.transforms.get_transform('document', 'render')

        program.vert['transform'] = view.transforms.get_transform()

    def draw(self):
        """Draw the visual

        Parameters
        ----------
        transforms : instance of TransformSystem
            The transforms to use.
        """

        self._program.draw('triangles')
        self.set_gl_state(cull_face=False)
        self._border_program.draw("triangle_strip")



# The padding multiplier that's used to place the text
# next to the Colorbar. Makes sure the text isn't
# visually "sticking" to the Colorbar
_TEXT_PADDING_FACTOR = 1.2


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
        self._border_width = border_width
        self._border_color = Color(border_color)

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
            halfdim, cmap,  orientation, border_width, border_color)

        CompoundVisual.__init__(self, [self._label,
                                     self._ticks[0],
                                    self._ticks[1],
                                     self._colorbar])

        self._update()

    def _update(self):
        """Rebuilds the shaders, and repositions the objects
           that are used internally by the ColorBarVisual
        """

        self._colorbar._update()

        x, y = self._center_pos
        halfw, halfh = self._halfdim

        anchor_x, anchor_y = ColorBarVisual._get_anchors(self._orientation)
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

        # test that width and height are non-zero
        if halfw <= 0:
            raise ValueError("half-width must be positive and non-zero"
                             ", not %s", halfw)
        if halfh <= 0:
            raise ValueError("half-height must be positive and non-zero"
                             ", not %s", halfh)


        # Place the labels according to the given orientation
        if self._orientation == "bottom":
            text_x = x
            text_y = y + _TEXT_PADDING_FACTOR * (halfh + self.border_width)

            self._label.pos = text_x, text_y

            # TODO, HACK: This should ideally be a single TextVisual
            # However, one TextVisual with multiple strings
            # does not seem to be working as of now. (See #981)
            # https://github.com/vispy/vispy/issues/981
            self._ticks[0].pos = x - halfw, text_y
            self._ticks[1].pos = x + halfw, text_y

        elif self._orientation == "top":
            text_x = x
            text_y = y - _TEXT_PADDING_FACTOR * (halfh + self.border_width)
            self._label.pos = text_x, text_y

            self._ticks[0].pos = x - halfw, text_y
            self._ticks[1].pos = x + halfw, text_y

        elif self._orientation == "right":
            text_x = x + _TEXT_PADDING_FACTOR * (halfw + self.border_width)
            text_y = y
            self._label.pos = text_x, text_y
            self._label.rotation = -90

            # TODO, HACK: See comment about ticks on "horizontal" conditional
            self._ticks[0].pos = text_x, y + halfh
            self._ticks[1].pos = text_x, y - halfh
            self._ticks[0].rotation = self.ticks[1].rotation = -90

        elif self._orientation == "left":
            text_x = x - _TEXT_PADDING_FACTOR * (halfw + self.border_width)
            text_y = y
            self._label.pos = text_x, text_y
            self._label.rotation = -90

            self._ticks[0].pos = text_x, y + halfh
            self._ticks[1].pos = text_x, y - halfh
            self._ticks[0].rotation = self.ticks[1].rotation = -90

        else:
            # raise an error since the orientation is now what was
            # expected
            raise ColorBarVisual._get_orientation_error(self._orientation)

    @staticmethod
    def _get_orientation_error(orientation):
        return ValueError("orientation must"
                          " be 'horizontal' or 'vertical', "
                          "not '%s'" % (orientation, ))

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
        return self._colorbar.border_width

    @border_width.setter
    def border_width(self, border_width):
        self._colorbar.border_width = border_width
        # positions of text need to be changed accordingly
        self._update()

    @property
    def border_color(self):
        """ The color of the border around the ColorBar in pixels
        """
        return self._colorbar.border_color

    @border_color.setter
    def border_color(self, border_color):
        self._colorbar.border_color = border_color


# class ColorBarVisual(Visual):
#     """Visual subclass displaying a colorbar

#     Parameters
#     ----------
#     center_pos : tuple (x, y)
#         Position where the colorbar is to be placed with
#         respect to the center of the colorbar
#     halfdim : tuple (half_width, half_height)
#         Half the dimensions of the colorbar measured
#         from the center. That way, the total dimensions
#         of the colorbar is (x - half_width) to (x + half_width)
#         and (y - half_height) to (y + half_height)
#     cmap : str | vispy.color.ColorMap
#         Either the name of the ColorMap to be used from the standard
#         set of names (refer to `vispy.color.get_colormap`),
#         or a custom ColorMap object.
#         The ColorMap is used to apply a gradient on the colorbar.
#     orientation : {'left', 'right', 'top', 'bottom'}
#         The orientation of the colorbar, used for rendering. The
#         orientation can be thought of as the position of the label
#         relative to the color bar.

#         When the orientation is 'left' or 'right', the colorbar is
#         vertically placed. When it is 'top' or 'bottom', the colorbar is
#         horizontally placed.

#             * 'top': the colorbar is horizontal.
#               Color is applied from left to right.
#               Minimum corresponds to left and maximum to right.
#               Label is to the top of the colorbar

#             * 'bottom': Same as top, except that
#               label is to the bottom of the colorbar

#             * 'left': the colorbar is vertical.
#               Color is applied from bottom to top.
#               Minimum corresponds to bottom and maximum to top.
#               Label is to the left of the colorbar

#             * 'right': Same as left, except that the
#               label is placed to the right of the colorbar
#     label_str : str
#         The label that is to be drawn with the colorbar
#         that provides information about the colorbar.
#     clim : tuple (min, max)
#         the minimum and maximum values of the data that
#         is given to the colorbar. This is used to draw the scale
#         on the side of the colorbar.
#     border_width : float (in px)
#         The width of the border the colormap should have. This measurement
#         is given in pixels
#     border_color : str | vispy.color.Color
#         The color of the border of the colormap. This can either be a
#         str as the color's name or an actual instace of a vipy.color.Color
#     """

#     def __init__(self, center_pos, halfdim,
#                  cmap,
#                  orientation,
#                  label_str="",
#                  clim=(0.0, 1.0),
#                  border_width=1.0,
#                  border_color="black",
#                  **kwargs):

#         self._label_str = label_str
#         self._cmap = get_colormap(cmap)
#         self._clim = clim
#         self._center_pos = center_pos
#         self._halfdim = halfdim
#         self._orientation = orientation
#         self._border_width = border_width
#         self._border_color = border_color

#         self._label = None
#         self._ticks = []
#         # setup border rendering
#         self._border_color = Color(border_color)
#         self._border_program = ModularProgram(VERT_SHADER_BORDER,
#                                               FRAG_SHADER_BORDER)

#         # Direction each vertex should move to correct for line width
#         adjust_dir = np.array([
#             [0, 0],
#             [1, 1],
#             [0, 0],
#             [-1, 1],
#             [0, 0],
#             [-1, -1],
#             [0, 0],
#             [1, -1],
#             [0, 0],
#             [1, 1],
#         ], dtype=np.float32)

#         self._border_program['a_adjust_dir'] = adjust_dir.astype(np.float32)

#         # setup the right program shader based on color
#         if orientation == "top" or orientation == "bottom":
#             # self._program=ModularProgram(VERT_SHADER,FRAG_SHADER_HORIZONTAL)
#             Visual.__init__(self, vcode=VERT_SHADER,
#                             fcode=FRAG_SHADER_HORIZONTAL, **kwargs)

#         elif orientation == "left" or orientation == "right":
#             Visual.__init__(self, vcode=VERT_SHADER,
#                             fcode=FRAG_SHADER_VERTICAL, **kwargs)

#             # self._program = ModularProgram(VERT_SHADER, FRAG_SHADER_VERTICAL)
#         else:
#             raise ColorBarVisual._get_orientation_error(self._orientation)

#         tex_coords = np.array([[0, 0], [1, 0], [1, 1],
#                               [0, 0], [1, 1], [0, 1]],
#                               dtype=np.float32)

#         glsl_map_fn = Function(self._cmap.glsl_map)
#         self.shared_program.frag['color_transform'] = glsl_map_fn
#         self.shared_program['a_texcoord'] = tex_coords.astype(np.float32)

#         self._update()

#     def _update(self):
#         """Rebuilds the shaders, and repositions the objects
#            that are used internally by the ColorBarVisual
#         """

#         x, y = self._center_pos
#         halfw, halfh = self._halfdim

#         anchor_x, anchor_y = ColorBarVisual._get_anchors(self._orientation)
#         # create a new label if this is the first time this function
#         # is being called. Otherwise, just update the existing bar
#         if self._label is None:
#             self.label = TextVisual(text=self._label_str,
#                                     anchor_x=anchor_x,
#                                     anchor_y=anchor_y)
#             self.label.transforms = self.transforms
#             self.label._prepare_transforms(self.label)

#         else:
#             self.label.text = self._label_str

#         # if this is the first time we're initializing ever
#         # i.e - from the constructor, then create the TextVisual objects
#         # otherwise, just change the _text_.
#         # this is SUPER IMPORTANT, since the user might have modified the
#         # ticks first to have say, a white color. And then he might have
#         # edited the ticks.
#         # This way, we retain any changes made by the user
#         # to the _ticks while still reflecting changes in _clim
#         if self._ticks == []:
#             self._ticks.append(TextVisual(str(self._clim[0]),
#                                           anchor_x=anchor_x,
#                                           anchor_y=anchor_y))
#             self._ticks.append(TextVisual(str(self._clim[1]),
#                                           anchor_x=anchor_x,
#                                           anchor_y=anchor_y))

#             self.ticks[0].transforms = self.transforms
#             self.ticks[0]._prepare_transforms(self.label)
#             self.ticks[1].transforms = self.transforms
#             self.ticks[1]._prepare_transforms(self.label)

#         else:
#             self._ticks[0].text = str(self._clim[0])
#             self._ticks[1].text = str(self._clim[1])

#         # test that width and height are non-zero
#         if halfw <= 0:
#             raise ValueError("half-width must be positive and non-zero"
#                              ", not %s", halfw)
#         if halfh <= 0:
#             raise ValueError("half-height must be positive and non-zero"
#                              ", not %s", halfh)

#         # test that the given width and height is consistent
#         # with the orientation
#         if (self._orientation == "bottom" or
#            self._orientation == "top"):
#                 if halfw < halfh:
#                     raise ValueError("half-width(%s) < half-height(%s) for"
#                                      "%s orientation,"
#                                      " expected half-width >= half-height",
#                                      (halfw, halfh, self._orientation, ))
#         else:  # orientation == left or orientation == right
#             if halfw > halfh:
#                 raise ValueError("half-width(%s) > half-height(%s) for"
#                                  "%s orientation,"
#                                  " expected half-width <= half-height",
#                                  (halfw, halfh, self._orientation, ))

#         # Place the labels according to the given orientation
#         if self._orientation == "bottom":
#             text_x = x
#             text_y = y + _TEXT_PADDING_FACTOR * (halfh + self.border_width)

#             self._label.pos = text_x, text_y

#             # TODO, HACK: This should ideally be a single TextVisual
#             # However, one TextVisual with multiple strings
#             # does not seem to be working as of now. (See #981)
#             # https://github.com/vispy/vispy/issues/981
#             self._ticks[0].pos = x - halfw, text_y
#             self._ticks[1].pos = x + halfw, text_y

#         elif self._orientation == "top":
#             text_x = x
#             text_y = y - _TEXT_PADDING_FACTOR * (halfh + self.border_width)
#             self._label.pos = text_x, text_y

#             self._ticks[0].pos = x - halfw, text_y
#             self._ticks[1].pos = x + halfw, text_y

#         elif self._orientation == "right":
#             text_x = x + _TEXT_PADDING_FACTOR * (halfw + self.border_width)
#             text_y = y
#             self._label.pos = text_x, text_y
#             self._label.rotation = -90

#             # TODO, HACK: See comment about ticks on "horizontal" conditional
#             self._ticks[0].pos = text_x, y + halfh
#             self._ticks[1].pos = text_x, y - halfh
#             self._ticks[0].rotation = self.ticks[1].rotation = -90

#         elif self._orientation == "left":
#             text_x = x - _TEXT_PADDING_FACTOR * (halfw + self.border_width)
#             text_y = y
#             self._label.pos = text_x, text_y
#             self._label.rotation = -90

#             self._ticks[0].pos = text_x, y + halfh
#             self._ticks[1].pos = text_x, y - halfh
#             self._ticks[0].rotation = self.ticks[1].rotation = -90

#         else:
#             # raise an error since the orientation is now what was
#             # expected
#             raise ColorBarVisual._get_orientation_error(self._orientation)

#         # Set up the attributes that the shaders require
#         vertices = np.array([[x - halfw, y - halfh],
#                              [x + halfw, y - halfh],
#                              [x + halfw, y + halfh],
#                              # tri 2
#                              [x - halfw, y - halfh],
#                              [x + halfw, y + halfh],
#                              [x - halfw, y + halfh]],
#                              dtype=np.float32)

#         border_vertices = np.array([
#             [x - halfw, y - halfh],
#             [x - halfw, y - halfh],
#             [x + halfw, y - halfh],
#             [x + halfw, y - halfh],
#             [x + halfw, y + halfh],
#             [x + halfw, y + halfh],
#             [x - halfw, y + halfh],
#             [x - halfw, y + halfh],
#             [x - halfw, y - halfh],
#             [x - halfw, y - halfh],
#         ], dtype=np.float32)

#         self.shared_program['a_position'] = vertices
#         self._border_program['a_position'] = border_vertices

#         self._border_program.vert['border_width'] = self._border_width
#         self._border_program.frag['border_color'] = self._border_color.rgba

#     @staticmethod
#     def _get_orientation_error(orientation):
#         return ValueError("orientation must"
#                           " be 'horizontal' or 'vertical', "
#                           "not '%s'" % (orientation, ))

#     @staticmethod
#     def _get_anchors(orientation):
#         if orientation == "top":
#             return "center", "bottom"
#         elif orientation == "bottom":
#             return "center", "top"
#         elif orientation == "left":
#             return "center", "bottom"
#         else:  # orientation == "right"
#             return "center", "top"

#     @property
#     def cmap(self):
#         """ The colormap of the Colorbar
#         """
#         return self._cmap

#     @cmap.setter
#     def cmap(self, cmap):
#         self._cmap = get_colormap(cmap)
#         self._program.frag['color_transform'] = Function(self._cmap.glsl_map)

#     @property
#     def clim(self):
#         """ The data limits of the Colorbar

#         Returns
#         -------
#         clim: tuple(min, max)
#         """

#         return self._clim

#     @clim.setter
#     def clim(self, clim):
#         self._clim = clim
#         # new TextVisuals need to be created
#         self._update()

#     @property
#     def label(self):
#         """ The vispy.visuals.TextVisual associated with the label
#         """
#         return self._label

#     @label.setter
#     def label(self, label):
#         self._label = label
#         # position, styling has to be applied
#         self._update()

#     @property
#     def ticks(self):
#         """ The vispy.visuals.TextVisual associated with the ticks

#         Returns
#         -------
#         ticks: [vispy.visual.TextVisual]
#             The array is of length 2
#         """
#         return self._ticks

#     @ticks.setter
#     def ticks(self, ticks):
#         self._ticks = ticks
#         self._update()

#     @property
#     def border_width(self):
#         """ The width of the border around the ColorBar in pixels
#         """
#         return self._border_width

#     @border_width.setter
#     def border_width(self, border_width):
#         self._border_width = border_width
#         # positions of text need to be changed accordingly
#         self._update()

#     @property
#     def border_color(self):
#         """ The color of the border around the ColorBar in pixels
#         """
#         return self._border_color

#     @border_color.setter
#     def border_color(self, border_color):
#         self._border_color = Color(border_color)
#         self._border_program.frag['border_color'] = self._border_color.rgba

#     @staticmethod
#     def _prepare_transforms(view):
#         # transfrorm = view.transforms.get_transform()

#         program = view.view_program
#         border_program = view._border_program

#         border_program.vert['visual_to_doc'] = \
#             view.transforms.get_transform('visual', 'document')
#         border_program.vert['doc_to_render'] = \
#             view.transforms.get_transform('document', 'render')

#         program.vert['transform'] = view.transforms.get_transform()

#         # program.vert['transform'] = transforms.get_full_transform()
#         if view._label is not None:
#             view._label._prepare_transforms(view)

#         if view._ticks is not None:
#             for tick in view._ticks:
#                 tick._prepare_transforms(view)

#     def draw(self):
#         """Draw the visual

#         Parameters
#         ----------
#         transforms : instance of TransformSystem
#             The transforms to use.
#         """

#         self._program.draw('triangles')
#         self.set_gl_state(cull_face=False)
#         self._border_program.draw("triangle_strip")

#         self._label.draw()

#         for tick in self._ticks:
#             tick.draw()
