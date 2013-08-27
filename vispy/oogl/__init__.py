# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Object oriented interface to OpenGL.

This module implements classes for most things that are "objetcs" in
OpenGL, such as textures, FBO's, VBO's and shaders. Further, some
convenience classes are implemented (like the collection class?).

This set of classes provides a friendly (Pythonic) interface
to OpenGL, and is designed to provide OpenGL's full functionality.

Central to each visualization is the ShaderProgram. To enable it, it
should be used as a context manager. Other objects, such as Texture2D
and VertexBuffer should be set as uniforms and attributes of the
ShaderProgram object. 

Example::
    
    # Init
    program = ShaderProgram(...)
    program.attributes['a_position'] = VertexBuffer(my_positions_array)
    
    ...
    
    # Paint event handler
    with program:
        program.uniforms['u_color'] = 0.0, 1.0, 0.0
        program.draw_arrays(gl.GL_TRIANGLES)


The oogl classes:
    
  * :class:`ShaderProgram`
  * :class:`FragmentShader` and :class:`VertexShader`
  * :class:`VertexBuffer` and :class:`ElementBuffer`
  * :class:`Texture2D`, :class:`Texture3D`, :class:`TextureCubeMap`
  * :class:`FrameBuffer`
  * :class:`RenderBuffer`

.. Note::
    
    With vispy.oogl we strive to offer a Python interface that provides
    the full functionality of OpenGL. However, this layer is a work in
    progress and there are yet a few known limitations. Most notably:
    
      * TextureCubeMap is not yet implemented
      * FBO's can only to 2D textures (not 3D textures or cube maps)
      * Sharing of Shaders and RenderBuffers (between multiple ShaderProgram and
        FrameBuffers, respecitively) is not well supported.
      * We're having some problems with point sprites due to incompatibilities
        between OpenGL ES 2.0 and normal OpenGL.
      * There is no support for texture mipmapping yet
      * No support for compressed textures.
      * Besides the above, there might be the occasional bug, please report!
    
"""

from __future__ import print_function, division, absolute_import

from vispy import gl


def ext_available(extension_name):
    return True # for now


from .globject import GLObject
from .vbo import VertexBuffer, ElementBuffer
from .texture import Texture, Texture2D, Texture3D, TextureCubeMap
from .shader import VertexShader, FragmentShader
from .fbo import FrameBuffer, RenderBuffer
from .program import Program
