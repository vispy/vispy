"""
Object oriented interface to OpenGL.

This module implements classes for most things that are "objetcs" in OpenGL,
such as textures, FBO's, VBO's and shaders. Further, some convenience classes
are implemented (like the collection class).

Most classes should be used (during drawing) as context handlers. The
context handler will call glPushAttrib, so that the object can configure
OpenGL as they need, without needing to undo these effects to prevent
the state from "leaking" into other parts of the visualization.

Example::

    # Context with one object
    with texture:
        draw_vertices()
    
    # Context with multiple objects
    with enable(texture(0), texture(1), shader):
        draw_vertices()
    
    # Or maybe like this? (No need to import the ambiguous enable function)
    with texture(0) & texture(1) & shader:
        draw_vertices()

"""

from __future__ import print_function, division, absolute_import

import OpenGL.GL as gl

# ALL_ATTRIBUTES = (gl.GL_ACCUM_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT |
#     gl.GL_CURRENT_BIT | gl.GL_DEPTH_BUFFER_BIT | gl.GL_ENABLE_BIT |
#     gl.GL_EVAL_BIT | gl.GL_FOG_BIT | gl.GL_HINT_BIT | gl.GL_LIGHTING_BIT |
#     gl.GL_LINE_BIT | gl.GL_LIST_BIT | gl.GL_MULTISAMPLE_BIT |
#     gl.GL_PIXEL_MODE_BIT | gl.GL_POINT_BIT | gl.GL_POLYGON_BIT |
#     gl.GL_POLYGON_STIPPLE_BIT | gl.GL_SCISSOR_BIT | gl.GL_STENCIL_BUFFER_BIT |
#     gl.GL_TEXTURE_BIT | gl.GL_TRANSFORM_BIT | gl.GL_VIEWPORT_BIT
#     )  # but we also have gl.GL_ALL_ATTRIB_BITS


class GLObject(object):
    """ This class implements a context manager and the `handle` property.
    """
     
    def __enter__(self):
        gl.glPushAttrib(gl.GL_ALL_ATTRIB_BITS)
        try:
            self._enable()
        except Exception:
            gl.glPopAttrib()
            raise
        return self
    
    def __exit__(self, type, value, traceback):
        try:
            self._disable()
        finally:
            gl.glPopAttrib()
    
    @property
    def handle(self):
        """ The handle (i.e. 'name') to the underlying OpenGL object.
        """
        return self._handle


class _GLObjectWrapper(GLObject):
    """ Class that acts as a context manager for multiple GLObjects.
    """
    def __init__(self, *children):
        self._children = children
    def _enable(self):
        for child in self._children:
            child._enable()
    def _disable(self):
        for child in self._children:
            child._disable()


# todo: what about using the & operator to combine multiple objects?
def enable(*args):
    """ Enable multiple GLObjects at once in a snngle context.
    """ 
    return _GLObjectWrapper(*args)


from .texture import Texture, Texture1D, Texture2D, Texture3D
