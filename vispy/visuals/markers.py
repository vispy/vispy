# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""Marker Visual and shader definitions."""

import numpy as np

from ..color import ColorArray
from ..gloo import VertexBuffer
from .shaders import Function, Variable
from .visual import Visual


_VERTEX_SHADER = """
uniform float u_antialias;
uniform float u_px_scale;
uniform bool u_scaling;
uniform bool u_spherical;

attribute vec3 a_position;
attribute vec4 a_fg_color;
attribute vec4 a_bg_color;
attribute float a_edgewidth;
attribute float a_size;
attribute float a_symbol;

varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_edgewidth;
varying float v_depth_middle;
varying float v_alias_ratio;
varying float v_symbol;

float big_float = 1e10; // prevents numerical imprecision

void main (void) {
    v_fg_color  = a_fg_color;
    v_bg_color  = a_bg_color;
    // fluctuations can mess "fake integers" up, so we do +0.5 and floor to make sure it's right
    v_symbol = a_symbol + 0.5;

    vec4 pos = vec4(a_position, 1);
    vec4 fb_pos = $visual_to_framebuffer(pos);
    gl_Position = $framebuffer_to_render(fb_pos);

    // NOTE: gl_stuff uses framebuffer coords!

    if (u_scaling == true) {
        // calculate point size from visual to framebuffer coords to determine size
        // move horizontally in framebuffer space
        // then go to scene coordinates (not visual, so scaling is accounted for)
        vec4 x = $framebuffer_to_scene(fb_pos + vec4(big_float, 0, 0, 0));
        // subtract position, so we get the scene-coordinate vector describing
        // an "horizontal direction parallel to the screen"
        vec4 scene_pos = $framebuffer_to_scene(fb_pos);
        x = (x - scene_pos);
        // multiply that direction by the size (in scene space) and add it to the position
        // this gives us the position of the edge of the point, which we convert in screen space
        vec4 size_vec = $scene_to_framebuffer(scene_pos + normalize(x) * a_size);
        // divide by `w` for perspective, and subtract pos
        // this gives us the actual screen-space size of the point
        $v_size = size_vec.x / size_vec.w - fb_pos.x / fb_pos.w;
        v_edgewidth = ($v_size / a_size) * a_edgewidth;
    }
    else {
        $v_size = a_size * u_px_scale;
        v_edgewidth = a_edgewidth * u_px_scale;
    }

    // gl_PointSize is the diameter
    gl_PointSize = $v_size + 4. * (v_edgewidth + 1.5 * u_antialias);

    if (u_spherical == true) {
        // Get the framebuffer z direction relative to this sphere in visual coords
        vec4 z = $framebuffer_to_visual(fb_pos + vec4(0, 0, big_float, 0));
        z = (z - pos);
        // Get the depth of the sphere in its middle point on the screen
        // size/2 because we need the radius, not the diameter
        vec4 depth_z_vec = $visual_to_framebuffer(pos + normalize(z) * a_size / 2);
        v_depth_middle = depth_z_vec.z / depth_z_vec.w - fb_pos.z / fb_pos.w;
        // size ratio between aliased and non-aliased, needed for correct depth
        v_alias_ratio = gl_PointSize / $v_size;
    }
}
"""


_FRAGMENT_SHADER = """#version 120
uniform vec3 u_light_position;
uniform vec3 u_light_color;
uniform float u_light_ambient;
uniform float u_alpha;
uniform float u_antialias;
uniform bool u_spherical;

varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_edgewidth;
varying float v_depth_middle;
varying float v_alias_ratio;
varying float v_symbol;

void main()
{
    // Discard plotting marker body and edge if zero-size
    if ($v_size <= 0.)
        discard;

    float edgealphafactor = min(v_edgewidth, 1.0);

    float size = $v_size + 4.*(v_edgewidth + 1.5*u_antialias);
    // factor 6 for acute edge angles that need room as for star marker

    // The marker function needs to be linked with this shader
    float r = $marker(gl_PointCoord, size, int(v_symbol));

    // it takes into account an antialising layer
    // of size u_antialias inside the edge
    // r:
    // [-e/2-a, -e/2+a] antialising face-edge
    // [-e/2+a, e/2-a] core edge (center 0, diameter e-2a = 2t)
    // [e/2-a, e/2+a] antialising edge-background
    // use max because we don't want negative transition zone
    float t = max(0.5*v_edgewidth - u_antialias, 0);
    float d = abs(r) - t;

    if (r > 0.5*v_edgewidth + u_antialias)
    {
        // out of the marker (beyond the outer edge of the edge
        // including transition zone due to antialiasing)
        discard;
    }

    vec4 facecolor = v_bg_color;
    vec4 edgecolor = vec4(v_fg_color.rgb, edgealphafactor*v_fg_color.a);
    float depth_change = 0;

    // change color and depth if spherical mode is active
    if (u_spherical == true) {
        // multiply by alias_ratio and then clamp, so we're back to non-alias coordinates
        // and the aliasing ring has the same coordinates as the point just inside,
        // which is important for lighting
        vec2 texcoord = (gl_PointCoord * 2 - 1) * v_alias_ratio;
        float x = clamp(texcoord.x, -1, 1);
        float y = clamp(texcoord.y, -1, 1);
        float z = sqrt(clamp(1 - x*x - y*y, 0, 1));
        vec3 normal = vec3(x, y, z);

        // Diffuse color
        float diffuse = dot(u_light_position, normal);
        // clamp, because 0 < theta < pi/2
        diffuse = clamp(diffuse, 0, 1);
        vec3 diffuse_color = u_light_ambient + u_light_color * diffuse;

        // Specular color
        //   reflect light wrt normal for the reflected ray, then
        //   find the angle made with the eye
        vec3 eye = vec3(0, 0, -1);
        float specular = dot(reflect(u_light_position, normal), eye);
        specular = clamp(specular, 0, 1);
        // raise to the material's shininess, multiply with a
        // small factor for spread
        specular = pow(specular, 80);
        vec3 specular_color = u_light_color * specular;

        facecolor = vec4(facecolor.rgb * diffuse_color + specular_color, facecolor.a * u_alpha);
        edgecolor = vec4(edgecolor.rgb * diffuse_color + specular_color, edgecolor.a * u_alpha);
        // TODO: figure out why this 0.5 is needed, despite already having the radius, not diameter
        depth_change = -0.5 * z * v_depth_middle;
    }

    if (d < 0.0)
    {
        // inside the width of the edge
        // (core, out of the transition zone for antialiasing)
        gl_FragColor = edgecolor;
    }
    else if (v_edgewidth == 0.)
    {// no edge
        if (r > -u_antialias)
        {// outside
            float alpha = 1.0 + r/u_antialias;
            alpha = exp(-alpha*alpha);
            gl_FragColor = vec4(facecolor.rgb, alpha*facecolor.a);
        }
        else
        {// inside
            gl_FragColor = facecolor;
        }
    }
    else
    {// non-zero edge
        float alpha = d/u_antialias;
        alpha = exp(-alpha*alpha);
        if (r > 0.)
        {
            // outer part of the edge: fade out into the background...
            gl_FragColor = vec4(edgecolor.rgb, alpha*edgecolor.a);
        }
        else
        {
            // inner part of the edge: fade into the face color
            gl_FragColor = mix(facecolor, edgecolor, alpha);
        }
    }
    gl_FragDepth = gl_FragCoord.z + depth_change;
}
"""

disc = """
float r = length((pointcoord.xy - vec2(0.5,0.5))*size);
r -= $v_size/2.;
return r;
"""


arrow = """
const float sqrt2 = sqrt(2.);
float half_size = $v_size/2.;
float ady = abs(pointcoord.y -.5)*size;
float dx = (pointcoord.x -.5)*size;
float r1 = abs(dx) + ady - half_size;
float r2 = dx + 0.25*$v_size + ady - half_size;
float r = max(r1,-r2);
return r/sqrt2;//account for slanted edge and correct for width
"""


ring = """
float r1 = length((pointcoord.xy - vec2(0.5,0.5))*size) - $v_size/2.;
float r2 = length((pointcoord.xy - vec2(0.5,0.5))*size) - $v_size/4.;
float r = max(r1,-r2);
return r;
"""

clobber = """
const float sqrt3 = sqrt(3.);
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
"""


square = """
float r = max(abs(pointcoord.x -.5)*size, abs(pointcoord.y -.5)*size);
r -= $v_size/2.;
return r;
"""

x = """
vec2 rotcoord = vec2((pointcoord.x + pointcoord.y - 1.) / sqrt(2.),
 (pointcoord.y - pointcoord.x) / sqrt(2.));
//vbar
float r1 = abs(rotcoord.x)*size - $v_size/6.;
float r2 = abs(rotcoord.y)*size - $v_size/2.;
float vbar = max(r1,r2);
//hbar
float r3 = abs(rotcoord.y)*size - $v_size/6.;
float r4 = abs(rotcoord.x)*size - $v_size/2.;
float hbar = max(r3,r4);
return min(vbar, hbar);
"""


diamond = """
float r = abs(pointcoord.x -.5)*size + abs(pointcoord.y -.5)*size;
r -= $v_size/2.;
return r / sqrt(2.);//account for slanted edge and correct for width
"""


vbar = """
float r1 = abs(pointcoord.x - 0.5)*size - $v_size/6.;
float r3 = abs(pointcoord.y - 0.5)*size - $v_size/2.;
float r = max(r1,r3);
return r;
"""

hbar = """
float r2 = abs(pointcoord.y - 0.5)*size - $v_size/6.;
float r3 = abs(pointcoord.x - 0.5)*size - $v_size/2.;
float r = max(r2,r3);
return r;
"""

cross = """
//vbar
float r1 = abs(pointcoord.x - 0.5)*size - $v_size/6.;
float r2 = abs(pointcoord.y - 0.5)*size - $v_size/2.;
float vbar = max(r1,r2);
//hbar
float r3 = abs(pointcoord.y - 0.5)*size - $v_size/6.;
float r4 = abs(pointcoord.x - 0.5)*size - $v_size/2.;
float hbar = max(r3,r4);
return min(vbar, hbar);
"""


tailed_arrow = """
const float sqrt2 = sqrt(2.);
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
"""


triangle_up = """
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
"""

triangle_down = """
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
"""


star = """
float star = -10000.;
const float PI2_5 = 3.141592653589*2./5.;
const float PI2_20 = 3.141592653589/10.;  //PI*2/20
// downwards shift to that the marker center is halfway vertically
// between the top of the upward spike (y = -v_size/2.)
// and the bottom of one of two downward spikes
// (y = +v_size/2.*cos(2.*pi/10.) approx +v_size/2.*0.8)
// center is at -v_size/2.*0.1
float shift_y = -0.05*$v_size;
// first spike upwards,
// rotate spike by 72 deg four times to complete the star
for (int i = 0; i <= 4; i++)
{
//if not the first spike, rotate it upwards
float x = (pointcoord.x - 0.5)*size;
float y = (pointcoord.y - 0.5)*size;
float spike_rot_angle = float(i) * PI2_5;
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
float rot_center_y = -$v_size/2.;
float rot18x = cos(PI2_20) * spike_x
- sin(PI2_20) * (spike_y - rot_center_y);
//rotate -18 deg the zone x > 0 arount the top of the star
float rot_18x = cos(PI2_20) * spike_x
+ sin(PI2_20) * (spike_y - rot_center_y);
float bottom = spike_y - $v_size/10.;
// max(left edge, right edge)
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
"""

cross_lines = """
//vbar
float r1 = abs(pointcoord.x - 0.5)*size;
float r2 = abs(pointcoord.y - 0.5)*size - $v_size/2;
float vbar = max(r1,r2);
//hbar
float r3 = abs(pointcoord.y - 0.5)*size;
float r4 = abs(pointcoord.x - 0.5)*size - $v_size/2;
float hbar = max(r3,r4);
return min(vbar, hbar);
"""

symbol_shaders = {
    'disc': disc,
    'arrow': arrow,
    'ring': ring,
    'clobber': clobber,
    'square': square,
    'x': x,
    'diamond': diamond,
    'vbar': vbar,
    'hbar': hbar,
    'cross': cross,
    'tailed_arrow': tailed_arrow,
    'triangle_up': triangle_up,
    'triangle_down': triangle_down,
    'star': star,
    'cross_lines': cross_lines,
}

# combine all the symbol shaders in a big if-else statement
symbol_func = f"""
float symbol(vec2 pointcoord, float size, int symbol) {{
   {' else'.join(
    f''' if (symbol == {i}) {{
        // {name}
        {shader}
    }}'''
    for i, (name, shader) in enumerate(symbol_shaders.items())
    )}
}}"""

# aliases
symbol_aliases = {
    'o': 'disc',
    '+': 'cross',
    '++': 'cross_lines',
    's': 'square',
    '-': 'hbar',
    '|': 'vbar',
    '->': 'tailed_arrow',
    '>': 'arrow',
    '^': 'triangle_up',
    'v': 'triangle_down',
    '*': 'star',
}

symbol_shader_values = {name: i for i, name in enumerate(symbol_shaders)}
symbol_shader_values.update({
    **{alias: symbol_shader_values[name] for alias, name in symbol_aliases.items()},
})


class MarkersVisual(Visual):
    """Visual displaying marker symbols.

    Parameters
    ----------
    pos : array
        The array of locations to display each symbol.
    size : float or array
        The symbol size in screen (or data, if scaling is on) px.
    edge_width : float or array or None
        The width of the symbol outline in screen (or data, if scaling is on) px.
    edge_width_rel : float or array or None
        The width as a fraction of marker size. Exactly one of
        `edge_width` and `edge_width_rel` must be supplied.
    edge_color : Color | ColorArray
        The color used to draw each symbol outline.
    face_color : Color | ColorArray
        The color used to draw each symbol interior.
    symbol : str or array
        The style of symbol used to draw each marker (see Notes).
    scaling : bool
        If set to True, marker scales when rezooming.
    alpha : float
        The opacity level of the visual.
    antialias : float
        Antialiasing amount (in px).
    spherical : bool
        Whether to add a spherical effect on the marker using lighting.
    light_color : Color | ColorArray
        The color of the light used to create the spherical effect.
    light_position : array
        The coordinates of the light used to create the spherical effect.
    light_ambient : float
        The amount of ambient light used to create the spherical effect.

    Notes
    -----
    Allowed style strings are: disc, arrow, ring, clobber, square, diamond,
    vbar, hbar, cross, tailed_arrow, x, triangle_up, triangle_down,
    and star.
    """

    _shaders = {
        'vertex': _VERTEX_SHADER,
        'fragment': _FRAGMENT_SHADER,
    }
    _symbol_shader_values = symbol_shader_values
    _symbol_shader = symbol_func

    def __init__(self, scaling=False, alpha=1, antialias=1, spherical=False,
                 light_color='white', light_position=(1, -1, 1), light_ambient=0.3, **kwargs):
        self._vbo = VertexBuffer()
        self._data = None

        Visual.__init__(self, vcode=self._shaders['vertex'], fcode=self._shaders['fragment'])
        self._symbol_func = Function(self._symbol_shader)
        self.shared_program.frag['marker'] = self._symbol_func
        self._v_size_var = Variable('varying float v_size')
        self.shared_program.vert['v_size'] = self._v_size_var
        self.shared_program.frag['v_size'] = self._v_size_var
        self._symbol_func['v_size'] = self._v_size_var

        self.set_gl_state(depth_test=True, blend=True,
                          blend_func=('src_alpha', 'one_minus_src_alpha'))
        self._draw_mode = 'points'

        if len(kwargs) > 0:
            self.set_data(**kwargs)

        self.scaling = scaling
        self.antialias = antialias
        self.light_color = light_color
        self.light_position = light_position
        self.light_ambient = light_ambient
        self.alpha = alpha
        self.spherical = spherical

        self.freeze()

    def set_data(self, pos=None, size=10., edge_width=1., edge_width_rel=None,
                 edge_color='black', face_color='white',
                 symbol='o'):
        """Set the data used to display this visual.

        Parameters
        ----------
        pos : array
            The array of locations to display each symbol.
        size : float or array
            The symbol size in screen (or data, if scaling is on) px.
        edge_width : float or array or None
            The width of the symbol outline in screen (or data, if scaling is on) px.
        edge_width_rel : float or array or None
            The width as a fraction of marker size. Exactly one of
            `edge_width` and `edge_width_rel` must be supplied.
        edge_color : Color | ColorArray
            The color used to draw each symbol outline.
        face_color : Color | ColorArray
            The color used to draw each symbol interior.
        symbol : str or array
            The style of symbol used to draw each marker (see Notes).
        """
        if (edge_width is not None) + (edge_width_rel is not None) != 1:
            raise ValueError('exactly one of edge_width and edge_width_rel '
                             'must be non-None')

        if edge_width is not None:
            edge_width = np.asarray(edge_width)
            if np.any(edge_width < 0):
                raise ValueError('edge_width cannot be negative')
        else:
            edge_width_rel = np.asarray(edge_width_rel)
            if np.any(edge_width_rel < 0):
                raise ValueError('edge_width_rel cannot be negative')

        if symbol is not None:
            if not np.all(np.isin(np.asarray(symbol), self.symbols)):
                raise ValueError(f'symbols must one of {self.symbols}')

        edge_color = ColorArray(edge_color).rgba
        if len(edge_color) == 1:
            edge_color = edge_color[0]

        face_color = ColorArray(face_color).rgba
        if len(face_color) == 1:
            face_color = face_color[0]

        if pos is not None:
            assert (isinstance(pos, np.ndarray) and
                    pos.ndim == 2 and pos.shape[1] in (2, 3))

            n = len(pos)
            data = np.zeros(n, dtype=[('a_position', np.float32, 3),
                                      ('a_fg_color', np.float32, 4),
                                      ('a_bg_color', np.float32, 4),
                                      ('a_size', np.float32),
                                      ('a_edgewidth', np.float32),
                                      ('a_symbol', np.float32)])
            data['a_fg_color'] = edge_color
            data['a_bg_color'] = face_color
            if edge_width is not None:
                data['a_edgewidth'] = edge_width
            else:
                data['a_edgewidth'] = size * edge_width_rel
            data['a_position'][:, :pos.shape[1]] = pos
            data['a_size'] = size

            data['a_symbol'] = np.vectorize(self._symbol_shader_values.get)(symbol)

            self._data = data
            self._vbo.set_data(data)
            self.shared_program.bind(self._vbo)

        self.update()

    @property
    def symbols(self):
        return list(self._symbol_shader_values)

    @property
    def symbol(self):
        value_to_symbol = {v: k for k, v in self._symbol_shader_values.items()}
        return np.vectorize(value_to_symbol.get)(self._data['a_symbol'])

    @symbol.setter
    def symbol(self, value):
        rec_to_kw = {
            'a_position': 'pos',
            'a_fg_color': 'edge_color',
            'a_bg_color': 'face_color',
            'a_size': 'size',
            'a_edgewidth': 'edge_width',
            'a_symbol': 'symbol',
        }
        kwargs = {kw: self._data[rec] for rec, kw in rec_to_kw.items()}
        kwargs['symbol'] = value
        self.set_data(**kwargs)

    @property
    def scaling(self):
        """
        If set to True, marker scales when rezooming.
        """
        return self._scaling

    @scaling.setter
    def scaling(self, value):
        value = bool(value)
        self.shared_program['u_scaling'] = value
        self._scaling = value
        self.update()

    @property
    def antialias(self):
        """
        Antialiasing amount (in px).
        """
        return self._antialias

    @antialias.setter
    def antialias(self, value):
        value = float(value)
        self.shared_program['u_antialias'] = value
        self._antialias = value
        self.update()

    @property
    def light_position(self):
        """
        The coordinates of the light used to create the spherical effect.
        """
        return self._light_position

    @light_position.setter
    def light_position(self, value):
        value = np.array(value)
        self.shared_program['u_light_position'] = value / np.linalg.norm(value)
        self._light_position = value
        self.update()

    @property
    def light_ambient(self):
        """
        The amount of ambient light used to create the spherical effect.
        """
        return self._light_ambient

    @light_ambient.setter
    def light_ambient(self, value):
        self.shared_program['u_light_ambient'] = value
        self._light_ambient = value
        self.update()

    @property
    def light_color(self):
        """
        The color of the light used to create the spherical effect.
        """
        return self._light_color

    @light_color.setter
    def light_color(self, value):
        self.shared_program['u_light_color'] = ColorArray(value).rgb
        self._light_color = value
        self.update()

    @property
    def alpha(self):
        """
        The opacity level of the visual.
        """
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        self.shared_program['u_alpha'] = value
        self._alpha = value
        self.update()

    @property
    def spherical(self):
        """
        Whether to add a spherical effect on the marker using lighting.
        """
        return self._spherical

    @spherical.setter
    def spherical(self, value):
        self.shared_program['u_spherical'] = value
        self._spherical = value
        self.update()

    def _prepare_transforms(self, view):
        view.view_program.vert['visual_to_framebuffer'] = view.get_transform('visual', 'framebuffer')
        view.view_program.vert['framebuffer_to_visual'] = view.get_transform('framebuffer', 'visual')
        view.view_program.vert['framebuffer_to_render'] = view.get_transform('framebuffer', 'render')
        view.view_program.vert['framebuffer_to_scene'] = view.get_transform('framebuffer', 'scene')
        view.view_program.vert['scene_to_framebuffer'] = view.get_transform('scene', 'framebuffer')

    def _prepare_draw(self, view):
        if self._data is None:
            return False
        view.view_program['u_px_scale'] = view.transforms.pixel_scale
        view.view_program['u_scaling'] = self.scaling

    def _compute_bounds(self, axis, view):
        pos = self._data['a_position']
        if pos is None:
            return None
        if pos.shape[1] > axis:
            return (pos[:, axis].min(), pos[:, axis].max())
        else:
            return (0, 0)
