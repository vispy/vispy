
import numpy as np

from .line import LineVisual


class XYZAxisVisual(LineVisual):
    """
    Simple 3D axis for indicating coordinate system orientation. Axes are
    x=red, y=green, z=blue.
    """
    def __init__(self, **kwargs):
        verts = np.array([[0, 0, 0],
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
        LineVisual.__init__(self, pos=verts, color=color, connect='segments',
                            method='gl', **kwargs)
