import numpy as np


class Rect(object):
    """
    Representation of a rectangular area in a 2D coordinate system.

    Parameters
    ----------
    *args : arguments
        Can be in the form `Rect(x, y, w, h)`, `Rect(pos, size)`, or
        `Rect(Rect)`.
    """
    def __init__(self, *args, **kwargs):
        self._pos = (0, 0)
        self._size = (0, 0)

        if len(args) == 1 and isinstance(args[0], Rect):
            self._pos = args[0]._pos[:]
            self._size = args[0]._size[:]
        elif (len(args) == 1 and isinstance(args[0], (list, tuple)) and
              len(args[0]) == 4):
            self._pos = args[0][:2]
            self._size = args[0][2:]
        elif len(args) == 2:
            self._pos = tuple(args[0])
            self._size = tuple(args[1])
        elif len(args) == 4:
            self._pos = tuple(args[:2])
            self._size = tuple(args[2:])
        elif len(args) != 0:
            raise TypeError("Rect must be instantiated with 0, 1, 2, or 4 "
                            "non-keyword arguments.")

        self._pos = kwargs.get('pos', self._pos)
        self._size = kwargs.get('size', self._size)

        if len(self._pos) != 2 or len(self._size) != 2:
            raise ValueError("Rect pos and size arguments must have 2 "
                             "elements.")

    @property
    def pos(self):
        return tuple(self._pos)

    @pos.setter
    def pos(self, p):
        assert len(p) == 2
        self._pos = p

    @property
    def size(self):
        return tuple(self._size)

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
        self.size = (self.size[0] + (self.pos[0] - x), self.size[1])
        self.pos = (x, self.pos[1])

    @property
    def right(self):
        return self.pos[0] + self.size[0]

    @right.setter
    def right(self, x):
        self.size = (x - self.pos[0], self.size[1])

    @property
    def bottom(self):
        return self.pos[1]

    @bottom.setter
    def bottom(self, y):
        self.size = (self.size[0], self.size[1] + (self.pos[1] - y))
        self.pos = (self.pos[0], y)

    @property
    def top(self):
        return self.pos[1] + self.size[1]

    @top.setter
    def top(self, y):
        self.size = (self.size[0], y - self.pos[1])

    @property
    def center(self):
        return (self.pos[0] + self.size[0] * 0.5,
                self.pos[1] + self.size[1] * 0.5)

    def padded(self, padding):
        """Return a new Rect padded (smaller) by padding on all sides

        Parameters
        ----------
        padding : float
            The padding.

        Returns
        -------
        rect : instance of Rect
            The padded rectangle.
        """
        return Rect(pos=(self.pos[0]+padding, self.pos[1]+padding),
                    size=(self.size[0]-2*padding, self.size[1]-2*padding))

    def normalized(self):
        """Return a Rect covering the same area, but with height and width
        guaranteed to be positive."""
        return Rect(pos=(min(self.left, self.right),
                         min(self.top, self.bottom)),
                    size=(abs(self.width), abs(self.height)))

    def flipped(self, x=False, y=True):
        """Return a Rect with the same bounds but with axes inverted

        Parameters
        ----------
        x : bool
            Flip the X axis.
        y : bool
            Flip the Y axis.

        Returns
        -------
        rect : instance of Rect
            The flipped rectangle.
        """
        pos = list(self.pos)
        size = list(self.size)
        for i, flip in enumerate((x, y)):
            if flip:
                pos[i] += size[i]
                size[i] *= -1
        return Rect(pos, size)

    def __eq__(self, r):
        if not isinstance(r, Rect):
            return False
        return (np.all(np.equal(r.pos, self.pos)) and
                np.all(np.equal(r.size, self.size)))

    def __add__(self, a):
        """ Return this Rect translated by *a*.
        """
        return self._transform_out(self._transform_in()[:, :2] + a[:2])

    def contains(self, x, y):
        """Query if the rectangle contains points

        Parameters
        ----------
        x : float
            X coordinate.
        y : float
            Y coordinate.

        Returns
        -------
        contains : bool
            True if the point is within the rectangle.
        """
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
