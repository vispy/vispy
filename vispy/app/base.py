# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


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

    def _vispy_reuse(self):
        # Does nothing by default.
        pass

    def _vispy_quit(self):
        raise NotImplementedError()

    def _vispy_get_native_app(self):
        # Should return the native application object
        return self


class BaseCanvasBackend(object):
    """BaseCanvasBackend(vispy_canvas, capability, context_type)

    Abstract class that provides an interface between backends and Canvas.
    Each backend must implement a subclass of CanvasBackend, and
    implement all its _vispy_xxx methods. Also, also a backend must
    make sure to generate the following events: 'initialize', 'resize',
    'draw', 'mouse_press', 'mouse_release', 'mouse_move',
    'mouse_wheel', 'key_press', 'key_release'. When a backend detects
    that the canvas should be closed, the backend should call
    'self._vispy_canvas.close', because the close event is handled within
    the canvas itself.
    """

    def __init__(self, vispy_canvas):
        from .canvas import Canvas  # Avoid circular import
        assert isinstance(vispy_canvas, Canvas)
        self._vispy_canvas = vispy_canvas

        # We set the _backend attribute of the vispy_canvas to self,
        # because at the end of the __init__ of the CanvasBackend
        # implementation there might be a call to show or draw. By
        # setting it here, we ensure that the Canvas is "ready to go".
        vispy_canvas._backend = self

        # Data used in the construction of new mouse events
        self._vispy_mouse_data = {
            'buttons': [],
            'press_event': None,
            'last_event': None,
        }

    def _process_backend_kwargs(self, kwargs):
        """ Simple utility to retrieve kwargs in predetermined order.
        Also checks whether the values of the backend arguments do not
        violate the backend capabilities.
        """
        
        # Verify given argument with capability of the backend
        app = self._vispy_canvas.app
        capability = app.backend_module.capability
        if kwargs['context'].shared.name:  # name already assigned: shared
            if not capability['context']:
                raise RuntimeError('Cannot share context with this backend')
        for key in [key for (key, val) in capability.items() if not val]:
            if key in ['context', 'multi_window', 'scroll']:
                continue
            invert = key in ['resizable', 'decorate']
            if bool(kwargs[key]) - invert:
                raise RuntimeError('Config %s is not supported by backend %s'
                                   % (key, app.backend_name))

        # Return items in sequence
        keys = ['title', 'size', 'position', 'show', 'vsync', 'resizable',
                'decorate', 'fullscreen', 'parent', 'context']
        return [kwargs[k] for k in keys]

    def _vispy_set_current(self):
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

    def _vispy_set_fullscreen(self, fullscreen):
        # Set fullscreen mode
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

    def _vispy_get_fullscreen(self):
        # Should return bool for fullscreen status
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
        else:
            kwds['button'] = self._vispy_mouse_data['press_event'].button

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
