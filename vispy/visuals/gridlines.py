# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .. import gloo
from .visual import Visual

VERT = """
attribute vec2 pos;
varying vec4 v_pos;
void main() {
    v_pos = vec4(pos, 0, 1);
    gl_Position = v_pos;
}
"""

FRAG = """
varying vec4 v_pos;
uniform vec2 scale;

void main() {
    vec4 px_pos = $map_nd_to_doc(v_pos);

    // Compute vectors representing width, height of pixel in local coords
    float s = 1.;
    vec4 local_pos = $map_doc_to_local(px_pos);
    vec4 dx = $map_doc_to_local(px_pos + vec4(1.0 / s, 0, 0, 0)) - local_pos;
    vec4 dy = $map_doc_to_local(px_pos + vec4(0, 1.0 / s, 0, 0)) - local_pos;

    // Pixel length along each axis, rounded to the nearest power of 10
    vec2 px = s * vec2(abs(dx.x) + abs(dy.x), abs(dx.y) + abs(dy.y));
    float log10 = log(10.0);
    float sx = pow(10.0, floor(log(px.x) / log10)+1) * scale.x;
    float sy = pow(10.0, floor(log(px.y) / log10)+1) * scale.y;

    float max_alpha = 0.6;
    float x_alpha = 0.0;

    if (mod(local_pos.x, 1000 * sx) < px.x) {
        x_alpha = clamp(1 * sx/px.x, 0, max_alpha);
    }
    else if (mod(local_pos.x, 100 * sx) < px.x) {
        x_alpha = clamp(.1 * sx/px.x, 0, max_alpha);
    }
    else if (mod(local_pos.x, 10 * sx) < px.x) {
        x_alpha = clamp(0.01 * sx/px.x, 0, max_alpha);
    }

    float y_alpha = 0.0;
    if (mod(local_pos.y, 1000 * sy) < px.y) {
        y_alpha = clamp(1 * sy/px.y, 0, max_alpha);
    }
    else if (mod(local_pos.y, 100 * sy) < px.y) {
        y_alpha = clamp(.1 * sy/px.y, 0, max_alpha);
    }
    else if (mod(local_pos.y, 10 * sy) < px.y) {
        y_alpha = clamp(0.01 * sy/px.y, 0, max_alpha);
    }

    float alpha = (((log(max(x_alpha, y_alpha))/log(10.))+2) / 3);
    if (alpha == 0) {
        discard;
    }
    gl_FragColor = vec4(1, 1, 1, alpha);
}
"""


class GridLinesVisual(Visual):
    """ Displays regularly spaced grid lines in any coordinate system and at
    any scale.

    Parameters
    ----------
    scale : tuple
        The scale to use.
    """
    def __init__(self, scale=(1, 1)):
        Visual.__init__(self, vcode=VERT, fcode=FRAG)
        self._vbo = None
        self._scale = scale
        self.set_gl_state('additive', cull_face=False)
        self._draw_mode = 'triangles'

    def _buffer(self):
        if self._vbo is None:
            # quad covers entire view; frag. shader will deal with image shape
            quad = np.array([[-1, -1], [1, -1], [1, 1],
                             [-1, -1], [1, 1], [-1, 1]],
                            dtype=np.float32)
            self._vbo = gloo.VertexBuffer(quad)
        return self._vbo

    def _prepare_transforms(self, view):
        frag = view.view_program.frag
        trs = self.transforms
        frag['map_nd_to_doc'] = trs.get_transform('render', 'document')
        frag['map_doc_to_local'] = trs.get_transform('document', 'visual')

    def _prepare_draw(self, view):
        self._program['pos'] = self._buffer()
        self._program['scale'] = self._scale

    def _compute_bounds(self, axis, view):
        return None
