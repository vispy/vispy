# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author:   Nicolas P .Rougier
# Date:     06/03/2014
# Abstract: GPU computing using the framebuffer
# Keywords: framebuffer, GPU computing, cellular automata
# -----------------------------------------------------------------------------
import sys
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
from vispy.gloo import Program, FrameBuffer, DepthBuffer


render_vertex = """
attribute vec2 position;
attribute vec2 texcoord;
varying vec2 v_texcoord;
void main()
{
    gl_Position = vec4(position, 0.0, 1.0);
    v_texcoord = texcoord;
}
"""

render_fragment = """
uniform int pingpong;
uniform sampler2D texture;
varying vec2 v_texcoord;
void main()
{
    float v;
    if( pingpong == 0 )
        v = texture2D(texture, v_texcoord).r;
    else
        v = texture2D(texture, v_texcoord).g;
    gl_FragColor = vec4(1.0-v, 1.0-v, 1.0-v, 1.0);
}
"""

compute_vertex = """
attribute vec2 position;
attribute vec2 texcoord;
varying vec2 v_texcoord;
void main()
{
    gl_Position = vec4(position, 0.0, 1.0);
    v_texcoord = texcoord;
}
"""

compute_fragment = """
uniform int pingpong;
uniform sampler2D texture;
uniform float dx;          // horizontal distance between texels
uniform float dy;          // vertical distance between texels
varying vec2 v_texcoord;
void main(void)
{
    vec2  p = v_texcoord;
    float old_state, new_state, count;

    if( pingpong == 0 ) {
        old_state = texture2D(texture, p).r;
        count = texture2D(texture, p + vec2(-dx,-dy)).r
              + texture2D(texture, p + vec2( dx,-dy)).r
              + texture2D(texture, p + vec2(-dx, dy)).r
              + texture2D(texture, p + vec2( dx, dy)).r
              + texture2D(texture, p + vec2(-dx, 0.0)).r
              + texture2D(texture, p + vec2( dx, 0.0)).r
              + texture2D(texture, p + vec2(0.0,-dy)).r
              + texture2D(texture, p + vec2(0.0, dy)).r;
    } else {
        old_state = texture2D(texture, p).g;
        count = texture2D(texture, p + vec2(-dx,-dy)).g
              + texture2D(texture, p + vec2( dx,-dy)).g
              + texture2D(texture, p + vec2(-dx, dy)).g
              + texture2D(texture, p + vec2( dx, dy)).g
              + texture2D(texture, p + vec2(-dx, 0.0)).g
              + texture2D(texture, p + vec2( dx, 0.0)).g
              + texture2D(texture, p + vec2(0.0,-dy)).g
              + texture2D(texture, p + vec2(0.0, dy)).g;
    }

    new_state = old_state;
    if( old_state > 0.5 ) {
        // Any live cell with fewer than two live neighbours dies
        // as if caused by under-population.
        if( count  < 1.5 )
            new_state = 0.0;

        // Any live cell with two or three live neighbours
        // lives on to the next generation.

        // Any live cell with more than three live neighbours dies,
        //  as if by overcrowding.
        else if( count > 3.5 )
            new_state = 0.0;
    } else {
        // Any dead cell with exactly three live neighbours becomes
        //  a live cell, as if by reproduction.
       if( (count > 2.5) && (count < 3.5) )
           new_state = 1.0;
    }

    if( pingpong == 1 ) {
        gl_FragColor.r = new_state;
        gl_FragColor.g = old_state;
    } else {
        gl_FragColor.r = new_state;
        gl_FragColor.g = old_state;
    }
}
"""


def display():
    global comp_w, comp_h, disp_w, disp_h

    framebuffer.activate()
    gl.glViewport(0, 0, comp_w, comp_h)
    compute["texture"].interpolation = gl.GL_NEAREST
    compute.draw(gl.GL_TRIANGLE_STRIP)
    framebuffer.deactivate()

    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glViewport(0, 0, disp_w, disp_h)
    render["texture"].interpolation = gl.GL_LINEAR
    render.draw(gl.GL_TRIANGLE_STRIP)
    glut.glutSwapBuffers()


def reshape(width, height):
    global disp_w, disp_h
    gl.glViewport(0, 0, width, height)
    disp_w, disp_h = width, height


def keyboard(key, x, y):
    if key == '\033':
        sys.exit()


def idle():
    global pingpong
    pingpong = 1 - pingpong
    compute["pingpong"] = pingpong
    render["pingpong"] = pingpong
    glut.glutPostRedisplay()


# Glut init
# --------------------------------------
glut.glutInit(sys.argv)
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
glut.glutCreateWindow("Conway game of life")
glut.glutReshapeWindow(512, 512)
glut.glutReshapeFunc(reshape)
glut.glutKeyboardFunc(keyboard)
glut.glutDisplayFunc(display)
glut.glutIdleFunc(idle)


# Build programs
# --------------
comp_w, comp_h = 512, 512
disp_w, disp_h = 512, 512
Z = np.zeros((comp_h, comp_w, 4), dtype=np.float32)
Z[...] = np.random.randint(0, 2, (comp_h, comp_w, 4))
Z[:256, :256, :] = 0
gun = """
........................O...........
......................O.O...........
............OO......OO............OO
...........O...O....OO............OO
OO........O.....O...OO..............
OO........O...O.OO....O.O...........
..........O.....O.......O...........
...........O...O....................
............OO......................"""
x, y = 0, 0
for i in range(len(gun)):
    if gun[i] == '\n':
        y += 1
        x = 0
    elif gun[i] == 'O':
        Z[y, x] = 1
    x += 1

pingpong = 1
compute = Program(compute_vertex, compute_fragment, 4)
compute["texture"] = Z
compute["position"] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
compute["texcoord"] = [(0, 0), (0, 1), (1, 0), (1, 1)]
compute['dx'] = 1.0 / comp_w
compute['dy'] = 1.0 / comp_h
compute['pingpong'] = pingpong

render = Program(render_vertex, render_fragment, 4)
render["position"] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
render["texcoord"] = [(0, 0), (0, 1), (1, 0), (1, 1)]
render["texture"] = compute["texture"]
render['pingpong'] = pingpong

framebuffer = FrameBuffer(color=compute["texture"],
                          depth=DepthBuffer((comp_w, comp_h)))

# OpenGL initialization
# --------------------------------------
gl.glDisable(gl.GL_DEPTH_TEST)
gl.glClearColor(0, 0, 0, 1)

# Start
# --------------------------------------
glut.glutMainLoop()
