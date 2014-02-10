from ..entity import Entity
from ...visuals import LineVisual
from ...util.event import EmitterGroup, Event
from ...util.geometry import Rect
import numpy as np

__all__ = ['Box', 'Document', 'GridBox', 'ViewBox']

class Box(Entity):
    """
    Rectangular Entity used as a container for other entities.
    """
    def __init__(self, parent=None, pos=None, size=None, border=None, clip=False):
        super(Box, self).__init__(parent)
        self.events.add(rect_change=Event)
        
        if border is None:
            border = (0.2, 0.2, 0.2, 0.5)
        self._border = border
        self._visual = LineVisual(color=border, width=2) # for drawing border
        self._clip = clip
        self._pos = (0, 0)
        self._size = (1, 1)
        self.padding = 0
        self.margin = 0
        self._boxes = set()

    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, p):
        assert isinstance(p, tuple)
        assert len(p) == 2
        self._pos = p
        self._update_line()
        self.events.rect_change()
        
    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self, s):
        assert isinstance(s, tuple)
        assert len(s) == 2
        self._size = s
        self._update_line()
        self.update()
        self.events.rect_change()
        
    @property
    def rect(self):
        return Rect(self.pos, self.size)

    @rect.setter
    def rect(self, r):
        with self.events.rect_change.blocker():
            self.pos = r.pos
            self.size = r.size
        self.update()
        self.events.rect_change()

    @property
    def border(self):
        return self._border
    
    @border.setter
    def border(self, b):
        self._border = b
        self._visual.set_data(color=b)
        self.update()

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
        self._visual.set_data(pos=pos)
        
    def paint(self, canvas):
        self._visual.transform = self.root_transform()
        self._visual.paint()
        
    def on_rect_change(self, ev):
        self._update_child_boxes()

    def _update_child_boxes(self):
        # Set the position and size of child boxes (only those added
        # using add_box)
        for ch in self._boxes:
            ch.rect = self.rect.padded(self.padding + self.margin)

    def add_box(self, box):
        """
        Add a Box as a managed child of this Box. The child will be 
        automatically positioned and sized to fill the entire space inside
        this Box.        
        """
        self._boxes.add(box)
        box.add_parent(self)
        self._update_child_boxes()
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

    def remove_box(self, box):
        self._boxes.remove(box)
        box.remove_parent(self)


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
        self.spacing = 6
        
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
        box.add_parent(self)
        
        self._next_cell = [row, col+col_span]
        self._update_child_boxes()
        return box
        
    def next_row(self):
        self._next_cell = [self._next_cell[0] + 1, 0]

    def _update_child_boxes(self):
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
        # TODO: should rows run top to bottom, or bottom to top??
        rows = np.linspace(rect.bottom, rect.top, nrows+1)
        rowstart = rows[:-1] + s2
        rowend = rows[1:] - s2
        cols = np.linspace(rect.left, rect.right, ncols+1)
        colstart = cols[:-1] + s2
        colend = cols[1:] - s2
        
        for ch in self._boxes:
            row, col, rspan, cspan = self._boxes[ch]
            
            # Translate the origin of the entity to the corner of the area
            ch.transform.reset()
            ch.transform.translate((colstart[col], rowstart[row]))
            
            # ..and set the size to match.
            w = colend[col+cspan-1]-colstart[col]
            h = rowend[row+rspan-1]-rowstart[row]
            ch.size = w, h

    
class ViewBox(Box):
    """
    Box class that provides an interactive (pan/zoom) view on its children.    
    """
    def __init__(self, *args, **kwds):
        Box.__init__(self, *args, **kwds)
    
    def on_mouse_press(self, event):
        if event.handled:
            return
        print(event)
    
    def on_mouse_move(self, event):
        if event.handled:
            return
        
    
    def on_mouse_release(self, event):
        if event.handled:
            return
        print(event)
    
    