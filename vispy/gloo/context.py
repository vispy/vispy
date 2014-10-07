# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Functionality to deal with GL Contexts in vispy. This module is defined
in gloo, because gloo (and the layers that depend on it) need to be
context aware. The vispy.app module "provides" a context, and therefore
depends on this module. Although the GLContext class is aimed for use
by vispy.app (for practical reasons), it should be possible to use
GLContext without using vispy.app by overloading it in an appropriate
manner.

An GLContext object acts as a placeholder on which different parts
of vispy (or other systems) can keep track of information related to
an OpenGL context.
"""

from copy import deepcopy
import weakref

from .glir import GlirQueue


_default_dict = dict(red_size=8, green_size=8, blue_size=8, alpha_size=8,
                     depth_size=16, stencil_size=0, double_buffer=True,
                     stereo=False, samples=0)


def get_default_config():
    """Get the default OpenGL context configuration

    Returns
    -------
    config : dict
        Dictionary of config values.
    """
    return deepcopy(_default_dict)


def get_current_context():
    """ Get the currently active GLContext object
    
    Returns
    -------
    context : GLContext or None
        The context object that is now active, or None if there is no
        active context.
    """
    return GLContext._current_context


def get_a_context():
    """ Get a GLContext object
    
    This function is recommended to be used by context "consumers" (code
    that needs a context), and is used as such by `vispy.gloo`.
    
    Returns
    -------
    context : GLContext
        The currently active context, or a "pending" context object if
        there is currently no active context. This pending context will be
        the first context to be taken by a context "provider".
    """
    # Ensure that there is a default context
    if GLContext._default_context is None:
        GLContext._default_context = GLContext()
    # Return a context
    return GLContext._current_context or GLContext._default_context


def get_new_context():
    """ Get a new GLContext object that is not yet taken
    
    This function is recommended to be used by context "providers" (code
    that takes the context and provides a native GL context), and is used
    as such by `vispy.app`.
    
    Returns
    -------
    context : GLContext
        A context object that is guaranteed to have not been taken.
        This may be a "pending" context that is already passed to 
        context "consumers".
    """
    # Ensure that there is default context and that it is not taken
    if GLContext._default_context is None:
        GLContext._default_context = GLContext()
    elif GLContext._default_context.istaken:
        GLContext._default_context = GLContext()
    # Return context
    return GLContext._default_context


class GLContext(object):
    """An object encapsulating data necessary for a shared OpenGL context.
    The intended use is to subclass this and implement _vispy_activate().
    """
    
    _current_context = None  # The currently active context (always taken)
    _default_context = None  # The context that is likely to become active soon
    
    def __init__(self, config=None):
        self._backend_canvas = lambda x=None: None
        self._name = None
        self.set_config(config)
        self._glir = GlirQueue()
    
    def set_config(self, config):
        """ Set the config of this context. Setting the config after
        it it claimed generally has no effect.
        """
        self._config = deepcopy(_default_dict)
        self._config.update(config or {})
        # Check the config dict
        for key, val in self._config.items():
            if key not in _default_dict:
                raise KeyError('Key %r is not a valid GL config key.' % key)
            if not isinstance(val, type(_default_dict[key])):
                raise TypeError('Context value of %r has invalid type.' % key)
    
    @property
    def glir(self):
        """ The glir queue object
        
        The glir queue can be used to give GLIR commands, which will be parsed
        at the right moment (by the app canvas).
        """
        # There are three moments where the queue is flushed:
        # - On canvas.events.paint
        # - On gloo.flush() and gloo.finish()
        # - On gloo.Program.draw()
        return self._glir
    
    def take(self, name, backend_canvas):
        """ Claim ownership for this context. This can only be done if it is
        not already taken. 
        """
        if self.istaken:
            raise RuntimeError('Cannot take a GLContext that is already taken')
        self._name = name
        self._backend_canvas = weakref.ref(backend_canvas)
    
    @property
    def istaken(self):
        """ Whether this context it currently taken.
        """
        return self._name or False
    
    @property
    def backend_canvas(self):
        """ The backend canvas that claimed ownership for this context.
        If the context is not yet taken or if the backend canvas has
        been deleted, an error is raised.
        """
        backend_canvas = self._backend_canvas()
        if backend_canvas is not None:
            return backend_canvas
        else:
            raise RuntimeError('The backend_canvas is not available')
    
    @property
    def config(self):
        """ A dictionary describing the configuration of this GL context.
        """
        return self._config
    
    def set_current(self, apply_backend=True):
        """ Make this the current context. If apply_backend is True
        (default) the canvas_backend is set to be current.
        """
        if apply_backend:
            self.backend_canvas._vispy_set_current()
        GLContext._current_context = self
    
    @property
    def iscurrent(self):
        """ Whether this is currentlty the active context.
        """
        return GLContext._current_context is self
    
    def __repr__(self):
        backend = self.istaken or 'no'
        return "<GLContext of %s backend at 0x%x>" % (backend, id(self))
