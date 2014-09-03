# -*- coding: utf-8 -*-

from inspect import getargspec
from copy import deepcopy

from ._config import get_default_config


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
        self._vispy_canvas = vispy_canvas

        # Data used in the construction of new mouse events
        self._vispy_mouse_data = {
            'buttons': [],
            'press_event': None,
            'last_event': None,
        }

    def _process_backend_kwargs(self, kwargs):
        """Removes vispy-specific kwargs for CanvasBackend"""
        # these are the output arguments
        keys = ['title', 'size', 'position', 'show', 'vsync', 'resizable',
                'decorate', 'fullscreen', 'parent']
        from .canvas import Canvas
        outs = []
        spec = getargspec(Canvas.__init__)
        capability = self._vispy_canvas.app.backend_module.capability
        for key in keys:
            default = spec.defaults[spec.args.index(key) - 1]
            out = kwargs.get(key, default)
            if out != default and capability[key] is False:
                raise RuntimeError('Cannot set property %s using this '
                                   'backend' % key)
            outs.append(out)
    
        # todo: can we just move this context relates stuff to canvas
        # and begone with this method?
        # Ensure that context is a GLContext instance
        context = kwargs.get('context', GLContext())
        if isinstance(context, dict):
            context = GLContext(context=deepcopy(context))
        elif isinstance(context, GLContext):
            if not capability['context']:
                raise RuntimeError('Cannot share context with this backend')
        else:
            raise TypeError('context must be a dict or GLContext from '
                            'a Canvas with the same backend, not %s'
                            % type(context))
        
        # Ensure that the context has all the right fields
        default_config = get_default_config()
        # first, fill in context with any missing entries
        config = context.config
        for key, val in default_config.items():
            config[key] = config.get(key, default_config[key])
        # now make sure everything is of the proper type
        for key, val in config.items():
            if key not in default_config:
                raise KeyError('context.config has unknown key %s' % key)
            needed = type(default_config[key])
            if not isinstance(val, needed):
                raise TypeError('context.config["%s"] is of incorrect type (got '
                                '%s need %s)' % (key, type(val), needed))
        
        # Finalize outs and return
        outs.append(context)
        return outs

    def _vispy_init(self):
        # For any __init__-like actions that must occur *after*
        # self._vispy_canvas._backend is not None

        # Most backends won't need this. However, there are exceptions.
        # e.g., pyqt4 with show=True, "show" can't be done until this property
        # exists because it might call on_draw which might in turn call
        # canvas.size... which relies on canvas._backend being set.
        pass

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


# todo:  XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# get rid of SharedContext and _vispy_shared_context _vispy_capability
class GLContext(object):
    """An object encapsulating data necessary for a shared OpenGL context

    The data are backend dependent.
    """
    
    def __init__(self, context=None):
        self._value = None  # Used by vispy.app to store a ref
        self._backend = None  # Used by vispy.app to say what backend owns it
        self._config = context or {}  # Used by vispy.app to set context config
    
    def take(self, backend, value):
        if self._value is not None:
            raise RuntimeError('This GLContext is already owned.')
        self._backend = str(backend)
        self._value = value
    
    @property
    def istaken(self):
        return self._value is not None
    
    @property
    def value(self):
        return self._value
    
    @property
    def backend(self):
        return self._backend
    
    @property
    def config(self):
        return self._config
    
    def __repr__(self):
        backend = self._backend or 'no'
        return "<GLContext of %s backend at 0x%x>" % (backend, id(self))
