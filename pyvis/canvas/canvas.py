from pyvis.event import EventHandler
import pyvis


class Canvas(object):
    """Base class for a GUI element that can be rendered to by an OpenGL 
    context.
    
    Receives the following events:
    initialize, resize, paint, mouse, key, stylus, touch, close
    """
    
    def __init__(self, backend=None, **kwds):
        """Create a Canvas with the specified backend. 
        
        *backend* may be a string indicating the type of backend to use
        ('qt', 'gtk', 'pyglet', ...) or None, in which case 
        pyvis.config['default_backend'] will be used. The backend constructor 
        will be passed **kwds.
        
        Alternatively, a pre-constructed backend instance may be supplied
        instead.
        """
        self.events = EventHandler(source=self,
                        initialize=(self, 'initialize_event'),
                        resize=(self,'resize_event'), 
                        paint=(self, 'paint_event'), 
                        mouse=(self, 'mouse_event'), 
                        key=(self, 'key_event'), 
                        stylus=(self, 'stylus_event'), 
                        touch=(self, 'touch_event'), 
                        close=(self, 'close_event'),
                        )
        
        if backend is None:
            backend = pyvis.config['default_backend']
        
        if isinstance(backend, basestring):
            backend = CanvasBackend._pyvis_create(backend, self, **kwds)
        
        self.backend = backend
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
    
    def run_event_loop(self):
        """Execute the event loop for this Canvas's backend.
        """
        return self.backend._pyvis_run()
    
    def quit_event_loop(self):
        """Exit the event loop for this Canvas's backend.
        """
        return self.backend._pyvis_quit()
    
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
    
    @classmethod
    def _pyvis_create(cls, backend, canvas, *args, **kwds):
        """Create a new CanvasBackend instance from the named backend.
        (options are 'qt', 'pyglet', 'gtk', ...)
        
        This is equivalent to::
        
            import pyvis.opengl.backends.backend as B
            return B.BackendCanvas(*args, **kwds)
        """
        mod_name = 'pyvis.canvas.backends.' + backend
        __import__(mod_name)
        mod = getattr(pyvis.canvas.backends, backend)
        return getattr(mod, backend.capitalize()+"CanvasBackend")(*args, **kwds)
    
    def __init__(self):
        ## Initially the backend starts out with no canvas.
        ## Canvas takes care of setting this for us.
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

    def _pyvis_run(self):        
        raise Exception("Method must be reimplemented in subclass.")
    