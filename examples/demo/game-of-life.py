# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author:   Nicolas P .Rougier
# Date:     06/03/2014
# Abstract: GPU computing usingthe framebuffer
# Keywords: framebuffer, GPU computing, reaction-diffusion
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
uniform sampler2D texture;
varying vec2 v_texcoord;
void main()
{
    float r = texture2D(texture, v_texcoord).r;
    gl_FragColor = vec4(1.-r,1.-r,1.-r,1.);
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
uniform sampler2D texture;
uniform float dx;          // horizontal distance between texels
uniform float dy;          // vertical distance between texels
uniform float dd;          // unit of distance
uniform float dt;          // unit of time
varying vec2 v_texcoord;
void main(void)
{
    vec2  p = v_texcoord;
    float state = texture2D(texture, p).r;
    float count = texture2D(texture, p + vec2(-dx,-dy)).r
                + texture2D(texture, p + vec2( dx,-dy)).r
                + texture2D(texture, p + vec2(-dx, dy)).r
                + texture2D(texture, p + vec2( dx, dy)).r
                + texture2D(texture, p + vec2(-dx, 0.0)).r
                + texture2D(texture, p + vec2( dx, 0.0)).r
                + texture2D(texture, p + vec2(0.0,-dy)).r
                + texture2D(texture, p + vec2(0.0, dy)).r;

    if( state > 0.5 ) {
        // Any live cell with fewer than two live neighbours dies
        // as if caused by under-population.
        if( count  < 1.5 )
            state = 0.0;

        // Any live cell with two or three live neighbours
        // lives on to the next generation.

        // Any live cell with more than three live neighbours dies,
        //  as if by overcrowding.
        else if( count > 3.5 )
            state = 0.0;
    } else {
        // Any dead cell with exactly three live neighbours becomes
        //  a live cell, as if by reproduction.
       if( (count > 2.5) && (count < 3.5) )
           state = 1.0;
    }
    gl_FragColor = vec4(vec3(state),1);
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
Z = np.zeros((comp_h, comp_w, 4))
Z[..., 0] = np.random.randint(0, 2, (comp_h, comp_w))
compute = Program(compute_vertex, compute_fragment, 4)
compute["texture"] = Z
compute["position"] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
compute["texcoord"] = [(0, 0), (0, 1), (1, 0), (1, 1)]
compute['dx'] = 1.0 / comp_w
compute['dy'] = 1.0 / comp_h

render = Program(render_vertex, render_fragment, 4)
render["position"] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
render["texcoord"] = [(0, 0), (0, 1), (1, 0), (1, 1)]
render["texture"] = compute["texture"]

framebuffer = FrameBuffer(color=compute["texture"],
                          depth=DepthBuffer((comp_w, comp_h)))

# OpenGL initialization
# --------------------------------------
gl.glDisable(gl.GL_DEPTH_TEST)
gl.glClearColor(0, 0, 0, 1)

# Start
# --------------------------------------
glut.glutMainLoop()
