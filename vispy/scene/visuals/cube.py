import numpy as np

from ...geometry import create_cube
from .mesh import Mesh

vert = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1],
    [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]], dtype=np.float32)
ind = np.array([1, 5, 7, 7, 3, 1, 0, 2, 6, 6, 4, 0, 0, 1, 3, 3,
    2, 0, 7, 5, 4, 4, 6, 7, 2, 3, 7, 7, 6, 2, 1, 0, 4, 4, 5, 1], dtype=np.uint32)

dense_vert = vert[ind]

class Cube(Mesh):
    def __init__(self, **kwds):
        Mesh.__init__(self, dense_vert, **kwds)
