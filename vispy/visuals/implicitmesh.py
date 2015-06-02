
from .mesh import MeshVisual
from ..geometry.implicitmesh import create_implicit_mesh
from ..geometry.generation import create_cube

import numpy as np

class ImplicitMeshVisual(MeshVisual):
    """Displays a mesh implicitly constructed around x,y,z coordinates.

    """

    def __init__(self, xs, ys, zs, color=None):
        
        vertices, indices = create_implicit_mesh(xs, ys, zs)

        # shape = xs.shape
        # if color.shape[:2] == shape:
        #     color = colors.reshape((shape[0] * shape[1], 3))
        # print 'vertices', vertices
        # print 'indices', indices

        vertex_colors = np.random.random((xs.shape[0] * xs.shape[1], 3))

        MeshVisual.__init__(self, vertices, indices,
                            color='purple',
                            vertex_colors=vertex_colors,
                            # shading='smooth',
                            # shading='flat',
                            # mode='lines',
                            mode='triangles',
                            )

    def draw(self, transforms):
        MeshVisual.draw(self, transforms)
