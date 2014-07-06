import numpy as np
from numpy.testing import assert_array_almost_equal

from vispy.util.geometry.triangulation import Triangulation as T

def assert_array_eq(a, b):
    assert a.shape == b.shape
    assert a.dtype == b.dtype
    mask = np.isnan(a)
    assert np.all(np.isnan(b[mask]))
    assert np.all(a[~mask] == b[~mask])

def test_intersect_edge_arrays():
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
    t = T(None, None)
    
    # intersect array of one edge with a array of many edges
    intercepts = t.intersect_edge_arrays(lines[0:1], lines[1:])
    expect = np.array([0.5, 0.0, 0.5, 1.0, np.nan])
    assert_array_eq(intercepts, expect)

    # intersect every line with every line
    intercepts = t.intersect_edge_arrays(lines[:, np.newaxis, ...], 
                                         lines[np.newaxis, ...])
    for i in range(lines.shape[0]):
        int2 = t.intersect_edge_arrays(lines[i], lines)
        assert_array_eq(intercepts[i], int2)


def test_find_edge_intersections():
    pts = np.array([
        [0, 0],
        [1, 0],
        [1, 1],
        [0, 1],
        [0, 0.5],
        [2, 0.5],
        [-1, 0.2],
        [2, 0.8],
        ])
    edges = np.array([
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 0],
        [4, 5],
        [6, 7],
        ])
    
    t = T(pts, edges)
    
    cuts = t.find_edge_intersections()
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
    for k,v in expect.items():
        assert len(v) == len(cuts[k])
        for i,ecut in enumerate(v):
            vcut = cuts[k][i]
            assert len(vcut) == len(ecut)
            for j in range(len(vcut)):
                assert_array_almost_equal(np.array(ecut[j]), np.array(vcut[j]))
    

if __name__ == '__main__':
    test_find_edge_intersections()
    
    