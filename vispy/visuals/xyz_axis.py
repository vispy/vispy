
import numpy as np

from vispy.scene.visuals import Line


class XYZAxis(Line):
    """
    Simple 3D axis for indicating coordinate system orientation. Axes are
    x=red, y=green, z=blue.
    """
    def __init__(self, **kwds):
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
        Line.__init__(self, pos=verts, color=color, connect='segments',
                      mode='gl', **kwds)
