# -*- coding: utf-8 -*-


class BaseApplicationBackend(object):
    """BaseApplicationBackend()

    Abstract class that provides an interface between backends and Application.
    Each backend must implement a subclass of ApplicationBackend, and
    implement all its _vispy_xxx methods.
    """

    def _vispy_get_backend_name(self):
        raise NotImplementedError()

    def _vispy_process_events(self):
        raise NotImplementedError()

    def _vispy_run(self):
        raise NotImplementedError()

    def _vispy_quit(self):
        raise NotImplementedError()

    def _vispy_get_native_app(self):
        # Should return the native application object
        return self


class BaseCanvasBackend(object):
    """BaseCanvasBackend(vispy_canvas, *args, **kwargs)

    Abstract class that provides an interface between backends and Canvas.
    Each backend must implement a subclass of CanvasBackend, and
    implement all its _vispy_xxx methods. Also, also a backend must
    make sure to generate the following events: 'initialize', 'resize',
    'paint', 'mouse_press', 'mouse_release', 'mouse_move',
    'mouse_wheel', 'key_press', 'key_release', 'close'.
    """

    def __init__(self, *args, **kwargs):
        # Initially the backend starts out with no canvas.
        # Canvas takes care of setting this for us.
        self._vispy_canvas = None

        # Data used in the construction of new mouse events
        self._vispy_mouse_data = {
            'buttons': [],
            'press_event': None,
            'last_event': None,
        }

    def _vispy_set_current(self):
        # todo: this is currently not used internally
        # --> I think the backends should call this themselves before
        #     emitting the paint event
        # Make this the current context
        raise NotImplementedError()

    def _vispy_swap_buffers(self):
        # Swap front and back buffer
        raise NotImplementedError()

    def _vispy_set_title(self, title):
        # Set the window title. Has no effect for widgets
        raise NotImplementedError()

    def _vispy_set_size(self, w, h):
        # Set size of the widget or window
        raise NotImplementedError()

    def _vispy_set_position(self, x, y):
        # Set location of the widget or window. May have no effect for widgets
        raise NotImplementedError()

    def _vispy_set_visible(self, visible):
        # Show or hide the window or widget
        raise NotImplementedError()

    def _vispy_update(self):
        # Invoke a redraw
        raise NotImplementedError()

    def _vispy_close(self):
        # Force the window or widget to shut down
        raise NotImplementedError()

    def _vispy_get_size(self):
        # Should return widget size
        raise NotImplementedError()

    def _vispy_get_position(self):
        # Should return widget position
        raise NotImplementedError()

    def _vispy_get_geometry(self):
        # Should return widget (x, y, w, h)
        x, y = self._vispy_get_position()
        w, h = self._vispy_get_size()
        return x, y, w, h

    def _vispy_get_native_canvas(self):
        # Should return the native widget object
        # Most backends would not need to implement this
        return self

    def _vispy_mouse_press(self, **kwds):
        # default method for delivering mouse press events to the canvas
        kwds.update(self._vispy_mouse_data)
        ev = self._vispy_canvas.events.mouse_press(**kwds)
        if self._vispy_mouse_data['press_event'] is None:
            self._vispy_mouse_data['press_event'] = ev

        self._vispy_mouse_data['buttons'].append(ev.button)
        self._vispy_mouse_data['last_event'] = ev
        return ev

    def _vispy_mouse_move(self, **kwds):
        # default method for delivering mouse move events to the canvas
        kwds.update(self._vispy_mouse_data)

        # Break the chain of prior mouse events if no buttons are pressed
        # (this means that during a mouse drag, we have full access to every
        # move event generated since the drag started)
        if self._vispy_mouse_data['press_event'] is None:
            last_event = self._vispy_mouse_data['last_event']
            if last_event is not None:
                last_event._forget_last_event()

        ev = self._vispy_canvas.events.mouse_move(**kwds)
        self._vispy_mouse_data['last_event'] = ev
        return ev

    def _vispy_mouse_release(self, **kwds):
        # default method for delivering mouse release events to the canvas
        kwds.update(self._vispy_mouse_data)
        ev = self._vispy_canvas.events.mouse_release(**kwds)
        if ev.button == self._vispy_mouse_data['press_event'].button:
            self._vispy_mouse_data['press_event'] = None

        self._vispy_mouse_data['buttons'].remove(ev.button)
        self._vispy_mouse_data['last_event'] = ev
        return ev


class BaseTimerBackend(object):
    """BaseTimerBackend(vispy_timer)

    Abstract class that provides an interface between backends and Timer.
    Each backend must implement a subclass of TimerBackend, and
    implement all its _vispy_xxx methods.
    """

    def __init__(self, vispy_timer):
        self._vispy_timer = vispy_timer

    def _vispy_start(self, interval):
        raise NotImplementedError

    def _vispy_stop(self):
        raise NotImplementedError

    def _vispy_get_native_timer(self):
        # Should return the native timer object
        # Most backends would not need to implement this
        return self
