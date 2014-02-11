from ..entity import Entity
from ...visuals import LineVisual

__all__ = ['Line']

class Line(Entity):
    """
    """
    WrapMethods = []

    def __init__(self, *args, **kwds):
        parents = kwds.pop('parents', None)
        Entity.__init__(self, parents)
        self._visual = LineVisual(*args, **kwds)
        for method in self.WrapMethods:
            setattr(self, method, getattr(self._visual, method))
        
    def on_paint(self, event):
        self._visual.transform = event.root_transform()
        self._visual.paint()


