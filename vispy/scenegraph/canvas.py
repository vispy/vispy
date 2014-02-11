from ..gloo import gl
from .. import app
from .entities import Document
from ..visuals.transforms import STTransform
from .events import ScenePaintEvent, SceneMouseEvent

class SceneCanvas(app.Canvas):

    """ SceneCanvas provides a Canvas that automatically draws the contents
    of a scene.
    
    Automatically constructs a Document instance as the root entity.
    """

    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        self.events.mouse_press.connect(self._process_mouse_event)
        self.events.mouse_move.connect(self._process_mouse_event)
        self.events.mouse_release.connect(self._process_mouse_event)
        
        root = Document()
        root.transform = STTransform()
        self.root = root

    @property
    def root(self):
        """ The root entity of the scene graph to be displayed.
        """
        return self._root
    
    @root.setter
    def root(self, e):
        self._root = e
        self._update_document()

    def _update_document(self):
        # 1. Set scaling on document such that its local coordinate system 
        #    represents pixels in the canvas.
        self.root.transform.scale = (2. / self.size[0], 2. / self.size[1])
        self.root.transform.translate = (-1, -1)
        
        # 2. Set size of document to match the area of the canvas
        self.root.size = self.size

    def on_resize(self, event):
        self._update_document()

    def on_paint(self, event):
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glViewport(0, 0, *self.size)

        # Draw viewbox
        scene_event = ScenePaintEvent(canvas=self, event=event)
        self._root._process_paint_event(scene_event)
        

    def _process_mouse_event(self, event):
        scene_event = SceneMouseEvent(canvas=self, event=event)
        self._root._process_mouse_event(scene_event)
        
        # If something in the scene handled the scene_event, then we mark
        # the original event accordingly.
        event.handled = scene_event.handled

    def nd_transform(self):
        """
        Return the transform that maps from ND coordinates to pixel coordinates
        on the Canvas.        
        """
        s = (self.size[0]/2., self.size[1]/2.)
        return STTransform(scale=s, translate=s)
