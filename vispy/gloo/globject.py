# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""
Base gloo object
"""

"""
On queues
---------

The queue on the GLObject can be associated with other queues. These
can be queues of other gloo objects, or of the canvas.context. A program
associates the textures/buffers when they are set via __setitem__. A
FrameBuffer does so when assigning buffers. A program associates itself
with the canvas.context in draw(). A FrameBuffer does the same in
activate().

Example:

    prog1, prog2 = Program(), Program()
    tex1, tex2 = Texture(), Texture()

    prog1.glir.associate(tex1.glir)
    prog1.glir.associate(tex2.glir)

    canvas1.context.glir.associate(prog1.glir)
    canvas1.context.glir.associate(prog2.glir)
    canvas2.context.glir.associate(prog2.glir)

Now, when canvas1 flushes its queue, it takes all the pending commands
from prog1 and prog2, and subsequently from tex1 and tex2. When canvas2
is flushed, only commands from prog2 get taken. A similar situation
holds for a texture that is associated with a program and a frame
buffer.
"""

from .glir import GlirQueue


class GLObject(object):
    """ Generic GL object that represents an object on the GPU.
    
    When a GLObject is instantiated, it is associated with the currently
    active Canvas, or with the next Canvas to be created if there is
    no current Canvas
    """
    
    # Type of GLIR object, reset in subclasses
    _GLIR_TYPE = 'DummyGlirType'
    
    # Internal id counter to keep track of GPU objects
    _idcount = 0
    
    def __init__(self):
        """ Initialize the object in the default state """
        
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
        # Worse, there might be multiple contexts and calling delete()
        # at the wrong moment might remove other gl objects, leading to
        # very strange and hard to debug behavior.
        #
        # So we don't do anything. If each GLObject was aware of the
        # context in which it resides, we could do auto-cleanup though...
        # todo: it's not very Pythonic to have to delete an object.
        pass

    def delete(self):
        """ Delete the object from GPU memory """
        self._glir.command('DELETE', self._id)
    
    @property
    def id(self):
        """ The id of this GL object used to reference the GL object
        in GLIR. id's are unique within a process.
        """
        return self._id
    
    @property
    def glir(self):
        """ The glir queue for this object.
        """
        return self._glir
