# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""
GPU-based ray tracing example.

GLSL port of the following Python example:
    https://gist.github.com/rossant/6046463
    https://pbs.twimg.com/media/BPpbJTiCIAEoEPl.png

TODO:
* Once uniform structs are supported, refactor the code to encapsulate 
  objects (spheres, planes, lights) in structures.
* Customizable engine with an arbitrary number of objects.

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
const int SPHERE = 1;
const int PLANE = 2;

uniform float u_time;
uniform float u_aspect_ratio;
varying vec2 v_position;

uniform vec3 sphere_position;
uniform float sphere_radius;
uniform vec3 sphere_color;

uniform vec3 plane_position;
uniform vec3 plane_normal;

uniform float light_intensity;
uniform vec2 light_specular;
uniform vec3 light_position;
uniform vec3 light_color;

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

vec3 run(float x, float y, float t) {
    vec3 Q = vec3(x, y, 0.);
    vec3 D = normalize(Q - O);
    int depth = 0;
    float t0, t1;
    vec3 rayO = O;
    vec3 rayD = D;
    vec3 col;
    vec3 col_ray;
    float reflection = 1.;
    
    int object_index;
    vec3 object_color;
    vec3 object_normal;
    float object_reflection;
    vec3 M;
    vec3 N, toL, toO;
    
    while (depth < 5) {
        
        /* start trace_ray */
        
        t0 = intersect_sphere(rayO, rayD, sphere_position, sphere_radius);
        t1 = intersect_plane(rayO, rayD, plane_position, plane_normal);
        
        if (t0 < t1) {
            // Sphere.
            M = rayO + rayD * t0;
            object_normal = normalize(M - sphere_position);
            object_color = sphere_color;
            object_reflection = .5;
            object_index = SPHERE;
        }
        else if (t1 < t0) {
            // Plane.
            M = rayO + rayD * t1;
            object_normal = plane_normal;
            // Plane texture.
            if (mod(int(2*M.x), 2) == mod(int(2*M.z), 2)) {
                object_color = vec3(1., 1., 1.);
            }
            else {
                object_color = vec3(0., 0., 0.);
            }
            object_reflection = .25;
            object_index = PLANE;
        }
        else {
            break;
        }
        
        N = object_normal;
        toL = normalize(light_position - M);
        toO = normalize(O - M);
        
        // Shadow of the sphere on the plane.
        if (object_index == PLANE) {
            t0 = intersect_sphere(M + N * .0001, toL, sphere_position, sphere_radius);
            if (t0 < 100000.) {
                return vec3(0., 0., 0.);
            }
        }
        
        col_ray = vec3(ambient, ambient, ambient);
        col_ray += light_intensity * max(dot(N, toL), 0.) * object_color;
        col_ray += light_specular.x * pow(max(dot(N, normalize(toL + toO)), 0.), light_specular.y) * light_color;
        
        /* end trace_ray */
        
        rayO = M + N * .0001;
        rayD = normalize(rayD - 2. * dot(rayD, N) * N);
        col += reflection * col_ray;
        reflection *= object_reflection;
        
        depth++;
    }
    
    return clamp(col, 0., 1.);
}

void main() {
    vec2 pos = v_position;
    gl_FragColor = vec4(run(pos.x*u_aspect_ratio, pos.y, u_time), 1.);
}
"""

class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, position=(300, 100), 
                            size=(800, 600), close_keys='escape')
        
        self.program = gloo.Program(vertex, fragment)
        self.program['a_position'] = [(-1., -1.), (-1., +1.),
                                      (+1., -1.), (+1., +1.)]

        self.program['sphere_position'] = (.75, .1, 1.)
        self.program['sphere_radius'] = .6
        self.program['sphere_color'] = (0., 0., 1.)

        self.program['plane_position'] = (0., -.5, 0.)
        self.program['plane_normal'] = (0., 1., 0.)
        
        self.program['light_intensity'] = 1.
        self.program['light_specular'] = (1., 50.)
        self.program['light_position'] = (5., 5., -10.)
        self.program['light_color'] = (1., 1., 1.)
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
        self.program['u_aspect_ratio'] = width/float(height)

    def on_draw(self, event):
        self.program.draw('triangle_strip')

if __name__ == '__main__':
    canvas = Canvas()
    canvas.show()
    app.run()
