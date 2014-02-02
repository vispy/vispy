from ..entity import Entity
from ...visuals import LineVisual

class Line(Entity):
    """
    """
    VisualClass = Line
    WrapMethods = []

    def __init__(self, *args, **kwds):
        parent = kwds.pop('parent', None)
        Entity.__init__(self, parent)
        self._visual = self.VisualClass(*args, **kwds)
        for method in self.WrapMethods:
            setattr(self, method, getattr(self._visual, method))
        
    def paint(self, canvas, path):
        tr = self.get_path_transform(path)
        self._visual.transform = tr
        self._visual.paint()


