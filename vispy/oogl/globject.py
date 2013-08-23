# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Definition of the base class for all oogl objects.
"""


class GLObject(object):
    """ Base class for classes that wrap an OpenGL object.
    All GLObject's can be used as a context manager to enable them,
    although some are better used by setting them as a uniform or
    attribute of a ShaderProgram.
    
    All GLObject's apply deferred (a.k.a. lazy) loading, which means
    that the objects can be created and data can be set even if no
    OpenGL context is available yet. 
    
    There are a few exceptions, most notably when enabling an object
    by using it as a context manager or via ShaderProgram.enable_object(), 
    and the delete method. In these cases, the called should ensure
    that the proper OpenGL context is current.
    """
    
    # Internal id counter to keep track of created objects
    _idcount = 0
    
    def __init__(self):
        
        # The type of object (e.g. GL_TEXTURE_2D or GL_ARRAY_BUFFER)
        # Used by some GLObjects internally
        self._target = 0
        
        # Name of this object on the GPU ( >0 means there is an OpenGL object)
        # GLObjects should set this in _enable()
        self._handle = 0
        
        # Whether this object needs an update
        # GLObjects can set this to True to receive a call to _update()
        self._need_update = False
        
        # Whether the object is in a state that it can be used
        # Is set to True if _update() returns without errors
        self._is_valid = False
        
        
        # Error counters (only used here)
        self._error_enter = 0  # Track error on __enter__
        self._error_exit = 0  # track errors on __exit__
        
        # Object internal id (for e.g. debugging)
        self._id = GLObject._idcount+1
        GLObject._idcount += 1
    
    
    def __enter__(self):
        try:
            # Try to enable, reset error state on success
            self.activate()
            self._error_enter = 0
        except Exception:
            # Error: increase error state. If this is the first error, raise
            self._error_enter += 1
            if self._error_enter == 1:
                raise
        
        return self
    
    
    def __exit__(self, type, value, traceback):
        if value is None:
            # Reset error state on success
            self._error_exit = 0
        else:
            # Error: increase error state. If not the first error, suppress
            self._error_exit += 1
            if self._error_exit > 1: 
                return True  # Suppress error
        self.deactivate()
    
    
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
        self._is_valid = False
    
    
    def activate(self):
        # Create if necessart
        if self._handle <= 0:
            self._is_valid = False
            self._create()
        # Update if necessary
        if self._need_update:
            self._need_update = False
            self._update()
            self._is_valid = True  # If update ok, we assume we are valid
        # Activate the object
        return self._activate()
    
    
    def deactivate(self):
        return self._deactivate()
    
    
    @property
    def handle(self):
        """  The handle (name in OpenGL) of the underlying OpenGL object (int).
        """
        return self._handle
    
    
    @property
    def id(self):
        # todo: should this be part of the public API?
        """ Internal object id. """
        return self._id
    
    
    # Subclasses need to implement the methods below
    
    def _create(self):
        # Create object in OpenGL memory and save the name in self._handle
        raise NotImplementedError()
    
    def _delete(self):
        # Remove self._object from OpenGL memory
        raise NotImplementedError()
    
    def _update(self):
        # Update data, compile, whatever, raise an error if needed
        raise NotImplementedError()
    
    def _activate(self):
        # Actvate / bind the object
        raise NotImplementedError()
    
    def _deactivate(self):
        # Deactivate / unbind the object
        raise NotImplementedError()

