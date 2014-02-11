# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Definition of the base class for all gloo objects.
"""

from ..util import logger


class GLObject(object):

    """ Base class for classes that wrap an OpenGL object.
    All GLObject's can be used as a context manager to enable them,
    although some are better used by setting them as a uniform or
    attribute of a Program.

    All GLObject's apply deferred (a.k.a. lazy) loading, which means
    that the objects can be created and data can be set even if no
    OpenGL context is available yet.

    There are a few exceptions, most notably when enabling an object
    by using it as a context manager, and the delete method. In these
    cases, the called should ensure that the proper OpenGL context is
    current.
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
        self._valid = False

        # Error counters (only used here)
        self._error_enter = 0  # Track error on __enter__
        self._error_exit = 0  # track errors on __exit__

        # Object internal id (for e.g. debugging)
        GLObject._idcount += 1
        self._id = GLObject._idcount

    def __enter__(self):
        """ Entering context  """

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
        """ Leaving context  """
        returnval = None
        if value is None:
            # Reset error state on success
            self._error_exit = 0
        else:
            # Error: increase error state. If not the first error, suppress
            self._error_exit += 1
            if self._error_enter or self._error_exit > 1:
                returnval = True  # Suppress error
        self.deactivate()
        return returnval

    def __del__(self):
        """ Delete the object from OpenGl memory. """
        # You never know when this is goint to happen. The window might
        # already be closed and no OpenGL context might be available.
        # So we try, but suppress errors unless the user explicity asks them
        try:
            self.delete()
        except Exception as err:
            logger.warn('Error deleting %r: %s' % (self, err))

    def delete(self):
        """ Delete the object from OpenGl memory. """

        # Only delete object if it was created on GPU
        if self._handle:
            self._delete()
        # Reset
        self._handle = 0
        self._valid = False

    def activate(self):
        """ Activate the object (a GL context must be available).
        Note that the object can also be activated (and automatically
        deactivated) by using it as a context manager.
        """

        # Ensure that the GPU equivalent of this object exists
        if not self.handle:
            try:
                self._create()
            except Exception:
                raise RuntimeError('Could not create %r, perhaps there is '
                                   'no OpenGL context?' % self)
        # Perform an update if necessary
        if self._need_update:
            self._update()  # If it does not raise an error, assume valid
            self._need_update = False
            self._valid = True
        # Activate
        self._activate()

    def deactivate(self):
        """ Deactivate the object.
        """

        return self._deactivate()

    @property
    def handle(self):
        """ Name of this object in GPU.
        """

        return self._handle

    # Subclasses may need to overload methods below
    def _create(self):
        pass

    def _delete(self):
        pass

    def _update(self):
        pass

    def _activate(self):
        pass

    def _deactivate(self):
        pass
