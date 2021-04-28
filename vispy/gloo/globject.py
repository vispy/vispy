# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Base gloo object

On queues
---------
The queue on the GLObject can be associated with other queues. These
can be queues of other gloo objects, or of the canvas.context. Queues that are
associated behave as if they are a single queue; this allows GL commands for
two or more interdependent GL objects to be combined such that they are always
sent to the same context together.

A program associates the textures/buffers when they are set via __setitem__. A
FrameBuffer does so when assigning buffers. A program associates itself
with the canvas.context in draw(). A FrameBuffer does the same in
activate().

Example:
    prog1, prog2 = Program(), Program()
    tex1, tex2 = Texture(), Texture()

    prog1.glir.associate(tex1.glir)  # prog1 and tex1 now share a queue
    prog2.glir.associate(tex2.glir)  # prog2 and tex2 now share a queue

    # this causes prog1, tex1, and canvas.context to all share a queue:
    canvas.context.glir.associate(prog1.glir)
    # and now all objects share a single queue
    canvas.context.glir.associate(prog2.glir)
 
Now, when the canvas flushes its queue, it takes all the pending commands
from prog1, prog2, tex1, and tex2. 
"""

from .glir import GlirQueue


class GLObject(object):
    """Generic GL object that represents an object on the GPU.

    When a GLObject is instantiated, it is associated with the currently
    active Canvas, or with the next Canvas to be created if there is no current Canvas
    """

    # Type of GLIR object, reset in subclasses
    _GLIR_TYPE = 'DummyGlirType'

    # Internal id counter to keep track of GPU objects
    _idcount = 0

    def __init__(self):
        """Initialize the object in the default state"""
        # Give this object an id
        GLObject._idcount += 1
        self._id = GLObject._idcount

        # Create the GLIR queue in which we queue our commands. 
        # See docs above for details.
        self._glir = GlirQueue()

        # Give glir command to create GL representation of this object
        self._glir.command('CREATE', self._id, self._GLIR_TYPE)

    def __del__(self):
        # You never know when this is goint to happen. The window might
        # already be closed and no OpenGL context might be available.
        # However, since we are using GLIR queue, this does not matter!
        # If the command gets transported to the canvas, that is great,
        # if not, this probably means that the canvas no longer exists.
        self.delete()

    def delete(self):
        """Delete the object from GPU memory. 

        Note that the GPU object will also be deleted when this gloo
        object is about to be deleted. However, sometimes you want to explicitly delete the GPU object explicitly.
        """
        # We only allow the object from being deleted once, otherwise
        # we might be deleting another GPU object that got our gl-id
        # after our GPU object was deleted. Also note that e.g.
        # DataBufferView does not have the _glir attribute.
        if hasattr(self, '_glir'):
            # Send our final command into the queue
            self._glir.command('DELETE', self._id)
            # Tell main glir queue that this queue is no longer being used
            self._glir._deletable = True
            # Detach the queue
            del self._glir

    @property
    def id(self):
        """The id of this GL object used to reference the GL object in GLIR. id's are unique within a process."""
        return self._id

    @property
    def glir(self):
        """The glir queue for this object."""
        return self._glir
