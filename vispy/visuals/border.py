# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: Siddharth Bhat
# -----------------------------------------------------------------------------

import numpy as np

from . import Visual
from ..color import Color

VERT_SHADER_BORDER = """
attribute vec2 a_position;
attribute vec2 a_adjust_dir;

void main() {
    // First map the vertex to document coordinates
    vec4 doc_pos = $visual_to_doc(vec4(a_position, 0, 1));

    // Also need to map the adjustment direction vector, but this is tricky!
    // We need to adjust separately for each component of the vector:
    vec4 adjusted;
    if ( a_adjust_dir.x == 0 ) {
        // If this is an outer vertex, no adjustment for line weight is needed.
        // (In fact, trying to make the adjustment would result in no
        // triangles being drawn, hence the if/else block)
        adjusted = doc_pos;
    }
    else {
        // Inner vertexes must be adjusted for line width, but this is
        // surprisingly tricky given that the rectangle may have been scaled
        // and rotated!
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
        adjusted = doc_pos + ($border_width / cur_width) * (doc_x + doc_y);
    }

    // Finally map the remainder of the way to render coordinates
    gl_Position = $doc_to_render(adjusted);
}
"""

FRAG_SHADER_BORDER = """
void main() {
    gl_FragColor = $border_color;
}
"""  # noqa


class _BorderVisual(Visual):
    """
    Visual subclass to display 2D pixel-width borders.

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
    border_width : float (in px)
        The width of the border the colormap should have. This measurement
        is given in pixels
    border_color : str | vispy.color.Color
        The color of the border of the colormap. This can either be a
        str as the color's name or an actual instace of a vipy.color.Color
    """

    def __init__(self, pos, halfdim,
                 border_width=1.0,
                 border_color=None,
                 **kwargs):

        self._pos = pos
        self._halfdim = halfdim
        self._border_width = border_width
        self._border_color = Color(border_color)

        Visual.__init__(self, vcode=VERT_SHADER_BORDER,
                        fcode=FRAG_SHADER_BORDER, **kwargs)

    @staticmethod
    def _prepare_transforms(view):

        program = view.shared_program
        program.vert['visual_to_doc'] = \
            view.transforms.get_transform('visual', 'document')
        program.vert['doc_to_render'] = \
            view.transforms.get_transform('document', 'render')

    @property
    def visual_border_width(self):
        """ The border width in visual coordinates
        """
        render_to_doc =  \
            self.transforms.get_transform('document', 'visual')

        vec = render_to_doc.map([self.border_width, self.border_width, 0])
        origin = render_to_doc.map([0, 0, 0])

        visual_border_width = [vec[0] - origin[0], vec[1] - origin[1]]

        # we need to flip the y axis because coordinate systems are inverted
        visual_border_width[1] *= -1

        return visual_border_width

    def _update(self):
        x, y = self._pos
        halfw, halfh = self._halfdim

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

        # Direction each vertex should move to correct for line width
        adjust_dir = np.array([
            [0, 0], [-1, -1],
            [0, 0], [1, -1],
            [0, 0], [1, 1],
            [0, 0], [-1, 1],
            [0, 0], [-1, -1],
        ], dtype=np.float32)

        self.shared_program['a_position'] = border_vertices
        self.shared_program['a_adjust_dir'] = adjust_dir
        self.shared_program.vert['border_width'] = self._border_width
        self.shared_program.frag['border_color'] = self._border_color.rgba

    def _prepare_draw(self, view=None):
        self._update()
        self._draw_mode = "triangle_strip"
        return True

    @property
    def border_width(self):
        """ The width of the border
        """
        return self._border_width

    @border_width.setter
    def border_width(self, border_width):
        self._border_width = border_width
        # positions of text need to be changed accordingly
        self._update()

    @property
    def border_color(self):
        """ The color of the border in pixels
        """
        return self._border_color

    @border_color.setter
    def border_color(self, border_color):
        self._border_color = Color(border_color)
        self.shared_program.frag['border_color'] = self._border_color.rgba

    @property
    def pos(self):
        """ The center of the BorderVisual
        """
        return self._pos

    @pos.setter
    def pos(self, pos):
        self._pos = pos
        self._update()

    @property
    def halfdim(self):
        """ The half-dimensions measured from the center of the BorderVisual
        """

        return self._halfdim

    @halfdim.setter
    def halfdim(self, halfdim):
        self._halfdim = halfdim
        self._update()
