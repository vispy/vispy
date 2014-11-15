# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------


from .context import get_current_glir_queue


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
        
        # Store context that this object is associated to
        self._glir = get_current_glir_queue()
        #print(self._GLIR_TYPE, 'takes', self._context)
        
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
