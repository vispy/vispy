# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
vispy backend for the IPython notebook (static approach).

We aim to have:
* ipynb_static - export visualization to a static notebook
* ipynb_vnc - vnc-approach: render in Python, send result to JS as png
* ipynb_webgl - send gl commands to JS and execute in webgl context

"""

from __future__ import division

from ..base import BaseApplicationBackend, BaseCanvasBackend
from .. import Application, Canvas
from ...util import logger

# Imports for screenshot
from ...gloo.util import _screenshot
from ...io import _make_png
from base64 import b64encode

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
    always_on_top=False,
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
except Exception:
    _msg = 'ipynb_static backend relies on a core backend'
    available, testable, why_not, which = False, False, _msg, None
else:
    # Try importing IPython
    try:
        from IPython.display import display_png
    except Exception as exp:
        available, testable, why_not, which = False, False, str(exp), None
    else:
        available, testable, why_not = True, False, None
        which = _app.backend_module.which

    # Use that backend's shared context
    KEYMAP = _app.backend_module.KEYMAP


# ------------------------------------------------------------- application ---

# todo: maybe trigger something in JS on any of these methods?
class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)
        self._backend2 = _app._backend

    def _vispy_get_backend_name(self):
        realname = self._backend2._vispy_get_backend_name()
        return 'ipynb_static (via %s)' % realname

    def _vispy_process_events(self):
        return self._backend2._vispy_process_events()

    def _vispy_run(self):
        pass  # We run in IPython, so we don't run!
        #return self._backend2._vispy_run()

    def _vispy_quit(self):
        return self._backend2._vispy_quit()

    def _vispy_get_native_app(self):
        return self._backend2._vispy_get_native_app()


# ------------------------------------------------------------------ canvas ---

class CanvasBackend(BaseCanvasBackend):

    # args are for BaseCanvasBackend, kwargs are for us.
    def __init__(self, *args, **kwargs):
        BaseCanvasBackend.__init__(self, *args)
        self._initialized = False

        # Test kwargs
#         if kwargs['position']:
#             raise RuntimeError('ipynb_static Canvas is not positionable')
        if not kwargs['decorate']:
            raise RuntimeError('ipynb_static Canvas is not decoratable')
        if kwargs['vsync']:
            raise RuntimeError('ipynb_static Canvas does not support vsync')
        if kwargs['fullscreen']:
            raise RuntimeError('ipynb_static Canvas does not support '
                               'fullscreen')

        # Create real canvas. It is a backend to this backend
        kwargs.pop('vispy_canvas', None)
        kwargs['autoswap'] = False
        canvas = Canvas(app=_app, **kwargs)  # Pass kwargs to underlying canvas
        self._backend2 = canvas.native

        # Connect to events of canvas to keep up to date with size and draw
        canvas.events.draw.connect(self._on_draw)
        canvas.events.resize.connect(self._on_resize)
        
        # Show the widget
        canvas.show()
        # todo: hide that canvas

        # Raw PNG that will be displayed on canvas.show()
        self._im = ""

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
        return self._backend2._vispy_set_size(w, h)

    def _vispy_set_position(self, x, y):
        logger.warn('IPython notebook canvas cannot be repositioned.')

    def _vispy_set_visible(self, visible):
        #self._backend2._vispy_set_visible(visible)
        if not visible:
            logger.warn('IPython notebook canvas cannot be hidden.')
        else:
            self._vispy_update()
            self._vispy_canvas.app.process_events()
            self._vispy_close()
            display_png(self._im, raw=True)

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
        self._vispy_canvas.set_current()
        self._vispy_canvas.events.draw(region=None)

        # Generate base64 encoded PNG string
        self._gen_png()

    def _gen_png(self):
        # Take the screenshot
        screenshot = _screenshot()
        # Convert to PNG
        png = _make_png(screenshot)
        # Encode base64
        self._im = b64encode(png)
