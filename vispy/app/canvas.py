# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import print_function, division, absolute_import

from vispy.event import EmitterGroup, Event
import vispy

# todo: add functions for asking about current mouse/keyboard state
# todo: add hover enter/exit events
# todo: add focus events

class Canvas(object):
    """ Representation of a GUI element that can be rendered to by an OpenGL
    context. The args and kwargs are used to instantiate the native widget.
    
    Further, there are two special keyword arguments:
      * app: an vispy Application instance (vispy.app is used by default)
      * create_native: a bool that indicates whether to create the
        widget immediately (default True)
    
    Receives the following events:
    initialize, resize, paint, 
    mouse_press, mouse_release, mouse_move, mouse_wheel,
    key_press, key_release,
    stylus, touch, close
    """
    
    def __init__(self, *args, **kwargs):
        self.events = EmitterGroup(source=self, 
                        initialize=Event, 
                        resize=ResizeEvent,
                        paint=PaintEvent,
                        mouse_press=MouseEvent,
                        mouse_release=MouseEvent,
                        mouse_move=MouseEvent, 
                        mouse_wheel=MouseEvent,
                        key_press=KeyEvent,
                        key_release=KeyEvent,
                        stylus=Event,
                        touch=Event,
                        close=Event,
                        )
        
        # Store input and initialize backend attribute
        self._args = args
        self._kwargs = kwargs
        self._backend = None
        
        # Initialise some values
        self._title = ''
        
        # Get app instance 
        self._app = kwargs.pop('app', vispy.app.default_app)
        
        # Create widget now
        if 'native' in kwargs:
            self._set_backend(kwargs.pop('native'))
        else:
            self.create_native()
        
    
    def create_native(self):
        """ Create the native widget if not already done so. If the widget
        is already created, this function does nothing.
        """
        if self._backend is None:
            # Make sure that the app is active
            self._app.use()
            self._app.native
            # Instantiate the backed with the right class
            self._set_backend(self._app.backend_module.CanvasBackend(*self._args, **self._kwargs))
            # Set initial size. Let OS determine location
            self.geometry = None, None, 560, 420 
            # Clean up
            del self._args 
            del self._kwargs
    
    def _set_backend(self, backend):
        self._backend = backend
        if backend is not None:
            backend._vispy_canvas = self
    
    @property
    def app(self):
        """ The vispy Application instance on which this Canvas is based.
        """
        return self._app
    
    
    @property
    def native(self):
        """ The native widget object on which this Canvas is based.
        """
        return self._backend._vispy_get_native_canvas()
    
    
    @property
    def geometry(self):
        """ Get or set the location and size of the Canvas in window
        coordinates (x, y, width, height). When setting, width and
        height may be omitted. Similarly, specifying None for x and y
        will prevent the widget from being moved.
        """
        return self._backend._vispy_get_geometry()
    
    @geometry.setter
    def geometry(self, args):
        if len(args) == 2:
            self._backend._vispy_set_location(*args)
        elif len(args) == 4:
            cur = self._backend._vispy_get_geometry()
            if args[:2] != cur[:2] and not None in args[:2]:
                self._backend._vispy_set_location(args[0], args[1])
            if args[2:] != cur[2:] and not None in args[2:]:
                self._backend._vispy_set_size(args[2], args[3])
        else:
            raise ValueError('Setting geometry requires 2 or 4 values.')
        
    def swap_buffers(self):
        """ Swap GL buffers such that the offscreen buffer becomes visible.
        """
        self._backend._vispy_swap_buffers()
    
#     @property
#     def context(self):
#         """Return the OpenGL context handle in use for this Canvas."""
#         return self._backend._vispy_context
    
    @property
    def title(self):
        """ The title of the canvas. If the canvas represents a window, the
        title is shown in its title bar.
        """
        return self._title
    
    @title.setter
    def title(self, title):
        self._title = title
        self._backend._vispy_set_title(title)
    
    
#     def resize(self, w, h):
#         """Resize the canvas to w x h pixels."""
#         return self._backend._vispy_set_size(w, h)
#     
#     def move(self, x, y):
#         """ Move the widget or window to the given location.
#         """ 
#         self._backend._vispy_set_location(x,y)
    
    def show(self, visible=True):
        """ Show (or hide) the canvas.
        """
        return self._backend._vispy_set_visible(visible)
    
    def update(self):
        """Inform the backend that the Canvas needs to be repainted."""
        return self._backend._vispy_update()
    
    def close(self):
        """ Close the canvas.
        """
        self._backend._vispy_close()
    
    
    #def mouse_event(self, event):
        #"""Called when a mouse input event has occurred (the mouse has moved,
        #a button was pressed/released, or the wheel has moved)."""
        
    #def key_event(self, event):
        #"""Called when a keyboard event has occurred (a key was pressed or 
        #released while the canvas has focus)."""
        
    #def touch_event(self, event):
        #"""Called when the user touches the screen over a Canvas.
        
        #Event properties:
        
            #event.touches
                #[ (x,y,pressure), ... ]
        #"""
        
    #def stylus_event(self, event):
        #"""Called when a stylus has been used to interact with the Canvas.
        
        #Event properties:
        
            #event.device
            #event.pos  (x,y)
            #event.pressure
            #event.angle
            
        #"""
        

    #def initialize_event(self, event):
        #"""Called when the OpenGL context is initialy made available for this 
        #Canvas."""
        
    #def resize_event(self, event):
        #"""Called when the Canvas is resized.
        
        #Event properties:
        
            #event.size  (w,h)
        #"""
        
    #def paint_event(self, event):
        #"""Called when all or part of the Canvas needs to be repainted.
        
        #Event properties:
        
            #event.region  (x,y,w,h) region of Canvas requiring repaint
        #"""
    


class CanvasBackend(object):
    """ CanvasBackend(vispy_canvas, *args, **kwargs)
    
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
    
    def _vispy_set_current(self):  
        # todo: this is currently not used internally
        # --> I think the backends should call this themselves before emitting the paint event
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
        # Should return the native widget object
        # Most backends would not need to implement this
        return self


## Event subclasses specific to the Canvas


class MouseEvent(Event):
    """ Class describing mouse events.
    
     Note that each event object has an attribute for each of the input
    arguments listed below.
    
    Input arguments
    ---------------
    type : str
       String indicating the event type (e.g. mouse_press, key_release)
    native : object (optional)
       The native GUI event object
    pos : (int, int)
        The position of the mouse (in screen coordinates).
    button : int
        The button that this event applies to (can be None).
        Left=1, right=2, middle=3.
    modifiers : tuple of Key instances
        Tuple that specifies which modifier keys were pressed down at the
        time of the event (shift, control, alt, meta).
    delta : (float, float)
        The amount of scrolling in horizontal and vertical direction. One 
        "tick" corresponds to a delta of 1.0.
    **kwds : keyword arguments
        All extra keyword arguments become attributes of the event object.
    
    """
    
    def __init__(self, type, pos=None, button=None, modifiers=None, delta=None, **kwds):
        Event.__init__(self, type, **kwds)
        self._pos = (0,0) if (pos is None) else (pos[0], pos[1])
        self._button = int(button) if (button is not None) else 0
        self._modifiers = tuple( modifiers or () )
        self._delta = (0.0,0.0) if (delta is None) else (delta[0], delta[1])
    
    @property
    def pos(self):
        return self._pos
    
    @property
    def button(self):
        return self._button
    
    @property
    def modifiers(self):
        return self._modifiers
    
    @property
    def delta(self):
        return self._delta


class KeyEvent(Event):
    """ Class describing mouse events.
    
    Note that each event object has an attribute for each of the input
    arguments listed below.
    
    Input arguments
    ---------------
    type : str
       String indicating the event type (e.g. mouse_press, key_release)
    native : object (optional)
       The native GUI event object
    key : vispy.keys.Key instance
        The Key object for this event. Can be compared to string names.
    text : str
        The text representation of the key (can be an empty string).
    modifiers : tuple of Key instances
        Tuple that specifies which modifier keys were pressed down at the
        time of the event (shift, control, alt, meta).
    **kwds : keyword arguments
        All extra keyword arguments become attributes of the event object.
    """
    
    def __init__(self, type, key=None, text='', modifiers=None, **kwds):
        Event.__init__(self, type, **kwds)
        self._key = key
        self._text = text
        self._modifiers = tuple( modifiers or () )
    
    @property
    def key(self):
        return self._key
    
    @property
    def text(self):
        return self._text
    
    @property
    def modifiers(self):
        return self._modifiers



class ResizeEvent(Event):
    """ Class describing canvas resize events.
    
    Note that each event object has an attribute for each of the input
    arguments listed below.
    
    Input arguments
    ---------------
    type : str
       String indicating the event type (e.g. mouse_press, key_release)
    native : object (optional)
       The native GUI event object
    size : (int, int)
        The new size of the Canvas.
    **kwds : extra keyword arguments
        All extra keyword arguments become attributes of the event object.
    """
    
    def __init__(self, type, size=None, **kwds):
        Event.__init__(self, type, **kwds)
        self._size = tuple(size)
    
    @property
    def size(self):
        return self._size


class PaintEvent(Event):
    """ Class describing canvas paint events.
    This type of event is sent to Canvas.events.paint when a repaint 
    is required.
    
    Note that each event object has an attribute for each of the input
    arguments listed below.
    
    Input arguments
    ---------------
    type : str
       String indicating the event type (e.g. mouse_press, key_release)
    native : object (optional)
       The native GUI event object
    region : (int, int, int, int) or None
        The region of the canvas which needs to be repainted (x, y, w, h). 
        If None, the entire canvas must be repainted.
    **kwds : extra keyword arguments
        All extra keyword arguments become attributes of the event object.
    """
    
    def __init__(self, type, region=None, **kwds):
        Event.__init__(self, type, **kwds)
        self._region = region
    
    @property 
    def region(self):
        return self._region
