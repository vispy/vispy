# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Functionality to deal with GL Contexts in vispy. This module is not in
app, because we want to make it possible to use parts of vispy without
relying on app.

The GLContext object is more like a placeholder on which different parts
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
    """An object encapsulating data necessary for a shared OpenGL context

    The data are backend dependent.
    """
    
    def __init__(self, config=None):
        self._value = None  # Used by vispy.app to store a ref
        self._taken = None  # Used by vispy.app to say what backend owns it
        self._config = deepcopy(_default_dict)
        self._config.update(config or {})
        # Check the config dict
        for key, val in self._config.items():
            if key not in _default_dict:
                raise KeyError('Key %r is not a valid GL config key.' % key)
            if not isinstance(val, type(_default_dict[key])):
                raise TypeError('Context value of %r has invalid type.' % key)
    
    def take(self, value, who, weak=False):
        """ Claim ownership of this context. Can only be done if the
        context is not yet taken. The value should be a reference to
        the actual GL context (which is stored on this object using a
        weak reference). The string ``who`` should specify who took it.
        """
        if self.istaken:
            raise RuntimeError('This GLContext is already taken by %s.' % 
                               self.istaken)
        if not weak:
            self._value_nonweak = value
        self._taken = str(who)
        self._value = weakref.ref(value)
    
    @property
    def istaken(self):
        """ Whether the context is owned by a GUI system. If taken, this
        returns the string name of the system that took it.
        """
        return self._taken
    
    @property
    def value(self):
        """ The value that the GUI system set when it took this coontext.
        This is stored with a weakref, so it can be None if the value
        has been cleaned up.
        """
        if self._value:
            return self._value()
    
    @property
    def config(self):
        """ A dictionary describing the configuration of this GL context.
        """
        return self._config
    
    def __repr__(self):
        backend = self._backend or 'no'
        return "<GLContext of %s backend at 0x%x>" % (backend, id(self))
