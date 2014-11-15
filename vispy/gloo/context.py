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


canvasses = []
pending_glir_queue = GlirQueue()


def get_default_config():
    """Get the default OpenGL context configuration

    Returns
    -------
    config : dict
        Dictionary of config values.
    """
    return deepcopy(_default_dict)


def get_current_glir_queue():
    """ Get the current GLIR queue
    
    This will be the glir queue on the current canvas, unless there
    is no canvas available. In this case a new GLIR queue is provided
    which is associated with the first canvas that gets created.
    
    Used by the gloo objects to acquire their glir queue.
    """
    canvas = get_current_canvas()
    if canvas is not None:
        return canvas.glir
    else:
        return pending_glir_queue


def get_current_canvas():
    """ Get the currently active canvas
    
    Returns None if there is no canvas available. A canvas is made
    active on initialization and before the draw event is emitted.
    
    When a gloo object is created, it is associated with the currently
    active Canvas, or with the next Canvas to be created if there is
    no current Canvas. Use Canvas.set_current() to manually activate a
    canvas.
    """
    cc = [c() for c in canvasses if c() is not None]
    if cc:
        return cc[-1]
    else:
        return None


def set_current_canvas(canvas):
    """ Make a canvas active. Used primarily by the canvas itself.
    """
    # Notify glir 
    canvas.glir.command('CURRENT', 0)
    # Try to be quick
    if canvasses and canvasses[-1]() is canvas:
        return
    # Make this the current
    cc = [c() for c in canvasses if c() is not None]
    while canvas in cc:
        cc.remove(canvas)
    cc.append(canvas)
    canvasses[:] = [weakref.ref(c) for c in cc]


def forget_canvas(canvas):
    """ Forget about the given canvas. Used by the canvas when closed.
    """
    cc = [c() for c in canvasses if c() is not None]
    while canvas in cc:
        cc.remove(canvas)
    canvasses[:] = [weakref.ref(c) for c in cc]


def take_pending_glir_queue():
    """ Get the current pending glir queue object and replace it
    with a new glir queue. Used by the Canvas class to get a glir queue
    to which some gloo objects may already have been associated.
    """
    global pending_glir_queue
    q = pending_glir_queue
    pending_glir_queue = GlirQueue()
    return q


class GLContext(object):
    """An object encapsulating data necessary for a shared OpenGL context.
    The intended use is to subclass this and implement _vispy_activate().
    """
    
    def __init__(self, config=None):
        self._backend_canvas = lambda x=None: None
        self._name = None
        self.set_config(config)
    
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
   
    def __repr__(self):
        backend = self.istaken or 'no'
        return "<GLContext of %s backend at 0x%x>" % (backend, id(self))
