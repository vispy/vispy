# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division, print_function

import sys
import numpy as np
from time import sleep

from ..util.event import EmitterGroup, Event, WarningEmitter
from ..util.ptime import time
from ..util.dpi import get_dpi
from ..util import config as util_config, logger
from . import Application, use_app
from ..gloo.context import (GLContext, set_current_canvas, forget_canvas)
from ..gloo import FrameBuffer, RenderBuffer


# todo: add functions for asking about current mouse/keyboard state
# todo: add hover enter/exit events
# todo: add focus events


class Canvas(object):
    """Representation of a GUI element with an OpenGL context

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
        Whether to swap the buffers automatically after a draw event.
        Default True. If True, the ``swap_buffers`` Canvas method will
        be called last (by default) by the ``canvas.draw`` event handler.
    app : Application | str
        Give vispy Application instance to use as a backend.
        (vispy.app is used by default.) If str, then an application
        using the chosen backend (e.g., 'pyglet') will be created.
        Note the canvas application can be accessed at ``canvas.app``.
    create_native : bool
        Whether to create the widget immediately. Default True.
    vsync : bool
        Enable vertical synchronization.
    resizable : bool
        Allow the window to be resized.
    decorate : bool
        Decorate the window. Default True.
    fullscreen : bool | int
        If False, windowed mode is used (default). If True, the default
        monitor is used. If int, the given monitor number is used.
    config : dict
        A dict with OpenGL configuration options, which is combined
        with the default configuration options and used to initialize
        the context. See ``canvas.context.config`` for possible
        options.
    shared : Canvas | GLContext | None
        An existing canvas or context to share OpenGL objects with.
    keys : str | dict | None
        Default key mapping to use. If 'interactive', escape and F11 will
        close the canvas and toggle full-screen mode, respectively.
        If dict, maps keys to functions. If dict values are strings,
        they are assumed to be ``Canvas`` methods, otherwise they should
        be callable.
    parent : widget-object
        The parent widget if this makes sense for the used backend.
    dpi : float | None
        Resolution in dots-per-inch to use for the canvas. If dpi is None,
        then the value will be determined by querying the global config first,
        and then the operating system.
    always_on_top : bool
        If True, try to create the window in always-on-top mode.
    px_scale : int > 0
        A scale factor to apply between logical and physical pixels in addition
        to the actual scale factor determined by the backend. This option
        allows the scale factor to be adjusted for testing.
    backend_kwargs : dict
        Keyword arguments to be supplied to the backend canvas object.

    Notes
    -----
    The `Canvas` receives the following events:

        * initialize
        * resize
        * draw
        * mouse_press
        * mouse_release
        * mouse_double_click
        * mouse_move
        * mouse_wheel
        * key_press
        * key_release
        * stylus
        * touch
        * close

    The ordering of the mouse_double_click, mouse_press, and mouse_release
    events are not guaranteed to be consistent between backends. Only certain
    backends natively support double-clicking (currently Qt and WX); on other
    backends, they are detected manually with a fixed time delay.
    This can cause problems with accessibility, as increasing the OS detection
    time or using a dedicated double-click button will not be respected.

    Backend-specific arguments can be given through the `backend_kwargs`
    argument.
    """

    def __init__(self, title='VisPy canvas', size=(800, 600), position=None,
                 show=False, autoswap=True, app=None, create_native=True,
                 vsync=False, resizable=True, decorate=True, fullscreen=False,
                 config=None, shared=None, keys=None, parent=None, dpi=None,
                 always_on_top=False, px_scale=1, backend_kwargs=None):

        size = tuple(int(s) * px_scale for s in size)
        if len(size) != 2:
            raise ValueError('size must be a 2-element list')
        title = str(title)
        if not isinstance(fullscreen, (bool, int)):
            raise TypeError('fullscreen must be bool or int')

        # Initialize some values
        self._autoswap = autoswap
        self._title = title
        self._frame_count = 0
        self._fps = 0
        self._basetime = time()
        self._fps_callback = None
        self._backend = None
        self._closed = False
        self._fps_window = 0.
        self._px_scale = int(px_scale)

        if dpi is None:
            dpi = util_config['dpi']
        if dpi is None:
            dpi = get_dpi(raise_error=False)
        self.dpi = dpi

        # Create events
        self.events = EmitterGroup(source=self,
                                   initialize=Event,
                                   resize=ResizeEvent,
                                   draw=DrawEvent,
                                   mouse_press=MouseEvent,
                                   mouse_release=MouseEvent,
                                   mouse_double_click=MouseEvent,
                                   mouse_move=MouseEvent,
                                   mouse_wheel=MouseEvent,
                                   key_press=KeyEvent,
                                   key_release=KeyEvent,
                                   stylus=Event,
                                   touch=Event,
                                   close=Event)

        # Deprecated paint emitter
        emitter = WarningEmitter('Canvas.events.paint and Canvas.on_paint are '
                                 'deprecated; use Canvas.events.draw and '
                                 'Canvas.on_draw instead.',
                                 source=self, type='draw',
                                 event_class=DrawEvent)
        self.events.add(paint=emitter)
        self.events.draw.connect(self.events.paint)

        # Get app instance
        if app is None:
            self._app = use_app(call_reuse=False)
        elif isinstance(app, Application):
            self._app = app
        elif isinstance(app, str):
            self._app = Application(app)
        else:
            raise ValueError('Invalid value for app %r' % app)

        # Check shared and context
        if shared is None:
            pass
        elif isinstance(shared, Canvas):
            shared = shared.context.shared
        elif isinstance(shared, GLContext):
            shared = shared.shared
        else:
            raise TypeError('shared must be a Canvas, not %s' % type(shared))
        config = config or {}
        if not isinstance(config, dict):
            raise TypeError('config must be a dict, not %s' % type(config))

        # Create new context
        self._context = GLContext(config, shared)

        # Deal with special keys
        self._set_keys(keys)

        # store arguments that get set on Canvas init
        self._backend_kwargs = dict(
            title=title, size=size, position=position, show=show,
            vsync=vsync, resizable=resizable, decorate=decorate,
            fullscreen=fullscreen, context=self._context,
            parent=parent, always_on_top=always_on_top)
        if backend_kwargs is not None:
            self._backend_kwargs.update(**backend_kwargs)

        # Create widget now (always do this *last*, after all err checks)
        if create_native:
            self.create_native()

            # Now we're ready to become current
            self.set_current()

        if '--vispy-fps' in sys.argv:
            self.measure_fps()

    def create_native(self):
        """Create the native widget if not already done so. If the widget
        is already created, this function does nothing.
        """
        if self._backend is not None:
            return
        # Make sure that the app is active
        assert self._app.native
        # Instantiate the backend with the right class
        self._app.backend_module.CanvasBackend(self, **self._backend_kwargs)
        # self._backend = set by BaseCanvasBackend
        self._backend_kwargs = None  # Clean up

        # Connect to draw event (append to the end)
        # Process GLIR commands at each paint event
        self.events.draw.connect(self.context.flush_commands, position='last')
        if self._autoswap:
            self.events.draw.connect((self, 'swap_buffers'),
                                     ref=True, position='last')

    def _set_keys(self, keys):
        if keys is not None:
            if isinstance(keys, str):
                if keys != 'interactive':
                    raise ValueError('keys, if string, must be "interactive", '
                                     'not %s' % (keys,))

                def toggle_fs():
                    self.fullscreen = not self.fullscreen
                keys = dict(escape='close', F11=toggle_fs)
        else:
            keys = {}
        if not isinstance(keys, dict):
            raise TypeError('keys must be a dict, str, or None')
        if len(keys) > 0:
            lower_keys = {}
            # ensure all are callable
            for key, val in keys.items():
                if isinstance(val, str):
                    new_val = getattr(self, val, None)
                    if new_val is None:
                        raise ValueError('value %s is not an attribute of '
                                         'Canvas' % val)
                    val = new_val
                if not hasattr(val, '__call__'):
                    raise TypeError('Entry for key %s is not callable' % key)
                # convert to lower-case representation
                lower_keys[key.lower()] = val
            self._keys_check = lower_keys

            def keys_check(event):
                if event.key is not None:
                    use_name = event.key.name.lower()
                    if use_name in self._keys_check:
                        self._keys_check[use_name]()
            self.events.key_press.connect(keys_check, ref=True)

    @property
    def context(self):
        """The OpenGL context of the native widget

        It gives access to OpenGL functions to call on this canvas object,
        and to the shared context namespace.
        """
        return self._context

    @property
    def app(self):
        """The vispy Application instance on which this Canvas is based."""
        return self._app

    @property
    def native(self):
        """The native widget object on which this Canvas is based."""
        return self._backend._vispy_get_native_canvas()

    @property
    def dpi(self):
        """The physical resolution of the canvas in dots per inch."""
        return self._dpi

    @dpi.setter
    def dpi(self, dpi):
        self._dpi = float(dpi)
        self.update()

    def connect(self, fun):
        """Connect a function to an event

        The name of the function
        should be on_X, with X the name of the event (e.g. 'on_draw').

        This method is typically used as a decorator on a function
        definition for an event handler.

        Parameters
        ----------
        fun : callable
            The function.
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
        """The size of canvas/window."""
        # Note that _px_scale is an additional factor applied in addition to
        # the scale factor imposed by the backend.
        size = self._backend._vispy_get_size()
        return (size[0] // self._px_scale, size[1] // self._px_scale)

    @size.setter
    def size(self, size):
        return self._backend._vispy_set_size(size[0] * self._px_scale,
                                             size[1] * self._px_scale)

    @property
    def physical_size(self):
        """The physical size of the canvas/window, which may differ from the
        size property on backends that expose HiDPI.
        """
        return self._backend._vispy_get_physical_size()

    @property
    def pixel_scale(self):
        """The ratio between the number of logical pixels, or 'points', and
        the physical pixels on the device. In most cases this will be 1.0,
        but on certain backends this will be greater than 1. This should be
        used as a scaling factor when writing your own visualisations
        with gloo (make a copy and multiply all your logical pixel values
        by it). When writing Visuals or SceneGraph visualisations, this value
        is exposed as `TransformSystem.px_scale`.
        """
        return self.physical_size[0] / self.size[0]

    @property
    def fullscreen(self):
        return self._backend._vispy_get_fullscreen()

    @fullscreen.setter
    def fullscreen(self, fullscreen):
        return self._backend._vispy_set_fullscreen(fullscreen)

    # ------------------------------------------------------------ position ---
    @property
    def position(self):
        """The position of canvas/window relative to screen."""
        return self._backend._vispy_get_position()

    @position.setter
    def position(self, position):
        assert len(position) == 2
        return self._backend._vispy_set_position(position[0], position[1])

    # --------------------------------------------------------------- title ---
    @property
    def title(self):
        """The title of canvas/window."""
        return self._title

    @title.setter
    def title(self, title):
        self._title = title
        self._backend._vispy_set_title(title)

    # ----------------------------------------------------------------- fps ---
    @property
    def fps(self):
        """The fps of canvas/window, as the rate that events.draw is emitted."""
        return self._fps

    def set_current(self, event=None):
        """Make this the active GL canvas

        Parameters
        ----------
        event : None
            Not used.
        """
        self._backend._vispy_set_current()
        set_current_canvas(self)

    def swap_buffers(self, event=None):
        """Swap GL buffers such that the offscreen buffer becomes visible

        Parameters
        ----------
        event : None
            Not used.
        """
        self._backend._vispy_swap_buffers()

    def show(self, visible=True, run=False):
        """Show or hide the canvas

        Parameters
        ----------
        visible : bool
            Make the canvas visible.
        run : bool
            Run the backend event loop.
        """
        self._backend._vispy_set_visible(visible)
        if run:
            self.app.run()

    def update(self, event=None):
        """Inform the backend that the Canvas needs to be redrawn

        Parameters
        ----------
        event : None
            Not used.
        """
        if self._backend is not None:
            self._backend._vispy_update()

    def close(self):
        """Close the canvas

        Notes
        -----
        This will usually destroy the GL context. For Qt, the context
        (and widget) will be destroyed only if the widget is top-level.
        To avoid having the widget destroyed (more like standard Qt
        behavior), consider making the widget a sub-widget.
        """
        if self._backend is not None and not self._closed:
            logger.debug('Closing canvas %s' % (self,))
            self._closed = True
            self.events.close()
            self._backend._vispy_close()
        forget_canvas(self)

    def _update_fps(self, event):
        """Update the fps after every window"""
        self._frame_count += 1
        diff = time() - self._basetime
        if (diff > self._fps_window):
            self._fps = self._frame_count / diff
            self._basetime = time()
            self._frame_count = 0
            self._fps_callback(self.fps)

    def measure_fps(self, window=1, callback='%1.1f FPS'):
        """Measure the current FPS

        Sets the update window, connects the draw event to update_fps
        and sets the callback function.

        Parameters
        ----------
        window : float
            The time-window (in seconds) to calculate FPS. Default 1.0.
        callback : function | str
            The function to call with the float FPS value, or the string
            to be formatted with the fps value and then printed. The
            default is ``'%1.1f FPS'``. If callback evaluates to False, the
            FPS measurement is stopped.
        """
        # Connect update_fps function to draw
        self.events.draw.disconnect(self._update_fps)
        if callback:
            if isinstance(callback, str):
                callback_str = callback  # because callback gets overwritten

                def callback(x):
                    print(callback_str % x)

            self._fps_window = window
            self.events.draw.connect(self._update_fps)
            self._fps_callback = callback
        else:
            self._fps_callback = None

    # ---------------------------------------------------------------- misc ---
    def __repr__(self):
        return ('<%s (%s) at %s>'
                % (self.__class__.__name__,
                   self.app.backend_name, hex(id(self))))

    def _repr_mimebundle_(self, *args, **kwargs):
        """If the backend implements _repr_mimebundle_, we proxy it here.
        """
        # See https://ipython.readthedocs.io/en/stable/config/integrating.html
        f = getattr(self._backend, "_repr_mimebundle_", None)
        if f is not None:
            return f(*args, **kwargs)
        else:
            # Let Jupyter know this failed - otherwise the standard repr is not shown
            raise NotImplementedError()

    def _ipython_display_(self):
        """If the backend implements _ipython_display_, we proxy it here.
        """
        # See https://ipython.readthedocs.io/en/stable/config/integrating.html
        f = getattr(self._backend, "_ipython_display_", None)
        if f is not None:
            return f()
        else:
            # Let Jupyter know this failed - otherwise the standard repr is not shown
            raise NotImplementedError()

    def __enter__(self):
        logger.debug('Context manager enter starting for %s' % (self,))
        self.show()
        self._backend._vispy_warmup()
        return self

    def __exit__(self, type, value, traceback):
        # ensure all GL calls are complete
        logger.debug('Context manager exit starting for %s' % (self,))
        if not self._closed:
            self._backend._vispy_set_current()
            self.context.finish()
            self.close()
        sleep(0.1)  # ensure window is really closed/destroyed
        logger.debug('Context manager exit complete for %s' % (self,))

    def render(self, alpha=True):
        """Render the canvas to an offscreen buffer and return the image array.

        Parameters
        ----------
        alpha : bool
            If True (default) produce an RGBA array (M, N, 4). If False,
            remove the Alpha channel and return the RGB array (M, N, 3).
            This may be useful if blending of various elements requires a
            solid background to produce the expected visualization.

        Returns
        -------
        image : array
            Numpy array of type ubyte and shape (h, w, 4). Index [0, 0] is the
            upper-left corner of the rendered region. If ``alpha`` is ``False``,
            then only 3 channels will be returned (RGB).


        """
        self.set_current()
        size = self.physical_size
        fbo = FrameBuffer(color=RenderBuffer(size[::-1]),
                          depth=RenderBuffer(size[::-1]))

        try:
            fbo.activate()
            self.events.draw()
            result = fbo.read()
        finally:
            fbo.deactivate()

        if not alpha:
            result = result[..., :3]
        return result


# Event subclasses specific to the Canvas
class MouseEvent(Event):
    """Mouse event class

    Note that each event object has an attribute for each of the input
    arguments listed below, as well as a "time" attribute with the event's
    precision start time.

    Parameters
    ----------
    type : str
       String indicating the event type (e.g. mouse_press, key_release)
    pos : (int, int)
        The position of the mouse (in screen coordinates).
    button : int | None
        The button that generated this event (can be None).
        Left=1, right=2, middle=3. During a mouse drag, this
        will return the button that started the drag (same thing as
        ``event.press_event.button``).
    buttons : [int, ...]
        The list of buttons pressed during this event.
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
    **kwargs : keyword arguments
        All extra keyword arguments become attributes of the event object.
    """

    def __init__(self, type, pos=None, button=None, buttons=None,
                 modifiers=None, delta=None, last_event=None, press_event=None,
                 **kwargs):
        Event.__init__(self, type, **kwargs)
        self._pos = np.array([0, 0]) if (pos is None) else np.array(pos)
        self._button = int(button) if (button is not None) else None
        # Explicitly add button to buttons if newly pressed, check #2344 for more reference
        newly_pressed_buttons = [button] if button is not None and type == 'mouse_press' else []
        self._buttons = [] if (buttons is None) else buttons + newly_pressed_buttons
        self._modifiers = tuple(modifiers or ())
        self._delta = np.zeros(2) if (delta is None) else np.array(delta)
        self._last_event = last_event
        self._press_event = press_event
        self._time = time()

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

    @property
    def time(self):
        return self._time

    def _forget_last_event(self):
        # Needed to break otherwise endless last-event chains
        self._last_event = None

    @property
    def is_dragging(self):
        """Indicates whether this event is part of a mouse drag operation."""
        return self.press_event is not None

    def drag_events(self):
        """Return a list of all mouse events in the current drag operation.

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
        """Return an (N, 2) array of mouse coordinates for every event in the
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
    **kwargs : keyword arguments
        All extra keyword arguments become attributes of the event object.
    """

    def __init__(self, type, key=None, text='', modifiers=None, **kwargs):
        Event.__init__(self, type, **kwargs)
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
    """Resize event class

    Note that each event object has an attribute for each of the input
    arguments listed below.

    Parameters
    ----------
    type : str
       String indicating the event type (e.g. mouse_press, key_release)
    size : (int, int)
        The new size of the Canvas, in points (logical pixels).
    physical_size : (int, int)
        The new physical size of the Canvas, in pixels.
    native : object (optional)
       The native GUI event object
    **kwargs : extra keyword arguments
        All extra keyword arguments become attributes of the event object.
    """

    def __init__(self, type, size=None, physical_size=None, **kwargs):
        Event.__init__(self, type, **kwargs)
        self._size = tuple(size)
        if physical_size is None:
            self._physical_size = self._size
        else:
            self._physical_size = tuple(physical_size)

    @property
    def size(self):
        return self._size

    @property
    def physical_size(self):
        return self._physical_size


class DrawEvent(Event):
    """Draw event class

    This type of event is sent to Canvas.events.draw when a redraw
    is required.

    Note that each event object has an attribute for each of the input
    arguments listed below.

    Parameters
    ----------
    type : str
       String indicating the event type (e.g. mouse_press, key_release)
    region : (int, int, int, int) or None
        The region of the canvas which needs to be redrawn (x, y, w, h).
        If None, the entire canvas must be redrawn.
    native : object (optional)
       The native GUI event object
    **kwargs : extra keyword arguments
        All extra keyword arguments become attributes of the event object.
    """

    def __init__(self, type, region=None, **kwargs):
        Event.__init__(self, type, **kwargs)
        self._region = region

    @property
    def region(self):
        return self._region
