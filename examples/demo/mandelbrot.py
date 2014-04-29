# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: John David Reaver
# Date:   04/29/2014
# -----------------------------------------------------------------------------
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import sys

from vispy import gloo

RES_X = 800
RES_Y = 800

scale = 3
center = [-0.5, 0]
bounds = [-2, 2]
iterations = 300
min_scale = 0.00005
max_scale = 4


# GLUT callback functions
# -----------------------------------------------------------------------------
def display():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    program.draw(gl.GL_TRIANGLES)
    glut.glutSwapBuffers()


def reshape(width, height):
    gl.glViewport(0, 0, width, height)


def timer(fps):
    global scale, center
    program["scale"] = scale
    program["center"] = center

    glut.glutTimerFunc(int(1000 / fps), timer, fps)
    glut.glutPostRedisplay()


# Mouse/keyboard input
# Click to recenter plot, and use mouse wheel or +/- buttons to zoom.
# -----------------------------------------------------------------------------
def mouse(button, state, x, y):
    global scale, center
    if (state == glut.GLUT_UP):
        return  # Disregard redundant GLUT_UP events
    if button == 3:  # Wheel up
        zoom_in()
    elif button == 4:  # Wheel down
        zoom_out()
    elif button == 0:  # Left click
        X, Y = pixel_to_coords(x, y)
        center[0] = min(max(X, bounds[0]), bounds[1])
        center[1] = min(max(Y, bounds[0]), bounds[1])


def keyboard(key, x, y):
    if key == b'+':
        zoom_in()
    elif key == b'-':
        zoom_out()


def zoom_in():
    global scale
    scale *= 0.9
    scale = max(min(scale, max_scale), min_scale)


def zoom_out():
    global scale
    scale *= 1/0.9
    scale = max(min(scale, max_scale), min_scale)


def pixel_to_coords(x, y):
    rx, ry = float(RES_X), float(RES_Y)
    nx = (x / rx - 0.5) * scale + center[0]
    ny = ((ry - y) / ry - 0.5) * scale + center[1]
    return [nx, ny]


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
uniform vec2 resolution;
uniform vec2 center;
uniform float scale;
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

void main() {
    vec2 z, c;

    // Recover coordinates from pixel coordinates
    c.x = (gl_FragCoord.x / resolution.x - 0.5) * scale + center.x;
    c.y = (gl_FragCoord.y / resolution.y - 0.5) * scale + center.y;

    // Main Mandelbrot computation
    int i;
    z = c;
    for(i = 0; i < iter; i++) {
        float x = (z.x * z.x - z.y * z.y) + c.x;
        float y = (z.y * z.x + z.x * z.y) + c.y;

        if((x * x + y * y) > 4.0) break;
        z.x = x;
        z.y = y;
    }

    // Convert iterations to color
    float color = 1.0 - float(i) / float(iter);
    gl_FragColor = color_scheme(color);

}
"""


# GLUT Init
# -----------------------------------------------------------------------------
glut.glutInit(sys.argv)
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
glut.glutCreateWindow("First PyOpenGL program")
glut.glutReshapeWindow(RES_X, RES_Y)
glut.glutDisplayFunc(display)
glut.glutReshapeFunc(reshape)
glut.glutMouseFunc(mouse)
glut.glutKeyboardFunc(keyboard)
glut.glutTimerFunc(int(1000 / 60), timer, 60)

# Build program
# -----------------------------------------------------------------------------
program = gloo.Program(vertex, fragment, count=6)
program["position"] = [(-1, -1), (-1, 1), (1, 1),
                       (-1, -1), (1, 1), (1, -1)]

program["resolution"] = [RES_X, RES_Y]
program["iter"] = iterations

# Start
# -----------------------------------------------------------------------------
glut.glutMainLoop()
