# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
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
    program = gloo.Program(vertex_source, fragment_source)
    program['a_position'] = gloo.VertexBuffer(my_positions_array)
    program['s_texture'] = gloo.Texture2D(my_image)
    ...

    # Paint event handler
    program['u_color'] = 0.0, 1.0, 0.0
    program.draw(gl.GL_TRIANGLES)

.. Note::

    With vispy.gloo we strive to offer a Python interface that provides
    the full functionality of OpenGL. However, this layer is a work in
    progress and there are yet a few known limitations. Most notably:

    * TextureCubeMap is not yet implemented
    * FBO's can only do 2D textures (not 3D textures or cube maps)
    * Sharing of Shaders and RenderBuffers (between multiple Program's and
      FrameBuffers, respecitively) is not well supported.
    * No support for compressed textures.

"""

from __future__ import division

from ..util.six import string_types
from . import gl


def ext_available(extension_name):
    """ Get whether an extension is available.
    For now, this always returns True...
    """
    return True  # for now


def convert_to_enum(param, allow_none=False):
    """ Convert parameter (e.g. a string) to GL enum.
    """
    if isinstance(param, string_types):
        param = param.upper()
        if not param.startswith('GL'):
            param = 'GL_' + param
        try:
            param = getattr(gl, param)
        except AttributeError:
            raise ValueError('Unknown GL enum: "%s".' % param)
    elif isinstance(param, int):
        pass  # We assume this is a valid enum
    elif param is None and allow_none:
        pass
    else:
        raise ValueError('Invalid type for GL enum: %r.' % type(param))
    return param


from .globject import GLObject  # noqa

from .buffer import VertexBuffer, ElementBuffer  # noqa
#from .buffer import ClientVertexBuffer, ClientElementBuffer
from .texture import Texture2D, Texture3D, TextureCubeMap  # noqa
from .shader import VertexShader, FragmentShader  # noqa
from .framebuffer import FrameBuffer, RenderBuffer  # noqa
from .program import Program  # noqa
from .util import _screenshot  # noqa
