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
    with texture(0), texture(1), shader:
        draw_vertices()

"""

from __future__ import print_function, division, absolute_import

from vispy import gl


## Replacement for glPushAttrib (which is deprecated)

ENABLE_QUEUE = {}

def push_enable(enum):
    """ Like glEnable, but keeps track of how often it is called
    and really enables/disables if necessary. Only works as it should
    if the application does not make glEnable/glDisable calls by itself.
    """
    cur = ENABLE_QUEUE.get(enum, 0)
    if cur == 0:
        gl.glEnable(enum)
    ENABLE_QUEUE[enum] = cur + 1
    

def pop_enable(enum):
    """ Like glDisable, but keeps track of how often it is called
    and really enables/disables if necessary. Only works as it should
    if the application does not make glEnable/glDisable calls by itself.
    """
    cur = ENABLE_QUEUE.get(enum, 0)
    if cur == 1:
        gl.glDisable(enum)
    ENABLE_QUEUE[enum] = max(0, cur-1)


##

def ext_available(extension_name):
    return True # for now


class GLObject(object):
    """ This class implements a context manager and the `handle` property.
    """
    
    def __enter__(self):
        self._enable()
        return self
    
    def __exit__(self, type, value, traceback):
        self._disable()
    
    def __del__(self):
        self.delete()
    
    def delete(self):
        """ Delete the object from OpenGl memory. Note that the right
        context should be active when this method is called.
        """
        try:
            if self._handle > 0:
                self._delete()
        except Exception:
            pass  # At least we tried
        self._handle = 0
    
    @property
    def handle(self):
        """  The handle (i.e. id or name) of the underlying OpenGL object.
        """
        return self._handle
    
    
    def _enable(self):
        raise NotImplementedError()
    
    def _disable(self):
        raise NotImplementedError()
    
    def _delete(self):
        raise NotImplementedError()



from .vbo import VertexBuffer, IndexBuffer
from .texture import Texture, Texture2D, Texture3D
from .shader import VertexShader, FragmentShader
from .program import ShaderProgram
