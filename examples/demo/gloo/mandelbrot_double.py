# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: John David Reaver
# Date:   09/12/2014
# -----------------------------------------------------------------------------

"""
Example demonstrating the use of emulated double-precision floating point
numbers. Based off of mandelbrot.py.

The shader program emulates double-precision variables using a vec2 instead of
single-precision floats. Any function starting with ds_* operates on these
variables. See http://www.thasler.org/blog/?p=93.

NOTE: Some NVIDIA cards optimize the double-precision code away. Results are
therefore hardware dependent.

"""

from __future__ import division

import numpy as np
from vispy import app, gloo

# Shader source code
# -----------------------------------------------------------------------------
vertex = """
attribute vec2 position;

void main()
{
    gl_Position = vec4(position, 0, 1.0);
}
"""

fragment = """
#pragma optionNV(fastmath off)
#pragma optionNV(fastprecision off)

uniform vec2 inv_resolution_x;  // Inverse resolutions
uniform vec2 inv_resolution_y;
uniform vec2 center_x;
uniform vec2 center_y;
uniform vec2 scale;
uniform int iter;

// Jet color scheme
vec4 color_scheme(float x) {
    vec3 a, b;
    float c;
    if (x < 0.34) {
        a = vec3(0, 0, 0.5);
        b = vec3(0, 0.8, 0.95);
        c = (x - 0.0) / (0.34 - 0.0);
    } else if (x < 0.64) {
        a = vec3(0, 0.8, 0.95);
        b = vec3(0.85, 1, 0.04);
        c = (x - 0.34) / (0.64 - 0.34);
    } else if (x < 0.89) {
        a = vec3(0.85, 1, 0.04);
        b = vec3(0.96, 0.7, 0);
        c = (x - 0.64) / (0.89 - 0.64);
    } else {
        a = vec3(0.96, 0.7, 0);
        b = vec3(0.5, 0, 0);
        c = (x - 0.89) / (1.0 - 0.89);
    }
    return vec4(mix(a, b, c), 1.0);
}

vec2 ds_set(float a) {
    // Create an emulated double by storing first part of float in first half
    // of vec2
    vec2 z;
    z.x = a;
    z.y = 0.0;
    return z;
}

vec2 ds_add (vec2 dsa, vec2 dsb)
{
    // Add two emulated doubles. Complexity comes from carry-over.
    vec2 dsc;
    float t1, t2, e;

    t1 = dsa.x + dsb.x;
    e = t1 - dsa.x;
    t2 = ((dsb.x - e) + (dsa.x - (t1 - e))) + dsa.y + dsb.y;

    dsc.x = t1 + t2;
    dsc.y = t2 - (dsc.x - t1);
    return dsc;
}

vec2 ds_mul (vec2 dsa, vec2 dsb)
{
    vec2 dsc;
    float c11, c21, c2, e, t1, t2;
    float a1, a2, b1, b2, cona, conb, split = 8193.;

    cona = dsa.x * split;
    conb = dsb.x * split;
    a1 = cona - (cona - dsa.x);
    b1 = conb - (conb - dsb.x);
    a2 = dsa.x - a1;
    b2 = dsb.x - b1;

    c11 = dsa.x * dsb.x;
    c21 = a2 * b2 + (a2 * b1 + (a1 * b2 + (a1 * b1 - c11)));

    c2 = dsa.x * dsb.y + dsa.y * dsb.x;

    t1 = c11 + c2;
    e = t1 - c11;
    t2 = dsa.y * dsb.y + ((c2 - e) + (c11 - (t1 - e))) + c21;

    dsc.x = t1 + t2;
    dsc.y = t2 - (dsc.x - t1);

    return dsc;
}

// Compare: res = -1 if a < b
//              = 0 if a == b
//              = 1 if a > b
float ds_compare(vec2 dsa, vec2 dsb)
{
    if (dsa.x < dsb.x) return -1.;
    else if (dsa.x == dsb.x) {
        if (dsa.y < dsb.y) return -1.;
        else if (dsa.y == dsb.y) return 0.;
        else return 1.;
    }
    else return 1.;
}

void main() {
    vec2 z_x, z_y, c_x, c_y, x, y, frag_x, frag_y;
    vec2 four = ds_set(4.0);
    vec2 point5 = ds_set(0.5);

    // Recover coordinates from pixel coordinates
    frag_x = ds_set(gl_FragCoord.x);
    frag_y = ds_set(gl_FragCoord.y);

    c_x = ds_add(ds_mul(frag_x, inv_resolution_x), -point5);
    c_x = ds_add(ds_mul(c_x, scale), center_x);
    c_y = ds_add(ds_mul(frag_y, inv_resolution_y), -point5);
    c_y = ds_add(ds_mul(c_y, scale), center_y);


    // Main Mandelbrot computation
    int i;
    z_x = c_x;
    z_y = c_y;
    for(i = 0; i < iter; i++) {
        x = ds_add(ds_add(ds_mul(z_x, z_x), -ds_mul(z_y, z_y)), c_x);
        y = ds_add(ds_add(ds_mul(z_y, z_x), ds_mul(z_x, z_y)), c_y);

        if(ds_compare(ds_add(ds_mul(x, x), ds_mul(y, y)), four) > 0.) break;
        z_x = x;
        z_y = y;
    }

    // Convert iterations to color
    float color = 1.0 - float(i) / float(iter);
    gl_FragColor = color_scheme(color);

}
"""


# vispy Canvas
# -----------------------------------------------------------------------------
class Canvas(app.Canvas):

    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        self.program = gloo.Program(vertex, fragment)

        # Draw a rectangle that takes up the whole screen. All of the work is
        # done in the shader.
        self.program["position"] = [(-1, -1), (-1, 1), (1, 1),
                                    (-1, -1), (1, 1), (1, -1)]

        self.scale = 3
        self.program["scale"] = set_emulated_double(self.scale)
        self.center = [-0.5, 0]
        self.bounds = [-2, 2]
        self.translate_center(0, 0)
        self.iterations = self.program["iter"] = 300

        self.apply_zoom()

        self.min_scale = 1e-12
        self.max_scale = 4

        gloo.set_clear_color(color='black')

        self.show()

    def on_draw(self, event):
        self.program.draw()

    def on_resize(self, event):
        self.apply_zoom()

    def apply_zoom(self):
        width, height = self.physical_size
        gloo.set_viewport(0, 0, width, height)
        self.program['inv_resolution_x'] = set_emulated_double(1 / width)
        self.program['inv_resolution_y'] = set_emulated_double(1 / height)

    def on_mouse_move(self, event):
        """Pan the view based on the change in mouse position."""
        if event.is_dragging and event.buttons[0] == 1:
            x0, y0 = event.last_event.pos[0], event.last_event.pos[1]
            x1, y1 = event.pos[0], event.pos[1]
            X0, Y0 = self.pixel_to_coords(float(x0), float(y0))
            X1, Y1 = self.pixel_to_coords(float(x1), float(y1))
            self.translate_center(X1 - X0, Y1 - Y0)
            self.update()

    def translate_center(self, dx, dy):
        """Translates the center point, and keeps it in bounds."""
        center = self.center
        center[0] -= dx
        center[1] -= dy
        center[0] = min(max(center[0], self.bounds[0]), self.bounds[1])
        center[1] = min(max(center[1], self.bounds[0]), self.bounds[1])
        self.center = center

        center_x = set_emulated_double(center[0])
        center_y = set_emulated_double(center[1])
        self.program["center_x"] = center_x
        self.program["center_y"] = center_y

    def pixel_to_coords(self, x, y):
        """Convert pixel coordinates to Mandelbrot set coordinates."""
        rx, ry = self.size
        nx = (x / rx - 0.5) * self.scale + self.center[0]
        ny = ((ry - y) / ry - 0.5) * self.scale + self.center[1]
        return [nx, ny]

    def on_mouse_wheel(self, event):
        """Use the mouse wheel to zoom."""
        delta = event.delta[1]
        if delta > 0:  # Zoom in
            factor = 0.9
        elif delta < 0:  # Zoom out
            factor = 1 / 0.9
        for _ in range(int(abs(delta))):
            self.zoom(factor, event.pos)
        self.update()

    def on_key_press(self, event):
        """Use + or - to zoom in and out.

        The mouse wheel can be used to zoom, but some people don't have mouse
        wheels :)

        """
        if event.text == '+' or event.text == '=':
            self.zoom(0.9)
        elif event.text == '-':
            self.zoom(1/0.9)
        self.update()

    def zoom(self, factor, mouse_coords=None):
        """Factors less than zero zoom in, and greater than zero zoom out.

        If mouse_coords is given, the point under the mouse stays stationary
        while zooming. mouse_coords should come from MouseEvent.pos.

        """
        if mouse_coords is not None:  # Record the position of the mouse
            x, y = float(mouse_coords[0]), float(mouse_coords[1])
            x0, y0 = self.pixel_to_coords(x, y)

        self.scale *= factor
        self.scale = max(min(self.scale, self.max_scale), self.min_scale)
        self.program["scale"] = set_emulated_double(self.scale)

        if mouse_coords is not None:  # Translate so mouse point is stationary
            x1, y1 = self.pixel_to_coords(x, y)
            self.translate_center(x1 - x0, y1 - y0)


def set_emulated_double(number):
    """Emulate a double using two numbers of type float32."""
    double = np.array([number, 0], dtype=np.float32)  # Cast number to float32
    double[1] = number - double[0]  # Remainder stored in second half of array
    return double


if __name__ == '__main__':
    canvas = Canvas(size=(800, 800), keys='interactive')
    app.run()
