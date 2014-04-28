# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division, print_function

import numpy as np

from ._default_app import default_app
from ..util.event import EmitterGroup, Event
from ..util.ptime import time
from ..util.six import string_types
from .application import Application
from ._config import get_default_config

# todo: add functions for asking about current mouse/keyboard state
# todo: add hover enter/exit events
# todo: add focus events


def _gloo_initialize(event):
    from ..gloo import gl_initialize
    gl_initialize()


class Canvas(object):
    """Representation of a GUI element with an OpenGL context

    Receives the following events:
    initialize, resize, paint, mouse_press, mouse_release, mouse_move,
    mouse_wheel, key_press, key_release, stylus, touch, close

    Parameters
    ----------
    title : str
        The widget title
    size : (width, height)
        The size of the window.
    position : (x, y)
        The position of the window in screen coordinates.
    show : bool
        Whether to show the widget immediately. Default False.
    autoswap : bool
        Whether to swap the buffers automatically after a paint event.
        Default True. If True, the ``swap_buffers`` Canvas method will
        be called last (by default) by the ``canvas.paint`` event handler.
    app : Application | str
        Give vispy Application instance to use as a backend.
        (vispy.app is used by default.) If str, then an application
        using the chosen backend (e.g., 'pyglet') will be created.
        Note the canvas application can be accessed at ``canvas.app``.
    create_native : bool
        Whether to create the widget immediately. Default True.
    init_gloo : bool
        Initialize standard values in gloo (e.g., ``GL_POINT_SPRITE``).
    vsync : bool
        Enable vertical synchronization.
    resizable : bool
        Allow the window to be resized.
    decorate : bool
        Decorate the window.
    fullscreen : bool | int
        If False, windowed mode is used (default). If True, the default
        monitor is used. If int, the given monitor number is used.
    context : dict | instance SharedContext | None
        OpenGL configuration to use when creating the context for the canvas,
        or a context to share. If None, ``vispy.app.get_default_config`` will
        be used to set the OpenGL context parameters. Alternatively, the
        ``canvas.context`` property from an existing canvas (using the
        same backend) will return a ``SharedContext`` that can be used,
        thereby sharing the existing context.
    close_keys : list of str
        Key to use that will cause the canvas to be closed.
    """

    def __init__(self, title='Vispy canvas', size=(800, 600), position=None,
                 show=False, autoswap=True, app=None, create_native=True,
                 init_gloo=True, vsync=False, resizable=True, decorate=True,
                 fullscreen=False, context=None, close_keys=()):
        self.events = EmitterGroup(source=self,
                                   initialize=Event,
                                   resize=ResizeEvent,
                                   paint=PaintEvent,
                                   mouse_press=MouseEvent,
                                   mouse_release=MouseEvent,
                                   mouse_move=MouseEvent,
                                   mouse_wheel=MouseEvent,
                                   key_press=KeyEvent,
                                   key_release=KeyEvent,
                                   stylus=Event,
                                   touch=Event,
                                   close=Event)
        size = [int(s) for s in size]
        if len(size) != 2:
            raise ValueError('size must be a 2-element list')
        title = str(title)
        if not isinstance(fullscreen, (bool, int)):
            raise TypeError('fullscreen must be bool or int')
        if context is None:
            context = get_default_config()

        # Initialize backend attribute
        self._backend = None
        if init_gloo:
            self.events.initialize.connect(_gloo_initialize,
                                           ref='gloo_initialize')

        # store arguments that get set on Canvas init
        kwargs = dict(title=title, size=size, position=position, show=show,
                      vsync=vsync, resizable=resizable, decorate=decorate,
                      fullscreen=fullscreen, context=context)
        self._backend_kwargs = kwargs

        # Initialise some values
        self._autoswap = autoswap
        self._title = title
        self._frame_count = 0
        self._fps = 0
        self._basetime = time()
        self._fps_callback = None

        # Get app instance
        if isinstance(app, string_types):
            app = Application(app)
        self._app = default_app if app is None else app

        # Create widget now
        if create_native:
            self.create_native()
        self.close_keys = close_keys

        def close_keys_check(event):
            if event.key in self.close_keys:
                self.close()
        self.events.key_press.connect(close_keys_check, ref=True)

    def create_native(self):
        """ Create the native widget if not already done so. If the widget
        is already created, this function does nothing.
        """
        if self._backend is not None:
            return
        # Make sure that the app is active
        self._app.use()
        assert self._app.native
        # Instantiate the backend with the right class
        be = self._app.backend_module.CanvasBackend(**self._backend_kwargs)
        self._set_backend(be)

    def _set_backend(self, backend):
        """ Set backend<->canvas references and autoswap
        """
        assert backend is not None  # should never happen
        self._backend = backend
        self._backend._vispy_canvas = self
        if self._autoswap:
            # append to the end
            self.events.paint.connect((self, 'swap_buffers'),
                                      ref=True, position='last')

    @property
    def context(self):
        """ The OpenGL context of the native widget
        """
        return self._backend._vispy_context

    @property
    def app(self):
        """ The vispy Application instance on which this Canvas is based.
        """
        return self._app

    @property
    def native(self):
        """ The native widget object on which this Canvas is based.
        """
        return self._backend._vispy_get_native_canvas()

    def connect(self, fun):
        """ Connect a function to an event. The name of the function
        should be on_X, with X the name of the event (e.g. 'on_paint').

        This method is typically used as a decorater on a function
        definition for an event handler.
        """
        # Get and check name
        name = fun.__name__
        if not name.startswith('on_'):
            raise ValueError('When connecting a function based on its name, '
                             'the name should start with "on_"')
        eventname = name[3:]
        # Get emitter
        try:
            emitter = self.events[eventname]
        except KeyError:
            raise ValueError(
                'Event "%s" not available on this canvas.' %
                eventname)
        # Connect
        emitter.connect(fun)

    # ---------------------------------------------------------------- size ---
    @property
    def size(self):
        """ The size of canvas/window """
        return self._backend._vispy_get_size()

    @size.setter
    def size(self, size):
        return self._backend._vispy_set_size(size[0], size[1])

    # ------------------------------------------------------------ position ---
    @property
    def position(self):
        """ The position of canvas/window relative to screen """
        return self._backend._vispy_get_position()

    @position.setter
    def position(self, position):
        assert len(position) == 2
        return self._backend._vispy_set_position(position[0], position[1])

    # --------------------------------------------------------------- title ---
    @property
    def title(self):
        """ The title of canvas/window """
        return self._title

    @title.setter
    def title(self, title):
        self._title = title
        self._backend._vispy_set_title(title)

    # --------------------------------------------------------------- fps ---
    @property
    def fps(self):
        """ The fps of canvas/window, measured as the rate that events.paint
        is emitted. """
        return self._fps

    def swap_buffers(self, event=None):
        """ Swap GL buffers such that the offscreen buffer becomes visible.
        """
        self._backend._vispy_swap_buffers()

    def show(self, visible=True):
        """ Show (or hide) the canvas """
        return self._backend._vispy_set_visible(visible)

    def update(self):
        """ Inform the backend that the Canvas needs to be repainted """
        if self._backend is not None:
            return self._backend._vispy_update()
        else:
            return

    def close(self):
        """ Close the canvas

        Note: This will usually destroy the GL context. For Qt, the context
        (and widget) will be destroyed only if the widget is top-level.
        To avoid having the widget destroyed (more like standard Qt
        behavior), consider making the widget a sub-widget.
        """
        if self._backend is not None:
            self._backend._vispy_close()

    def _update_fps(self, event):
        """ Updates the fps after every window and resets the basetime
        and frame count to current time and 0, respectively
        """
        self._frame_count += 1
        diff = time() - self._basetime
        if (diff > self._fps_window):
            self._fps = self._frame_count/diff
            self._basetime = time()
            self._frame_count = 0
            self._fps_callback(self.fps)

    def measure_fps(self, window=1, callback=print):
        """Measure the current FPS

        Sets the update window, connects the paint event to
        update_fps and sets the callback function
        If no callback is passed, measurement stops.

        Parameters
        ----------
        window : int
            The window number.
        callback : function
            The function to call with the FPS. Default is ``print``.
        """
        # Connect update_fps function to paint
        self.events.paint.disconnect(self._update_fps)
        if callback:
            self._fps_window = window
            self.events.paint.connect(self._update_fps)
            self._fps_callback = callback
        else:
            self._fps_callback = None

    def __repr__(self):
        return ('<Vispy canvas (%s backend) at %s>'
                % (self.app.backend_name, hex(id(self))))

    def __enter__(self):
        self.show()
        self._backend._vispy_warmup()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    # def mouse_event(self, event):
        #"""Called when a mouse input event has occurred (the mouse has moved,
        # a button was pressed/released, or the wheel has moved)."""

    # def key_event(self, event):
        #"""Called when a keyboard event has occurred (a key was pressed or
        # released while the canvas has focus)."""

    # def touch_event(self, event):
        #"""Called when the user touches the screen over a Canvas.

        # Event properties:
        #     event.touches
        #     [ (x,y,pressure), ... ]
        #"""

    # def stylus_event(self, event):
        #"""Called when a stylus has been used to interact with the Canvas.

        # Event properties:
        #     event.device
        #     event.pos  (x,y)
        #     event.pressure
        #     event.angle
        #"""

    # def initialize_event(self, event):
        #"""Called when the OpenGL context is initialy made available for this
        # Canvas."""

    # def resize_event(self, event):
        #"""Called when the Canvas is resized.

        # Event properties:
        #     event.size  (w,h)
        #"""

    # def paint_event(self, event):
        #"""Called when all or part of the Canvas needs to be repainted.

        # Event properties:
        #     event.region  (x,y,w,h) region of Canvas requiring repaint
        #"""


# Event subclasses specific to the Canvas
class MouseEvent(Event):

    """Mouse event class

    Note that each event object has an attribute for each of the input
    arguments listed below.

    Parameters
    ----------
    type : str
       String indicating the event type (e.g. mouse_press, key_release)
    pos : (int, int)
        The position of the mouse (in screen coordinates).
    button : int
        The button that generated this event (can be None).
        Left=1, right=2, middle=3.
    buttons : [int, ...]
        The list of buttons depressed during this event.
    modifiers : tuple of Key instances
        Tuple that specifies which modifier keys were pressed down at the
        time of the event (shift, control, alt, meta).
    delta : (float, float)
        The amount of scrolling in horizontal and vertical direction. One
        "tick" corresponds to a delta of 1.0.
    press_event : MouseEvent
        The press event that was generated at the start of the current drag,
        if any.
    last_event : MouseEvent
        The MouseEvent immediately preceding the current event. During drag
        operations, all generated events retain their last_event properties,
        allowing the entire drag to be reconstructed.
    native : object (optional)
       The native GUI event object
    **kwds : keyword arguments
        All extra keyword arguments become attributes of the event object.

    """

    def __init__(self, type, pos=None, button=None, buttons=None,
                 modifiers=None, delta=None, last_event=None, press_event=None,
                 **kwds):
        Event.__init__(self, type, **kwds)
        self._pos = (0, 0) if (pos is None) else (pos[0], pos[1])
        self._button = int(button) if (button is not None) else 0
        self._buttons = [] if (buttons is None) else buttons
        self._modifiers = tuple(modifiers or ())
        self._delta = (0.0, 0.0) if (delta is None) else (delta[0], delta[1])
        self._last_event = last_event
        self._press_event = press_event

    @property
    def pos(self):
        return self._pos

    @property
    def button(self):
        return self._button

    @property
    def buttons(self):
        return self._buttons

    @property
    def modifiers(self):
        return self._modifiers

    @property
    def delta(self):
        return self._delta

    @property
    def press_event(self):
        return self._press_event

    @property
    def last_event(self):
        return self._last_event

    def _forget_last_event(self):
        # Needed to break otherwise endless last-event chains
        self._last_event = None

    @property
    def is_dragging(self):
        """ Indicates whether this event is part of a mouse drag operation.
        """
        return self.press_event is not None

    def drag_events(self):
        """ Return a list of all mouse events in the current drag operation.

        Returns None if there is no current drag operation.
        """
        if not self.is_dragging:
            return None

        event = self
        events = []
        while True:
            # mouse_press events can only be the start of a trail
            if event is None or event.type == 'mouse_press':
                break
            events.append(event)
            event = event.last_event

        return events[::-1]

    def trail(self):
        """ Return an (N, 2) array of mouse coordinates for every event in the
        current mouse drag operation.

        Returns None if there is no current drag operation.
        """
        events = self.drag_events()
        if events is None:
            return None

        trail = np.empty((len(events), 2), dtype=int)
        for i, ev in enumerate(events):
            trail[i] = ev.pos

        return trail


class KeyEvent(Event):

    """Key event class

    Note that each event object has an attribute for each of the input
    arguments listed below.

    Parameters
    ----------
    type : str
       String indicating the event type (e.g. mouse_press, key_release)
    key : vispy.keys.Key instance
        The Key object for this event. Can be compared to string names.
    text : str
        The text representation of the key (can be an empty string).
    modifiers : tuple of Key instances
        Tuple that specifies which modifier keys were pressed down at the
        time of the event (shift, control, alt, meta).
    native : object (optional)
       The native GUI event object
    **kwds : keyword arguments
        All extra keyword arguments become attributes of the event object.
    """

    def __init__(self, type, key=None, text='', modifiers=None, **kwds):
        Event.__init__(self, type, **kwds)
        self._key = key
        self._text = text
        self._modifiers = tuple(modifiers or ())

    @property
    def key(self):
        return self._key

    @property
    def text(self):
        return self._text

    @property
    def modifiers(self):
        return self._modifiers


class ResizeEvent(Event):

    """ Resize event class

    Note that each event object has an attribute for each of the input
    arguments listed below.

    Parameters
    ----------
    type : str
       String indicating the event type (e.g. mouse_press, key_release)
    size : (int, int)
        The new size of the Canvas.
    native : object (optional)
       The native GUI event object
    **kwds : extra keyword arguments
        All extra keyword arguments become attributes of the event object.
    """

    def __init__(self, type, size=None, **kwds):
        Event.__init__(self, type, **kwds)
        self._size = tuple(size)

    @property
    def size(self):
        return self._size


class PaintEvent(Event):

    """ Paint event class

    This type of event is sent to Canvas.events.paint when a repaint
    is required.

    Note that each event object has an attribute for each of the input
    arguments listed below.

    Parameters
    ----------
    type : str
       String indicating the event type (e.g. mouse_press, key_release)
    region : (int, int, int, int) or None
        The region of the canvas which needs to be repainted (x, y, w, h).
        If None, the entire canvas must be repainted.
    native : object (optional)
       The native GUI event object
    **kwds : extra keyword arguments
        All extra keyword arguments become attributes of the event object.
    """

    def __init__(self, type, region=None, **kwds):
        Event.__init__(self, type, **kwds)
        self._region = region

    @property
    def region(self):
        return self._region
