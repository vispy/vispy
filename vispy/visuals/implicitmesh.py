
from .mesh import MeshVisual
from ..geometry import create_implicit_mesh
from ..color import ColorArray

import numpy as np

class ImplicitMeshVisual(MeshVisual):
    """Displays a mesh implicitly constructed around x,y,z coordinates.

    This makes it simple to generate a mesh from e.g. the output
    of numpy.meshgrid.

    Parameters
    ----------
    xs : ndarray
        A 2d array of x coordinates for the vertices of the mesh. Must
        have the same dimensions as ys and zs.
    ys : ndarray
        A 2d array of y coordinates for the vertices of the mesh. Must
        have the same dimensions as xs and zs.
    zs : ndarray
        A 2d array of z coordinates for the vertices of the mesh. Must
        have the same dimensions as xs and ys.
    color : Color | ColorArray | ndarray
        The color(s) of the points of the mesh. If a Color or ColorArray
        is passed, the vertex_colors are constructed by cycling their
        contents. If an ndarray of ndim 3 is passed, it is assumed that
        this has the same shape as the xs, ys and zs arrays and gives
        one colour per vertex.
    shading : str | None
        Same as for the `MeshVisual` class. Defaults to 'smooth'.
    vertex_colors: ndarray | None
        Same as for the `MeshVisual` class. Defaults to None. Overrides
        the color argument if set.
    face_colors: ndarray | None
        Same as for the `MeshVisual` class. Defaults to None.
    mode : str
        Same as for the `MeshVisual` class. Defaults to 'triangles'.
    """

    def __init__(self, xs, ys, zs, color=None,
                 shading='smooth',
                 vertex_colors=None,
                 face_colors=None,
                 mode='triangles'):
        
        vertices, indices = create_implicit_mesh(xs, ys, zs)

        shape = xs.shape
        if isinstance(color, np.ndarray) and color.ndim == 3:
            color = color.reshape((shape[0] * shape[1], color.shape[2]))
        color = ColorArray(color).rgba
        if vertex_colors is None:
            vertex_colors = np.resize(color, (shape[0] * shape[1], 4))

        MeshVisual.__init__(self, vertices, indices,
                            vertex_colors=vertex_colors,
                            face_colors=face_colors,
                            color='purple',
                            shading=shading,
                            mode=mode)
    def draw(self, transforms):
        MeshVisual.draw(self, transforms)
