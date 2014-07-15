import numpy as np
from numpy.testing import assert_array_equal

from vispy.util.meshdata import MeshData


def test_meshdata():
    """Test meshdata Class
       It's a unit square cut in two trangular element
    """
    square_vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
                               dtype=np.float)
    square_faces = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint)
    square_normals = np.array([[0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1]],
                              dtype=np.float)
    square_edges = np.array([[0, 1], [0, 2], [0, 3], [1, 2], [2, 3]],
                            dtype=np.uint)

    mesh = MeshData(vertices=square_vertices, faces=square_faces)
    # test vertices and faces assignement
    assert_array_equal(square_vertices, mesh.vertices())
    assert_array_equal(square_faces, mesh.faces())
    # test normals calculus
    assert_array_equal(square_normals, mesh.vertex_normals())
    # test edge calculus
    assert_array_equal(square_edges, mesh.edges())

if __name__ == '__main__':
    test_meshdata()
