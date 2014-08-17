# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""
GPU-based ray tracing example.
"""

import numpy as np
from math import exp, cos, sin
from vispy import app, gloo

vertex = """
#version 120

attribute vec2 a_position;
varying vec2 v_position;
void main()
{
    gl_Position = vec4(a_position, 0.0, 1.0);
    v_position = a_position;
}
"""

fragment = """
#version 120

const float M_PI = 3.14159265358979323846;
uniform float u_time;
varying vec2 v_position;

uniform vec3 sphere_position;
uniform float sphere_radius;
uniform vec4 sphere_color;
uniform float light_intensity;
uniform vec2 light_specular;
uniform vec3 light_position;
uniform vec4 light_color;
uniform float ambient;
uniform vec3 O;

float intersect_sphere(vec3 O, vec3 D, vec3 S, float R) {
    float a = dot(D, D);
    vec3 OS = O - S;
    float b = 2. * dot(D, OS);
    float c = dot(OS, OS) - R * R;
    float disc = b * b - 4. * a * c;
    if (disc > 0.) {
        float distSqrt = sqrt(disc);
        float q = (-b - distSqrt) / 2.0;
        if (b >= 0.) {
            q = (-b + distSqrt) / 2.0;
        }
        float t0 = q / a;
        float t1 = c / q;
        t0 = min(t0, t1);
        t1 = max(t0, t1);
        if (t1 >= 0.) {
            if (t0 < 0.) {
                return t1;
            }
            else {
                return t0;
            }
        }
    }
    return 100000000.;
}

float intersect_plane(vec3 O, vec3 D, vec3 P, vec3 N) {
    float denom = dot(D, N);
    if (abs(denom) < 1e-6) {
        return 100000000.;
    }
    float d = dot(P - O, N) / denom;
    if (d < 0.) {
        return 100000000.;
    }
    return d;
}

vec4 trace_ray(vec3 rayO, vec3 rayD) {
    float t = intersect_sphere(rayO, rayD, sphere_position, sphere_radius);
    if (t >= 10000000.)
        return vec4(0., 0., 0., 0.);
    vec3 M = rayO + rayD * t;
    vec3 N = normalize(M - sphere_position);
    vec3 toL = normalize(light_position - M);
    vec3 toO = normalize(O - M);
    vec4 col_ray = vec4(ambient, ambient, ambient, 1.);
    col_ray += light_intensity * max(dot(N, toL), 0.) * sphere_color;
    col_ray += light_specular.x * pow(max(dot(N, normalize(toL + toO)), 0.), light_specular.y) * light_color;
    return col_ray;
}

vec4 run(float x, float y, float t) {
    vec3 Q = vec3(x, y, 0.);
    vec3 D = normalize(Q - O);
    vec3 rayO = O;
    vec3 rayD = D;
    vec4 col_ray = trace_ray(rayO, rayD);
    return clamp(col_ray, 0., 1.);
}

void main() {
    vec2 pos = v_position;
    gl_FragColor = run(pos.x, pos.y, u_time);
}
"""

class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, position=(300, 100), 
                            size=(800, 800), close_keys='escape')
        
        self.program = gloo.Program(vertex, fragment)
        self.program['a_position'] = [(-1., -1.), (-1., +1.),
                                      (+1., -1.), (+1., +1.)]

        self.program['sphere_position'] = (0., 0., 1.)
        self.program['sphere_radius'] = 1.
        self.program['sphere_color'] = (0., 0., 1., 1.)
        self.program['light_intensity'] = 1.
        self.program['light_specular'] = (1., 50.)
        self.program['light_position'] = (5., 5., -10.)
        self.program['light_color'] = (1., 1., 1., 1.)
        self.program['ambient'] = .05
        self.program['O']= (0., 0., -1.)
                                      
        self.timer = app.Timer(1.0 / 60)
        self.timer.connect(self.on_timer)
        self.timer.start()
    
    def on_timer(self, event):
        t = event.elapsed
        self.program['u_time'] = t
        self.update()

    def on_resize(self, event):
        width, height = event.size
        gloo.set_viewport(0, 0, width, height)

    def on_draw(self, event):
        self.program.draw('triangle_strip')

if __name__ == '__main__':
    canvas = Canvas()
    canvas.show()
    app.run()
