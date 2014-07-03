# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
vispy backend for the IPython notebook (vnc approach).

We aim to have:
* ipynb_static - export visualization to a static notebook
* ipynb_vnc - vnc-approach: render in Python, send result to JS as png
* ipynb_webgl - send gl commands to JS and execute in webgl context

"""

from __future__ import division

from ..base import (BaseApplicationBackend, BaseCanvasBackend, 
                    BaseTimerBackend)
from .. import Application, Canvas
from ...util import logger


# -------------------------------------------------------------------- init ---

capability = dict(  # things that can be set by the backend
    title=True,  # But it only applies to the dummy window :P
    size=True,  # We cannot possibly say we dont, because Canvas always sets it
    position=True,  # Dito
    show=True,  # Note: we don't alow this, but all scripts call show ...
    vsync=False,
    resizable=True,  # Yes, you can set to not be resizable (it always is)
    decorate=False,
    fullscreen=False,
    context=True,
    multi_window=True,
    scroll=True,
    parent=False,
)


def _set_config(c):
    _app.backend_module._set_config(c)


# Create our "backend" backend; The toolkit that is going to provide a
# canvas (e.g. OpenGL context) so we can render images.
# Note that if IPython has already loaded a GUI backend, vispy is
# probably going to use that as well, because it prefers loaded backends.
try:
    # Explicitly use default (avoid using test-app)
    _app = Application('default')
    if 'glut' in _app.backend_module.__name__:
        _msg = 'ipynb_vnc backend refuses to work with GLUT'
        available, testable, why_not = False, False, _msg
except RuntimeError:
    _msg = 'ipynb_vnc backend relies on a core backend'
    available, testable, why_not = False, False, _msg
else:
    available, testable, why_not = True, True, None
    
    # Use that backend's shared context
    KEYMAP = _app.backend_module.KEYMAP
    SharedContext = _app.backend_module.SharedContext


# ------------------------------------------------------------- application ---

# todo: maybe trigger something in JS on any of these methods?
class ApplicationBackend(BaseApplicationBackend):
    
    def __init__(self):
        BaseApplicationBackend.__init__(self)
        self._backend2 = _app._backend
    
    def _vispy_get_backend_name(self):
        realname = self._backend2._vispy_get_backend_name()
        return 'ipynb_vnc (via %s)' % realname

    def _vispy_process_events(self):
        return self._backend2._vispy_process_events()

    def _vispy_run(self):
        return self._backend2._vispy_run()

    def _vispy_quit(self):
        return self._backend2._vispy_quit()

    def _vispy_get_native_app(self):
        return self._backend2._vispy_get_native_app()


# ------------------------------------------------------------------ canvas ---

class CanvasBackend(BaseCanvasBackend):
    
    def __init__(self, *args, **kwargs):
        BaseCanvasBackend.__init__(self, capability, SharedContext)
     
        # Test kwargs
#         if kwargs['size']:
#             raise RuntimeError('ipynb_vnc Canvas is not resizable')
#         if kwargs['position']:
#             raise RuntimeError('ipynb_vnc Canvas is not positionable')
        if not kwargs['decorate']:
            raise RuntimeError('ipynb_vnc Canvas is not decoratable (or not)')
        if kwargs['vsync']:
            raise RuntimeError('ipynb_vnc Canvas does not support vsync')
        if kwargs['fullscreen']:
            raise RuntimeError('ipynb_vnc Canvas does not support fullscreen')
        
        # Create real canvas. It is a backend to this backend
        kwargs['autoswap'] = False
        canvas = Canvas(app=_app, **kwargs)
        self._backend2 = canvas.native
        
        # Connect to events of canvas to keep up to date with size and draws
        canvas.events.draw.connect(self._on_draw)
        canvas.events.resize.connect(self._on_resize)
        self._initialized = False
        
        # Show the widget
        canvas.show()
        # todo: hide that canvas
    
    @property
    def _vispy_context(self):
        """Context to return for sharing"""
        return self._backend2._vispy_context

    def _vispy_warmup(self):
        return self._backend2._vispy_warmup()

    def _vispy_set_current(self):
        return self._backend2._vispy_set_current()

    def _vispy_swap_buffers(self):
        return self._backend2._vispy_swap_buffers()

    def _vispy_set_title(self, title):
        return self._backend2._vispy_set_title(title)
        #logger.warn('IPython notebook canvas has not title.')

    def _vispy_set_size(self, w, h):
        #return self._backend2._vispy_set_size(w, h)
        logger.warn('IPython notebook canvas cannot be resized.')

    def _vispy_set_position(self, x, y):
        logger.warn('IPython notebook canvas cannot be repositioned.')

    def _vispy_set_visible(self, visible):
        #self._backend2._vispy_set_visible(visible)
        if not visible:
            logger.warn('IPython notebook canvas cannot be hidden.')

    def _vispy_update(self):
        return self._backend2._vispy_update()

    def _vispy_close(self):
        return self._backend2._vispy_close()
        # todo: can we close on IPython side?

    def _vispy_get_position(self):
        return 0, 0

    def _vispy_get_size(self):
        return self._backend2._vispy_get_size()
    
    def _on_resize(self, event=None):
        # Event handler that is called by the underlying canvas
        if self._vispy_canvas is None:
            return
        size = self._backend2._vispy_get_size()
        self._vispy_canvas.events.resize(size=size)
    
    def _on_draw(self, event=None):
        # Event handler that is called by the underlying canvas
        if self._vispy_canvas is None:
            return
        # Handle initialization
        if not self._initialized:
            self._initialized = True
            self._vispy_canvas.events.initialize()
            self._on_resize()
        # Normal behavior
        self._vispy_set_current()
        self._vispy_canvas.events.draw(region=None)
        # todo: send screenshot to js
    
    def _get_events_from_js(self):
        pass
        # todo: implement this
        # Below are the events that you want to inject into vispy
#         self._vispy_canvas.events.resize(size=(w, h))
#         self._vispy_canvas.events.close()
#         self._keyEvent(self._vispy_canvas.events.key_press, ev)
#         self._keyEvent(self._vispy_canvas.events.key_release, ev)
#         
#         self._vispy_mouse_press(native=ev,
#             pos=(ev.pos().x(), ev.pos().y()),
#             button=BUTTONMAP.get(ev.button(), 0),
#             modifiers = self._modifiers(ev),
#             )
# 
#         self._vispy_mouse_release(
#             native=ev,
#             pos=(ev.pos().x(), ev.pos().y()),
#             button=BUTTONMAP[ev.button()],
#             modifiers = self._modifiers(ev),
#             )
#         
#         self._vispy_mouse_move(
#             native=ev,
#             pos=(ev.pos().x(), ev.pos().y()),
#             modifiers=self._modifiers(ev),
#             )
#         
#         self._vispy_canvas.events.mouse_wheel(
#             native=ev,
#             delta=(deltax, deltay),
#             pos=(ev.pos().x(), ev.pos().y()),
#             modifiers=self._modifiers(ev),
#             )


# ------------------------------------------------------------------- timer ---

class TimerBackend(BaseTimerBackend):

    def __init__(self, vispy_timer):
        self._backend2 = _app.backend_module.TimerBackend(vispy_timer)

    def _vispy_start(self, interval):
        return self._backend2._vispy_start(interval)

    def _vispy_stop(self):
        return self._backend2._vispy_stop()

    def _vispy_timeout(self):
        return self._backend2._vispy_timeout()
