from ..entity import Entity
from ...util.geometry import Rect
from ...visuals import LineVisual
from ...util.event import EmitterGroup, Event
import numpy as np

__all__ = ['Box', 'Document', 'GridBox', 'ViewBox']

class Box(Entity):
    """
    Rectangular Entity used as a container for other entities.
    
    By default, Boxes automatically resize their child boxes unless they have
    been explicitly assigned a position or size.
    """
    def __init__(self, parent=None, pos=None, size=None, border=None, clip=False):
        self._auto_rect = pos is None and size is None
        self._rect = Rect()
        if border is None:
            border = (0.2, 0.2, 0.2, 0.5)
        self._visual = LineVisual(color=border, width=4) # for drawing border
        self.rect = Rect(pos, size)
        self._clip = clip
        self.padding = 10
        self.margin = 10
        self.events = EmitterGroup(source=self,
                                   auto_connect=True,
                                   rect_change=Event)
        
        Entity.__init__(self, parent)

    @property
    def rect(self):
        return self._rect
    
    @rect.setter
    def rect(self, r):
        # TODO: don't use mutable objects as properties!
        assert isinstance(r, Rect)
        if self._rect == r:
            return
        self._rect = r
        self._update_line()
        self.events.rect_change(rect=self._rect)
        
    @property
    def pos(self):
        return self._rect.pos
    
    @pos.setter
    def pos(self, p):
        self.rect.pos = p
        self._update_line()
        self.events.rect_change(rect=self._rect)
        
    @property
    def size(self):
        return self._rect.size
    
    @size.setter
    def size(self, s):
        self.rect.size = s
        self._update_line()
        self.events.rect_change(rect=self._rect)

    def _update_line(self):
        pad = self.margin
        left = self.pos[0] + pad
        right = self.pos[0] + self.size[0] - pad
        bottom = self.pos[1] + pad
        top = self.pos[1] + self.size[1] - pad
        
        pos = np.array([
            [left, bottom],
            [right, bottom],
            [right, top],
            [left, top],
            [left, bottom]])
        print(pos)
        self._visual.set_data(pos=pos)
        
    def paint(self, canvas):
        self._visual.transform = self.root_transform()
        self._visual.paint()
        
    def on_rect_change(self, ev):
        print('rc')
        for ch in self:
            if isinstance(ch, Box) and ch._auto_rect:
                ch.rect = self.rect.padded(self.padding + self.margin)


class Document(Box):
    """
    Box that represents the area of a rectangular document with 
    physical dimensions. 
    """
    def __init__(self, *args, **kwds):
        self._dpi = 100  # will be used to relate other units to pixels
        super(Document, self).__init__(*args, **kwds)
        
    @property
    def dpi(self):
        return self._dpi
    
    @dpi.setter
    def dpi(self, d):
        self._dpi = dpi
        # TODO: inform tree that resolution has changed..


class GridBox(Box):
    """
    Box that automatically sets the position and size of child Boxes to
    proportionally divide its internal area into a grid.
    """
    def __init__(self, parent=None, pos=None, size=None, border=None):
        Box.__init__(self, parent, pos, size, border)
        self._next_cell = [0, 0]  # row, col
        self._cells = {}
        self._boxes = {}
        self.spacing = 20
        
    def add_box(self, box=None, row=None, col=None, row_span=1, col_span=1):
        """
        Add a new box to this grid.
        """
        if row is None:
            row = self._next_cell[0]
        if col is None:
            col = self._next_cell[1]
        
        if box is None:
            box = Box()
            
        _row = self._cells.setdefault(row, {})
        _row[col] = box
        self._boxes[box] = row, col, row_span, col_span
        box.parent = self
        
        self._next_cell = [row, col+col_span]
        self._update_grid()
        return box
        
    def add_grid(self, *args, **kwds):
        """
        Convenience function that creates a new GridBox and adds it to the grid.
        
        All arguments are given to add_box().
        """
        grid = GridBox()
        return self.add_box(grid, *args, **kwds)
    
    def add_view(self, *args, **kwds):
        """
        Convenience function that creates a new ViewBox and adds it to the grid.
        
        All arguments are given to add_box().
        """
        view = ViewBox()
        return self.add_box(view, *args, **kwds)
        
    
    def next_row(self):
        self._next_cell = [self._next_cell[0] + 1, 0]

    def _update_grid(self):
        # Resize all boxes in this grid to share space.
        # This logic will need a lot of work..

        rvals = [box[0]+box[2] for box in self._boxes.values()]
        cvals = [box[1]+box[3] for box in self._boxes.values()]
        if len(rvals) == 0 or len(cvals) == 0:
            return
        
        nrows = max(rvals)
        ncols = max(cvals)
        
        # determine starting/ending position of each row and column
        s2 = self.spacing / 2.
        rect = self.rect.padded(self.padding + self.margin - s2)
        rows = np.linspace(rect.bottom, rect.top, nrows+1)
        rowstart = rows[:-1] + s2
        rowend = rows[1:] - s2
        cols = np.linspace(rect.left, rect.right, ncols+1)
        colstart = cols[:-1] + s2
        colend = cols[1:] - s2
        
        print('----------')
        for ch in self:
            if isinstance(ch, Box) and ch._auto_rect:
                row, col, rspan, cspan = self._boxes[ch]
                r = Rect(pos=(rowstart[row], colstart[col]),
                         size=(rowend[row+rspan-1]-rowstart[row], 
                               colend[col+cspan-1]-colstart[col])
                         )
                ch.rect = r
                print(r)

    def on_rect_change(self, ev):
        self._update_grid()

    
class ViewBox(Box):
    """
    Box class that provides an interactive (pan/zoom) view on its children.    
    """
    def __init__(self, *args, **kwds):
        Box.__init__(self, *args, **kwds)
    
    