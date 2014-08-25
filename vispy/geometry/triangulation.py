# -*- coding: utf8 -*-
from __future__ import division, print_function

import numpy as np
from ..ext.ordereddict import OrderedDict
from itertools import permutations


class Triangulation(object):
    """Constrained delaunay triangulation

    Implementation based on:

        * Domiter, V. and Žalik, B. Sweep‐line algorithm for constrained
          Delaunay triangulation

    Parameters
    ----------
    pts : array
        Nx2 array of points.
    edges : array
        Nx2 array of edges (dtype=int).

    Notes
    -----
    * Delaunay legalization is not yet implemented. This produces a proper
      triangulation, but adding legalisation would produce fewer thin
      triangles.
    * The pts and edges arrays may be modified.
    """
    def __init__(self, pts, edges):
        self.pts = pts[:, :2].astype(np.float32)
        self.edges = edges
        if self.pts.ndim != 2 or self.pts.shape[1] != 2:
            raise TypeError('pts argument must be ndarray of shape (N, 2).')
        if self.edges.ndim != 2 or self.edges.shape[1] != 2:
            raise TypeError('edges argument must be ndarray of shape (N, 2).')
        
        # described in initialize()
        self.front = None
        self.tris = OrderedDict()
        self.edges_lookup = {}
        
    def normalize(self):
        # Clean up data   (not discussed in original publication)
        
        # (i) Split intersecting edges. Every edge that intersects another 
        #     edge or point is split. This extends self.pts and self.edges.
        self.split_intersecting_edges()
        
        # (ii) Merge identical points. If any two points are found to be equal,
        #      the second is removed and the edge table is updated accordingly. 
        self.merge_duplicate_points()

        # (iii) Remove duplicate edges
        # TODO

    def initialize(self):
        self.normalize()
        ## Initialization (sec. 3.3)

        # sort points by y, then x
        flat_shape = self.pts.shape[0] * self.pts.shape[1]
        pts = self.pts.reshape(flat_shape).view([('x', np.float32), 
                                                 ('y', np.float32)])
        order = np.argsort(pts, order=('y', 'x'))
        pts = pts[order]
        # update edges to match new point order
        invorder = np.argsort(order)
        self.edges = invorder[self.edges]
        self.pts = pts.view(np.float32).reshape(len(pts), 2)

        # make artificial points P-1 and P-2
        xmax = self.pts[:, 0].max()
        xmin = self.pts[:, 0].min()
        ymax = self.pts[:, 1].max()
        ymin = self.pts[:, 1].min()
        xa = (xmax-xmin) * 0.3
        ya = (ymax-ymin) * 0.3
        p1 = (xmin - xa, ymin - ya)
        p2 = (xmax + xa, ymin - ya)

        # prepend artificial points to point list
        newpts = np.empty((self.pts.shape[0]+2, 2), dtype=float)
        newpts[0] = p1
        newpts[1] = p2
        newpts[2:] = self.pts
        self.pts = newpts
        self.edges += 2

        # find topmost point in each edge
        self.tops = self.edges.max(axis=1)
        self.bottoms = self.edges.min(axis=1)

        # inintialize sweep front
        # values in this list are indexes into self.pts
        self.front = [0, 2, 1]
        
        # empty triangle list. 
        # This will contain [(a, b, c), ...] where a,b,c are indexes into 
        # self.pts
        self.tris = OrderedDict()

        # For each triangle, maps (a, b): c
        # This is used to look up the thrid point in a triangle, given any 
        # edge. Since each edge has two triangles, they are independently 
        # stored as (a, b): c and (b, a): d
        self.edges_lookup = {}

    def triangulate(self):
        self.initialize()
        
        pts = self.pts
        front = self.front
        
        ## Begin sweep (sec. 3.4)
        for i in range(3, pts.shape[0]):
            pi = pts[i]
            #debug("========== New point %d: %s ==========" % (i, pi))
            
            # First, triangulate from front to new point
            # This applies to both "point events" (3.4.1) 
            # and "edge events" (3.4.2).

            # get index along front that intersects pts[i]
            l = 0
            while pts[front[l+1], 0] <= pi[0]:
                l += 1
            pl = pts[front[l]]
            
            # "(i) middle case"
            if pi[0] > pl[0]:  
                #debug("  mid case")
                # Add a single triangle connecting pi,pl,pr
                self.add_tri(front[l], front[l+1], i)
                front.insert(l+1, i)
            # "(ii) left case"
            else:
                #debug("  left case")
                # Add triangles connecting pi,pl,ps and pi,pl,pr
                self.add_tri(front[l], front[l+1], i)
                self.add_tri(front[l-1], front[l], i)
                front[l] = i
            
            #debug(front)
                
            # Continue adding triangles to smooth out front
            # (heuristics shown in figs. 9, 10)
            #debug("Smoothing front...")
            for direction in -1, 1:
                while True:
                    # Find point connected to pi
                    ind0 = front.index(i)
                    ind1 = ind0 + direction
                    ind2 = ind1 + direction
                    if ind2 < 0 or ind2 >= len(front):
                        break
                    
                    # measure angle made with front
                    p1 = pts[front[ind1]]
                    p2 = pts[front[ind2]]
                    err = np.geterr()
                    np.seterr(invalid='ignore')
                    try:
                        angle = np.arccos(self.cosine(pi, p1, p2))
                    finally:
                        np.seterr(**err)
                    
                    # if angle is < pi/2, make new triangle
                    #debug("Smooth angle:", pi, p1, p2, angle)
                    if angle > np.pi/2. or np.isnan(angle):
                        break
                    
                    assert (i != front[ind1] and 
                            front[ind1] != front[ind2] and 
                            front[ind2] != i)
                    self.add_tri(i, front[ind1], front[ind2], source='smooth1')
                    front.pop(ind1)
            #debug("Finished smoothing front.")
            
            # "edge event" (sec. 3.4.2)
            # remove any triangles cut by completed edges and re-fill 
            # the holes.
            if i in self.tops:
                for j in self.bottoms[self.tops == i]:
                    # Make sure edge (j, i) is present in mesh
                    # because edge event may have created a new front list
                    self.edge_event(i, j)  
                    front = self.front 
                
        self.finalize()
        
        self.tris = np.array(list(self.tris.keys()), dtype=int)
        
        #debug("Finished with %d tris:" % self.tris.shape[0])
        #debug(str(self.tris))
        
    def finalize(self):
        ## Finalize (sec. 3.5)

        # (i) Add bordering triangles to fill hull
        #debug("== Fill hull")
        front = list(OrderedDict.fromkeys(self.front))

        l = len(front) - 2
        k = 1
        while k < l-1:
            # if edges lie in counterclockwise direction, then signed area 
            # is positive
            if self.iscounterclockwise(front[k], front[k+1], front[k+2]):
                self.add_tri(front[k], front[k+1], front[k+2], legal=False, 
                             source='fill_hull')
                front.pop(k+1)
                l -= 1
                continue
            k += 1

        # (ii) Remove all triangles not inside the hull 
        #      (not described in article)
        #debug("== Remove triangles outside hull")

        tris = []  # triangles to check
        tri_state = {}  # 0 for outside, 1 for inside
        
        # find a starting triangle
        for t in self.tris:
            if 0 in t or 1 in t:
                tri_state[t] = 0
                tris.append(t)
                break
        
        while tris:
            #debug("iterate:", tris)
            next_tris = []
            for t in tris:
                v = tri_state[t]
                for i in (0, 1, 2):
                    edge = (t[i], t[(i + 1) % 3])
                    pt = t[(i + 2) % 3]
                    t2 = self.adjacent_tri(edge, pt)
                    if t2 is None:
                        continue
                    t2a = t2[1:3] + t2[0:1]
                    t2b = t2[2:3] + t2[0:2]
                    if t2 in tri_state or t2a in tri_state or t2b in tri_state:
                        continue
                    if self.is_constraining_edge(edge):
                        tri_state[t2] = 1 - v
                    else:
                        tri_state[t2] = v
                    next_tris.append(t2)
            tris = next_tris
        
        for t, v in tri_state.items():
            if v == 0:
                self.remove_tri(*t)

    def edge_event(self, i, j):
        """
        Force edge (i, j) to be present in mesh. 
        This works by removing intersected triangles and filling holes up to
        the cutting edge.
        """
        front_index = self.front.index(i)
        
        #debug("  == edge event ==")
        front = self.front

        # First just see whether this edge is already present
        # (this is not in the published algorithm)
        if (i, j) in self.edges_lookup or (j, i) in self.edges_lookup:
            #debug("    already added.")
            return
        #debug("    Edge (%d,%d) not added yet. Do edge event. (%s - %s)" % 
        #      (i, j, pts[i], pts[j]))
        
        # traverse in two different modes:
        #  1. If cutting edge is below front, traverse through triangles. These
        #     must be removed and the resulting hole re-filled. (fig. 12)
        #  2. If cutting edge is above the front, then follow the front until 
        #     crossing under again. (fig. 13)
        # We must be able to switch back and forth between these 
        # modes (fig. 14)

        # Collect points that draw the open polygons on either side of the 
        # cutting edge. Note that our use of 'upper' and 'lower' is not strict;
        # in some cases the two may be swapped.
        upper_polygon = [i]
        lower_polygon = [i]
        
        # Keep track of which section of the front must be replaced
        # and with what it should be replaced
        front_holes = []  # contains indexes for sections of front to remove
        
        next_tri = None   # next triangle to cut (already set if in mode 1)
        last_edge = None  # or last triangle edge crossed (if in mode 1)
        
        # Which direction to traverse front
        front_dir = 1 if self.pts[j][0] > self.pts[i][0] else -1
                
        # Initialize search state
        if self.edge_below_front((i, j), front_index):
            mode = 1  # follow triangles
            tri = self.find_cut_triangle((i, j))
            last_edge = self.edge_opposite_point(tri, i)
            next_tri = self.adjacent_tri(last_edge, i)
            assert next_tri is not None
            self.remove_tri(*tri)
            # todo: does this work? can we count on last_edge to be clockwise
            # around point i?
            lower_polygon.append(last_edge[1])
            upper_polygon.append(last_edge[0])
        else:
            mode = 2  # follow front

        # Loop until we reach point j
        while True:
            #debug("  == edge_event loop: mode %d ==" % mode)
            #debug("      front_holes:", front_holes, front)
            #debug("      front_index:", front_index)
            #debug("      next_tri:", next_tri)
            #debug("      last_edge:", last_edge)
            #debug("      upper_polygon:", upper_polygon)
            #debug("      lower_polygon:", lower_polygon)
            #debug("      =====")
            if mode == 1:
                # crossing from one triangle into another
                if j in next_tri:
                    #debug("    -> hit endpoint!")
                    # reached endpoint! 
                    # update front / polygons
                    upper_polygon.append(j)
                    lower_polygon.append(j)
                    #debug("    Appended to upper_polygon:", upper_polygon)
                    #debug("    Appended to lower_polygon:", lower_polygon)
                    self.remove_tri(*next_tri)
                    break
                else:
                    # next triangle does not contain the end point; we will
                    # cut one of the two far edges.
                    tri_edges = self.edges_in_tri_except(next_tri, last_edge)
                    
                    # select the edge that is cut
                    last_edge = self.intersected_edge(tri_edges, (i, j))
                    #debug("    set last_edge to intersected edge:", last_edge)
                    last_tri = next_tri
                    next_tri = self.adjacent_tri(last_edge, last_tri)
                    #debug("    set next_tri:", next_tri)
                    self.remove_tri(*last_tri)

                    # Crossing an edge adds one point to one of the polygons
                    if lower_polygon[-1] == last_edge[0]:
                        upper_polygon.append(last_edge[1])
                        #debug("    Appended to upper_polygon:", upper_polygon)
                    elif lower_polygon[-1] == last_edge[1]:
                        upper_polygon.append(last_edge[0])
                        #debug("    Appended to upper_polygon:", upper_polygon)
                    elif upper_polygon[-1] == last_edge[0]:
                        lower_polygon.append(last_edge[1])
                        #debug("    Appended to lower_polygon:", lower_polygon)
                    elif upper_polygon[-1] == last_edge[1]:
                        lower_polygon.append(last_edge[0])
                        #debug("    Appended to lower_polygon:", lower_polygon)
                    else:
                        raise RuntimeError("Something went wrong..")
                    
                    # If we crossed the front, go to mode 2
                    x = self.edge_in_front(last_edge)
                    if x >= 0:  # crossing over front
                        #debug("    -> crossed over front, prepare for mode 2")
                        mode = 2
                        next_tri = None
                        #debug("    set next_tri: None")
                        
                        # where did we cross the front?
                        # nearest to new point
                        front_index = x + (1 if front_dir == -1 else 0)
                        #debug("    set front_index:", front_index)
                        
                        # Select the correct polygon to be lower_polygon
                        # (because mode 2 requires this). 
                        # We know that last_edge is in the front, and 
                        # front[front_index] is the point _above_ the front. 
                        # So if this point is currently the last element in
                        # lower_polygon, then the polys must be swapped.
                        if lower_polygon[-1] == front[front_index]:
                            tmp = lower_polygon, upper_polygon
                            upper_polygon, lower_polygon = tmp
                            #debug('    Swap upper/lower polygons')
                        else:
                            assert upper_polygon[-1] == front[front_index]
                        
                    else:
                        assert next_tri is not None
                
            else:  # mode == 2
                # At each iteration, we require:
                #   * front_index is the starting index of the edge _preceding_
                #     the edge that will be handled in this iteration
                #   * lower_polygon is the polygon to which points should be
                #     added while traversing the front
                
                front_index += front_dir
                #debug("    Increment front_index: %d" % front_index)
                next_edge = (front[front_index], front[front_index+front_dir])
                #debug("    Set next_edge: %s" % repr(next_edge))
                
                assert front_index >= 0
                if front[front_index] == j:
                    # found endpoint!
                    #debug("    -> hit endpoint!")
                    lower_polygon.append(j)
                    upper_polygon.append(j)
                    #debug("    Appended to upper_polygon:", upper_polygon)
                    #debug("    Appended to lower_polygon:", lower_polygon)
                    break

                # Add point to lower_polygon. 
                # The conditional is because there are cases where the 
                # point was already added if we just crossed from mode 1.
                if lower_polygon[-1] != front[front_index]:
                    lower_polygon.append(front[front_index])
                    #debug("    Appended to lower_polygon:", lower_polygon)

                front_holes.append(front_index)
                #debug("    Append to front_holes:", front_holes)

                if self.edges_intersect((i, j), next_edge):
                    # crossing over front into triangle
                    #debug("    -> crossed over front, prepare for mode 1")
                    mode = 1
                    
                    last_edge = next_edge
                    #debug("    Set last_edge:", last_edge)
                    
                    # we are crossing the front, so this edge only has one
                    # triangle. 
                    next_tri = self.tri_from_edge(last_edge)
                    #debug("    Set next_tri:", next_tri)
                    
                    upper_polygon.append(front[front_index+front_dir])
                    #debug("    Appended to upper_polygon:", upper_polygon)
                #else:
                    #debug("    -> did not cross front..")
        
        #debug("Finished edge_event:")
        #debug("  front_holes:", front_holes)
        #debug("  upper_polygon:", upper_polygon)
        #debug("  lower_polygon:", lower_polygon)

        # (iii) triangluate empty areas
        
        #debug("Filling edge_event polygons...")
        for polygon in [lower_polygon, upper_polygon]:
            dist = self.distances_from_line((i, j), polygon)
            #debug("Distances:", dist)
            while len(polygon) > 2:
                ind = np.argmax(dist)
                #debug("Next index: %d" % ind)
                self.add_tri(polygon[ind], polygon[ind-1],
                             polygon[ind+1], legal=False, 
                             source='edge_event')
                polygon.pop(ind)
                dist.pop(ind)

        #debug("Finished filling edge_event polygons.")
        
        # update front by removing points in the holes (places where front 
        # passes below the cut edge)
        front_holes.sort(reverse=True)
        for i in front_holes:
            front.pop(i)

        #debug("Finished updating front after edge_event.")
        
    def find_cut_triangle(self, edge):
        """
        Return the triangle that has edge[0] as one of its vertices and is 
        bisected by edge.
        
        Return None if no triangle is found.
        """
        edges = []  # opposite edge for each triangle attached to edge[0]
        for tri in self.tris:
            if edge[0] in tri:
                edges.append(self.edge_opposite_point(tri, edge[0]))
                
        for oedge in edges:
            o1 = self.orientation(edge, oedge[0])
            o2 = self.orientation(edge, oedge[1]) 
            #debug(edge, oedge, o1, o2)
            #debug(self.pts[np.array(edge)])
            #debug(self.pts[np.array(oedge)])
            if o1 != o2:
                return (edge[0], oedge[0], oedge[1])
        
        return None

    def edge_in_front(self, edge):
        """ Return the index where *edge* appears in the current front.
        If the edge is not in the front, return -1
        """
        e = (list(edge), list(edge)[::-1])
        for i in range(len(self.front)-1):
            if self.front[i:i+2] in e:
                return i
        return -1

    def edge_opposite_point(self, tri, i):
        """ Given a triangle, return the edge that is opposite point i.
        Vertexes are returned in the same orientation as in tri.
        """
        ind = tri.index(i)
        return (tri[(ind+1) % 3], tri[(ind+2) % 3])

    def adjacent_tri(self, edge, i):
        """
        Given a triangle formed by edge and i, return the triangle that shares
        edge. *i* may be either a point or the entire triangle.
        """
        if not np.isscalar(i):
            i = [x for x in i if x not in edge][0]

        try:
            pt1 = self.edges_lookup[edge]
            pt2 = self.edges_lookup[(edge[1], edge[0])]
        except KeyError:
            return None
            
        if pt1 == i:
            return (edge[1], edge[0], pt2)
        elif pt2 == i:
            return (edge[1], edge[0], pt1)
        else:
            raise RuntimeError("Edge %s and point %d do not form a triangle "
                               "in this mesh." % (edge, i))

    def tri_from_edge(self, edge):
        """Return the only tri that contains *edge*. If two tris share this
        edge, raise an exception.
        """
        edge = tuple(edge)
        p1 = self.edges_lookup.get(edge, None)
        p2 = self.edges_lookup.get(edge[::-1], None)
        if p1 is None:
            if p2 is None:
                raise RuntimeError("No tris connected to edge %r" % (edge,))
            return edge + (p2,)
        elif p2 is None:
            return edge + (p1,)
        else:
            raise RuntimeError("Two triangles connected to edge %r" % (edge,))

    def edges_in_tri_except(self, tri, edge):
        """Return the edges in *tri*, excluding *edge*.
        """
        edges = [(tri[i], tri[(i+1) % 3]) for i in range(3)]
        try:
            edges.remove(tuple(edge))
        except ValueError:
            edges.remove(tuple(edge[::-1]))
        return edges

    def edge_below_front(self, edge, front_index):
        """Return True if *edge* is below the current front. 
        
        One of the points in *edge* must be _on_ the front, at *front_index*.
        """
        f0 = self.front[front_index-1]
        f1 = self.front[front_index+1]
        return (self.orientation(edge, f0) > 0 and 
                self.orientation(edge, f1) < 0)

    def is_constraining_edge(self, edge):
        mask1 = self.edges == edge[0]
        mask2 = self.edges == edge[1]
        return (np.any(mask1[:, 0] & mask2[:, 1]) or 
                np.any(mask2[:, 0] & mask1[:, 1]))
    
    def intersected_edge(self, edges, cut_edge):
        """ Given a list of *edges*, return the first that is intersected by
        *cut_edge*.
        """
        for edge in edges:
            if self.edges_intersect(edge, cut_edge):
                return edge

    def find_edge_intersections(self):
        """
        Return a dictionary containing, for each edge in self.edges, a list
        of the positions at which the edge should be split.
        """
        edges = self.pts[self.edges]
        cuts = {}  # { edge: [(intercept, point), ...], ... }
        for i in range(edges.shape[0]-1):
            # intersection of edge i onto all others
            int1 = self.intersect_edge_arrays(edges[i:i+1], edges[i+1:])
            # intersection of all edges onto edge i
            int2 = self.intersect_edge_arrays(edges[i+1:], edges[i:i+1])
        
            # select for pairs that intersect
            err = np.geterr()
            np.seterr(divide='ignore', invalid='ignore')
            try:
                mask1 = (int1 >= 0) & (int1 <= 1)
                mask2 = (int2 >= 0) & (int2 <= 1)
                mask3 = mask1 & mask2  # all intersections
            finally:
                np.seterr(**err)
            
            # compute points of intersection
            inds = np.argwhere(mask3)[:, 0]
            if len(inds) == 0:
                continue
            h = int2[inds][:, np.newaxis]
            pts = (edges[i, 0][np.newaxis, :] * (1.0 - h) + 
                   edges[i, 1][np.newaxis, :] * h)
            
            # record for all edges the location of cut points
            edge_cuts = cuts.setdefault(i, [])
            for j, ind in enumerate(inds):
                if 0 < int2[ind] < 1:
                    edge_cuts.append((int2[ind], pts[j]))
                if 0 < int1[ind] < 1:
                    other_cuts = cuts.setdefault(ind+i+1, [])
                    other_cuts.append((int1[ind], pts[j]))
        
        # sort all cut lists by intercept, remove duplicates
        for k, v in cuts.items():
            v.sort(key=lambda x: x[0])
            for i in range(len(v)-2, -1, -1):
                if v[i][0] == v[i+1][0]:
                    v.pop(i+1)
        return cuts

    def split_intersecting_edges(self):
        # we can do all intersections at once, but this has excessive memory
        # overhead.
        #int1 = self.intersection_matrix(edges)
        #int2 = int1.T
        
        # measure intersection point between all pairs of edges
        all_cuts = self.find_edge_intersections()

        # cut edges at each intersection
        add_pts = []
        add_edges = []
        for edge, cuts in all_cuts.items():
            if len(cuts) == 0:
                continue
            
            #debug("Edge intersections:", edge, self.edges[edge], 
            #      self.pts[self.edges[edge]], cuts)
            
            # add new points
            pt_offset = self.pts.shape[0] + len(add_pts)
            new_pts = [x[1] for x in cuts]
            add_pts.extend(new_pts)
            #debug("Add new points:", new_pts)
            
            # list of point indexes for all new edges
            pt_indexes = list(range(pt_offset, pt_offset + len(cuts)))
            pt_indexes.append(self.edges[edge, 1])
            
            # modify original edge
            self.edges[edge, 1] = pt_indexes[0]
            
            # add new edges
            new_edges = [[pt_indexes[i-1], pt_indexes[i]] 
                         for i in range(1, len(pt_indexes))] 
            add_edges.extend(new_edges)
            
        #debug("Adding %d points and %d edges to remove intersections." % 
        #      (len(add_pts), len(add_edges)))
        if add_pts:
            add_pts = np.array(add_pts, dtype=self.pts.dtype)
            self.pts = np.append(self.pts, add_pts, axis=0)
        if add_edges:
            add_edges = np.array(add_edges, dtype=self.edges.dtype)
            self.edges = np.append(self.edges, add_edges, axis=0)

    def merge_duplicate_points(self):
        # generate a list of all pairs (i,j) of identical points
        dups = []
        for i in range(self.pts.shape[0]-1):
            test_pt = self.pts[i:i+1]
            comp_pts = self.pts[i+1:]
            eq = test_pt == comp_pts
            eq = eq[:, 0] & eq[:, 1]
            for j in np.argwhere(eq)[:, 0]:
                dups.append((i, i+1+j))

        dups_arr = np.array(dups)
        # remove duplicate points
        pt_mask = np.ones(self.pts.shape[0], dtype=bool)
        for i, inds in enumerate(dups_arr):
            # remove j from points
            # (note we pull the index from the original dups instead of 
            # dups_arr because the indexes in pt_mask do not change)
            pt_mask[dups[i][1]] = False
            
            i, j = inds
            
            # rewrite edges to use i instead of j
            self.edges[self.edges == j] = i
            
            #assert not np.any(self.edges[:,0] == self.edges[:,1])
            
            # decrement all point indexes > j
            self.edges[self.edges > j] -= 1
            dups_arr[dups_arr > j] -= 1
            #assert not np.any(self.edges[:,0] == self.edges[:,1])
        
        self.pts = self.pts[pt_mask]
        
        # remove zero-length edges
        mask = self.edges[:, 0] != self.edges[:, 1]
        self.edges = self.edges[mask]
    
    def distance(self, A, B):
        # Distance between points A and B
        n = len(A)
        assert len(B) == n
        return np.linalg.norm(np.array(list(A)) - np.array(list(B)))

    def distances_from_line(self, edge, points):
        # Distance of a set of points from a given line
        #debug("distance from %r to %r" % (points, edge))
        e1 = self.pts[edge[0]]
        e2 = self.pts[edge[1]]
        distances = []
        for i in points:
            p = self.pts[i]
            proj = self.projection(e1, p, e2)
            distances.append(((p - proj)**2).sum()**0.5)
        assert distances[0] == 0 and distances[-1] == 0
        return distances

    def projection(self, a, b, c):
        """Return projection of (a,b) onto (a,c)
        Arguments are point locations, not indexes.
        """
        ab = b - a
        ac = c - a
        return a + ((ab*ac).sum() / (ac*ac).sum()) * ac

    def cosine(self, A, B, C):
        # Cosine of angle ABC
        a = ((C - B)**2).sum()
        b = ((C - A)**2).sum()
        c = ((B - A)**2).sum()
        d = (a + c - b) / ((4 * a * c)**0.5)
        return d

    #def barycentric(self, A, B, C, p, q, r):
        ## Cartesian coordinates of the point whose barycentric coordinates
        ## with respect to the triangle ABC are [p,q,r]
        #n = len(A)
        #assert len(B) == len(C) == n
        #s = p+q+r
        #p, q, r = p/s, q/s, r/s
        #return tuple([p*A[i]+q*B[i]+r*C[i] for i in range(n)])

    #def trilinear(self, A, B, C, alpha, beta, gamma):
        ## Cartesian coordinates of the point whose trilinear coordinates
        ## with respect to the triangle ABC are [alpha,beta,gamma]
        #a = distance(B, C)
        #b = distance(A, C)
        #c = distance(A, B)
        #return barycentric(A, B, C, a*alpha, b*beta, c*gamma)
                
    #def circuminfo(self, A, B, C):
        ## Cartesian coordinates of the circumcenter of triangle ABC
        #cosA = cosine(C, A, B)
        #cosB = cosine(A, B, C)
        #cosC = cosine(B, C, A)
        #cc = trilinear(A, B, C, cosA, cosB, cosC)
        ## returns circumcenter and circumradius
        #return cc, distance(cc, A)

    def iscounterclockwise(self, a, b, c):
        # Check if the points lie in counter-clockwise order or not
        A = self.pts[a]
        B = self.pts[b]
        C = self.pts[c]
        return np.cross(B-A, C-B) > 0

    def edges_intersect(self, edge1, edge2):
        """
        Return 1 if edges intersect completely (endpoints excluded)
        """
        h12 = self.intersect_edge_arrays(self.pts[np.array(edge1)], 
                                         self.pts[np.array(edge2)])
        h21 = self.intersect_edge_arrays(self.pts[np.array(edge2)], 
                                         self.pts[np.array(edge1)])
        err = np.geterr()
        np.seterr(divide='ignore', invalid='ignore')
        try:
            out = (0 < h12 < 1) and (0 < h21 < 1)
        finally:
            np.seterr(**err)
        return out

    def intersection_matrix(self, lines):
        """
        Return a 2D array of intercepts such that 
        intercepts[i, j] is the intercept of lines[i] onto lines[j].
        
        *lines* must be an array of point locations with shape (N, 2, 2), where
        the axes are (lines, points_per_line, xy_per_point).
        
        The intercept is described in intersect_edge_arrays().
        """
        return self.intersect_edge_arrays(lines[:, np.newaxis, ...], 
                                          lines[np.newaxis, ...])
        
    def intersect_edge_arrays(self, lines1, lines2):
        """Return the intercepts of all lines defined in *lines1* as they 
        intersect all lines in *lines2*. 
        
        Arguments are of shape (..., 2, 2), where axes are:
        
        0: number of lines
        1: two points per line
        2: x,y pair per point

        Lines are compared elementwise across the arrays (lines1[i] is compared
        against lines2[i]). If one of the arrays has N=1, then that line is
        compared against all lines in the other array.
        
        Returns an array of shape (N,) where each value indicates the intercept
        relative to the defined line segment. A value of 0 indicates 
        intersection at the first endpoint, and a value of 1 indicates 
        intersection at the second endpoint. Values between 1 and 0 are on the
        segment, whereas values outside 1 and 0 are off of the segment. 
        """
        # vector for each line in lines1
        l1 = lines1[..., 1, :] - lines1[..., 0, :]
        # vector for each line in lines2
        l2 = lines2[..., 1, :] - lines2[..., 0, :]
        # vector between first point of each line
        diff = lines1[..., 0, :] - lines2[..., 0, :]
        
        p = l1.copy()[..., ::-1]  # vectors perpendicular to l1
        p[..., 0] *= -1
        
        f = (l2 * p).sum(axis=-1)  # l2 dot p
        # tempting, but bad idea! 
        #f = np.where(f==0, 1, f)
        err = np.geterr()
        np.seterr(divide='ignore', invalid='ignore')
        try:
            h = (diff * p).sum(axis=-1) / f  # diff dot p / f
        finally:
            np.seterr(**err)
        
        return h

    def orientation(self, edge, point):
        """ Returns +1 if edge[0]->point is clockwise from edge[0]->edge[1], 
        -1 if counterclockwise, and 0 if parallel.
        """
        v1 = self.pts[point] - self.pts[edge[0]]
        v2 = self.pts[edge[1]] - self.pts[edge[0]]
        c = np.cross(v1, v2)  # positive if v1 is CW from v2
        return 1 if c > 0 else (-1 if c < 0 else 0)

    #def legalize(self, p):
        ### Legalize recursively - incomplete
        #return p  # disabled for now
    
        #f00, f11, p = p

        #debug("Legalizing points = {}, {}, {}".format(f00, f11, p))
        #a = pts[f00]
        #b = pts[f11]
        #c = pts[p]
        #cc, cr = circuminfo(a, b, c)
        #for point in pts:
        #    if np.all(point == a) or np.all(point == b) or np.all(point == c):
        #        continue
        #    elif distance(cc, point) < cr:
        #        #debug("Illegal point")
        #        #debug(point)
        #        pass

        #return (f00, f11, p)

    def add_tri(self, a, b, c, legal=True, source=None):
        # source is just used for #debugging
        #debug("Add triangle [%s]:" % source, (a, b, c))
        
        # sanity check
        assert a != b and b != c and c != a
        
        # ignore flat tris
        pa = self.pts[a]
        pb = self.pts[b]
        pc = self.pts[c]
        if np.all(pa == pb) or np.all(pb == pc) or np.all(pc == pa):
            #debug("   Triangle is flat; refusing to add.")
            return
        
        # check this tri is unique
        for t in permutations((a, b, c)):
            if t in self.tris:
                raise Exception("Cannot add %s; already have %s" % 
                                ((a, b, c), t))
        
        # TODO: should add to edges_lookup after legalization??
        if self.iscounterclockwise(a, b, c):
            #debug("    ", (a, b), (b, c), (c, a))
            assert (a, b) not in self.edges_lookup
            assert (b, c) not in self.edges_lookup
            assert (c, a) not in self.edges_lookup
            self.edges_lookup[(a, b)] = c
            self.edges_lookup[(b, c)] = a
            self.edges_lookup[(c, a)] = b
        else:
            #debug("    ", (b, a), (c, b), (a, c))
            assert (b, a) not in self.edges_lookup
            assert (c, b) not in self.edges_lookup
            assert (a, c) not in self.edges_lookup
            self.edges_lookup[(b, a)] = c
            self.edges_lookup[(c, b)] = a
            self.edges_lookup[(a, c)] = b
        
        #if legal:
            #tri = self.legalize((a, b, c))
        #else:
        tri = (a, b, c)
        
        self.tris[tri] = None

    def remove_tri(self, a, b, c):
        #debug("Remove triangle:", (a, b, c))
        
        for k in permutations((a, b, c)):
            if k in self.tris:
                break
        del self.tris[k]
        (a, b, c) = k

        if self.edges_lookup.get((a, b), -1) == c:
            #debug("    ", (a,b), (b,c), (c,a))
            del self.edges_lookup[(a, b)]
            del self.edges_lookup[(b, c)]
            del self.edges_lookup[(c, a)]
        elif self.edges_lookup.get((b, a), -1) == c:
            #debug("    ", (b,a), (c,b), (a,c))
            del self.edges_lookup[(b, a)]
            del self.edges_lookup[(a, c)]
            del self.edges_lookup[(c, b)]
        else:
            raise RuntimeError("Lost edges_lookup for tri (%d, %d, %d)" % 
                               (a, b, c))

        return k


# Note: using custom #debug instead of logging because 
# there are MANY messages and logger might be too expensive.
# After this becomes stable, we might just remove them altogether.
def debug(*args):
    print(*args)
