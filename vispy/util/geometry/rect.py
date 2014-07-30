import numpy as np


class Rect(object):
    """
    Representation of a rectangular area in a 2D coordinate system.
    """
    def __init__(self, pos=None, size=None):
        self._pos = tuple(pos) if pos is not None else (0, 0)
        self._size = tuple(size) if pos is not None else (0, 0)
        if len(self._pos) != 2 or len(self._size) != 2:
            raise ValueError("Rect pos and size arguments must have 2 "
                             "elements.")

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, p):
        assert len(p) == 2
        self._pos = p

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, s):
        assert len(s) == 2
        self._size = s

    @property
    def width(self):
        return self.size[0]

    @width.setter
    def width(self, w):
        self.size[0] = w

    @property
    def height(self):
        return self.size[1]

    @height.setter
    def height(self, h):
        self.size[1] = h

    @property
    def left(self):
        return self.pos[0]

    @left.setter
    def left(self, x):
        self.pos[0] = x

    @property
    def right(self):
        return self.pos[0] + self.size[0]

    @right.setter
    def right(self, x):
        self.size[0] = x - self.pos[0]

    @property
    def bottom(self):
        return self.pos[1]

    @bottom.setter
    def bottom(self, y):
        self.pos[1] = y

    @property
    def top(self):
        return self.pos[1] + self.size[1]

    @top.setter
    def top(self, y):
        self.size[1] = y - self.pos[1]

    def padded(self, padding):
        """Return a new Rect padded (smaller) by *padding* on all sides."""
        return Rect(pos=(self.pos[0]+padding, self.pos[1]+padding),
                    size=(self.size[0]-2*padding, self.size[1]-2*padding))

    def normalized(self):
        """Return a Rect covering the same area, but with height and width
        guaranteed to be positive."""
        return Rect(pos=(min(self.left, self.right),
                         min(self.top, self.bottom)),
                    size=(abs(self.width), abs(self.height)))

    def __eq__(self, r):
        if not isinstance(r, Rect):
            return False
        return r.pos == self.pos and r.size == self.size

    def contains(self, x, y):
        return (x >= self.left and x <= self.right and
                y >= self.bottom and y <= self.top)

    def __repr__(self):
        return "<Rect (%g, %g) (%g, %g)>" % (self.pos + self.size)

    def _transform_in(self):
        """Return array of coordinates that can be mapped by Transform
        classes."""
        return np.array([
            [self.left, self.bottom, 0, 1],
            [self.right, self.top, 0, 1]])

    def _transform_out(self, coords):
        """Return a new Rect from coordinates mapped after _transform_in()."""
        return Rect(pos=coords[0, :2], size=coords[1, :2]-coords[0, :2])
