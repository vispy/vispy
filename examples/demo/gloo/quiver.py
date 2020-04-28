#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
# Distributed under the (new) BSD License.
# -----------------------------------------------------------------------------

from vispy import app, gloo

vertex = """
attribute vec2 position;
void main()
{
    gl_Position = vec4(position, 0.0, 1.0);
}
"""

fragment = """
#include "math/constants.glsl"
#include "arrows/arrows.glsl"
#include "antialias/antialias.glsl"

uniform vec2 iResolution;
uniform vec2 iMouse;
void main()
{
    const float M_PI = 3.14159265358979323846;
    const float SQRT_2 = 1.4142135623730951;
    const float linewidth = 3.0;
    const float antialias =  1.0;
    const float rows = 32.0;
    const float cols = 32.0;

    float body = min(iResolution.x/cols, iResolution.y/rows) / SQRT_2;
    vec2 texcoord = gl_FragCoord.xy;
    vec2 size   = iResolution.xy / vec2(cols,rows);
    vec2 center = (floor(texcoord/size) + vec2(0.5,0.5)) * size;
    texcoord -= center;
    float theta = M_PI-atan(center.y-iMouse.y,  center.x-iMouse.x);
    float cos_theta = cos(theta);
    float sin_theta = sin(theta);


    texcoord = vec2(cos_theta*texcoord.x - sin_theta*texcoord.y,
                    sin_theta*texcoord.x + cos_theta*texcoord.y);

    float d = arrow_stealth(texcoord, body, 0.25*body, linewidth, antialias);
    gl_FragColor = filled(d, linewidth, antialias, vec4(0,0,0,1));
}
"""


canvas = app.Canvas(size=(2*512, 2*512), keys='interactive')
canvas.context.set_state(blend=True, 
                         blend_func=('src_alpha', 'one_minus_src_alpha'),
                         blend_equation='func_add')


@canvas.connect
def on_draw(event):
    gloo.clear('white')
    program.draw('triangle_strip')


@canvas.connect
def on_resize(event):
    program["iResolution"] = event.size
    gloo.set_viewport(0, 0, event.size[0], event.size[1])


@canvas.connect
def on_mouse_move(event):
    x, y = event.pos
    program["iMouse"] = x, canvas.size[1] - y
    canvas.update()


program = gloo.Program(vertex, fragment, count=4)
dx, dy = 1, 1
program['position'] = (-dx, -dy), (-dx, +dy), (+dx, -dy), (+dx, +dy)
program["iResolution"] = (2 * 512, 2 * 512)
program["iMouse"] = (0., 0.)

if __name__ == '__main__':
    canvas.show()
    app.run()
