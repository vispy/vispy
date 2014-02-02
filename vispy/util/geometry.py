class Rect(object):
    """
    Representation of a rectangular area in a 2D coordinate system.
    """
    def __init__(self, pos=None, size=None):
        self._pos = pos or (0,0)
        self._size = size or (0,0)

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
    
    @property
    def height(self):
        return self.size[1]
    
    @property
    def x(self):
        return self.pos[0]
    
    @property
    def y(self):
        return self.pos[1]
    
    
