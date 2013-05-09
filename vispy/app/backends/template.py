""" This module provides an template for creating backends for vispy.
It clearly indicates what methods should be implemented and what events
should be emitted.
"""

import vispy
from vispy import app
from vispy import keys

# Map native keys to vispy keys
KEYMAP = {
    -1: keys.SHIFT,
    -1: keys.CONTROL,
    -1: keys.ALT,
    
    -1: keys.LEFT,
    -1: keys.UP,
    -1: keys.RIGHT,
    -1: keys.DOWN,
    -1: keys.PAGEUP,
    -1: keys.PAGEDOWN,
    -1: keys.ESCAPE,
    -1: keys.DELETE,
    -1: keys.BACKSPACE,
    
    -1: keys.SPACE,
    -1: keys.ENTER,
}



class ApplicationBackend(app.ApplicationBackend):
    
    def __init__(self):
        app.ApplicationBackend.__init__(self)
    
    def _vispy_get_backend_name(self):
        return 'ThisBackendsName' 
    
    def _vispy_process_events(self):
        raise NotImplementedError()
    
    def _vispy_run(self):
        raise NotImplementedError()
    
    def _vispy_quit(self):
        raise NotImplementedError()
    
    def _vispy_get_native_app(self):
        raise NotImplementedError()



class CanvasBackend(app.CanvasBackend):  # You can mix this class with the native widget
    
    def __init__(self, vispy_canvas, *args, **kwargs):
        #NativeWidgetClass.__init__(self, *args, **kwargs)
        app.CanvasBackend.__init__(self, vispy_canvas)
    
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
    
    def _vispy_set_location(self, x, y):
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
    
    def _vispy_get_geometry(self):
        # Should return widget (x, y, w, h)
        raise NotImplementedError()
    
    def _vispy_get_native_canvas(self):
        # Should return the native widget object.
        # If this is self, this method can be omitted.
        return self
    
    
    def events_to_emit(self):
        """ Shown here in one method, but most backends will probably
        have one method for each event.
        """
        if self._vispy_canvas is None:
            return
        
        self._vispy_canvas.events.initialize()
        self._vispy_canvas.events.resize(size=(w,h)) # todo: new event?
        self._vispy_canvas.events.paint()  # todo: has region attribute?
        
        self._vispy_canvas.events.mouse_press(pos=(x, y), button=1, modifiers=())
        self._vispy_canvas.events.mouse_release(pos=(x, y), button=1, modifiers=())
        self._vispy_canvas.events.mouse_move(pos=(x, y), modifiers=())
        self._vispy_canvas.events.mouse_wheel(pos=(x, y), delta=1, modifiers=()) 
        # todo: what should delta be, follow qt?
        
        self._vispy_canvas.events.key_press(key=key, text=text, modifiers=())
        self._vispy_canvas.events.key_release(key=key, text=text, modifiers=())



class TimerBackend(app.TimerBackend):  # Can be mixed with native timer class
    def __init__(self, vispy_timer):
        app.TimerBackend.__init__(self, vispy_timer)
    
    def _vispy_start(self, interval):
        raise NotImplementedError()
    
    def _vispy_stop(self):
        raise NotImplementedError()
    
    def _vispy_timeout(self):
        raise NotImplementedError()
    
    def _vispy_get_native_timer(self):
        # Should return the native widget object.
        # If this is self, this method can be omitted.
        return self
