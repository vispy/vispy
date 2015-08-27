# -*- coding: utf-8 -*-
# vispy: testskip
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
OSMesa backend for offscreen rendering on Linux/Unix
"""
# -------------------------------------------------------------- capability ---
capability = dict(
    # if True they mean:
    title=True,          # can set title on the fly
    size=True,           # can set size on the fly
    position=False,       # can set position on the fly
    show=False,           # can show/hide window XXX ?
    vsync=False,          # can set window to sync to blank
    resizable=False,      # can toggle resizability (e.g., no user resizing)
    decorate=False,       # can toggle decorations
    fullscreen=False,     # fullscreen window support
    context=False,        # can share contexts between windows
    multi_window=False,   # can use multiple windows at once
    scroll=False,         # scroll-wheel events are supported
    parent=False,         # can pass native widget backend parent
    always_on_top=False,  # can be made always-on-top
)

# ------------------------------------------------------- set_configuration ---
def _set_config(c):
    """Set the OpenGL configuration"""
    glformat = QGLFormat()
    glformat.setRedBufferSize(c['red_size'])
    glformat.setGreenBufferSize(c['green_size'])
    glformat.setBlueBufferSize(c['blue_size'])
    glformat.setAlphaBufferSize(c['alpha_size'])
    glformat.setAccum(False)
    glformat.setRgba(True)
    glformat.setDoubleBuffer(True if c['double_buffer'] else False)
    glformat.setDepth(True if c['depth_size'] else False)
    glformat.setDepthBufferSize(c['depth_size'] if c['depth_size'] else 0)
    glformat.setStencil(True if c['stencil_size'] else False)
    glformat.setStencilBufferSize(c['stencil_size'] if c['stencil_size']
                                  else 0)
    glformat.setSampleBuffers(True if c['samples'] else False)
    glformat.setSamples(c['samples'] if c['samples'] else 0)
    glformat.setStereo(c['stereo'])
    return glformat


# ------------------------------------------------------------- application ---
class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)

    def _vispy_get_backend_name(self):
        return 'osmesa'

    def _vispy_process_events(self):
        pass

    def _vispy_run(self):
        pass

    def _vispy_quit(self):
        pass

    def _vispy_get_native_app(self):
        pass

# ------------------------------------------------------------------ canvas ---

class CanvasBackend(BaseCanvasBackend):
    """OSMesa backend for Canvas"""
    # TODO: For now, this is copied from _template

    # args are for BaseCanvasBackend, kwargs are for us.
    def __init__(self, *args, **kwargs):
        BaseCanvasBackend.__init__(self, *args)
        # We use _process_backend_kwargs() to "serialize" the kwargs
        # and to check whether they match this backend's capability
        p = self._process_backend_kwargs(kwargs)

        # Deal with config
        # ... use context.config
        # Deal with context
        p.context.shared.add_ref('backend-name', self)
        if p.context.shared.ref is self:
            self._native_context = None  # ...
        else:
            self._native_context = p.context.shared.ref._native_context

        # NativeWidgetClass.__init__(self, foo, bar)

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
        # Set the current fullscreen state
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
        # Should return the current fullscreen state
        raise NotImplementedError()

    def _vispy_get_native_canvas(self):
        # Should return the native widget object.
        # If this is self, this method can be omitted.
        return self


