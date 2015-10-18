
from .mesh import MeshVisual
from ..geometry import create_grid_mesh, MeshData


class GridMeshVisual(MeshVisual):
    """Displays a mesh in a Cartesian grid about x,y,z coordinates.

    This makes it simple to generate a mesh from e.g. the output
    of numpy.meshgrid.

    All arguments are optional, though they can be changed
    individually later with the set_data method.

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
    colors : ndarray | None
        The colors of the points of the mesh. Should be either a
        (width, height, 4) array of rgba colors at each grid point or
        a (width, height, 3) array of rgb colors at each grid point.
        Defaults to None, in which case the default color of a
        MeshVisual is used.
    shading : str | None
        Same as for the `MeshVisual` class. Defaults to 'smooth'.
    **kwargs :
        Other arguments are passed directly to MeshVisual.
    """

    def __init__(self, xs, ys, zs, colors=None, shading='smooth',
                 **kwargs):

        if xs is None or ys is None or zs is None:
            raise ValueError('All of xs, ys and zs must be initialised '
                             'with arrays.')

        self._xs = None
        self._ys = None
        self._zs = None

        self.__vertices = None
        self.__meshdata = MeshData()

        MeshVisual.__init__(self, shading=shading, **kwargs)
        self.set_data(xs, ys, zs, colors)

    def set_data(self, xs=None, ys=None, zs=None, colors=None):
        '''Update the mesh data.

        Parameters
        ----------
        xs : ndarray | None
            A 2d array of x coordinates for the vertices of the mesh.
        ys : ndarray | None
            A 2d array of y coordinates for the vertices of the mesh.
        zs : ndarray | None
            A 2d array of z coordinates for the vertices of the mesh.
        colors : ndarray | None
            The color at each point of the mesh. Must have shape
            (width, height, 4) or (width, height, 3) for rgba or rgb
            color definitions respectively.
        '''

        if xs is None:
            xs = self._xs
            self.__vertices = None

        if ys is None:
            ys = self._ys
            self.__vertices = None

        if zs is None:
            zs = self._zs
            self.__vertices = None

        if self.__vertices is None:
            vertices, indices = create_grid_mesh(xs, ys, zs)
            self._xs = xs
            self._ys = ys
            self._zs = zs

        if self.__vertices is None:
            vertices, indices = create_grid_mesh(self._xs, self._ys, self._zs)
            self.__meshdata.set_vertices(vertices)
            self.__meshdata.set_faces(indices)

        if colors is not None:
            self.__meshdata.set_vertex_colors(colors.reshape(
                colors.shape[0] * colors.shape[1], colors.shape[2]))

        MeshVisual.set_data(self, meshdata=self.__meshdata)
