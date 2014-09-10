# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Functionality to deal with GL Contexts in vispy. This module is not in
vispy.app, because we want to make it possible to use parts of vispy
without relying on app (and vice versa). Although this *looks* like
something from vispy.app (for practical reasons), it should be possible
to use GLContext without using vispy.app by overloading it in an
appropriate manner.

An GLContext object acts as a placeholder on which different parts
of vispy (or other systems) can keep track of information related to
an OpenGL context.
"""

from copy import deepcopy
import weakref

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


class GLContext(object):
    """An object encapsulating data necessary for a shared OpenGL context.
    The intended use is to subclass this and implement _vispy_activate().
    """
    
    _active_context = None
    
    def __init__(self, config=None):
        self._config = deepcopy(_default_dict)
        self._config.update(config or {})
        # Check the config dict
        for key, val in self._config.items():
            if key not in _default_dict:
                raise KeyError('Key %r is not a valid GL config key.' % key)
            if not isinstance(val, type(_default_dict[key])):
                raise TypeError('Context value of %r has invalid type.' % key)
        # Init backend canvas and name
        self._backend_canvas = lambda x=None: None
        self._name = None
    
    def take(self, name, backend_canvas):
        """ Claim ownership for this context. This can only be done if it is
        not already taken. 
        """
        if self.istaken:
            raise ValueError('Cannot take an GLContext that is already taken')
        self._name = name
        self._backend_canvas = weakref.ref(backend_canvas)
    
    @property
    def istaken(self):
        """ Whether this context currently is taken.
        """
        return self._name or False
    
    @property
    def backend_canvas(self):
        """ The backend canvas that claimed ownership for this context. 
        If the context is not yet taken or if the backend canvas has been
        deleted, an error is raised.
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
    
    def activate(self):
        """ Activate this context. There can only be one active context at 
        all times.
        """
        self.backend_canvas._vispy_make_current()
        GLContext._active_context = self
    
    @property
    def isactive(self):
        """ Whether this is currentlty the active context.
        """
        return GLContext._active_context is self
    
    def __repr__(self):
        backend = self.istaken or 'no'
        return "<GLContext of %s backend at 0x%x>" % (backend, id(self))
