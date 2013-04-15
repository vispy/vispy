# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

from pyvis.event import EmitterGroup
import pyvis

# todo: add functions for asking about current mouse/keyboard state
# todo: add hover enter/exit events

class Canvas(object):
    """Base class for a GUI element that can be rendered to by an OpenGL 
    context.
    
    Receives the following events:
    initialize, resize, paint, mouse, key, stylus, touch, close
    """
    
    def __init__(self, *args, **kwargs):
        """Create a Canvas with the specified backend.
        
        *backend* may be a string indicating the type of backend to use
        ('qt', 'gtk', 'pyglet', ...) or None, in which case 
        pyvis.config['default_backend'] will be used. The backend constructor 
        will be passed **kwds.
        
        Alternatively, a pre-constructed backend instance may be supplied
        instead.
        """
        self.events = EmitterGroup(source=self, 
                        event_names=['initialize', 'resize', 'paint',
                        'mouse_press', 'mouse_release', 'mouse_move', 
                        'mouse_wheel',
                        'key_press', 'key_release', 'stylus', 'touch', 'close'])

        # Get app instance and make sure that it has an associated backend 
        app = kwargs.pop('app', pyvis.app.default_app)
        app.use()
        
        # Store app instance
        # todo: should this be private, and do we need it at all?
        self.app = app
        
        # Instantiate the backed with the right class
        self.backend = app.backend_module.CanvasBackend(*args, **kwargs)
        self.backend._pyvis_set_canvas(self)
        
    
    @property
    def geometry(self):
        """Return the position and size of the Canvas in window coordinates
        (x, y, width, height)."""
        return self.backend._pyvis_geometry
    
    @property
    def context(self):
        """Return the OpenGL context handle in use for this Canvas."""
        return self.backend._pyvis_context

    def resize(self, w, h):
        """Resize the canvas to w x h pixels."""
        return self.backend._pyvis_resize(w, h)
    
    def show(self):
        return self.backend._pyvis_show()
    
    def update(self):
        """Inform the backend that the Canvas needs to be repainted."""
        return self.backend._pyvis_update()
    
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
    
#     @classmethod
#     def _pyvis_create(cls, backend, canvas, *args, **kwds):
#         """Create a new CanvasBackend instance from the named backend.
#         (options are 'qt', 'pyglet', 'gtk', ...)
#         
#         This is equivalent to::
#         
#             import pyvis.opengl.backends.backend as B
#             return B.BackendCanvas(*args, **kwds)
#         """
#         mod_name = 'pyvis.app.backends.' + backend
#         __import__(mod_name)
#         mod = getattr(pyvis.app.backends, backend)
#         return getattr(mod, backend.capitalize()+"CanvasBackend")(*args, **kwds)
    
    def __init__(self):
        # Initially the backend starts out with no canvas.
        # Canvas takes care of setting this for us.
        self._pyvis_canvas = None  

    def _pyvis_set_canvas(self, canvas):
        self._pyvis_canvas = canvas
        
    @property 
    def _pyvis_geometry(self):
        raise Exception("Method must be reimplemented in subclass.")

    @property
    def _pyvis_context(self):
        raise Exception("Method must be reimplemented in subclass.")
    
    def _pyvis_resize(self, w, h):
        raise Exception("Method must be reimplemented in subclass.")
        
    def _pyvis_show(self):
        raise Exception("Method must be reimplemented in subclass.")

    def _pyvis_update(self):        
        raise Exception("Method must be reimplemented in subclass.")
    