# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Object oriented interface to OpenGL.

This module implements classes for the things that are "objects" in
OpenGL, such as textures, FBO's, VBO's and shaders. Further, some
convenience classes are implemented (like the collection class).

This set of classes provides a friendly (Pythonic) interface
to OpenGL, and is designed to provide OpenGL's full functionality.

All classes inherit from GLObject, which provide a basic interface,
enabling, activating and deleting the object. Central to each
visualization is the Program. Other objects, such as Texture2D and
VertexBuffer should be set as uniforms and attributes of the Program
object.

Example::

    # Init
    program = gloo.Program(vertex_source, fragment_source)
    program['a_position'] = gloo.VertexBuffer(my_positions_array)
    program['s_texture'] = gloo.Texture2D(my_image)
    ...

    # Draw event handler
    program['u_color'] = 0.0, 1.0, 0.0
    program.draw(gl.GL_TRIANGLES)

.. Note::

    With vispy.gloo we strive to offer a Python interface that provides
    the full functionality of OpenGL. However, this layer is a work in
    progress and there are still a few known limitations. Most notably:

    * TextureCubeMap is not yet implemented
    * FBOs can only do 2D textures (not 3D textures or cube maps)
    * No support for compressed textures.

"""

from __future__ import division

from . import gl  # noqa
from .wrappers import *  # noqa
from .context import (GLContext, get_default_config,  # noqa
                      get_current_canvas)  # noqa
from .globject import GLObject  # noqa
from .buffer import VertexBuffer, IndexBuffer  # noqa
from .texture import Texture1D, Texture2D, TextureAtlas, Texture3D, TextureEmulated3D  # noqa
from .program import Program  # noqa
from .framebuffer import FrameBuffer, RenderBuffer  # noqa
from . import util  # noqa
