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


## Code for adding some docs

def _get_docs_for_class(klass):
    """ Get props and methods for a class.
    """
    
    # Prepare
    baseatts = dir(GLObject)
    functype = type(GLObject.activate)
    proptype = type(GLObject.handle)
    props, funcs = set(), set()
    
    for att in sorted(dir(klass)):
        if klass is not GLObject and att in baseatts:
            continue
        if att.startswith('_') or att.lower() != att:
            continue
        # Get ob and module name
        attob = getattr(klass, att)
        modulename = klass.__module__.split('.')[-1]
        # Get actual klass
        actualklass = klass
        while True:
            tmp = actualklass.__base__
            if att in dir(tmp):
                actualklass = tmp
            else:
                break
        if actualklass == klass:
            modulename = ''
        # Append
        if isinstance(attob, functype):
            funcs.add(' :meth:`~%s.%s.%s`,' % (
                                    modulename, actualklass.__name__, att))
        elif isinstance(attob, proptype):
            props.add(' :attr:`~%s.%s.%s`,' % (
                                    modulename, actualklass.__name__, att))
    # Done
    return props, funcs


def _generate_overview_docs():
    """ Generate the overview section for the OOGL docs.
    """
    
    lines = []
    lines.append('Overview')
    lines.append('='*len(lines[-1]))
    
    for klasses in [(GLObject,),
                    (Program,),
                    (VertexShader, FragmentShader), 
                    (VertexBuffer, ElementBuffer), 
                    (Texture2D, Texture3D, TextureCubeMap),
                    (RenderBuffer,), 
                    (FrameBuffer,),
                ]:
        # Init line
        line = '*'
        for klass in klasses:
            line += ' :class:`%s`,' % klass.__name__
        line = line[:-1]
        # Get atts for these classes, sort by name, prop/func
        funcs, props = set(), set()
        for klass in klasses:
            props_, funcs_ = _get_docs_for_class(klass)
            props.update(props_)
            funcs.update(funcs_)
        # Add props and funcs
        if props:
            line += '\n\n  * properties:'
            for item in sorted(props):
                line += item
        if funcs:
            line += '\n\n  * methods:'
            for item in sorted(funcs):
                line += item
            # Add line, strip last char
            lines.append(line[:-1]) 
    
    return '\n'.join(lines)


# This is called in doc/conf.py
#__doc__ += _generate_overview_docs()
