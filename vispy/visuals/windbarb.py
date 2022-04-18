# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""Windbarb Visual and shader definitions."""

import numpy as np

from vispy.color import ColorArray
from vispy.gloo import VertexBuffer
from vispy.visuals.shaders import Variable
from vispy.visuals.visual import Visual

_VERTEX_SHADER = """
uniform float u_antialias;
uniform float u_px_scale;
uniform float u_scale;

attribute vec3  a_position;
attribute vec2  a_wind;
attribute vec4  a_fg_color;
attribute vec4  a_bg_color;
attribute float a_edgewidth;
attribute float a_size;
attribute float a_trig;

varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying vec2 v_wind;
varying float v_trig;
varying float v_edgewidth;
varying float v_antialias;

void main (void) {
    $v_size = a_size * u_px_scale * u_scale;
    v_edgewidth = a_edgewidth * float(u_px_scale);
    v_wind = a_wind.xy;
    v_trig = a_trig;
    v_antialias = u_antialias;
    v_fg_color  = a_fg_color;
    v_bg_color  = a_bg_color;
    gl_Position = $transform(vec4(a_position,1.0));
    float edgewidth = max(v_edgewidth, 1.0);
    gl_PointSize = ($v_size) + 4.*(edgewidth + 1.5*v_antialias);
}
"""

_FRAGMENT_SHADER = """
#include "math/constants.glsl"
#include "math/signed-segment-distance.glsl"
#include "antialias/antialias.glsl"
varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying vec2 v_wind;
varying float v_trig;
varying float v_edgewidth;
varying float v_antialias;

// SDF-Triangle by @rougier
// https://github.com/rougier/python-opengl/blob/master/code/chapter-06/SDF-triangle.py
float sdf_triangle(vec2 p, vec2 p0, vec2 p1, vec2 p2)
{
    vec2 e0 = p1 - p0;
    vec2 e1 = p2 - p1;
    vec2 e2 = p0 - p2;
    vec2 v0 = p - p0;
    vec2 v1 = p - p1;
    vec2 v2 = p - p2;
    vec2 pq0 = v0 - e0*clamp( dot(v0,e0)/dot(e0,e0), 0.0, 1.0 );
    vec2 pq1 = v1 - e1*clamp( dot(v1,e1)/dot(e1,e1), 0.0, 1.0 );
    vec2 pq2 = v2 - e2*clamp( dot(v2,e2)/dot(e2,e2), 0.0, 1.0 );
    float s = sign( e0.x*e2.y - e0.y*e2.x );
    vec2 d = min( min( vec2( dot( pq0, pq0 ), s*(v0.x*e0.y-v0.y*e0.x) ),
                     vec2( dot( pq1, pq1 ), s*(v1.x*e1.y-v1.y*e1.x) )),
                     vec2( dot( pq2, pq2 ), s*(v2.x*e2.y-v2.y*e2.x) ));
    return -sqrt(d.x)*sign(d.y);
}

void main()
{
    // Discard plotting marker body and edge if zero-size
    if ($v_size <= 0.)
        discard;

    float edgewidth = max(v_edgewidth, 1.0);
    float linewidth = max(v_edgewidth, 1.0);
    float edgealphafactor = min(v_edgewidth, 1.0);

    float size = $v_size + 4.*(edgewidth + 1.5*v_antialias);
    // factor 6 for acute edge angles that need room as for star marker
    
    vec2 wind = v_wind;
    
    if (v_trig > 0.)
    {
        float u = wind.x * cos(radians(wind.y));
        float v = wind.x * sin(radians(wind.y));
        wind = vec2(u, v);
    }
    
    // knots to m/s
    wind *= 2.;
    
    // normalized distance
    float dx = 0.5;
    // normalized center point
    vec2 O = vec2(dx);
    // normalized x-component
    vec2 X = normalize(wind) * dx / M_SQRT2 / 1.1 * vec2(1, -1);
    // normalized y-component
    // here the barb can be mirrored for southern earth * (vec2(1., -1.)
    //vec2 Y = X.yx * vec2(1., -1.); // southern hemisphere
    vec2 Y = X.yx * vec2(-1., 1.); // northern hemisphere
    // PointCoordinate
    vec2 P = gl_PointCoord;

    // calculate barb items
    float speed = length(wind);
    int flag = int(floor(speed / 50.));
    speed -= float (50 * flag);
    int longbarb = int(floor(speed / 10.));
    speed -= float (longbarb * 10);
    int shortbarb = int(floor(speed / 5.));
    int calm = shortbarb + longbarb + flag;

    // starting distance
    float r;
    // calm, plot circles
    if (calm == 0)
    {
        r = abs(length(O-P)- dx * 0.2);
        r = min(r, abs(length(O-P)- dx * 0.1));
    }
    else
    {
        // plot shaft
        r = segment_distance(P, O, O-X);
        float pos = 1.;

        // plot flag(s)
        while(flag >= 1)
        {
            r = min(r, sdf_triangle(P, O-X*pos, O-X*pos-X*.4-Y*.4, O-X*pos-X*.4));
            flag -= 1;
            pos -= 0.15;
        }
        // plot longbarb(s)
        while(longbarb >= 1)
        {
            r = min(r, segment_distance(P, O-X*pos, O-X*pos-X*.4-Y*.4));
            longbarb -= 1;
            pos -= 0.15;
        }
        // plot shortbarb
        while(shortbarb >= 1)
        {
            if (pos == 1.0)
                pos -= 0.15;
            r = min(r, segment_distance(P, O-X*pos, O-X*pos-X*.2-Y*.2));
            shortbarb -= 1;
            pos -= 0.15;
        }
    }

    // apply correction for size
    r *= size;

    vec4 edgecolor = vec4(v_fg_color.rgb, edgealphafactor*v_fg_color.a);

    if (r > 0.5 * v_edgewidth + v_antialias)
    {
        // out of the marker (beyond the outer edge of the edge
        // including transition zone due to antialiasing)
        discard;
    }

    gl_FragColor = filled(r, edgewidth, v_antialias, edgecolor);
}
"""


class WindbarbVisual(Visual):
    """Visual displaying windbarbs."""

    _shaders = {
        'vertex': _VERTEX_SHADER,
        'fragment': _FRAGMENT_SHADER,
    }

    def __init__(self, **kwargs):
        self._vbo = VertexBuffer()
        self._v_size_var = Variable('varying float v_size')
        self._marker_fun = None
        self._data = None
        Visual.__init__(self, vcode=self._shaders['vertex'], fcode=self._shaders['fragment'])
        self.shared_program.vert['v_size'] = self._v_size_var
        self.shared_program.frag['v_size'] = self._v_size_var
        self.set_gl_state(depth_test=True, blend=True,
                          blend_func=('src_alpha', 'one_minus_src_alpha'))
        self._draw_mode = 'points'
        if len(kwargs) > 0:
            self.set_data(**kwargs)
        self.freeze()

    def set_data(self, pos=None, wind=None, trig=True, size=50.,
                 antialias=1., edge_width=1., edge_color='black',
                 face_color='white'):
        """Set the data used to display this visual.

        Parameters
        ----------
        pos : array
            The array of locations to display each windbarb.
        wind : array
            The array of wind vector components to display each windbarb.
            in m/s. For knots divide by two.
        trig : bool
            True - wind contains (mag, ang)
            False - wind contains (u, v)
            defaults to True
        size : float or array
            The windbarb size in px.
        antialias : float
            The antialiased area (in pixels).
        edge_width : float | None
            The width of the windbarb outline in pixels.
        edge_color : Color | ColorArray
            The color used to draw each symbol outline.
        face_color : Color | ColorArray
            The color used to draw each symbol interior.
        """
        assert (isinstance(pos, np.ndarray) and
                pos.ndim == 2 and pos.shape[1] in (2, 3))
        assert (isinstance(wind, np.ndarray) and
                pos.ndim == 2 and pos.shape[1] == 2)
        if edge_width < 0:
            raise ValueError('edge_width cannot be negative')

        # since the windbarb starts in the fragment center,
        # we need to multiply by 2 for correct length
        size *= 2

        edge_color = ColorArray(edge_color).rgba
        if len(edge_color) == 1:
            edge_color = edge_color[0]

        face_color = ColorArray(face_color).rgba
        if len(face_color) == 1:
            face_color = face_color[0]

        n = len(pos)
        data = np.zeros(n, dtype=[('a_position', np.float32, 3),
                                  ('a_wind', np.float32, 2),
                                  ('a_trig', np.float32, 0),
                                  ('a_fg_color', np.float32, 4),
                                  ('a_bg_color', np.float32, 4),
                                  ('a_size', np.float32),
                                  ('a_edgewidth', np.float32)])
        data['a_fg_color'] = edge_color
        data['a_bg_color'] = face_color
        data['a_edgewidth'] = edge_width
        data['a_position'][:, :pos.shape[1]] = pos
        data['a_wind'][:, :wind.shape[1]] = wind
        if trig:
            data['a_trig'] = 1.
        else:
            data['a_trig'] = 0.
        data['a_size'] = size
        self.shared_program['u_antialias'] = antialias
        self._data = data
        self._vbo.set_data(data)
        self.shared_program.bind(self._vbo)
        self.update()

    def _prepare_transforms(self, view):
        xform = view.transforms.get_transform()
        view.view_program.vert['transform'] = xform

    def _prepare_draw(self, view):
        view.view_program['u_px_scale'] = view.transforms.pixel_scale
        view.view_program['u_scale'] = 1

    def _compute_bounds(self, axis, view):
        pos = self._data['a_position']
        if pos is None:
            return None
        if pos.shape[1] > axis:
            return (pos[:, axis].min(), pos[:, axis].max())
        else:
            return (0, 0)
