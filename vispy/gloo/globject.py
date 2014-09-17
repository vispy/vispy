# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------


from .context import get_a_context
from .glir import GlirQueue


class GLObject(object):
    """ Generic GL object that may live both on CPU and GPU 
    """
    
    _GLIR_TYPE = None
    
    # Internal id counter to keep track of GPU objects
    _idcount = 0

    def __init__(self):
        """ Initialize the object in the default state """

        self._handle = -1
        self._target = None
        self._need_create = True
        self._need_delete = False
        
        GLObject._idcount += 1
        self._id = GLObject._idcount
        
        # Store context that this object is in
        self._context = get_a_context()
        if not hasattr(self._context, 'glir'):
            self._context.glir = GlirQueue()
        
        # Give glir command to create GL representation of this object
        if not self._GLIR_TYPE:
            #raise ValueError('GLObject %r must set GLIR_TYPE' % type(self))
            print('TODO: GLObject %r must set GLIR_TYPE' % type(self))
        self._context.glir.command('CREATE', self._id, self._GLIR_TYPE)
    
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

        if self._need_delete:
            self._delete()
        self._handle = -1
        self._need_create = True
        self._need_delete = False
        
        self._context.glir.command('DELETE', self._id)
    
    def activate(self):
        """ Activate the object on GPU """
        # As a base class, we only provide functionality for
        # automatically creating the object. The other stages are so
        # different that it's more clear if each GLObject specifies
        # what it does in _activate().
        if self._need_create:
            self._create()
            self._need_create = False
        self._activate()
        self._context.glir.command('ACTIVATE', self._id)
    
    def deactivate(self):
        """ Deactivate the object on GPU """

        self._deactivate()
        self._context.glir.command('DEACTIVATE', self._id)

    @property
    def handle(self):
        """ Name of this object on the GPU """

        return self._handle
    
    def _create(self):
        """ Dummy create method """
        raise NotImplementedError()

    def _delete(self):
        """ Dummy delete method """
        raise NotImplementedError()

    def _activate(self):
        """ Dummy activate method """
        raise NotImplementedError()

    def _deactivate(self):
        """ Dummy deactivate method """
        raise NotImplementedError()
