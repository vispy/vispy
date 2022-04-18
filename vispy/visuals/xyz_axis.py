
import numpy as np

from .line import LineVisual


class XYZAxisVisual(LineVisual):
    """
    Simple 3D axis for indicating coordinate system orientation. Axes are
    x=red, y=green, z=blue.
    """

    def __init__(self, **kwargs):
        pos = np.array([[0, 0, 0],
                        [1, 0, 0],
                        [0, 0, 0],
                        [0, 1, 0],
                        [0, 0, 0],
                        [0, 0, 1]])
        color = np.array([[1, 0, 0, 1],
                          [1, 0, 0, 1],
                          [0, 1, 0, 1],
                          [0, 1, 0, 1],
                          [0, 0, 1, 1],
                          [0, 0, 1, 1]])
        connect = 'segments'
        method = 'gl'

        kwargs.setdefault('pos', pos)
        kwargs.setdefault('color', color)
        kwargs.setdefault('connect', connect)
        kwargs.setdefault('method', method)

        LineVisual.__init__(self, **kwargs)
