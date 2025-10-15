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
from ..util.event import Event


_VERTEX_SHADER_TEMPLATE = """
uniform float u_antialias;
uniform float u_px_scale;
uniform bool u_scaling;
uniform bool u_spherical;
uniform float u_canvas_size_min;
uniform float u_canvas_size_max;

attribute vec3 a_position;
attribute vec4 a_fg_color;
attribute vec4 a_bg_color;
attribute float a_edgewidth;
attribute float a_size;
attribute float a_symbol;
{extra_attributes}

varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_edgewidth;
varying float v_depth_middle;
varying float v_alias_ratio;
varying float v_symbol;
{extra_varyings}

float big_float = 1e10; // prevents numerical imprecision

void main (void) {{
    v_fg_color  = a_fg_color;
    v_bg_color  = a_bg_color;
    // fluctuations can mess "fake integers" up, so we do +0.5 and floor to make sure it's right
    v_symbol = a_symbol + 0.5;

    {pre_transform}

    vec4 pos = vec4(a_position, 1);
    vec4 fb_pos = $visual_to_framebuffer(pos);
    vec4 x;
    vec4 size_vec;
    {initial_position}

    // NOTE: gl_stuff uses framebuffer coords!
    if (u_scaling) {{
        // scaling == "scene": scale marker using entire visual -> framebuffer set of transforms
        // scaling == "visual": scale marker using only the Visual's transform
        pos = $framebuffer_to_scene_or_visual(fb_pos);
        x = $framebuffer_to_scene_or_visual(fb_pos + vec4(big_float, 0, 0, 0));
        x = (x - pos);
        // multiply that direction by the size and add it to the position
        // this gives us the position of the edge of the point, which we convert in screen space
        size_vec = $scene_or_visual_to_framebuffer(pos + normalize(x) * a_size);
        // divide by `w` for perspective, and subtract pos
        // this gives us the actual screen-space size of the point
        $v_size = size_vec.x / size_vec.w - fb_pos.x / fb_pos.w;
        v_edgewidth = ($v_size / a_size) * a_edgewidth;
    }}
    else {{
        // scaling == "fixed": marker is always the same number of pixels
        $v_size = a_size * u_px_scale;
        v_edgewidth = a_edgewidth * u_px_scale;
    }}

    // Optional canvas size clamping
    float original_size = $v_size;
    if (u_canvas_size_min >= 0.0) {{
        $v_size = max($v_size, u_canvas_size_min);
    }}
    if (u_canvas_size_max >= 0.0) {{
        $v_size = min($v_size, u_canvas_size_max);
    }}
    // Update edge width proportionally if size was clamped
    if ($v_size != original_size) {{
        v_edgewidth = v_edgewidth * ($v_size / original_size);
    }}

    // Total size including edge and antialiasing
    float total_size = $v_size + 4. * (v_edgewidth + 1.5 * u_antialias);

    {post_size}

    if (u_spherical == true) {{
        // similar as above for scaling, but in towards the screen direction
        // Get the framebuffer z direction relative to this sphere in visual coords
        vec4 z = $framebuffer_to_scene_or_visual(fb_pos + vec4(0, 0, big_float, 0));
        z = (z - pos);
        // Get the depth of the sphere in its middle point on the screen
        // size/2 because we need the radius, not the diameter
        vec4 depth_z_vec = $scene_or_visual_to_framebuffer(pos + normalize(z) * a_size / 2);
        v_depth_middle = depth_z_vec.z / depth_z_vec.w - fb_pos.z / fb_pos.w;
        // size ratio between aliased and non-aliased, needed for correct depth
        v_alias_ratio = total_size / $v_size;
    }}
}}
"""

_VERTEX_SHADER = _VERTEX_SHADER_TEMPLATE.format(
    extra_attributes="",
    extra_varyings="",
    pre_transform="",
    initial_position="gl_Position = $framebuffer_to_render(fb_pos);",
    post_size="gl_PointSize = total_size;",
)

_INSTANCED_VERTEX_SHADER = _VERTEX_SHADER_TEMPLATE.format(
    extra_attributes="attribute vec2 a_quad_pos;",
    extra_varyings="varying vec2 v_texcoord;",
    pre_transform="""\
    // Convert from (-0.5, 0.5) to (0, 1) for texture sampling
    v_texcoord = a_quad_pos + 0.5;
    v_texcoord.y = 1.0 - v_texcoord.y;""",
    initial_position="",
    post_size="""\
    // Apply offset in framebuffer space
    vec2 offset = a_quad_pos * total_size;
    vec4 offset_fb_pos = fb_pos + vec4(offset, 0, 0);
    gl_Position = $framebuffer_to_render(offset_fb_pos);""",
)


_FRAGMENT_SHADER_TEMPLATE = """#version 120
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
{extra_varyings}

void main()
{{
    // Discard plotting marker body and edge if zero-size
    if ($v_size <= 0.)
        discard;

    float edgealphafactor = min(v_edgewidth, 1.0);

    float size = $v_size + 4.*(v_edgewidth + 1.5*u_antialias);
    // factor 6 for acute edge angles that need room as for star marker

    // The marker function needs to be linked with this shader
    float r = $marker({pointcoord}, size, int(v_symbol));

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
    {{
        // out of the marker (beyond the outer edge of the edge
        // including transition zone due to antialiasing)
        discard;
    }}

    vec4 facecolor = v_bg_color;
    vec4 edgecolor = vec4(v_fg_color.rgb, edgealphafactor*v_fg_color.a);
    float depth_change = 0;

    // change color and depth if spherical mode is active
    if (u_spherical == true) {{
        // multiply by alias_ratio and then clamp, so we're back to non-alias coordinates
        // and the aliasing ring has the same coordinates as the point just inside,
        // which is important for lighting
        vec2 texcoord = ({pointcoord} * 2 - 1) * v_alias_ratio;
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
    }}

    if (d < 0.0)
    {{
        // inside the width of the edge
        // (core, out of the transition zone for antialiasing)
        gl_FragColor = edgecolor;
    }}
    else if (v_edgewidth == 0.)
    {{// no edge
        if (r > -u_antialias)
        {{// outside
            float alpha = 1.0 + r/u_antialias;
            alpha = exp(-alpha*alpha);
            gl_FragColor = vec4(facecolor.rgb, alpha*facecolor.a);
        }}
        else
        {{// inside
            gl_FragColor = facecolor;
        }}
    }}
    else
    {{// non-zero edge
        float alpha = d/u_antialias;
        alpha = exp(-alpha*alpha);
        if (r > 0.)
        {{
            // outer part of the edge: fade out into the background...
            gl_FragColor = vec4(edgecolor.rgb, alpha*edgecolor.a);
        }}
        else
        {{
            // inner part of the edge: fade into the face color
            gl_FragColor = mix(facecolor, edgecolor, alpha);
        }}
    }}
    gl_FragDepth = gl_FragCoord.z + depth_change;
}}
"""

_FRAGMENT_SHADER = _FRAGMENT_SHADER_TEMPLATE.format(
    pointcoord="gl_PointCoord",
    extra_varyings=""
)

_INSTANCED_FRAGMENT_SHADER = _FRAGMENT_SHADER_TEMPLATE.format(
    pointcoord="v_texcoord",
    extra_varyings="varying vec2 v_texcoord;"
)


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
        Defaults to 1.0 if None or not provided and ``edge_width_rel`` is not
        provided.
    edge_width_rel : float or array or None
        The width as a fraction of marker size. Can not be specified along with
        edge_width. A ValueError will be raised if both are provided.
    edge_color : Color | ColorArray
        The color used to draw each symbol outline.
    face_color : Color | ColorArray
        The color used to draw each symbol interior.
    symbol : str or array
        The style of symbol used to draw each marker (see Notes).
    scaling : str | bool
        Scaling method of individual markers. If set to "fixed" (default) then
        no scaling is done and markers will always be the same number of
        pixels on the screen. If set to "scene" then the chain of transforms
        from the Visual's transform to the transform mapping to the OpenGL
        framebuffer are used to scaling the marker. This has the effect of the
        marker staying the same size in the "scene" coordinate space and
        changing size as the visualization is zoomed in and out. If set to
        "visual" the marker is scaled only using the transform of the Visual
        and not the rest of the scene/camera. This means that something like
        a camera changing the view will not affect the size of the marker, but
        the user can still scale it using the Visual's transform. For
        backwards compatibility this can be set to the boolean ``False`` for
        "fixed" or ``True`` for "scene".
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
    method : str
        Rendering method for markers. Options are:

        * 'points' (default): Use GL_POINTS primitive. Fast but may have
          platform-specific size limitations.
        * 'instanced': Use instanced rendering of quads. Works around point
          size limitations on some platforms.

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
    _instanced_shaders = {
        'vertex': _INSTANCED_VERTEX_SHADER,
        'fragment': _INSTANCED_FRAGMENT_SHADER,
    }
    _symbol_shader_values = symbol_shader_values
    _symbol_shader = symbol_func

    def __init__(self, scaling="fixed", alpha=1, antialias=1, spherical=False,
                 light_color='white', light_position=(1, -1, 1), light_ambient=0.3,
                 method='points', **kwargs):
        self._vbo = VertexBuffer()
        self._quad_vbo = None
        self._data = None
        self._scaling = "fixed"
        self._canvas_size_limits = None

        if method == 'points':
            shaders = self._shaders
        elif method == 'instanced':
            shaders = self._instanced_shaders
            # instancing draws a small quad for each marker
            quad_vertices = np.array([
                # triangle 1
                [-0.5, -0.5],  # bottom-left
                [0.5, -0.5],   # bottom-right
                [-0.5, 0.5],   # top-left
                # triangle 2
                [0.5, -0.5],   # bottom-right
                [0.5, 0.5],    # top-right
                [-0.5, 0.5],   # top-left
            ], dtype=np.float32)
            self._quad_vbo = VertexBuffer(quad_vertices)
        else:
            raise ValueError(f"method must be 'points' or 'instanced', got {method!r}")

        self._method = method

        Visual.__init__(self, vcode=shaders['vertex'], fcode=shaders['fragment'])
        self._symbol_func = Function(self._symbol_shader)
        self.shared_program.frag['marker'] = self._symbol_func
        self._v_size_var = Variable('varying float v_size')
        self.shared_program.vert['v_size'] = self._v_size_var
        self.shared_program.frag['v_size'] = self._v_size_var
        self._symbol_func['v_size'] = self._v_size_var
        self.shared_program['u_canvas_size_min'] = -1.0
        self.shared_program['u_canvas_size_max'] = -1.0

        self._draw_mode = 'points' if self._method == 'points' else 'triangles'

        self.set_gl_state(depth_test=True, blend=True,
                          blend_func=('src_alpha', 'one_minus_src_alpha'))

        self.events.add(data_updated=Event)

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

    def _prepare_edge_width(self, edge_width, edge_width_rel):
        """Validate and return edge width parameters."""
        if edge_width is not None and edge_width_rel is not None:
            raise ValueError("either edge_width or edge_width_rel "
                             "should be provided, not both")

        if edge_width is None and edge_width_rel is None:
            return np.asarray(1.0), None

        if edge_width is not None:
            edge_width = np.asarray(edge_width)
            if np.any(edge_width < 0):
                raise ValueError('edge_width cannot be negative')
            return edge_width, None
        else:
            edge_width_rel = np.asarray(edge_width_rel)
            if np.any(edge_width_rel < 0):
                raise ValueError('edge_width_rel cannot be negative')
            return None, edge_width_rel

    def _prepare_colors(self, edge_color, face_color):
        """Prepare and normalize color arrays."""
        edge_color = ColorArray(edge_color).rgba
        if len(edge_color) == 1:
            edge_color = edge_color[0]

        face_color = ColorArray(face_color).rgba
        if len(face_color) == 1:
            face_color = face_color[0]

        return edge_color, face_color

    def _prepare_symbol_values(self, symbol, n):
        """Convert symbol names to numeric values and broadcast."""
        if symbol is None:
            return np.zeros(n, dtype=np.float32)

        if isinstance(symbol, str):
            symbol = [symbol]

        try:
            symbol_values = np.array([self._symbol_shader_values[x] for x in symbol], dtype=np.float32)
            if len(symbol_values) == 1:
                symbol_values = np.full(n, symbol_values[0], dtype=np.float32)
            return symbol_values
        except KeyError:
            raise ValueError(f'symbols must one of {self.symbols}')

    def _prepare_data_dict(self, pos, size, edge_width, edge_width_rel,
                           edge_color, face_color, symbol):
        """Prepare attribute data as a dictionary."""
        assert (isinstance(pos, np.ndarray) and
                pos.ndim == 2 and pos.shape[1] in (2, 3))

        n = len(pos)

        position = np.zeros((n, 3), dtype=np.float32)
        position[:, :pos.shape[1]] = pos

        symbol_values = self._prepare_symbol_values(symbol, n)

        edgewidth = edge_width if edge_width is not None else size * edge_width_rel

        size_array = _broadcast_scalar(size, n)
        edgewidth_array = _broadcast_scalar(edgewidth, n)
        edge_color_array = _broadcast_color(edge_color, n)
        face_color_array = _broadcast_color(face_color, n)

        return {
            'a_position': position,
            'a_fg_color': edge_color_array,
            'a_bg_color': face_color_array,
            'a_size': size_array,
            'a_edgewidth': edgewidth_array,
            'a_symbol': symbol_values,
        }

    def _upload_instanced_data(self, data_dict):
        """Upload data for instanced rendering."""
        self._data = data_dict
        self.shared_program['a_quad_pos'] = self._quad_vbo

        for attr_name, attr_data in data_dict.items():
            self.shared_program[attr_name] = VertexBuffer(
                np.require(attr_data, requirements='C'),
                divisor=1
            )

    def _upload_points_data(self, data_dict):
        """Upload data for points rendering."""
        n = len(data_dict['a_position'])
        structured_data = np.zeros(n, dtype=[
            ('a_position', np.float32, 3),
            ('a_fg_color', np.float32, 4),
            ('a_bg_color', np.float32, 4),
            ('a_size', np.float32),
            ('a_edgewidth', np.float32),
            ('a_symbol', np.float32)
        ])
        for attr_name, attr_data in data_dict.items():
            structured_data[attr_name] = attr_data

        self._data = structured_data
        self._vbo.set_data(structured_data)
        self.shared_program.bind(self._vbo)

    def set_data(self, pos=None, size=10., edge_width=None, edge_width_rel=None,
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
            Defaults to 1.0 if None or not provided and ``edge_width_rel`` is not
        provided.
        edge_width_rel : float or array or None
            The width as a fraction of marker size. Can not be specified along with
            edge_width. A ValueError will be raised if both are provided.
        edge_color : Color | ColorArray
            The color used to draw each symbol outline.
        face_color : Color | ColorArray
            The color used to draw each symbol interior.
        symbol : str or array
            The style of symbol used to draw each marker (see Notes).
        """
        edge_width, edge_width_rel = self._prepare_edge_width(edge_width, edge_width_rel)
        edge_color, face_color = self._prepare_colors(edge_color, face_color)

        if pos is not None and len(pos):
            data_dict = self._prepare_data_dict(
                pos,
                size,
                edge_width,
                edge_width_rel,
                edge_color,
                face_color,
                symbol,
            )

            if self._method == 'instanced':
                self._upload_instanced_data(data_dict)
            else:
                self._upload_points_data(data_dict)
        else:
            self._data = None

        self.events.data_updated()
        self.update()

    @property
    def symbols(self):
        return list(self._symbol_shader_values)

    @property
    def symbol(self):
        if self._data is None:
            return None
        value_to_symbol = {v: k for k, v in self._symbol_shader_values.items()}
        return np.vectorize(value_to_symbol.get)(self._data['a_symbol'])

    @symbol.setter
    def symbol(self, value):
        if self._data is not None:
            rec_to_kw = {
                'a_position': 'pos',
                'a_fg_color': 'edge_color',
                'a_bg_color': 'face_color',
                'a_size': 'size',
                'a_edgewidth': 'edge_width',
                'a_symbol': 'symbol',
            }
            kwargs = {kw: self._data[rec] for rec, kw in rec_to_kw.items()}
        else:
            kwargs = {}
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
        scaling_modes = {
            False: "fixed",
            True: "scene",
            "fixed": "fixed",
            "scene": "scene",
            "visual": "visual",
        }
        if value not in scaling_modes:
            possible_options = ", ".join(repr(opt) for opt in scaling_modes)
            raise ValueError(f"Unknown scaling option {value!r}, expected one of: {possible_options}")
        self._scaling = scaling_modes[value]
        self.shared_program['u_scaling'] = self._scaling != "fixed"
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

    @property
    def canvas_size_limits(self):
        """
        Tuple of (min, max) size limits for markers in canvas pixels.

        If set, marker sizes will be clamped to this range. This is useful
        for preventing markers from becoming too large or too small when
        zooming with scene/visual scaling.

        Either min or max can be None to clamp only one side.
        Set to None to disable clamping entirely (default).

        Returns
        -------
        tuple or None
            (min_size, max_size) or None if clamping is disabled.
        """
        return self._canvas_size_limits

    @canvas_size_limits.setter
    def canvas_size_limits(self, value):
        if value is not None:
            if not isinstance(value, (tuple, list)) or len(value) != 2:
                raise ValueError("canvas_size_limits must be a tuple of (min, max) or None")
            min_val, max_val = value
            if min_val is not None and min_val < 0:
                raise ValueError("canvas_size_limits min must be non-negative or None")
            if max_val is not None and max_val < 0:
                raise ValueError("canvas_size_limits max must be non-negative or None")
            if min_val is not None and max_val is not None and min_val > max_val:
                raise ValueError("canvas_size_limits min must be <= max")
        self._canvas_size_limits = value
        self._update_canvas_size_clamping()

    def _update_canvas_size_clamping(self):
        """Update the canvas size clamping uniforms."""
        min_size, max_size = self._canvas_size_limits or (None, None)
        self.shared_program['u_canvas_size_min'] = float(min_size) if min_size is not None else -1.0
        self.shared_program['u_canvas_size_max'] = float(max_size) if max_size is not None else -1.0
        self.update()

    def _prepare_transforms(self, view):
        view.view_program.vert['visual_to_framebuffer'] = view.get_transform('visual', 'framebuffer')
        view.view_program.vert['framebuffer_to_render'] = view.get_transform('framebuffer', 'render')
        scaling = view._scaling if view._scaling != "fixed" else "scene"
        view.view_program.vert['framebuffer_to_scene_or_visual'] = view.get_transform('framebuffer', scaling)
        view.view_program.vert['scene_or_visual_to_framebuffer'] = view.get_transform(scaling, 'framebuffer')

    def _prepare_draw(self, view):
        if self._data is None:
            return False
        view.view_program['u_px_scale'] = view.transforms.pixel_scale

    def _compute_bounds(self, axis, view):
        pos = self._data['a_position']
        if pos is None:
            return None
        if pos.shape[1] > axis:
            return (pos[:, axis].min(), pos[:, axis].max())
        else:
            return (0, 0)


def _broadcast_scalar(value, n, dtype=np.float32):
    """Broadcast scalar or array to length n."""
    array = np.asarray(value, dtype=dtype)
    if array.ndim == 0:
        return np.full(n, array, dtype=dtype)
    return array


def _broadcast_color(color, n, dtype=np.float32):
    """Broadcast color (4,) to (n, 4) or return (n, 4) as-is."""
    array = np.asarray(color, dtype=dtype)
    if array.ndim == 1:
        return np.tile(array, (n, 1))
    return array
