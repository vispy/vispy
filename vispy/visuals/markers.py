# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Marker Visual and shader definitions.
"""

import numpy as np

from ..color import ColorArray
from ..gloo import VertexBuffer, _check_valid
from .shaders import Function, Variable
from .visual import Visual


vert = """
uniform float u_antialias;
uniform float u_px_scale;
uniform float u_scale;

attribute vec3  a_position;
attribute vec4  a_fg_color;
attribute vec4  a_bg_color;
attribute float a_edgewidth;
attribute float a_size;

varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_edgewidth;
varying float v_antialias;

void main (void) {
    $v_size = a_size * u_px_scale * u_scale;
    v_edgewidth = a_edgewidth * u_px_scale;
    v_antialias = u_antialias;
    v_fg_color  = a_fg_color;
    v_bg_color  = a_bg_color;
    gl_Position = $transform(vec4(a_position,1.0));
    float edgewidth = max(v_edgewidth, 1.0);
    gl_PointSize = $v_size + 4*(edgewidth + 1.5*v_antialias);
}
"""


frag = """
varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_edgewidth;
varying float v_antialias;

void main()
{
    float edgewidth = max(v_edgewidth, 1.0);
    float edgealphafactor = min(v_edgewidth, 1.0);

    float size = $v_size + 4*(edgewidth + 1.5*v_antialias);
    // factor 6 for acute edge angles that need room as for star marker

    // The marker function needs to be linked with this shader
    float r = $marker(gl_PointCoord, size);

    // it takes into account an antialising layer
    // of size v_antialias inside the edge
    // r:
    // [-e/2-a, -e/2+a] antialising face-edge
    // [-e/2+a, e/2-a] core edge (center 0, diameter e-2a = 2t)
    // [e/2-a, e/2+a] antialising edge-background
    float t = 0.5*v_edgewidth - v_antialias;
    float d = abs(r) - t;

    vec4 edgecolor = vec4(v_fg_color.rgb, edgealphafactor*v_fg_color.a);

    if (r > 0.5*v_edgewidth + v_antialias)
    {
        // out of the marker (beyond the outer edge of the edge
        // including transition zone due to antialiasing)
        discard;
    }
    else if (d < 0.0)
    {
        // inside the width of the edge
        // (core, out of the transition zone for antialiasing)
        gl_FragColor = edgecolor;
    }
    else
    {
        if (v_edgewidth == 0.)
        {// no edge
            if (r > -v_antialias)
            {
                float alpha = 1.0 + r/v_antialias;
                alpha = exp(-alpha*alpha);
                gl_FragColor = vec4(v_bg_color.rgb, alpha*v_bg_color.a);
            }
            else
            {
                gl_FragColor = v_bg_color;
            }
        }
        else
        {
            float alpha = d/v_antialias;
            alpha = exp(-alpha*alpha);
            if (r > 0)
            {
                // outer part of the edge: fade out into the background...
                gl_FragColor = vec4(edgecolor.rgb, alpha*edgecolor.a);
            }
            else
            {
                gl_FragColor = mix(v_bg_color, edgecolor, alpha);
            }
        }
    }
}
"""

disc = """
float disc(vec2 pointcoord, float size)
{
    float r = length((pointcoord.xy - vec2(0.5,0.5))*size);
    r -= $v_size/2;
    return r;
}
"""


arrow = """
const float sqrt2 = sqrt(2.);
float rect(vec2 pointcoord, float size)
{
    float half_size = $v_size/2.;
    float ady = abs(pointcoord.y -.5)*size;
    float dx = (pointcoord.x -.5)*size;
    float r1 = abs(dx) + ady - half_size;
    float r2 = dx + 0.25*$v_size + ady - half_size;
    float r = max(r1,-r2);
    return r/sqrt2;//account for slanted edge and correct for width
}
"""


ring = """
float ring(vec2 pointcoord, float size)
{
    float r1 = length((pointcoord.xy - vec2(0.5,0.5))*size) - $v_size/2;
    float r2 = length((pointcoord.xy - vec2(0.5,0.5))*size) - $v_size/4;
    float r = max(r1,-r2);
    return r;
}
"""

clobber = """
const float sqrt3 = sqrt(3.);
float clobber(vec2 pointcoord, float size)
{
    const float PI = 3.14159265358979323846264;
    const float t1 = -PI/2;
    float circle_radius = 0.32 * $v_size;
    float center_shift = 0.36/sqrt3 * $v_size;
    //total size (horizontal) = 2*circle_radius + sqrt3*center_shirt = $v_size
    vec2  c1 = vec2(cos(t1),sin(t1))*center_shift;
    const float t2 = t1+2*PI/3;
    vec2  c2 = vec2(cos(t2),sin(t2))*center_shift;
    const float t3 = t2+2*PI/3;
    vec2  c3 = vec2(cos(t3),sin(t3))*center_shift;
    //xy is shift to center marker vertically
    vec2 xy = (pointcoord.xy-vec2(0.5,0.5))*size + vec2(0.,-0.25*center_shift);
    float r1 = length(xy - c1) - circle_radius;
    float r2 = length(xy - c2) - circle_radius;
    float r3 = length(xy - c3) - circle_radius;
    float r = min(min(r1,r2),r3);
    return r;
}
"""


square = """
float square(vec2 pointcoord, float size)
{
    float r = max(abs(pointcoord.x -.5)*size, abs(pointcoord.y -.5)*size);
    r -= $v_size/2;
    return r;
}
"""

x_ = """
float x_(vec2 pointcoord, float size)
{
    vec2 rotcoord = vec2((pointcoord.x + pointcoord.y - 1.) / sqrt(2.),
                         (pointcoord.y - pointcoord.x) / sqrt(2.));
    //vbar
    float r1 = abs(rotcoord.x)*size - $v_size/6;
    float r2 = abs(rotcoord.y)*size - $v_size/2;
    float vbar = max(r1,r2);
    //hbar
    float r3 = abs(rotcoord.y)*size - $v_size/6;
    float r4 = abs(rotcoord.x)*size - $v_size/2;
    float hbar = max(r3,r4);
    return min(vbar, hbar);
}
"""


diamond = """
float diamond(vec2 pointcoord, float size)
{
    float r = abs(pointcoord.x -.5)*size + abs(pointcoord.y -.5)*size;
    r -= $v_size/2;
    return r / sqrt(2.);//account for slanted edge and correct for width
}
"""


vbar = """
float vbar(vec2 pointcoord, float size)
{
    float r1 = abs(pointcoord.x - 0.5)*size - $v_size/6;
    float r3 = abs(pointcoord.y - 0.5)*size - $v_size/2;
    float r = max(r1,r3);
    return r;
}
"""

hbar = """
float rect(vec2 pointcoord, float size)
{
    float r2 = abs(pointcoord.y - 0.5)*size - $v_size/6;
    float r3 = abs(pointcoord.x - 0.5)*size - $v_size/2;
    float r = max(r2,r3);
    return r;
}
"""

cross = """
float cross(vec2 pointcoord, float size)
{
    //vbar
    float r1 = abs(pointcoord.x - 0.5)*size - $v_size/6;
    float r2 = abs(pointcoord.y - 0.5)*size - $v_size/2;
    float vbar = max(r1,r2);
    //hbar
    float r3 = abs(pointcoord.y - 0.5)*size - $v_size/6;
    float r4 = abs(pointcoord.x - 0.5)*size - $v_size/2;
    float hbar = max(r3,r4);
    return min(vbar, hbar);
}
"""


tailed_arrow = """
const float sqrt2 = sqrt(2.);
float rect(vec2 pointcoord, float size)
{
    float half_size = $v_size/2.;
    float ady = abs(pointcoord.y -.5)*size;
    float dx = (pointcoord.x -.5)*size;
    float r1 = abs(dx) + ady - half_size;
    float r2 = dx + 0.25*$v_size + ady - half_size;
    float arrow = max(r1,-r2);
    //hbar
    float upper_bottom_edges = ady - $v_size/8./sqrt2;
    float left_edge = -dx - half_size;
    float right_edge = dx + ady - half_size;
    float hbar = max(upper_bottom_edges, left_edge);
    float scale = 1.; //rescaling for slanted edge
    if (right_edge >= hbar)
    {
        hbar = right_edge;
        scale = sqrt2;
    }
    if (arrow <= hbar)
    {
        return arrow / sqrt2;//account for slanted edge and correct for width
    }
    else
    {
        return hbar / scale;
    }
}
"""


triangle_up = """
float rect(vec2 pointcoord, float size)
{
    float height = $v_size*sqrt(3.)/2.;
    float bottom = ((pointcoord.y - 0.5)*size - height/2.);
    float rotated_y = sqrt(3.)/2. * (pointcoord.x - 0.5) * size
              - 0.5 * ((pointcoord.y - 0.5)*size - height/6.) + height/6.;
    float right_edge = (rotated_y - height/2.);
    float cc_rotated_y = -sqrt(3.)/2. * (pointcoord.x - 0.5)*size
              - 0.5 * ((pointcoord.y - 0.5)*size - height/6.) + height/6.;
    float left_edge = (cc_rotated_y - height/2.);
    float slanted_edges = max(right_edge, left_edge);
    return max(slanted_edges, bottom);
}
"""

triangle_down = """
float rect(vec2 pointcoord, float size)
{
    float height = -$v_size*sqrt(3.)/2.;
    float bottom = -((pointcoord.y - 0.5)*size - height/2.);
    float rotated_y = sqrt(3.)/2. * (pointcoord.x - 0.5) * size
                - 0.5 * ((pointcoord.y - 0.5)*size - height/6.) + height/6.;
    float right_edge = -(rotated_y - height/2.);
    float cc_rotated_y = -sqrt(3.)/2. * (pointcoord.x - 0.5)*size
                - 0.5 * ((pointcoord.y - 0.5)*size - height/6.) + height/6.;
    float left_edge = -(cc_rotated_y - height/2.);
    float slanted_edges = max(right_edge, left_edge);
    return max(slanted_edges, bottom);
}
"""


star = """
float rect(vec2 pointcoord, float size)
{
    float star = -10000.;
    const float PI2_5 = 3.141592653589*2./5.;
    const float PI2_20 = 3.141592653589/10.;  //PI*2/20
    // downwards shift to that the marker center is halfway vertically
    // between the top of the upward spike (y = -v_size/2)
    // and the bottom of one of two downward spikes
    // (y = +v_size/2*cos(2*pi/10) approx +v_size/2*0.8)
    // center is at -v_size/2*0.1
    float shift_y = -0.05*$v_size;
    // first spike upwards,
    // rotate spike by 72 deg four times to complete the star
    for (int i = 0; i <= 4; i++)
    {
        //if not the first spike, rotate it upwards
        float x = (pointcoord.x - 0.5)*size;
        float y = (pointcoord.y - 0.5)*size;
        float spike_rot_angle = i*PI2_5;
        float cosangle = cos(spike_rot_angle);
        float sinangle = sin(spike_rot_angle);
        float spike_x = x;
        float spike_y = y + shift_y;
        if (i > 0)
        {
            spike_x = cosangle * x - sinangle * (y + shift_y);
            spike_y = sinangle * x + cosangle * (y + shift_y);
        }
        // in the frame where the spike is upwards:
        // rotate 18 deg the zone x < 0 around the top of the star
        // (point whose coords are -s/2, 0 where s is the size of the marker)
        // compute y coordonates as well because
        // we do a second rotation to put the spike at its final position
        float rot_center_y = -$v_size/2;
        float rot18x = cos(PI2_20) * spike_x
                            - sin(PI2_20) * (spike_y - rot_center_y);
        //rotate -18 deg the zone x > 0 arount the top of the star
        float rot_18x = cos(PI2_20) * spike_x
                            + sin(PI2_20) * (spike_y - rot_center_y);
        float bottom = spike_y - $v_size/10.;
        //                     max(left edge, right edge)
        float spike = max(bottom, max(rot18x, -rot_18x));
        if (i == 0)
        {// first spike, skip the rotation
            star = spike;
        }
        else // i > 0
        {
            star = min(star, spike);
        }
    }
    return star;
}
"""

# the following two markers needs x and y sizes
rect = """
float rect(vec2 pointcoord, float size)
{
    float x_boundaries = abs(pointcoord.x - 0.5)*size - $v_size.x/2.;
    float y_boundaries = abs(pointcoord.y - 0.5)*size - $v_size.y/2.;
    return max(x_boundaries, y_boundaries);
}
"""

ellipse = """
float rect(vec2 pointcoord, float size)
{
    float x = (pointcoord.x - 0.5)*size;
    float y = (pointcoord.y - 0.5)*size;
    // normalise radial distance (for edge and antialising to remain isotropic)
    // Scaling factor is the norm of the gradient of the function defining
    // the surface taken at a well chosen point on the edge of the ellipse
    // f(x, y) = (sqrt(x^2/a^2 + y^2/b^2) = 0.5 in this case
    // where a = v_size.x and b = v_size.y)
    // The well chosen point on the edge of the ellipse should be the point
    // whose normal points towards the current point.
    // Below we choose a different point whose computation
    // is simple enough to fit here.
    float f = length(vec2(x / $v_size.x, y / $v_size.y));
    // We set the default value of the norm so that
    // - near the axes (x=0 or y=0 +/- 1 pixel), the norm is correct
    //   (the computation below is unstable near the axes)
    // - if the ellipse is a circle, the norm is correct
    // - if we are deep in the interior of the ellipse the norm
    //   is set to an arbitrary value (but is not used)
    float norm = abs(x) < 1. ? 1./$v_size.y : 1./$v_size.x;
    if (f > 1e-3 && abs($v_size.x - $v_size.y) > 1e-3
        && abs(x) > 1. && abs(y) > 1.)
    {
        // Find the point x0, y0 on the ellipse which has the same hyperbola
        // coordinate in the elliptic coordinate system linked to the ellipse
        // (finding the right 'well chosen' point is too complicated)
        // Visually it's nice, even at high eccentricities, where
        // the approximation is visible but not ugly.
        float a = $v_size.x/2.;
        float b = $v_size.y/2.;
        float C = max(a, b);
        float c = min(a, b);
        float focal_length = sqrt(C*C - c*c);
        float fl2 = focal_length*focal_length;
        float x2 = x*x;
        float y2 = y*y;
        float tmp = fl2 + x2 + y2;
        float x0 = 0;
        float y0 = 0;
        if ($v_size.x > $v_size.y)
        {
            float cos2v = 0.5 * (tmp - sqrt(tmp*tmp - 4.*fl2*x2)) / fl2;
            cos2v = fract(cos2v);
            x0 = a * sqrt(cos2v);
            // v_size.x = focal_length*cosh m where m is the ellipse coordinate
            y0 = b * sqrt(1-cos2v);
            // v_size.y = focal_length*sinh m
        }
        else // $v_size.x < $v_size.y
        {//exchange x and y axis for elliptic coordinate
            float cos2v = 0.5 * (tmp - sqrt(tmp*tmp - 4.*fl2*y2)) / fl2;
            cos2v = fract(cos2v);
            x0 = a * sqrt(1-cos2v);
            // v_size.x = focal_length*sinh m where m is the ellipse coordinate
            y0 = b * sqrt(cos2v);
            // v_size.y = focal_length*cosh m
        }
        vec2 normal = vec2(2.*x0/v_size.x/v_size.x, 2.*y0/v_size.y/v_size.y);
        norm = length(normal);
    }
    return (f - 0.5) / norm;
}
"""

_marker_dict = {
    'disc': disc,
    'arrow': arrow,
    'ring': ring,
    'clobber': clobber,
    'square': square,
    'diamond': diamond,
    'vbar': vbar,
    'hbar': hbar,
    'cross': cross,
    'tailed_arrow': tailed_arrow,
    'x': x_,
    'triangle_up': triangle_up,
    'triangle_down': triangle_down,
    'star': star,
    # aliases
    'o': disc,
    '+': cross,
    's': square,
    '-': hbar,
    '|': vbar,
    '->': tailed_arrow,
    '>': arrow,
    '^': triangle_up,
    'v': triangle_down,
    '*': star,
}
marker_types = tuple(sorted(list(_marker_dict.keys())))


class MarkersVisual(Visual):
    """ Visual displaying marker symbols.
    """
    def __init__(self, **kwargs):
        self._vbo = VertexBuffer()
        self._v_size_var = Variable('varying float v_size')
        self._symbol = None
        self._marker_fun = None
        self._data = None
        self.antialias = 1
        self.scaling = False
        Visual.__init__(self, vcode=vert, fcode=frag)
        self.shared_program.vert['v_size'] = self._v_size_var
        self.shared_program.frag['v_size'] = self._v_size_var
        self.set_gl_state(depth_test=True, blend=True,
                          blend_func=('src_alpha', 'one_minus_src_alpha'))
        self._draw_mode = 'points'
        if len(kwargs) > 0:
            self.set_data(**kwargs)
        self.freeze()

    def set_data(self, pos=None, symbol='o', size=10., edge_width=1.,
                 edge_width_rel=None, edge_color='black', face_color='white',
                 scaling=False):
        """ Set the data used to display this visual.

        Parameters
        ----------
        pos : array
            The array of locations to display each symbol.
        symbol : str
            The style of symbol to draw (see Notes).
        size : float or array
            The symbol size in px.
        edge_width : float | None
            The width of the symbol outline in pixels.
        edge_width_rel : float | None
            The width as a fraction of marker size. Exactly one of
            `edge_width` and `edge_width_rel` must be supplied.
        edge_color : Color | ColorArray
            The color used to draw each symbol outline.
        face_color : Color | ColorArray
            The color used to draw each symbol interior.
        scaling : bool
            If set to True, marker scales when rezooming.

        Notes
        -----
        Allowed style strings are: disc, arrow, ring, clobber, square, diamond,
        vbar, hbar, cross, tailed_arrow, x, triangle_up, triangle_down,
        and star.
        """
        assert (isinstance(pos, np.ndarray) and
                pos.ndim == 2 and pos.shape[1] in (2, 3))
        if (edge_width is not None) + (edge_width_rel is not None) != 1:
            raise ValueError('exactly one of edge_width and edge_width_rel '
                             'must be non-None')
        if edge_width is not None:
            if edge_width < 0:
                raise ValueError('edge_width cannot be negative')
        else:
            if edge_width_rel < 0:
                raise ValueError('edge_width_rel cannot be negative')
        self.symbol = symbol
        self.scaling = scaling

        edge_color = ColorArray(edge_color).rgba
        if len(edge_color) == 1:
            edge_color = edge_color[0]

        face_color = ColorArray(face_color).rgba
        if len(face_color) == 1:
            face_color = face_color[0]

        n = len(pos)
        data = np.zeros(n, dtype=[('a_position', np.float32, 3),
                                  ('a_fg_color', np.float32, 4),
                                  ('a_bg_color', np.float32, 4),
                                  ('a_size', np.float32, 1),
                                  ('a_edgewidth', np.float32, 1)])
        data['a_fg_color'] = edge_color
        data['a_bg_color'] = face_color
        if edge_width is not None:
            data['a_edgewidth'] = edge_width
        else:
            data['a_edgewidth'] = size*edge_width_rel
        data['a_position'][:, :pos.shape[1]] = pos
        data['a_size'] = size
        self.shared_program['u_antialias'] = self.antialias  # XXX make prop
        self._data = data
        self._vbo.set_data(data)
        self.shared_program.bind(self._vbo)
        self.update()

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, symbol):
        if symbol == self._symbol:
            return
        self._symbol = symbol
        if symbol is None:
            self._marker_fun = None
        else:
            _check_valid('symbol', symbol, marker_types)
            self._marker_fun = Function(_marker_dict[symbol])
            self._marker_fun['v_size'] = self._v_size_var
            self.shared_program.frag['marker'] = self._marker_fun
        self.update()

    def _prepare_transforms(self, view):
        xform = view.transforms.get_transform()
        view.view_program.vert['transform'] = xform

    def _prepare_draw(self, view):
        if self._symbol is None:
            return False
        view.view_program['u_px_scale'] = view.transforms.pixel_scale
        if self.scaling:
            tr = view.transforms.get_transform('visual', 'document').simplified
            scale = np.linalg.norm((tr.map([1, 0]) - tr.map([0, 0]))[:2])
            view.view_program['u_scale'] = scale
        else:
            view.view_program['u_scale'] = 1

    def _compute_bounds(self, axis, view):
        pos = self._data['a_position']
        if pos is None:
            return None
        if pos.shape[1] > axis:
            return (pos[:, axis].min(), pos[:, axis].max())
        else:
            return (0, 0)
