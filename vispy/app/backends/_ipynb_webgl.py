# -*- coding: utf-8 -*-
# Copyright (c) 2014, 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Vispy backend for the IPython notebook (WebGL approach).
"""

from __future__ import division

from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend)
from ._ipynb_util import create_glir_message
from ...util import logger, keys
from ...ext import six
from vispy.gloo.glir import BaseGlirParser
from vispy.app import Timer

import os.path as op
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


# Init dummy objects needed to import this module withour errors.
# These are all overwritten with imports from IPython (on success)
DOMWidget = object
Unicode = Int = Float = Bool = lambda *args, **kwargs: None

# Try importing IPython
try:
    import tornado
    import IPython
    IPYTHON_MAJOR_VERSION = IPython.version_info[0]
    if IPYTHON_MAJOR_VERSION < 2:
        raise RuntimeError('ipynb_webgl backend requires IPython >= 2.0')
    from IPython.html.widgets import DOMWidget
    from IPython.utils.traitlets import Unicode, Int
    from IPython.html.nbextensions import install_nbextension
    from IPython.display import display
except Exception as exp:
    # raise ImportError("The WebGL backend requires IPython >= 2.0")
    available, testable, why_not, which = False, False, str(exp), None
else:
    available, testable, why_not, which = True, False, None, None


# ------------------------------------------------------------- application ---
def _prepare_js(force=False):
    pkgdir = op.dirname(__file__)
    jsdir = op.join(pkgdir, '../../html/static/js/')
    # Make sure the JS files are installed to user directory (new argument
    # in IPython 3.0).
    if IPYTHON_MAJOR_VERSION >= 3:
        kwargs = {'user': True}
    else:
        kwargs = {}
    install_nbextension(jsdir, overwrite=force, destination='vispy', symlink=True,
                        **kwargs)


class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)
        _prepare_js()

    def _vispy_reuse(self):
        _prepare_js()

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
    def __init__(self, widget):
        self._widget = widget

    def is_remote(self):
        return True

    def convert_shaders(self):
        return 'es2'

    def parse(self, commands):
        self._widget.send_glir_commands(commands)


class CanvasBackend(BaseCanvasBackend):
    # args are for BaseCanvasBackend, kwargs are for us.
    def __init__(self, *args, **kwargs):
        BaseCanvasBackend.__init__(self, *args)
        p = self._process_backend_kwargs(kwargs)
        self._context = p.context

        # TODO: do something with context.config
        # Take the context.
        p.context.shared.add_ref('webgl', self)
        if p.context.shared.ref is self:
            pass  # ok
        else:
            raise RuntimeError("WebGL doesn't yet support context sharing.")

        self._create_widget(size=p.size)

    def _create_widget(self, size=None):
        self._widget = VispyWidget(self, size=size)
        # Set glir parser on context and context.shared
        context = self._vispy_canvas.context
        context.shared.parser = WebGLGlirParser(self._widget)

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
        pass

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
        return (self._widget.width, self._widget.height)

    def _vispy_set_size(self, w, h):
        self._widget.width = w
        self._widget.height = h

    def _vispy_get_position(self):
        raise NotImplementedError()

    def _vispy_set_position(self, x, y):
        logger.warning('IPython notebook canvas cannot be repositioned.')

    def _vispy_set_visible(self, visible):
        if not visible:
            logger.warning('IPython notebook canvas cannot be hidden.')
        else:
            display(self._widget)
            self._reinit_widget()

    def _vispy_update(self):
        ioloop = tornado.ioloop.IOLoop.current()
        ioloop.add_callback(self._draw_event)

    def _draw_event(self):
        self._vispy_canvas.set_current()
        self._vispy_canvas.events.draw()

    def _vispy_close(self):
        raise NotImplementedError()

    def _vispy_mouse_release(self, **kwds):
        # HACK: override this method from the base canvas in order to
        # avoid breaking other backends.
        kwds.update(self._vispy_mouse_data)
        ev = self._vispy_canvas.events.mouse_release(**kwds)
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


# ---------------------------------------------------------- IPython Widget ---
def _stop_timers(canvas):
    """Stop all timers in a canvas."""
    for attr in dir(canvas):
        try:
            attr_obj = getattr(canvas, attr)
        except NotImplementedError:
            # This try/except is needed because canvas.position raises
            # an error (it is not implemented in this backend).
            attr_obj = None
        if isinstance(attr_obj, Timer):
            attr_obj.stop()


class VispyWidget(DOMWidget):
    _view_name = Unicode("VispyView", sync=True)
    _view_module = Unicode('/nbextensions/vispy/webgl-backend.js', sync=True)

    width = Int(sync=True)
    height = Int(sync=True)

    def __init__(self, canvas_backend, **kwargs):
        super(VispyWidget, self).__init__(**kwargs)
        w, h = kwargs.get('size', (500, 200))
        self.width = w
        self.height = h
        self.canvas_backend = canvas_backend
        self.gen_event = canvas_backend._gen_event
        self.on_msg(self.events_received)

    def events_received(self, _, msg):
        if msg['msg_type'] == 'events':
            events = msg['contents']
            for ev in events:
                self.gen_event(ev)
        elif msg['msg_type'] == 'status':
            if msg['contents'] == 'removed':
                # Stop all timers associated to the widget.
                _stop_timers(self.canvas_backend._vispy_canvas)

    def send_glir_commands(self, commands):
        # TODO: check whether binary websocket is available (ipython >= 3)
        # Until IPython 3.0 is released, use base64.
        array_serialization = 'base64'
        # array_serialization = 'binary'
        if array_serialization == 'base64':
            msg = create_glir_message(commands, 'base64')
            msg['array_serialization'] = 'base64'
            self.send(msg)
        elif array_serialization == 'binary':
            msg = create_glir_message(commands, 'binary')
            msg['array_serialization'] = 'binary'
            # Remove the buffers from the JSON message: they will be sent
            # independently via binary WebSocket.
            buffers = msg.pop('buffers')
            self.comm.send({"method": "custom", "content": msg},
                           buffers=buffers)
