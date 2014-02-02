from .. import app

class SceneCanvas(app.Canvas):

    """ SceneCanvas provides a Canvas that automatically draws the contents
    of a scene.
    """

    def __init__(self, *args, **kwargs):
        root = kwargs.pop('root', None)
        app.Canvas.__init__(self, *args, **kwargs)
        self._root_entity = root

    @property
    def root_entity(self):
        """ The root entity of the scene graph to be displayed.
        """
        return self._root_entity
    
    @root_entity.setter
    def root_entity(self, e):
        self._root_entity = e
        self.update()

    def on_paint(self, event):
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glViewport(0, 0, *self.size)

        # Draw viewbox
        self._root_entity.paint_tree(canvas=self)
