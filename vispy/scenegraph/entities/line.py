from ..entity import Entity
from ...visuals import LineVisual

__all__ = ['Line']

class Line(Entity):
    """
    """
    VisualClass = LineVisual
    WrapMethods = []

    def __init__(self, *args, **kwds):
        parent = kwds.pop('parent', None)
        Entity.__init__(self, parent)
        self._visual = self.VisualClass(*args, **kwds)
        for method in self.WrapMethods:
            setattr(self, method, getattr(self._visual, method))
        
    def paint(self, canvas):
        self._visual.transform = self.root_transform()
        self._visual.paint()


