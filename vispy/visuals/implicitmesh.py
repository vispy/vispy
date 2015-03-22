
from .mesh import MeshVisual
from ..geometry import create_implicit_mesh

import numpy as np

class ImplicitMeshVisual(MeshVisual):
    """Displays a mesh implicitly constructed around x,y,z coordinates.

    """

    def __init__(self, xs, ys, zs, color=None):
        
        vertices, indices = create_implicit_mesh(xs, ys, zs)

        shape = xs.shape
        if isinstance(color, np.ndarray):
            vertex_colors = color.reshape((shape[0] * shape[1], 3))
        else:
            vertex_colors = None
                

        MeshVisual.__init__(self, vertices, indices,
                            vertex_colors=vertex_colors,
                            color='purple',
                            shading='smooth',
                            mode='triangles',
                            )

    def draw(self, transforms):
        MeshVisual.draw(self, transforms)
