# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from .image import ImageVisual
from ..color import Color
from .shaders import Function


_GRID_COLOR = """
vec4 grid_color(vec2 pos) {
    vec4 px_pos = $map_to_doc(vec4(pos, 0, 1));
    px_pos /= px_pos.w;

    // Compute vectors representing width, height of pixel in local coords
    float s = 1.;
    vec4 local_pos = $map_doc_to_local(px_pos);
    vec4 dx = $map_doc_to_local(px_pos + vec4(1.0 / s, 0, 0, 0));
    vec4 dy = $map_doc_to_local(px_pos + vec4(0, 1.0 / s, 0, 0));
    local_pos /= local_pos.w;
    dx = dx / dx.w - local_pos;
    dy = dy / dy.w - local_pos;

    // Pixel length along each axis, rounded to the nearest power of 10
    vec2 px = s * vec2(abs(dx.x) + abs(dy.x), abs(dx.y) + abs(dy.y));
    float log10 = log(10.0);
    float sx = pow(10.0, floor(log(px.x) / log10) + 1.) * $scale.x;
    float sy = pow(10.0, floor(log(px.y) / log10) + 1.) * $scale.y;

    float max_alpha = 0.6;
    float x_alpha = 0.0;

    if (mod(local_pos.x, 1000. * sx) < px.x) {
        x_alpha = clamp(1. * sx/px.x, 0., max_alpha);
    }
    else if (mod(local_pos.x, 100. * sx) < px.x) {
        x_alpha = clamp(.1 * sx/px.x, 0., max_alpha);
    }
    else if (mod(local_pos.x, 10. * sx) < px.x) {
        x_alpha = clamp(0.01 * sx/px.x, 0., max_alpha);
    }

    float y_alpha = 0.0;
    if (mod(local_pos.y, 1000. * sy) < px.y) {
        y_alpha = clamp(1. * sy/px.y, 0., max_alpha);
    }
    else if (mod(local_pos.y, 100. * sy) < px.y) {
        y_alpha = clamp(.1 * sy/px.y, 0., max_alpha);
    }
    else if (mod(local_pos.y, 10. * sy) < px.y) {
        y_alpha = clamp(0.01 * sy/px.y, 0., max_alpha);
    }

    float alpha = (((log(max(x_alpha, y_alpha))/log(10.)) + 2.) / 3.);
    if (alpha == 0.) {
        discard;
    }
    return vec4($color.rgb, $color.a * alpha);
}
"""


class GridLinesVisual(ImageVisual):
    """Displays regularly spaced grid lines in any coordinate system and at
    any scale.

    Parameters
    ----------
    scale : tuple
        The scale factors to apply when determining the spacing of grid lines.
    color : Color
        The base color for grid lines. The final color may have its alpha
        channel modified.
    """

    def __init__(self, scale=(1, 1), color='w'):
        # todo: PlaneVisual should support subdivide/impostor methods from
        # image and gridlines should inherit from plane instead.
        self._grid_color_fn = Function(_GRID_COLOR)
        self._grid_color_fn['color'] = Color(color).rgba
        self._grid_color_fn['scale'] = scale
        ImageVisual.__init__(self, method='impostor')
        self.set_gl_state('additive', cull_face=False)
        self.shared_program.frag['get_data'] = self._grid_color_fn
        cfun = Function('vec4 null(vec4 x) { return x; }')
        self.shared_program.frag['color_transform'] = cfun

    @property
    def size(self):
        return (1, 1)

    def _prepare_transforms(self, view):
        fn = self._grid_color_fn
        fn['map_to_doc'] = self.get_transform('visual', 'document')
        fn['map_doc_to_local'] = self.get_transform('document', 'visual')
        ImageVisual._prepare_transforms(self, view)

    def _prepare_draw(self, view):
        if self._need_vertex_update:
            self._build_vertex_data()

        if view._need_method_update:
            self._update_method(view)
