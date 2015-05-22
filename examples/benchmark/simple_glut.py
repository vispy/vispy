#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
from vispy.gloo import gl


def on_display():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    glut.glutSwapBuffers()


def on_keyboard(key, x, y):
    if key == '\033':
        sys.exit()


def on_idle():
    global t, t0, frames
    t = glut.glutGet(glut.GLUT_ELAPSED_TIME)
    frames = frames + 1
    elapsed = (t - t0) / 1000.0
    if elapsed > 2.5:
        print("FPS : %.2f (%d frames in %.2f second)"
              % (frames / elapsed, frames, elapsed))
        t0, frames = t, 0
    glut.glutPostRedisplay()


if __name__ == '__main__':
    import sys
    import OpenGL.GLUT as glut

    glut.glutInit(sys.argv)
    glut.glutInitDisplayMode(
        glut.GLUT_DOUBLE | glut.GLUT_RGB | glut.GLUT_DEPTH)
    glut.glutInitWindowSize(512, 512)
    glut.glutCreateWindow("Do nothing benchmark (GLUT)")
    glut.glutDisplayFunc(on_display)
    glut.glutKeyboardFunc(on_keyboard)

    t0, frames, t = glut.glutGet(glut.GLUT_ELAPSED_TIME), 0, 0
    glut.glutIdleFunc(on_idle)
    glut.glutMainLoop()
