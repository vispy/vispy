# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
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

from .glir import GlirQueue, BaseGlirParser, GlirParser, glir_logger
from .wrappers import BaseGlooFunctions
from .. import config

_default_dict = dict(red_size=8, green_size=8, blue_size=8, alpha_size=8,
                     depth_size=24, stencil_size=0, double_buffer=True,
                     stereo=False, samples=0)


canvasses = []


def get_default_config():
    """Get the default OpenGL context configuration

    Returns
    -------
    config : dict
        Dictionary of config values.
    """
    return deepcopy(_default_dict)


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
    canvas.context._do_CURRENT_command = True
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


class GLContext(BaseGlooFunctions):
    """An object encapsulating data necessary for a OpenGL context

    Parameters
    ----------
    config : dict | None
        The requested configuration.
    shared : instance of GLContext | None
        The shared context.
    """
    
    def __init__(self, config=None, shared=None):
        self._set_config(config)
        self._shared = shared if (shared is not None) else GLShared()
        assert isinstance(self._shared, GLShared)
        self._glir = GlirQueue()
        self._do_CURRENT_command = False  # flag that CURRENT cmd must be given
        self._last_viewport = None

    def __repr__(self):
        return "<GLContext at 0x%x>" % id(self)
    
    def _set_config(self, config):
        self._config = deepcopy(_default_dict)
        self._config.update(config or {})
        # Check the config dict
        for key, val in self._config.items():
            if key not in _default_dict:
                raise KeyError('Key %r is not a valid GL config key.' % key)
            if not isinstance(val, type(_default_dict[key])):
                raise TypeError('Context value of %r has invalid type.' % key)
    
    def create_shared(self, name, ref):
        """ For the app backends to create the GLShared object.

        Parameters
        ----------
        name : str
            The name.
        ref : object
            The reference.
        """
        if self._shared is not None:
            raise RuntimeError('Can only set_shared once.')
        self._shared = GLShared(name, ref)
    
    @property
    def config(self):
        """ A dictionary describing the configuration of this GL context.
        """
        return self._config
    
    @property
    def glir(self):
        """ The glir queue for the context. This queue is for objects
        that can be shared accross canvases (if they share a contex).
        """
        return self._glir
    
    @property
    def shared(self):
        """ Get the object that represents the namespace that can
        potentially be shared between multiple contexts.
        """
        return self._shared

    @property
    def capabilities(self):
        """ The OpenGL capabilities
        """
        return deepcopy(self.shared.parser.capabilities)

    def flush_commands(self, event=None):
        """ Flush

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        if self._do_CURRENT_command:
            self._do_CURRENT_command = False
            self.shared.parser.parse([('CURRENT', 0)])
        self.glir.flush(self.shared.parser)
        
    def set_viewport(self, *args):
        BaseGlooFunctions.set_viewport(self, *args)
        self._last_viewport = args
        
    def get_viewport(self):
        return self._last_viewport


class GLShared(object):
    """ Representation of a "namespace" that can be shared between
    different contexts. App backends can associate themselves with this
    object via add_ref().
    
    This object can be used to establish whether two contexts/canvases
    share objects, and can be used as a placeholder to store shared
    information, such as glyph atlasses.
    """
    
    # We keep a (weak) ref of each backend that gets associated with
    # this object. In theory, this means that multiple canvases can
    # be created and also deleted; as long as there is at least one
    # left, things should Just Work. 
    
    def __init__(self):
        glir_file = config['glir_file']

        parser_cls = GlirParser
        if glir_file:
            parser_cls = glir_logger(parser_cls, glir_file)

        self._parser = parser_cls()
        self._name = None
        self._refs = []
    
    def __repr__(self):
        return "<GLShared of %s backend at 0x%x>" % (str(self.name), id(self))
    
    @property
    def parser(self):
        """The GLIR parser (shared between contexts) """
        return self._parser

    @parser.setter
    def parser(self, parser):
        assert isinstance(parser, BaseGlirParser) or parser is None
        self._parser = parser
    
    def add_ref(self, name, ref):
        """ Add a reference for the backend object that gives access
        to the low level context. Used in vispy.app.canvas.backends.
        The given name must match with that of previously added
        references.
        """
        if self._name is None:
            self._name = name
        elif name != self._name:
            raise RuntimeError('Contexts can only share between backends of '
                               'the same type')
        self._refs.append(weakref.ref(ref))
    
    @property
    def name(self):
        """ The name of the canvas backend that this shared namespace is
        associated with. Can be None.
        """
        return self._name
    
    @property
    def ref(self):
        """ A reference (stored internally via a weakref) to an object
        that the backend system can use to obtain the low-level
        information of the "reference context". In Vispy this will
        typically be the CanvasBackend object.
        """
        # Clean
        self._refs = [r for r in self._refs if (r() is not None)]
        # Get ref
        ref = self._refs[0]() if self._refs else None
        if ref is not None:
            return ref
        else:
            raise RuntimeError('No reference for available for GLShared')


class FakeCanvas(object):
    """ Fake canvas to allow using gloo without vispy.app
    
    Instantiate this class to collect GLIR commands from gloo
    interactions. Call flush() in your draw event handler to execute
    the commands in the active contect.
    """
    
    def __init__(self):
        self.context = GLContext()
        set_current_canvas(self)
    
    def flush(self):
        """ Flush commands. Call this after setting to context to current.
        """
        self.context.flush_commands()
