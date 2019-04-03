# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Vispy backend for the IPython notebook (WebGL approach).
"""

from __future__ import division

from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend)
from ...util import logger, keys
from ...ext import six
from ...gloo.glir import BaseGlirParser, convert_shader
from ...app.backends.ipython import VispyWidget

# -------------------------------------------------------------------- init ---

capability = dict(  # things that can be set by the backend
    title=True,  # But it only applies to the dummy window :P
    size=True,  # We cannot possibly say we dont, because Canvas always sets it
    position=True,  # Dito
    show=True,
    vsync=False,
    resizable=True,
    decorate=False,
    fullscreen=True,
    context=True,
    multi_window=False,
    scroll=True,
    parent=False,
    always_on_top=False,
)

# Try importing IPython
try:
    import tornado
    from IPython.display import display
except Exception as exp:
    # raise ImportError("The WebGL backend requires IPython >= 2.0")
    available, testable, why_not, which = False, False, str(exp), None
else:
    available, testable, why_not, which = True, False, None, None


class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)

    def _vispy_reuse(self):
        pass

    def _vispy_get_backend_name(self):
        return 'ipynb_webgl'

    def _vispy_process_events(self):
        # TODO: may be implemented later.
        raise NotImplementedError()

    def _vispy_run(self):
        pass

    def _vispy_quit(self):
        pass

    def _vispy_get_native_app(self):
        return self


# ------------------------------------------------------------------ canvas ---
class WebGLGlirParser(BaseGlirParser):
    def __init__(self, widget=None):
        super(WebGLGlirParser, self).__init__()
        self._widget = widget

    def set_widget(self, widget):
        self._widget = widget

    def is_remote(self):
        return True

    @property
    def shader_compatibility(self):
        return 'es2'

    def parse(self, commands):
        new_commands = []
        # Convert shaders
        for c in commands:
            if c[0] == 'DATA' and isinstance(c[3], str):
                # shader source code
                c = c[:3] + (convert_shader('es2', c[3]),)
            new_commands.append(c)
        if new_commands:
            self._widget.send_glir_commands(new_commands)


class CanvasBackend(BaseCanvasBackend):
    # args are for BaseCanvasBackend, kwargs are for us.
    def __init__(self, *args, **kwargs):
        BaseCanvasBackend.__init__(self, *args)
        self._widget = None

        p = self._process_backend_kwargs(kwargs)
        self._context = p.context

        # TODO: do something with context.config
        # Take the context.
        p.context.shared.add_ref('webgl', self)
        if p.context.shared.ref is self:
            pass  # ok
        else:
            raise RuntimeError("WebGL doesn't yet support context sharing.")

        #store a default size before the widget is available.
        #then we set the default size on the widget and only use the
        #widget size
        self._default_size = p.size
        self._init_glir()

    def set_widget(self, widget):
        self._widget = widget
        self._vispy_canvas.context.shared.parser.set_widget(widget)

    def _init_glir(self):
        context = self._vispy_canvas.context
        context.shared.parser = WebGLGlirParser()

    def _reinit_widget(self):
        self._vispy_canvas.set_current()

        self._vispy_canvas.events.initialize()
        self._vispy_canvas.events.resize(size=(self._widget.width,
                                               self._widget.height))
        self._vispy_canvas.events.draw()

    def _vispy_warmup(self):
        pass

    # Uncommenting these makes the backend crash.
    def _vispy_set_current(self):
        pass

    def _vispy_swap_buffers(self):
        if self._vispy_canvas is None:
            return
        # Send frontend a special "you're allowed to swap buffers now" command
        context = self._vispy_canvas.context
        context.shared.parser.parse([('SWAP',)])

    def _vispy_set_title(self, title):
        raise NotImplementedError()

    def _vispy_get_fullscreen(self):
        # We don't want error messages to show up when the user presses
        # F11 to fullscreen the browser.
        pass

    def _vispy_set_fullscreen(self, fullscreen):
        # We don't want error messages to show up when the user presses
        # F11 to fullscreen the browser.
        pass

    def _vispy_get_size(self):
        if self._widget:
            return (self._widget.width, self._widget.height)
        else:
            return self._default_size

    def _vispy_set_size(self, w, h):
        if self._widget:
            self._widget.width = w
            self._widget.height = h
        else:
            self._default_size = (w, h)

    def _vispy_get_position(self):
        raise NotImplementedError()

    def _vispy_set_position(self, x, y):
        logger.warning('IPython notebook canvas cannot be repositioned.')

    def _vispy_set_visible(self, visible):
        if not visible:
            logger.warning('IPython notebook canvas cannot be hidden.')
            return
        if self._widget is None:
            self._widget = VispyWidget()
            self._widget.set_canvas(self._vispy_canvas)
        display(self._widget)

    def _vispy_update(self):
        ioloop = tornado.ioloop.IOLoop.current()
        ioloop.add_callback(self._draw_event)

    def _draw_event(self):
        self._vispy_canvas.set_current()
        self._vispy_canvas.events.draw()

    def _vispy_close(self):
        raise NotImplementedError()

    def _vispy_mouse_release(self, **kwargs):
        # HACK: override this method from the base canvas in order to
        # avoid breaking other backends.
        kwargs.update(self._vispy_mouse_data)
        ev = self._vispy_canvas.events.mouse_release(**kwargs)
        if ev is None:
            return
        self._vispy_mouse_data['press_event'] = None
        # TODO: this is a bit ugly, need to improve mouse button handling in
        # app
        ev._button = None
        self._vispy_mouse_data['buttons'] = []
        self._vispy_mouse_data['last_event'] = ev
        return ev

    # Generate vispy events according to upcoming JS events
    _modifiers_map = {
        'ctrl': keys.CONTROL,
        'shift': keys.SHIFT,
        'alt': keys.ALT,
    }

    def _gen_event(self, ev):
        if self._vispy_canvas is None:
            return
        event_type = ev['type']
        key_code = ev.get('key_code', None)
        if key_code is None:
            key, key_text = None, None
        else:
            if hasattr(keys, key_code):
                key = getattr(keys, key_code)
            else:
                key = keys.Key(key_code)
            # Generate the key text to pass to the event handler.
            if key_code == 'SPACE':
                key_text = ' '
            else:
                key_text = six.text_type(key_code)
        # Process modifiers.
        modifiers = ev.get('modifiers', None)
        if modifiers:
            modifiers = tuple([self._modifiers_map[modifier]
                               for modifier in modifiers
                               if modifier in self._modifiers_map])
        if event_type == "mouse_move":
            self._vispy_mouse_move(native=ev,
                                   button=ev["button"],
                                   pos=ev["pos"],
                                   modifiers=modifiers,
                                   )
        elif event_type == "mouse_press":
            self._vispy_mouse_press(native=ev,
                                    pos=ev["pos"],
                                    button=ev["button"],
                                    modifiers=modifiers,
                                    )
        elif event_type == "mouse_release":
            self._vispy_mouse_release(native=ev,
                                      pos=ev["pos"],
                                      button=ev["button"],
                                      modifiers=modifiers,
                                      )
        elif event_type == "mouse_wheel":
            self._vispy_canvas.events.mouse_wheel(native=ev,
                                                  delta=ev["delta"],
                                                  pos=ev["pos"],
                                                  button=ev["button"],
                                                  modifiers=modifiers,
                                                  )
        elif event_type == "key_press":
            self._vispy_canvas.events.key_press(native=ev,
                                                key=key,
                                                text=key_text,
                                                modifiers=modifiers,
                                                )
        elif event_type == "key_release":
            self._vispy_canvas.events.key_release(native=ev,
                                                  key=key,
                                                  text=key_text,
                                                  modifiers=modifiers,
                                                  )
        elif event_type == "resize":
            self._vispy_canvas.events.resize(native=ev,
                                             size=ev["size"])
        elif event_type == "paint":
            self._vispy_canvas.events.draw()


# ------------------------------------------------------------------- Timer ---
class TimerBackend(BaseTimerBackend):
    def __init__(self, *args, **kwargs):
        super(TimerBackend, self).__init__(*args, **kwargs)
        self._timer = tornado.ioloop.PeriodicCallback(
            self._vispy_timer._timeout,
            1000)

    def _vispy_start(self, interval):
        self._timer.callback_time = interval * 1000
        self._timer.start()

    def _vispy_stop(self):
        self._timer.stop()
