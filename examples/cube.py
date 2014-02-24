# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import numpy as np


def cube():
    """ Generate vertices & indices for a filled and outlined cube """

    vtype = [('a_position', np.float32, 3),
             ('a_texcoord', np.float32, 2),
             ('a_normal'  , np.float32, 3),
             ('a_color',    np.float32, 4)] 
    itype = np.uint32

    # Vertices positions
    p = np.array([[ 1, 1, 1], [-1, 1, 1], [-1,-1, 1], [ 1,-1, 1],
                  [ 1,-1,-1], [ 1, 1,-1], [-1, 1,-1], [-1,-1,-1]])

    # Face Normals
    n = np.array([[ 0, 0, 1], [ 1, 0, 0], [ 0, 1, 0] ,
                  [-1, 0, 1], [ 0,-1, 0], [ 0, 0,-1]])

    # Vertice colors
    c = np.array([[0, 1, 1, 1], [0, 0, 1, 1], [0, 0, 0, 1], [0, 1, 0, 1],
                  [1, 1, 0, 1], [1, 1, 1, 1], [1, 0, 1, 1], [1, 0, 0, 1]])

    # Texture coords
    t = np.array([[0, 0], [0, 1], [1, 1], [1, 0]])

    faces_p = [0,1,2,3, 0,3,4,5, 0,5,6,1, 1,6,7,2, 7,4,3,2, 4,7,6,5]
    faces_c = [0,1,2,3, 0,3,4,5, 0,5,6,1, 1,6,7,2, 7,4,3,2, 4,7,6,5]
    faces_n = [0,0,0,0, 1,1,1,1, 2,2,2,2, 3,3,3,3, 4,4,4,4, 5,5,5,5]
    faces_t = [0,1,2,3, 0,1,2,3, 0,1,2,3, 0,1,2,3, 0,1,2,3, 0,1,2,3]
    
    vertices = np.zeros(24,vtype)
    vertices['a_position'] = p[faces_p]
    vertices['a_normal'] = n[faces_n]
    vertices['a_color'] = c[faces_c]
    vertices['a_texcoord'] = t[faces_t]

    filled = np.resize( np.array([0,1,2,0,2,3], dtype=np.uint32), 6*(2*3))
    filled += np.repeat( 4*np.arange(6), 6)

    outline = np.resize( np.array([0,1,1,2,2,3,3,0], dtype=np.uint32), 6*(2*4))
    outline += np.repeat( 4*np.arange(6), 8)

    return vertices, filled, outline
