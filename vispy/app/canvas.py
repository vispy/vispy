# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

from vispy.event import EmitterGroup
import vispy

# todo: add functions for asking about current mouse/keyboard state
# todo: add hover enter/exit events

class Canvas(object):
    """ Canvas(*args, **kwargs)
    
    Representation of a GUI element that can be rendered to by an OpenGL
    context. The args and kwargs are used to instantiate the native widget.
    
    Further, there are two special keyword arguments:
      * app: an vispy Application instance (vispy.app is used by default)
      * create_widget: a bool that indicates whether to create the
        widget immediately (default True)
    
    Receives the following events:
    initialize, resize, paint, mouse, key, stylus, touch, close
    """
    
    def __init__(self, *args, **kwargs):
        self.events = EmitterGroup(source=self, 
                        event_names=['initialize', 'resize', 'paint',
                        'mouse_press', 'mouse_release', 'mouse_move', 
                        'mouse_wheel',
                        'key_press', 'key_release', 'stylus', 'touch', 'close'])
        
        # Store input and initialize backend attribute
        self._args = args
        self._kwargs = kwargs
        self.backend = None
        
        # todo: make backend available via a property?
        # todo: rename backend to 'native' or 'widget' or keep 'backend'?
        
        # Initialise some values
        self._title = ''
        
        # Get app instance 
        self._app = kwargs.pop('app', vispy.app.default_app)
        
        # Create widget now
        if kwargs.pop('create_widget', True):
            self.create_widget()
    
    
    def create_widget(self):
        # todo: perhaps rename this to 'create_native'?
        """ Create the native widget if not already done so. If the widget
        is already created, this function does nothing.
        """
        if self.backend is None:
            # Make sure that the app is active
            self._app.use()
            self._app.native
            # Instantiate the backed with the right class
            self.backend = self._app.backend_module.CanvasBackend(self, *self._args, **self._kwargs)
            # Clean up
            del self._args 
            del self._kwargs
    
    
    @property
    def app(self):
        """ The vispy Application instance on which this Canvas is based.
        """
        return self._app
    
    
    @property
    def geometry(self):
        """ Get or set the location and size of the Canvas in window
        coordinates (x, y, width, height). When setting, width and
        height may be omitted. Similarly, specifying None for x and y
        will prevent the widget from being moved.
        """
        return self.backend._vispy_get_geometry()
    
    @geometry.setter
    def geometry(self, args):
        if len(args) == 2:
            self.backend._vispy_set_location(*args)
        elif len(args) == 4:
            cur = self.backend._vispy_get_geometry()
            if args[:2] != cur[:2] and not None in args[:2]:
                self.backend._vispy_set_location(args[0], args[1])
            if args[2:] != cur[2:] and not None in args[2:]:
                self.backend._vispy_set_size(args[2], args[3])
        else:
            raise ValueError('Setting geometry requires 2 or 4 values.')
    
#     @property
#     def context(self):
#         """Return the OpenGL context handle in use for this Canvas."""
#         return self.backend._vispy_context
    
    # todo: do we need swap_buffers or make_current?
    
    @property
    def title(self):
        """ The title of the canvas. If the canvas represents a window, the
        title is shown in its title bar.
        """
        return self._title
    
    @title.setter
    def title(self, title):
        self._title = title
        self.backend._vispy_set_title(title)
    
    
#     def resize(self, w, h):
#         """Resize the canvas to w x h pixels."""
#         return self.backend._vispy_set_size(w, h)
#     
#     def move(self, x, y):
#         """ Move the widget or window to the given location.
#         """ 
#         self.backend._vispy_set_location(x,y)
    
    def show(self, visible=True):
        """ Show (or hide) the canvas.
        """
        return self.backend._vispy_set_visible(visible)
    
    def update(self):
        """Inform the backend that the Canvas needs to be repainted."""
        return self.backend._vispy_update()
    
    def close(self):
        """ Close the canvas.
        """
        self.backend._vispy_close()
    
    
    def mouse_event(self, event):
        """Called when a mouse input event has occurred (the mouse has moved,
        a button was pressed/released, or the wheel has moved)."""
        
    def key_event(self, event):
        """Called when a keyboard event has occurred (a key was pressed or 
        released while the canvas has focus)."""
        
    def touch_event(self, event):
        """Called when the user touches the screen over a Canvas.
        
        Event properties:
        
            event.touches
                [ (x,y,pressure), ... ]
        """
        
    def stylus_event(self, event):
        """Called when a stylus has been used to interact with the Canvas.
        
        Event properties:
        
            event.device
            event.pos  (x,y)
            event.pressure
            event.angle
            
        """
        

    def initialize_event(self, event):
        """Called when the OpenGL context is initialy made available for this 
        Canvas."""
        
    def resize_event(self, event):
        """Called when the Canvas is resized.
        
        Event properties:
        
            event.size  (w,h)
        """
        
    def paint_event(self, event):
        """Called when all or part of the Canvas needs to be repainted.
        
        Event properties:
        
            event.region  (x,y,w,h) region of Canvas requiring repaint
        """
    


class CanvasBackend(object):
    """Abstract class that provides an interface between backends and Canvas.
    Each backend must implement a subclass of CanvasBackend.
    """
    
    def __init__(self, vispy_canvas, *args, **kwargs):
        # Initially the backend starts out with no canvas.
        # Canvas takes care of setting this for us.
        self._vispy_canvas = vispy_canvas  
    
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
