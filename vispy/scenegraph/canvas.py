from ..gloo import gl
from .. import app
from .entities import Document
from ..visuals.transforms import STTransform

class SceneCanvas(app.Canvas):

    """ SceneCanvas provides a Canvas that automatically draws the contents
    of a scene.
    
    Automatically constructs a Document instance as the root entity.
    """

    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        
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
        self.root.paint_tree(canvas=self)

    def on_mouse_press(self, event):
        if event.handled:
            return
        self._root.process_mouse_event(self, event)
        
    def on_mouse_move(self, event):
        if event.handled:
            return
        self._root.process_mouse_event(self, event)
        
    def on_mouse_release(self, event):
        if event.handled:
            return
        self._root.process_mouse_event(self, event)
        
