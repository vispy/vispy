import numpy as np
from numpy.testing import assert_array_almost_equal

from vispy.testing import run_tests_if_main
from vispy.geometry.triangulation import Triangulation as T


def assert_array_eq(a, b):
    assert a.shape == b.shape
    assert a.dtype == b.dtype
    mask = np.isnan(a)
    assert np.all(np.isnan(b[mask]))
    assert np.all(a[~mask] == b[~mask])


def test_intersect_edge_arrays():
    global t
    pts = np.array([
        [0., 0.],
        [0., 10.],
        [5., 0.],
        [-5., 0.],
        [-1., 11.],
        [1., 9.],
    ])
    edges = np.array([
        [0, 1],
        [2, 3],
        [0, 3],
        [4, 5],
        [4, 1],
        [0, 1],
    ])
    
    lines = pts[edges]
    t = T(pts, edges)
    
    # intersect array of one edge with a array of many edges
    intercepts = t._intersect_edge_arrays(lines[0:1], lines[1:])
    expect = np.array([0.5, 0.0, 0.5, 1.0, np.nan])
    assert_array_eq(intercepts, expect)

    # intersect every line with every line
    intercepts = t._intersect_edge_arrays(lines[:, np.newaxis, ...], 
                                          lines[np.newaxis, ...])
    for i in range(lines.shape[0]):
        int2 = t._intersect_edge_arrays(lines[i], lines)
        assert_array_eq(intercepts[i], int2)


def test_edge_intersections():
    global t
    pts = np.array([
        [0, 0],
        [1, 0],
        [1, 1],
        [0, 1],
        [0, 0.5],  # three edges intersect here
        [2, 0.5],
        [-1, 0.2],
        [2, 0.8],
        [-1, 1],
        [0, 0.5],
    ])
    edges = np.array([
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 0],
        [4, 5],
        [6, 7],
        [8, 9],
    ])
    
    t = T(pts, edges)
    
    # first test find_edge_intersections
    cuts = t._find_edge_intersections()
    expect = {
        0: [],
        1: [(0.5, [1., 0.5]), 
            (0.6, [1., 0.6])],
        2: [],
        3: [(0.5, [0., 0.5]), 
            (0.6, [0., 0.4])],
        4: [(0.25, [0.5, 0.5]), 
            (0.5, [1., 0.5])],
        5: [(1./3., [0., 0.4]), 
            (0.5, [0.5, 0.5]), 
            (2./3., [1., 0.6])],
    }
        
    assert len(expect) == len(cuts)
    for k, v in expect.items():
        assert len(v) == len(cuts[k])
        for i, ecut in enumerate(v):
            vcut = cuts[k][i]
            assert len(vcut) == len(ecut)
            for j in range(len(vcut)):
                assert_array_almost_equal(np.array(ecut[j]), np.array(vcut[j]))
                
    # next test that we can split the edges correctly
    t._split_intersecting_edges()
    pts = np.array([[0., 0.],
                    [1., 0.],
                    [1., 1.],
                    [0., 1.],
                    [0., 0.5],
                    [2., 0.5],
                    [-1., 0.2],
                    [2., 0.8],
                    [-1., 1.],
                    [0., 0.5],
                    [1., 0.5],
                    [1., 0.6],
                    [0., 0.5],
                    [0., 0.4],
                    [0.5, 0.5],
                    [1., 0.5],
                    [0., 0.4],
                    [0.5, 0.5],
                    [1., 0.6]])
    edges = np.array([[0, 1],
                      [1, 10],
                      [2, 3],
                      [3, 12],
                      [4, 14],
                      [6, 16],
                      [8, 9],
                      [10, 11],
                      [11, 2],
                      [12, 13],
                      [13, 0],
                      [14, 15],
                      [15, 5],
                      [16, 17],
                      [17, 18],
                      [18, 7]])
    
    assert_array_almost_equal(pts, t.pts)
    assert np.all(edges == t.edges)

    # Test _nearly_ parallel lines. 
    pts = np.array([[0., 0.],
                    [1.62434542,  0.],
                    [1.62434542, -0.61175638],
                    [1.09617364, -0.61175638]])
    
    edges = np.array([[0, 1], [1, 2], [2, 3], [3, 0]])
    t = T(pts, edges)
    for edge, cuts in t._find_edge_intersections().items():
        assert len(cuts) == 0

    
def test_merge_duplicate_points():
    global t
    pts = np.array([
        [0, 0],
        [1, 1], 
        [0.1, 0.7],
        [2, 3],
        [0, 0],
        [0.1, 0.7], 
        [5, 6],
    ])
    edges = np.array([
        [0, 6],
        [1, 5],
        [2, 4],
        [3, 6],
        [4, 5],
    ])
    
    t = T(pts, edges)
    t._merge_duplicate_points()

    pts = np.array([
        [0, 0],
        [1, 1], 
        [0.1, 0.7],
        [2, 3],
        [5, 6],
    ])
    edges = np.array([
        [0, 4],
        [1, 2],
        [2, 0],
        [3, 4],
        [0, 2],
    ])
    assert np.allclose(t.pts, pts)
    assert np.all(t.edges == edges)


def test_initialize():
    # check points are correctly sorted
    # check artificial points are outside bounds of all others
    # check tops / bottoms
    pass


def test_utility_methods():
    global t
    pts = np.array([
        [0, 0],
        [1, 0],
        [2, 0], 
        [3, 0],
        [1.5, 2],
        [1.5, -2],
    ])
    edges = np.array([
        [4, 5],  # edge cuts through triangle (1, 2, 4) 
    ])

    t = T(pts, edges)
    # skip initialization and just simulate being part-way through 
    # triangulation
    for tri in [[0, 1, 4], [1, 2, 4], [2, 3, 4]]:
        t._add_tri(*tri)
    
    # find_cut_triangle
    assert t._find_cut_triangle((4, 5)) == (4, 1, 2)
    
    # orientation
    assert t._orientation((4, 5), 0) == 1
    assert t._orientation((4, 5), 1) == 1
    assert t._orientation((4, 5), 2) == -1
    assert t._orientation((4, 5), 3) == -1
    assert t._orientation((4, 5), 4) == 0
    assert t._orientation((4, 5), 5) == 0
    
    # distance
    dist = ((t.pts[0]-t.pts[1])**2).sum()**0.5
    assert t._distance(t.pts[0], t.pts[1]) == dist

    # adjacent_tri
    assert t._adjacent_tri((1, 4), 0) == (4, 1, 2)
    assert t._adjacent_tri((0, 4), 1) is None
    assert t._adjacent_tri((1, 4), (1, 4, 0)) == (4, 1, 2)
    assert t._adjacent_tri((0, 4), (1, 4, 0)) is None
    try:
        t._adjacent_tri((1, 4), 5)
    except RuntimeError:
        pass
    else:
        raise Exception("Expected RuntimeError.")

    # edges_intersect
    assert not t._edges_intersect((0, 1), (1, 2))
    assert not t._edges_intersect((0, 2), (1, 2))
    assert t._edges_intersect((4, 5), (1, 2))

    # is_constraining_edge
    assert t._is_constraining_edge((4, 5))
    assert t._is_constraining_edge((5, 4))
    assert not t._is_constraining_edge((3, 5))
    assert not t._is_constraining_edge((3, 2))


def test_projection():
    pts = np.array([[0, 0],
                    [5, 0],
                    [1, 2],
                    [3, 4]])
    t = T(pts, np.zeros((0, 2)))
    
    a, b, c, d = pts
    assert np.allclose(t._projection(a, c, b), [1, 0]) 
    assert np.allclose(t._projection(b, c, a), [1, 0]) 
    assert np.allclose(t._projection(a, d, b), [3, 0]) 
    assert np.allclose(t._projection(b, d, a), [3, 0]) 
    assert np.allclose(t._projection(a, b, c), [1, 2]) 
    assert np.allclose(t._projection(c, b, a), [1, 2]) 

    
def test_random(): 
    # Just test that these triangulate without exception.
    # TODO: later on, we can turn this same test into an image comparison
    # with Polygon.
    N = 10
    np.random.seed(0)
    
    for i in range(4):
        pts = np.random.normal(size=(N, 2))
        edges = np.zeros((N, 2), dtype=int)
        edges[:, 0] = np.arange(N)
        edges[:, 1] = np.arange(1, N+1) % N
    
        t = T(pts, edges)
        t.triangulate()
    
    theta = np.linspace(0, 2*np.pi, 11)[:-1]
    pts = np.hstack([np.cos(theta)[:, np.newaxis], 
                    np.sin(theta)[:, np.newaxis]])
    pts[::2] *= 0.4
    edges = np.empty((pts.shape[0], 2), dtype=np.uint)
    edges[:, 0] = np.arange(pts.shape[0])
    edges[:, 1] = edges[:, 0] + 1
    edges[-1, 1] = 0
    t = T(pts, edges)
    t.triangulate()
    
    # much larger test
    # this should pass, but takes forever..
    #N = 4000
    #pts = np.random.normal(size=(N, 2))
    #pts = np.cumsum(pts, axis=0)
    #edges = np.zeros((N, 2), dtype=int)
    #edges[:,0] = np.arange(N)
    #edges[:,1] = np.arange(1,N+1) % N
    
    #t = T(pts, edges)
    #t.triangulate()


def test_orthogonal():
    # make lines that are entirely vertical / horizontal
    np.random.seed(1)
    N = 100
    pts = [[0, 0]]
    for i in range(N - 1):
        p = pts[-1][:]
        p[i % 2] += np.random.normal()
        pts.append(p)
    pts = np.array(pts)
    edges = np.zeros((N, 2), dtype=int)
    edges[:, 0] = np.arange(N)
    edges[:, 1] = np.arange(1, N + 1) % N
    
    t = T(pts, edges)
    t.triangulate()

    
def test_edge_event():
    # mode 1
    pts = np.array([[0, 0],
                    [5, -10],
                    [10, 0],
                    [6, -5],
                    [5, 5],
                    ])
    inds = np.arange(pts.shape[0])[:, np.newaxis]
    edges = np.hstack([inds, np.roll(inds, -1)])
    
    t = T(pts, edges)
    t.triangulate()

    t = T(pts * [-1, 1], edges)
    t.triangulate()
    
    # mode 2
    pts = np.array([[0, 0],
                    [10, 0],
                    [20, 0],
                    [5, 11],
                    ])
    inds = np.arange(pts.shape[0])[:, np.newaxis]
    edges = np.hstack([inds, np.roll(inds, -1)])
    
    t = T(pts, edges)
    t.triangulate()

    t = T(pts * [-1, 1], edges)
    t.triangulate()
    
    # mode 1, 2
    pts = np.array([[0, 0],
                    [10, 0],
                    [20, 0],
                    [5, 11],
                    [9, 10],
                    [0, 20],
                    ])
    inds = np.arange(pts.shape[0])[:, np.newaxis]
    edges = np.hstack([inds, np.roll(inds, -1)])
    
    t = T(pts, edges)
    t.triangulate()

    t = T(pts * [-1, 1], edges)
    t.triangulate()

    # mode 2, 1
    pts = np.array([[0, 0],
                    [10, 0],
                    [20, 0],
                    [15, 8],
                    [15, 1],
                    [-5, 10],
                    ])
    inds = np.arange(pts.shape[0])[:, np.newaxis]
    edges = np.hstack([inds, np.roll(inds, -1)])
    
    t = T(pts, edges)
    t.triangulate()

    t = T(pts * [-1, 1], edges)
    t.triangulate()
    
    # mode 2, 1 with many triangles
    pts = np.array([[0, 10],
                    [2, 8],
                    [4, 6],
                    [6, 4],
                    [8, 2],
                    [10, 0],
                    
                    [20, 5],
                    [20, 20],
                    
                    [2, 13],
                    [4, 11],
                    [6, 9],
                    [8, 7],
                    [10, 5],
                    
                    [10, 1],
                    [0, 15],
                    ])
    inds = np.arange(pts.shape[0])[:, np.newaxis]
    edges = np.hstack([inds, np.roll(inds, -1)])
    
    t = T(pts, edges)
    t.triangulate()

    t = T(pts * [-1, 1], edges)
    t.triangulate()

    # mode 1, 2, 1, 2, 1
    pts = np.array([[0, 10],
                    [2, 9],
                    [4, 8],
                    [6, 7],
                    [8, 6],
                    [10, 5],
                    
                    [20, 5],
                    [20, 20],
                    
                    [2, 11],
                    [19, 19],
                    [6, 9],
                    [19, 18],
                    [10, 7],
                    
                    [11, 5.1],
                    [0, 11.1],
                    ])
    inds = np.arange(pts.shape[0])[:, np.newaxis]
    edges = np.hstack([inds, np.roll(inds, -1)])
    
    t = T(pts, edges)
    t.triangulate()

    t = T(pts * [-1, 1], edges)
    t.triangulate()

    # mode 2, 1, 2, 1
    pts = np.array([[0, 10],
                    [2, 9],
                    [4, 8],
                    [6, 7],
                    [8, 6],
                    [10, 5],
                    
                    [20, 5],
                    [20, 20],
                    
                    [6, 9],
                    [19, 18],
                    [10, 7],
                    
                    [11, 5.1],
                    [0, 11.1],
                    ])
    inds = np.arange(pts.shape[0])[:, np.newaxis]
    edges = np.hstack([inds, np.roll(inds, -1)])
    
    t = T(pts, edges)
    t.triangulate()

    t = T(pts * [-1, 1], edges)
    t.triangulate()
    
    # 1, 2  upper/lower polygon order check
    pts = np.array([[-5, 0],
                    [-3, 0],
                    [10, 0],
                    [15, 15],
                    [4, 9],
                    [6, 8.8],
                    [9, 10],
                    ])
    inds = np.arange(pts.shape[0])[:, np.newaxis]
    edges = np.hstack([inds, np.roll(inds, -1)])
    
    t = T(pts, edges)
    t.triangulate()

    t = T(pts * [-1, 1], edges)
    t.triangulate()


run_tests_if_main()
