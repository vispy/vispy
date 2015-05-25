# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Demo of jump flooding algoritm for EDT using GLSL
Author: Stefan Gustavson (stefan.gustavson@gmail.com)
2010-08-24. This code is in the public domain.

Adapted to `vispy` by Eric Larson <larson.eric.d@gmail.com>.

This version is a translation of the OSX C code to Python.
Two modifications were made for OpenGL ES 2.0 compatibility:

    1. GL_CLAMP_TO_BORDER was changed to GL_CLAMP_TO_EDGE, with
       corresponding shader changes.
    2. GL_RG16 was changed to GL_RGBA with corresponding shader changes
       (including hard-coding "texlevels" at 65536).

"""

import numpy as np
from os import path as op
from vispy.ext import glfw
from vispy.io import load_data_file
from OpenGL import GL as gl
from OpenGL import GLU as glu
from PIL import Image
import time

this_dir = op.abspath(op.dirname(__file__))


def createShader(vert_fname, frag_fname):
    """createShader - create, load, compile and link the shader object"""
    with open(op.join(this_dir, vert_fname), 'rb') as fid:
        vert = fid.read().decode('ASCII')
    with open(op.join(this_dir, frag_fname), 'rb') as fid:
        frag = fid.read().decode('ASCII')
    vertexShader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    gl.glShaderSource(vertexShader, vert)
    gl.glCompileShader(vertexShader)
    fragmentShader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
    gl.glShaderSource(fragmentShader, frag)
    gl.glCompileShader(fragmentShader)
    programObj = gl.glCreateProgram()
    gl.glAttachShader(programObj, vertexShader)
    gl.glAttachShader(programObj, fragmentShader)
    gl.glLinkProgram(programObj)
    checkGLError()
    return programObj


def setUniformVariables(programObj, texture, texw, texh, step):
    """setUniformVariables - set the uniform shader variables we need"""
    gl.glUseProgram(programObj)
    location_texture = gl.glGetUniformLocation(programObj, "texture")
    if location_texture != -1:
        gl.glUniform1i(location_texture, texture)
    location_texw = gl.glGetUniformLocation(programObj, "texw")
    if location_texw != -1:
        gl.glUniform1f(location_texw, texw)
    location_texh = gl.glGetUniformLocation(programObj, "texh")
    if location_texh != -1:
        gl.glUniform1f(location_texh, texh)
    location_step = gl.glGetUniformLocation(programObj, "step")
    if(location_step != -1):
        gl.glUniform1f(location_step, step)
    gl.glUseProgram(0)
    checkGLError()


def loadImage(filename):  # adapted for Python
    img = Image.open(filename)
    w, h = img.size
    x = np.array(img)[::-1].tostring()
    assert len(x) == w * h
    return x, w, h


def loadShapeTexture(filename, texID):
    """loadShapeTexture - load 8-bit shape texture data
    from a TGA file and set up the corresponding texture object."""
    data, texw, texh = loadImage(load_data_file('jfa/' + filename))
    gl.glActiveTexture(gl.GL_TEXTURE0)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texID)
    # Load image into texture
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_LUMINANCE, texw, texh, 0,
                    gl.GL_LUMINANCE, gl.GL_UNSIGNED_BYTE, data)
    # This is the input image. We want unaltered 1-to-1 pixel values,
    # so specify nearest neighbor sampling to be sure.
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER,
                       gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER,
                       gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    checkGLError()
    return texw, texh


def createBufferTexture(texID, texw, texh):
    """createBufferTexture - create an 8-bit texture render target"""
    gl.glActiveTexture(gl.GL_TEXTURE0)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texID)
    black = (0., 0., 0., 0.)
    # The special shader used to render this texture performs a
    # per-pixel image processing where point sampling is required,
    # so specify nearest neighbor sampling.
    #
    # Also, the flood fill shader handles its own edge clamping, so
    # texture mode GL_REPEAT is inconsequential. "Zero outside" would
    # be useful, but separate edge values are deprecated in OpenGL.
    #
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER,
                       gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER,
                       gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S,
                       gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T,
                       gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameterfv(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_BORDER_COLOR, black)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, texw, texh, 0,
                    gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, '\x00' * texw*texh*4)
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    checkGLError()


t0 = 0.0
frames = 0


def showFPS(texw, texh):
    """showFPS - Calculate and report texture size and frames per second
    in the window title bar (updated once per second)"""
    global frames, t0
    t = time.time()
    if (t - t0) > 1.:
        fps = frames / (t - t0)
        titlestr = "%sx%s texture, %.1f FPS" % (texw, texh, fps)
        glfw.glfwSetWindowTitle(window, titlestr)
        t0 = t
        frames = 0
    frames += 1


def checkGLError():
    status = gl.glGetError()
    if status != gl.GL_NO_ERROR:
        raise RuntimeError('gl error %s' % (status,))


def renderScene(programObj, width, height):
    """renderScene - the OpenGL commands to render our scene."""
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluOrtho2D(0, width, 0, height)
    gl.glViewport(0, 0, width, height)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()
    gl.glUseProgram(programObj)
    # Draw one texture mapped quad in the (x,y) plane
    gl.glBegin(gl.GL_QUADS)
    gl.glTexCoord2f(0., 0.)
    gl.glVertex2f(0., 0.)
    gl.glTexCoord2f(1., 0.)
    gl.glVertex2f(float(width), 0.)
    gl.glTexCoord2f(1., 1.)
    gl.glVertex2f(float(width), float(height))
    gl.glTexCoord2f(0., 1.)
    gl.glVertex2f(0., float(height))
    gl.glEnd()
    gl.glUseProgram(0)
    checkGLError()


useShaders = True
glfw.glfwInit()
window = glfw.glfwCreateWindow(512, 512)
glfw.glfwShowWindow(window)
glfw.glfwMakeContextCurrent(window)
time.sleep(400e-3)  # needed on Linux for window to show up

# Load one texture with the original image
# and create two textures of the same size for the iterative rendering
gl.glEnable(gl.GL_TEXTURE_2D)
gl.glActiveTexture(gl.GL_TEXTURE0)
textureID = gl.glGenTextures(3)
texw, texh = loadShapeTexture("shape1.tga", textureID[0])
createBufferTexture(textureID[1], texw, texh)
createBufferTexture(textureID[2], texw, texh)
fboID = gl.glGenFramebuffers(1)
programObj0 = createShader("vertex.glsl", "fragment_seed.glsl")
programObj1 = createShader("vertex.glsl", "fragment_flood.glsl")
programObj2 = createShader("vertex.glsl", "fragment_display.glsl")
glfw.glfwSwapInterval(0)
running = True
while running:
    showFPS(texw, texh)
    if not useShaders:
        gl.glBindTexture(gl.GL_TEXTURE_2D, textureID[0])  # Pass-through
    else:
        setUniformVariables(programObj0, 0, texw, texh, 0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, textureID[0])
        gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, fboID)
        lastRendered = 1
        gl.glFramebufferTexture2D(gl.GL_DRAW_FRAMEBUFFER,
                                  gl.GL_COLOR_ATTACHMENT0,
                                  gl.GL_TEXTURE_2D,
                                  textureID[lastRendered], 0)
        renderScene(programObj0, texw, texh)
        stepsize = texw//2 if texw > texh else texh//2
        while stepsize > 0:
            setUniformVariables(programObj1, 0, texw, texh, stepsize)
            gl.glBindTexture(gl.GL_TEXTURE_2D, textureID[lastRendered])
            lastRendered = 1 if lastRendered == 2 else 2
            gl.glFramebufferTexture2D(gl.GL_DRAW_FRAMEBUFFER,
                                      gl.GL_COLOR_ATTACHMENT0,
                                      gl.GL_TEXTURE_2D,
                                      textureID[lastRendered], 0)
            renderScene(programObj1, texw, texh)
            stepsize = stepsize // 2
        gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, 0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, textureID[lastRendered])

    width, height = glfw.glfwGetWindowSize(window)
    height = max(height, 1)
    width = max(width, 1)
    setUniformVariables(programObj2, 0, texw, texh, 0)
    renderScene(programObj2, width, height)

    glfw.glfwSwapBuffers(window)
    glfw.glfwPollEvents()
    if glfw.glfwGetKey(window, glfw.GLFW_KEY_1) == glfw.GLFW_PRESS:
        texw, texh = loadShapeTexture("shape1.tga", textureID[0])
        createBufferTexture(textureID[1], texw, texh)
        createBufferTexture(textureID[2], texw, texh)
    if glfw.glfwGetKey(window, glfw.GLFW_KEY_2):
        texw, texh = loadShapeTexture("shape2.tga", textureID[0])
        createBufferTexture(textureID[1], texw, texh)
        createBufferTexture(textureID[2], texw, texh)
    if glfw.glfwGetKey(window, glfw.GLFW_KEY_3):
        texw, texh = loadShapeTexture("shape3.tga", textureID[0])
        createBufferTexture(textureID[1], texw, texh)
        createBufferTexture(textureID[2], texw, texh)
    if glfw.glfwGetKey(window, glfw.GLFW_KEY_4):
        texw, texh = loadShapeTexture("shape4.tga", textureID[0])
        createBufferTexture(textureID[1], texw, texh)
        createBufferTexture(textureID[2], texw, texh)
    if glfw.glfwGetKey(window, glfw.GLFW_KEY_F1):
        useShaders = True
    if glfw.glfwGetKey(window, glfw.GLFW_KEY_F2):
        useShaders = False
    # Check if the ESC key is pressed or the window has been closed
    running = not glfw.glfwGetKey(window, glfw.GLFW_KEY_ESCAPE)
glfw.glfwTerminate()
