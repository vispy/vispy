# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Object oriented interface to OpenGL.

This module implements classes for the things that are "objetcs" in
OpenGL, such as textures, FBO's, VBO's and shaders. Further, some
convenience classes are implemented (like the collection class?).

This set of classes provides a friendly (Pythonic) interface
to OpenGL, and is designed to provide OpenGL's full functionality.

All classes inherit from GLObject, which provide a basic interface,
enabling activatinge and deleting the object. Central to each
visualization is the Program. Other objects, such as Texture2D and
VertexBuffer should be set as uniforms and attributes of the Program
object.

Example::
    
    # Init
    program = oogl.Program(vertex_source, fragment_source)
    program['a_position'] = oogl.VertexBuffer(my_positions_array)
    program['s_texture'] = oogl.Texture2D(my_image)
    ...
    
    # Paint event handler
    program['u_color'] = 0.0, 1.0, 0.0
    program.draw(gl.GL_TRIANGLES)

.. Note::
    
    With vispy.oogl we strive to offer a Python interface that provides
    the full functionality of OpenGL. However, this layer is a work in
    progress and there are yet a few known limitations. Most notably:
    
    * TextureCubeMap is not yet implemented
    * FBO's can only do 2D textures (not 3D textures or cube maps)
    * Sharing of Shaders and RenderBuffers (between multiple Program's and
      FrameBuffers, respecitively) is not well supported.
    * No support for compressed textures.

"""

from __future__ import print_function, division, absolute_import

from vispy import gl


def ext_available(extension_name):
    return True # for now


from .globject import GLObject

from .buffer import VertexBuffer, ElementBuffer
#from .buffer import ClientVertexBuffer, ClientElementBuffer
from .data import Data
from .texture import Texture2D, Texture3D, TextureCubeMap
from .shader import VertexShader, FragmentShader
from .framebuffer import FrameBuffer, RenderBuffer
from .program import Program

