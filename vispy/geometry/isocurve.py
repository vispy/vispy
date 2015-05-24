# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from __future__ import division

import numpy as np


def isocurve(data, level, connected=False, extend_to_edge=False):
    """
    Generate isocurve from 2D data using marching squares algorithm.

    Parameters
    ----------
    data : ndarray
        2D numpy array of scalar values
    level : float
        The level at which to generate an isosurface
    connected : bool
        If False, return a single long list of point pairs
        If True, return multiple long lists of connected point 
        locations. (This is slower but better for drawing 
        continuous lines)
    extend_to_edge : bool
        If True, extend the curves to reach the exact edges of 
        the data. 
    """    
    # This function is SLOW; plenty of room for optimization here.
    
    if extend_to_edge:
        d2 = np.empty((data.shape[0]+2, data.shape[1]+2), dtype=data.dtype)
        d2[1:-1, 1:-1] = data
        d2[0, 1:-1] = data[0]
        d2[-1, 1:-1] = data[-1]
        d2[1:-1, 0] = data[:, 0]
        d2[1:-1, -1] = data[:, -1]
        d2[0, 0] = d2[0, 1]
        d2[0, -1] = d2[1, -1]
        d2[-1, 0] = d2[-1, 1]
        d2[-1, -1] = d2[-1, -2]
        data = d2
    
    side_table = [
        [],
        [0, 1],
        [1, 2],
        [0, 2],
        [0, 3],
        [1, 3],
        [0, 1, 2, 3],
        [2, 3],
        [2, 3],
        [0, 1, 2, 3],
        [1, 3],
        [0, 3],
        [0, 2],
        [1, 2],
        [0, 1],
        []
    ]
    
    edge_key = [
        [(0, 1), (0, 0)],
        [(0, 0), (1, 0)],
        [(1, 0), (1, 1)],
        [(1, 1), (0, 1)]
    ]
    
    level = float(level)
    lines = []
    
    # mark everything below the isosurface level
    mask = data < level
    
    ## make four sub-fields and compute indexes for grid cells
    index = np.zeros([x-1 for x in data.shape], dtype=np.ubyte)
    fields = np.empty((2, 2), dtype=object)
    slices = [slice(0, -1), slice(1, None)]
    for i in [0, 1]:
        for j in [0, 1]:
            fields[i, j] = mask[slices[i], slices[j]]
            vertIndex = i+2*j
            index += (fields[i, j] * 2**vertIndex).astype(np.ubyte)
    
    # add lines
    for i in range(index.shape[0]):                 # data x-axis
        for j in range(index.shape[1]):             # data y-axis     
            sides = side_table[index[i, j]]
            for l in range(0, len(sides), 2):     # faces for this grid cell
                edges = sides[l:l+2]
                pts = []
                for m in [0, 1]:      # points in this face
                    # p1, p2 are points at either side of an edge
                    p1 = edge_key[edges[m]][0] 
                    p2 = edge_key[edges[m]][1]
                    # v1 and v2 are the values at p1 and p2
                    v1 = data[i+p1[0], j+p1[1]] 
                    v2 = data[i+p2[0], j+p2[1]]
                    f = (level-v1) / (v2-v1)
                    fi = 1.0 - f
                    # interpolate between corners
                    p = (p1[0]*fi + p2[0]*f + i + 0.5, 
                         p1[1]*fi + p2[1]*f + j + 0.5)
                    if extend_to_edge:
                        # check bounds
                        p = (min(data.shape[0]-2, max(0, p[0]-1)),
                             min(data.shape[1]-2, max(0, p[1]-1)))
                    if connected:
                        gridKey = (i + (1 if edges[m] == 2 else 0), 
                                   j + (1 if edges[m] == 3 else 0), 
                                   edges[m] % 2)
                        # give the actual position and a key identifying the 
                        # grid location (for connecting segments)
                        pts.append((p, gridKey))
                    else:
                        pts.append(p)
                
                lines.append(pts)

    if not connected:
        return lines
                
    # turn disjoint list of segments into continuous lines

    points = {}  # maps each point to its connections
    for a, b in lines:
        if a[1] not in points:
            points[a[1]] = []
        points[a[1]].append([a, b])
        if b[1] not in points:
            points[b[1]] = []
        points[b[1]].append([b, a])

    # rearrange into chains
    for k in list(points.keys()):
        try:
            chains = points[k]
        except KeyError:  # already used this point elsewhere
            continue
        for chain in chains:
            x = None
            while True:
                if x == chain[-1][1]:
                    break  # nothing left to do on this chain
                    
                x = chain[-1][1]
                if x == k:
                    # chain has looped; we're done and can ignore the opposite
                    # chain
                    break
                y = chain[-2][1]
                connects = points[x]
                for conn in connects[:]:
                    if conn[1][1] != y:
                        chain.extend(conn[1:])
                del points[x]
            if chain[0][1] == chain[-1][1]:
                # looped chain; no need to continue the other direction
                chains.pop()
                break
                
    # extract point locations 
    lines = []
    for chain in points.values():
        if len(chain) == 2:
            # join together ends of chain
            chain = chain[1][1:][::-1] + chain[0]
        else:
            chain = chain[0]
        lines.append([pt[0] for pt in chain])
    
    return lines  # a list of pairs of points
