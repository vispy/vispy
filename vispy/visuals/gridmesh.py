
from .mesh import MeshVisual
from ..geometry import create_grid_mesh, MeshData
from ..color import ColorArray

import numpy as np


class GridMeshVisual(MeshVisual):
    """Displays a mesh in a Cartesian grid about x,y,z coordinates.

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
    color : ndarray | Color
        The color(s) of the points of the mesh. Should be either a
        (width, height, 4) array of rgba colors at each grid point,
        a (width, height, 3) array of rgb colors at each grid point,
        a (width, height) array of a Color at each grid point, or a
        single Color that will be applied to the entire mesh.
    shading : str | None
        Same as for the `MeshVisual` class. Defaults to 'smooth'.
    vertex_colors: ndarray | None
        Same as for the `MeshVisual` class. Defaults to None. Overrides
        the color argument if set.
    face_colors: ndarray | None
        Same as for the `MeshVisual` class. Defaults to None.
    """

    def __init__(self, xs, ys, zs, colors=None,
                 shading='smooth',
                 **kwargs):

        if xs is None or ys is None or zs is None:
            raise ValueError('All of xs, ys and zs must be initialised '
                             'with arrays.')
        self._xs = None
        self._ys = None
        self._zs = None

        self.__colors = None
        self.__vertices = None
        self.__meshdata = MeshData()

        MeshVisual.__init__(self, shading=shading, **kwargs)
        self.set_data(xs, ys, zs, colors)

    def set_data(self, xs=None, ys=None, zs=None, colors=None):

        if xs is not None:
            if self._xs is not None:
                self.__vertices = None
            self._xs = xs

        if ys is not None:
            if self._ys is not None:
                self.__vertices = None
            self._ys = ys

        if zs is not None:
            if self._zs is not None:
                self.__vertices = None
            self._zs = zs

        if self.__vertices is None:
            vertices, indices = create_grid_mesh(self._xs, self._ys, self._zs)
            self.__meshdata.set_vertices(vertices)
            self.__meshdata.set_faces(indices)

        if colors is not None:
            self.__colors = colors
            self.__meshdata.set_vertex_colors(colors.reshape(colors.shape[0] * colors.shape[1], colors.shape[2]))
            
        MeshVisual.set_data(self, meshdata=self.__meshdata)

        # shape = xs.shape
        # if isinstance(colors, np.ndarray) and colors.ndim == 3:
        #     colors = colors.reshape((shape[0] * shape[1], colors.shape[2]))
        
        # colors = ColorArray(colors).rgba
        # if vertex_colors is None:
        #     vertex_colors = np.resize(colors, (shape[0] * shape[1], 4))

        # MeshVisual.__init__(self, vertices, indices,
        #                     vertex_colors=vertex_colors,
        #                     face_colors=face_colors,
        #                     color='purple',
        #                     shading=shading)

    def draw(self, transforms):
        MeshVisual.draw(self, transforms)
