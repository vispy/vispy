
import numpy as np

from .line import LineVisual


class XYZAxisVisual(LineVisual):
    """
    Simple 3D axis for indicating coordinate system orientation. Axes are
    x=red, y=green, z=blue.
    """
    def __init__(self, **kwargs):
        if 'pos' not in kwargs:
            kwargs['pos'] = np.array([[0, 0, 0],
                                      [1, 0, 0],
                                      [0, 0, 0],
                                      [0, 1, 0],
                                      [0, 0, 0],
                                      [0, 0, 1]])
        if 'color' not in kwargs:
            kwargs['color'] = np.array([[1, 0, 0, 1],
                                        [1, 0, 0, 1],
                                        [0, 1, 0, 1],
                                        [0, 1, 0, 1],
                                        [0, 0, 1, 1],
                                        [0, 0, 1, 1]])
        if 'connect' not in kwargs:
            kwargs['connect'] = 'segments'
        if 'method' not in kwargs:
            kwargs['method'] = 'gl'

        LineVisual.__init__(self, **kwargs)
