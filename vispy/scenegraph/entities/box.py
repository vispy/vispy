from ..entity import Entity
from ...util.geometry import Rect

class Box(Entity):
    """
    Rectangular Entity used as a container for other entities. May also be used
    to clip children.
    """
    def __init__(self, parent=None, pos=None, size=None, border=None, clip=False):
        self._visual = self.LineVisual()
        self.rect = Rect(pos, size)
        self._clip = clip
        Entity.__init__(self, parent)

    @property
    def rect(self):
        return self._rect
    
    @rect.setter
    def rect(self, r):
        assert isinstance(r, Rect)
        self._rect = r
        self._update_line()
        
    @property
    def pos(self):
        return self._rect.pos
    
    @pos.setter
    def pos(self, p):
        self._rect.pos = p
        self._update_line()
        
    @property
    def size(self):
        return self._rect.size
    
    @size.setter
    def size(self, s):
        self._rect.size = s
        self._update_line()

    def _update_line(self):
        pos = np.array([
            [self.pos[0], self.pos[1]],
            [self.pos[0]+self.size[0], self.pos[1]],
            [self.pos[0]+self.size[0], self.pos[1]+self.size[1]],
            [self.pos[0], self.pos[1]+self.size[1]],
            [self.pos[0], self.pos[1]]])
        self._visual.set_data(pos=pos)
        
    def paint(self, canvas, path):
        tr = self.get_path_transform(path)
        self._visual.transform = tr
        self._visual.paint()

class GridBox(Box):
    """
    Box that automatically sets the position and size of child Boxes to
    proportionally divide its internal area into a grid.
    """
    def __init__(self, parent=None, pos=None, size=None, border=None):
        Box.__init__(self, parent, pos, size, border)
        
    def add_box(self, box, row=None, col=None, row_span=1, col_span=1):
        """
        Add a new box to this grid.
        """
        
    def add_grid(self, *args, **kwds):
        """
        Convenience function that creates a new GridBox and adds it to the grid.
        
        All arguments are given to add_box().
        """
        grid = GridBox()
        self.add_box(grid, *args, **kwds)
        return grid

    
class ViewBox(Box):
    """
    Box class that provides an interactive (pan/zoom) view on its children.    
    """
    def __init__(self, *args, **kwds):
        Box.__init__(self, *args, **kwds)
    
    