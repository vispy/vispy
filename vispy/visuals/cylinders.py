# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""Cylinders Visual and shader definitions."""

import numpy as np

from ..color import ColorArray
from ..gloo import VertexBuffer
from .visual import Visual


vert = """
uniform float u_width;

attribute vec3 a_position;
attribute vec4 a_color;

varying vec4 v_color;
varying float v_width;
varying float v_depth_middle;

float big_float = 1e10; // prevents numerical imprecision

void main (void) {
    v_color = a_color;

    vec4 pos = vec4(a_position, 1);
    vec4 fb_pos = $visual_to_framebuffer(pos);
    gl_Position = $framebuffer_to_render(fb_pos);

    // calculate point size from visual to framebuffer coords to determine size
    vec4 x = $framebuffer_to_visual(fb_pos + vec4(big_float, 0, 0, 0));
    x = (x - pos);
    vec4 size_vec = $visual_to_framebuffer(pos + normalize(x) * u_width);
    v_width = (size_vec.x - fb_pos.x) / 2;

    // Get the framebuffer z direction relative to this vertex in visual coords
    vec4 z = $framebuffer_to_visual(fb_pos + vec4(0, 0, big_float, 0));
    z = (z - pos);
    // Get the depth of the cylinder in its middle point on the screen
    // size/2 because we need the radius, not the diameter
    vec4 depth_z_vec = $visual_to_framebuffer(pos + normalize(z) * u_width / 2);
    v_depth_middle = depth_z_vec.z / depth_z_vec.w - fb_pos.z / fb_pos.w;
}
"""

geom = """
#version 450
layout (lines) in;
layout (triangle_strip, max_vertices=4) out;

in vec4 v_color[];
in float v_width[];
in float v_depth_middle[];

out vec4 v_color_out;
out vec2 v_texcoord;
out float v_depth_middle_out;

void main(void) {
    // start and end position of the cylinder
    vec4 start = gl_in[0].gl_Position;
    vec4 end = gl_in[1].gl_Position;

    // calculcations need to happen in framebuffer coords or clipping messes up
    vec4 start_fb = $render_to_framebuffer(start);
    vec4 end_fb = $render_to_framebuffer(end);

    // find the vector perpendicular to the cylinder direction projected on the screen
    vec4 direction = end_fb / end_fb.w - start_fb / start_fb.w;
    vec4 perp_screen = normalize(vec4(direction.y, -direction.x, 0, 0));

    vec4 shift_start = $framebuffer_to_render(perp_screen * v_width[0]);
    gl_Position = start + shift_start;
    v_color_out = v_color[0];
    v_texcoord = vec2(-1, 1);
    v_depth_middle_out = v_depth_middle[0];
    EmitVertex();

    gl_Position = start - shift_start;
    v_color_out = v_color[0];
    v_texcoord = vec2(1, 1);
    v_depth_middle_out = v_depth_middle[0];
    EmitVertex();

    vec4 shift_end = $framebuffer_to_render(perp_screen * v_width[1]);
    gl_Position = end + shift_end;
    v_color_out = v_color[1];
    v_texcoord = vec2(-1, -1);
    v_depth_middle_out = v_depth_middle[1];
    EmitVertex();

    gl_Position = end - shift_end;
    v_color_out = v_color[1];
    v_texcoord = vec2(1, -1);
    v_depth_middle_out = v_depth_middle[1];
    EmitVertex();

    EndPrimitive();
}
"""

frag = """
uniform vec3 u_light_position;
uniform vec3 u_light_color;
uniform float u_light_ambient;

varying vec4 v_color_out;
varying vec2 v_texcoord;
varying float v_depth_middle_out;

void main()
{
    float z = sqrt(1 - v_texcoord.x*v_texcoord.x);
    float y = sqrt(1 - v_texcoord.y*v_texcoord.y);
    if (z + y < 1)
        discard;

    vec3 normal = vec3(0, 0, z);
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

    gl_FragColor = vec4(v_color_out.rgb * diffuse_color + specular_color, v_color_out.a);

    gl_FragDepth = gl_FragCoord.z - 0.5 * z * v_depth_middle_out;
}
"""


class CylindersVisual(Visual):
    def __init__(self, width=5, light_color='white', light_position=(1, -1, 1),
                 light_ambient=0.3, **kwargs):
        self._vbo = VertexBuffer()
        self._data = None

        Visual.__init__(self, vcode=vert, gcode=geom, fcode=frag)

        self.set_gl_state(depth_test=True, blend=True,
                          blend_func=('src_alpha', 'one_minus_src_alpha'))
        self._draw_mode = 'lines'

        if len(kwargs) > 0:
            self.set_data(**kwargs)

        self.width = width
        self.light_color = light_color
        self.light_position = light_position
        self.light_ambient = light_ambient

        self.freeze()

    def set_data(self, pos=None, color='white'):
        color = ColorArray(color).rgba
        if len(color) == 1:
            color = color[0]

        if pos is not None:
            assert (isinstance(pos, np.ndarray) and
                    pos.ndim == 2 and pos.shape[1] in (2, 3))

            data = np.zeros(len(pos), dtype=[
                ('a_position', np.float32, 3),
                ('a_color', np.float32, 4),
            ])
            data['a_color'] = color
            data['a_position'] = pos
            self._data = data
            self._vbo.set_data(data)
            self.shared_program.bind(self._vbo)

        self.update()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self.shared_program['u_width'] = value
        self._width = value
        self.update()

    @property
    def light_position(self):
        return self._light_position

    @light_position.setter
    def light_position(self, value):
        value = np.array(value)
        self.shared_program['u_light_position'] = value / np.linalg.norm(value)
        self._light_position = value
        self.update()

    @property
    def light_ambient(self):
        return self._light_ambient

    @light_ambient.setter
    def light_ambient(self, value):
        self.shared_program['u_light_ambient'] = value
        self._light_ambient = value
        self.update()

    @property
    def light_color(self):
        return self._light_color

    @light_color.setter
    def light_color(self, value):
        self.shared_program['u_light_color'] = ColorArray(value).rgb
        self._light_color = value
        self.update()

    def _prepare_transforms(self, view):
        view.view_program.vert['visual_to_framebuffer'] = view.get_transform('visual', 'framebuffer')
        view.view_program.vert['framebuffer_to_render'] = view.get_transform('framebuffer', 'render')
        view.view_program.vert['framebuffer_to_visual'] = view.get_transform('framebuffer', 'visual')
        view.view_program.geom['render_to_framebuffer'] = view.get_transform('render', 'framebuffer')
        view.view_program.geom['framebuffer_to_render'] = view.get_transform('framebuffer', 'render')
