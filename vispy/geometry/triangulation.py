# -*- coding: utf-8 -*-

from __future__ import division, print_function

from itertools import permutations
import numpy as np

from collections import OrderedDict


class Triangulation(object):
    """Constrained delaunay triangulation

    Implementation based on [1]_.

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

    References
    ----------
    .. [1] Domiter, V. and Žalik, B. Sweep‐line algorithm for constrained
       Delaunay triangulation
    """

    def __init__(self, pts, edges):
        self.pts = pts[:, :2].astype(np.float32)
        self.edges = edges
        if self.pts.ndim != 2 or self.pts.shape[1] != 2:
            raise TypeError('pts argument must be ndarray of shape (N, 2).')
        if self.edges.ndim != 2 or self.edges.shape[1] != 2:
            raise TypeError('edges argument must be ndarray of shape (N, 2).')

        # described in initialize()
        self._front = None
        self.tris = OrderedDict()
        self._edges_lookup = {}

    def _normalize(self):
        # Clean up data   (not discussed in original publication)

        # (i) Split intersecting edges. Every edge that intersects another
        #     edge or point is split. This extends self.pts and self.edges.
        self._split_intersecting_edges()

        # (ii) Merge identical points. If any two points are found to be equal,
        #      the second is removed and the edge table is updated accordingly.
        self._merge_duplicate_points()

        # (iii) Remove duplicate edges
        # TODO

    def _initialize(self):
        self._normalize()
        # Initialization (sec. 3.3)

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
        self._tops = self.edges.max(axis=1)
        self._bottoms = self.edges.min(axis=1)

        # inintialize sweep front
        # values in this list are indexes into self.pts
        self._front = [0, 2, 1]

        # empty triangle list.
        # This will contain [(a, b, c), ...] where a,b,c are indexes into
        # self.pts
        self.tris = OrderedDict()

        # For each triangle, maps (a, b): c
        # This is used to look up the thrid point in a triangle, given any
        # edge. Since each edge has two triangles, they are independently
        # stored as (a, b): c and (b, a): d
        self._edges_lookup = {}

    def triangulate(self):
        """Do the triangulation."""
        self._initialize()

        pts = self.pts
        front = self._front

        # Begin sweep (sec. 3.4)
        for i in range(3, pts.shape[0]):
            pi = pts[i]

            # First, triangulate from front to new point
            # This applies to both "point events" (3.4.1)
            # and "edge events" (3.4.2).

            # get index along front that intersects pts[i]
            idx = 0
            while pts[front[idx+1], 0] <= pi[0]:
                idx += 1
            pl = pts[front[idx]]

            # "(i) middle case"
            if pi[0] > pl[0]:
                # Add a single triangle connecting pi,pl,pr
                self._add_tri(front[idx], front[idx+1], i)
                front.insert(idx+1, i)
            # "(ii) left case"
            else:
                # Add triangles connecting pi,pl,ps and pi,pl,pr
                self._add_tri(front[idx], front[idx+1], i)
                self._add_tri(front[idx-1], front[idx], i)
                front[idx] = i

            # Continue adding triangles to smooth out front
            # (heuristics shown in figs. 9, 10)
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
                        angle = np.arccos(self._cosine(pi, p1, p2))
                    finally:
                        np.seterr(**err)

                    # if angle is < pi/2, make new triangle
                    if angle > np.pi/2. or np.isnan(angle):
                        break

                    assert (i != front[ind1] and
                            front[ind1] != front[ind2] and
                            front[ind2] != i)
                    self._add_tri(i, front[ind1], front[ind2])
                    front.pop(ind1)

            # "edge event" (sec. 3.4.2)
            # remove any triangles cut by completed edges and re-fill
            # the holes.
            if i in self._tops:
                for j in self._bottoms[self._tops == i]:
                    # Make sure edge (j, i) is present in mesh
                    # because edge event may have created a new front list
                    self._edge_event(i, j)
                    front = self._front

        self._finalize()

        self.tris = np.array(list(self.tris.keys()), dtype=int)

    def _finalize(self):
        # Finalize (sec. 3.5)

        # (i) Add bordering triangles to fill hull
        front = list(OrderedDict.fromkeys(self._front))

        idx = len(front) - 2
        k = 1
        while k < idx-1:
            # if edges lie in counterclockwise direction, then signed area
            # is positive
            if self._iscounterclockwise(front[k], front[k+1], front[k+2]):
                self._add_tri(front[k], front[k+1], front[k+2])
                front.pop(k+1)
                idx -= 1
                continue
            k += 1

        # (ii) Remove all triangles not inside the hull
        #      (not described in article)

        tris = []  # triangles to check
        tri_state = {}  # 0 for outside, 1 for inside

        # find a starting triangle
        for t in self.tris:
            if 0 in t or 1 in t:
                tri_state[t] = 0
                tris.append(t)
                break

        while tris:
            next_tris = []
            for t in tris:
                v = tri_state[t]
                for i in (0, 1, 2):
                    edge = (t[i], t[(i + 1) % 3])
                    pt = t[(i + 2) % 3]
                    t2 = self._adjacent_tri(edge, pt)
                    if t2 is None:
                        continue
                    t2a = t2[1:3] + t2[0:1]
                    t2b = t2[2:3] + t2[0:2]
                    if t2 in tri_state or t2a in tri_state or t2b in tri_state:
                        continue
                    if self._is_constraining_edge(edge):
                        tri_state[t2] = 1 - v
                    else:
                        tri_state[t2] = v
                    next_tris.append(t2)
            tris = next_tris

        for t, v in tri_state.items():
            if v == 0:
                self._remove_tri(*t)

    def _edge_event(self, i, j):
        """Force edge (i, j) to be present in mesh.

        This works by removing intersected triangles and filling holes up to
        the cutting edge.
        """
        front_index = self._front.index(i)

        front = self._front

        # First just see whether this edge is already present
        # (this is not in the published algorithm)
        if (i, j) in self._edges_lookup or (j, i) in self._edges_lookup:
            return

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
        if self._edge_below_front((i, j), front_index):
            mode = 1  # follow triangles
            tri = self._find_cut_triangle((i, j))
            last_edge = self._edge_opposite_point(tri, i)
            next_tri = self._adjacent_tri(last_edge, i)
            assert next_tri is not None
            self._remove_tri(*tri)
            # todo: does this work? can we count on last_edge to be clockwise
            # around point i?
            lower_polygon.append(last_edge[1])
            upper_polygon.append(last_edge[0])
        else:
            mode = 2  # follow front

        # Loop until we reach point j
        while True:
            if mode == 1:
                # crossing from one triangle into another
                if j in next_tri:
                    # reached endpoint!
                    # update front / polygons
                    upper_polygon.append(j)
                    lower_polygon.append(j)
                    self._remove_tri(*next_tri)
                    break
                else:
                    # next triangle does not contain the end point; we will
                    # cut one of the two far edges.
                    tri_edges = self._edges_in_tri_except(next_tri, last_edge)

                    # select the edge that is cut
                    last_edge = self._intersected_edge(tri_edges, (i, j))
                    last_tri = next_tri
                    next_tri = self._adjacent_tri(last_edge, last_tri)
                    self._remove_tri(*last_tri)

                    # Crossing an edge adds one point to one of the polygons
                    if lower_polygon[-1] == last_edge[0]:
                        upper_polygon.append(last_edge[1])
                    elif lower_polygon[-1] == last_edge[1]:
                        upper_polygon.append(last_edge[0])
                    elif upper_polygon[-1] == last_edge[0]:
                        lower_polygon.append(last_edge[1])
                    elif upper_polygon[-1] == last_edge[1]:
                        lower_polygon.append(last_edge[0])
                    else:
                        raise RuntimeError("Something went wrong..")

                    # If we crossed the front, go to mode 2
                    x = self._edge_in_front(last_edge)
                    if x >= 0:  # crossing over front
                        mode = 2
                        next_tri = None

                        # where did we cross the front?
                        # nearest to new point
                        front_index = x + (1 if front_dir == -1 else 0)

                        # Select the correct polygon to be lower_polygon
                        # (because mode 2 requires this).
                        # We know that last_edge is in the front, and
                        # front[front_index] is the point _above_ the front.
                        # So if this point is currently the last element in
                        # lower_polygon, then the polys must be swapped.
                        if lower_polygon[-1] == front[front_index]:
                            tmp = lower_polygon, upper_polygon
                            upper_polygon, lower_polygon = tmp
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
                next_edge = (front[front_index], front[front_index+front_dir])

                assert front_index >= 0
                if front[front_index] == j:
                    # found endpoint!
                    lower_polygon.append(j)
                    upper_polygon.append(j)
                    break

                # Add point to lower_polygon.
                # The conditional is because there are cases where the
                # point was already added if we just crossed from mode 1.
                if lower_polygon[-1] != front[front_index]:
                    lower_polygon.append(front[front_index])

                front_holes.append(front_index)

                if self._edges_intersect((i, j), next_edge):
                    # crossing over front into triangle
                    mode = 1

                    last_edge = next_edge

                    # we are crossing the front, so this edge only has one
                    # triangle.
                    next_tri = self._tri_from_edge(last_edge)

                    upper_polygon.append(front[front_index+front_dir])

        # (iii) triangluate empty areas

        for polygon in [lower_polygon, upper_polygon]:
            dist = self._distances_from_line((i, j), polygon)
            while len(polygon) > 2:
                ind = np.argmax(dist)
                self._add_tri(polygon[ind], polygon[ind-1],
                              polygon[ind+1])
                polygon.pop(ind)
                dist.pop(ind)

        # update front by removing points in the holes (places where front
        # passes below the cut edge)
        front_holes.sort(reverse=True)
        for i in front_holes:
            front.pop(i)

    def _find_cut_triangle(self, edge):
        """
        Return the triangle that has edge[0] as one of its vertices and is
        bisected by edge.

        Return None if no triangle is found.
        """
        edges = []  # opposite edge for each triangle attached to edge[0]
        for tri in self.tris:
            if edge[0] in tri:
                edges.append(self._edge_opposite_point(tri, edge[0]))

        for oedge in edges:
            o1 = self._orientation(edge, oedge[0])
            o2 = self._orientation(edge, oedge[1])
            if o1 != o2:
                return (edge[0], oedge[0], oedge[1])

        return None

    def _edge_in_front(self, edge):
        """Return the index where *edge* appears in the current front.

        If the edge is not in the front, return -1
        """
        e = (list(edge), list(edge)[::-1])
        for i in range(len(self._front)-1):
            if self._front[i:i+2] in e:
                return i
        return -1

    def _edge_opposite_point(self, tri, i):
        """Given a triangle, return the edge that is opposite point i.

        Vertexes are returned in the same orientation as in tri.
        """
        ind = tri.index(i)
        return (tri[(ind+1) % 3], tri[(ind+2) % 3])

    def _adjacent_tri(self, edge, i):
        """Given a triangle formed by edge and i, return the triangle that shares
        edge. *i* may be either a point or the entire triangle.
        """
        if not np.isscalar(i):
            i = [x for x in i if x not in edge][0]

        try:
            pt1 = self._edges_lookup[edge]
            pt2 = self._edges_lookup[(edge[1], edge[0])]
        except KeyError:
            return None

        if pt1 == i:
            return (edge[1], edge[0], pt2)
        elif pt2 == i:
            return (edge[1], edge[0], pt1)
        else:
            raise RuntimeError("Edge %s and point %d do not form a triangle "
                               "in this mesh." % (edge, i))

    def _tri_from_edge(self, edge):
        """Return the only tri that contains *edge*.

        If two tris share this edge, raise an exception.
        """
        edge = tuple(edge)
        p1 = self._edges_lookup.get(edge, None)
        p2 = self._edges_lookup.get(edge[::-1], None)
        if p1 is None:
            if p2 is None:
                raise RuntimeError("No tris connected to edge %r" % (edge,))
            return edge + (p2,)
        elif p2 is None:
            return edge + (p1,)
        else:
            raise RuntimeError("Two triangles connected to edge %r" % (edge,))

    def _edges_in_tri_except(self, tri, edge):
        """Return the edges in *tri*, excluding *edge*."""
        edges = [(tri[i], tri[(i+1) % 3]) for i in range(3)]
        try:
            edges.remove(tuple(edge))
        except ValueError:
            edges.remove(tuple(edge[::-1]))
        return edges

    def _edge_below_front(self, edge, front_index):
        """Return True if *edge* is below the current front.

        One of the points in *edge* must be _on_ the front, at *front_index*.
        """
        f0 = self._front[front_index-1]
        f1 = self._front[front_index+1]
        return (self._orientation(edge, f0) > 0 and
                self._orientation(edge, f1) < 0)

    def _is_constraining_edge(self, edge):
        mask1 = self.edges == edge[0]
        mask2 = self.edges == edge[1]
        return (np.any(mask1[:, 0] & mask2[:, 1]) or
                np.any(mask2[:, 0] & mask1[:, 1]))

    def _intersected_edge(self, edges, cut_edge):
        """Given a list of *edges*, return the first that is intersected by
        *cut_edge*.
        """
        for edge in edges:
            if self._edges_intersect(edge, cut_edge):
                return edge

    def _find_edge_intersections(self):
        """Return a dictionary containing, for each edge in self.edges, a list
        of the positions at which the edge should be split.
        """
        edges = self.pts[self.edges]
        cuts = {}  # { edge: [(intercept, point), ...], ... }
        for i in range(edges.shape[0]-1):
            # intersection of edge i onto all others
            int1 = self._intersect_edge_arrays(edges[i:i+1], edges[i+1:])
            # intersection of all edges onto edge i
            int2 = self._intersect_edge_arrays(edges[i+1:], edges[i:i+1])

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

    def _split_intersecting_edges(self):
        # we can do all intersections at once, but this has excessive memory
        # overhead.

        # measure intersection point between all pairs of edges
        all_cuts = self._find_edge_intersections()

        # cut edges at each intersection
        add_pts = []
        add_edges = []
        for edge, cuts in all_cuts.items():
            if len(cuts) == 0:
                continue

            # add new points
            pt_offset = self.pts.shape[0] + len(add_pts)
            new_pts = [x[1] for x in cuts]
            add_pts.extend(new_pts)

            # list of point indexes for all new edges
            pt_indexes = list(range(pt_offset, pt_offset + len(cuts)))
            pt_indexes.append(self.edges[edge, 1])

            # modify original edge
            self.edges[edge, 1] = pt_indexes[0]

            # add new edges
            new_edges = [[pt_indexes[i-1], pt_indexes[i]]
                         for i in range(1, len(pt_indexes))]
            add_edges.extend(new_edges)

        if add_pts:
            add_pts = np.array(add_pts, dtype=self.pts.dtype)
            self.pts = np.append(self.pts, add_pts, axis=0)
        if add_edges:
            add_edges = np.array(add_edges, dtype=self.edges.dtype)
            self.edges = np.append(self.edges, add_edges, axis=0)

    def _merge_duplicate_points(self):
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

            # decrement all point indexes > j
            self.edges[self.edges > j] -= 1
            dups_arr[dups_arr > j] -= 1

        self.pts = self.pts[pt_mask]

        # remove zero-length edges
        mask = self.edges[:, 0] != self.edges[:, 1]
        self.edges = self.edges[mask]

    def _distances_from_line(self, edge, points):
        # Distance of a set of points from a given line
        e1 = self.pts[edge[0]]
        e2 = self.pts[edge[1]]
        distances = []
        for i in points:
            p = self.pts[i]
            proj = self._projection(e1, p, e2)
            distances.append(((p - proj)**2).sum()**0.5)
        assert distances[0] == 0 and distances[-1] == 0
        return distances

    def _projection(self, a, b, c):
        """Return projection of (a,b) onto (a,c)
        Arguments are point locations, not indexes.
        """
        ab = b - a
        ac = c - a
        return a + ((ab*ac).sum() / (ac*ac).sum()) * ac

    def _cosine(self, A, B, C):
        # Cosine of angle ABC
        a = ((C - B)**2).sum()
        b = ((C - A)**2).sum()
        c = ((B - A)**2).sum()
        d = (a + c - b) / ((4 * a * c)**0.5)
        return d

    def _iscounterclockwise(self, a, b, c):
        # Check if the points lie in counter-clockwise order or not
        A = self.pts[a]
        B = self.pts[b]
        C = self.pts[c]
        return np.cross(B-A, C-B) > 0

    def _edges_intersect(self, edge1, edge2):
        """Return 1 if edges intersect completely (endpoints excluded)"""
        h12 = self._intersect_edge_arrays(self.pts[np.array(edge1)],
                                          self.pts[np.array(edge2)])
        h21 = self._intersect_edge_arrays(self.pts[np.array(edge2)],
                                          self.pts[np.array(edge1)])
        err = np.geterr()
        np.seterr(divide='ignore', invalid='ignore')
        try:
            out = (0 < h12 < 1) and (0 < h21 < 1)
        finally:
            np.seterr(**err)
        return out

    def _intersect_edge_arrays(self, lines1, lines2):
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
        err = np.geterr()
        np.seterr(divide='ignore', invalid='ignore')
        try:
            h = (diff * p).sum(axis=-1) / f  # diff dot p / f
        finally:
            np.seterr(**err)

        return h

    def _orientation(self, edge, point):
        """Returns +1 if edge[0]->point is clockwise from edge[0]->edge[1],
        -1 if counterclockwise, and 0 if parallel.
        """
        v1 = self.pts[point] - self.pts[edge[0]]
        v2 = self.pts[edge[1]] - self.pts[edge[0]]
        c = np.cross(v1, v2)  # positive if v1 is CW from v2
        return 1 if c > 0 else (-1 if c < 0 else 0)

    def _add_tri(self, a, b, c):
        # sanity check
        assert a != b and b != c and c != a

        # ignore flat tris
        pa = self.pts[a]
        pb = self.pts[b]
        pc = self.pts[c]
        if np.all(pa == pb) or np.all(pb == pc) or np.all(pc == pa):
            return

        # check this tri is unique
        for t in permutations((a, b, c)):
            if t in self.tris:
                raise Exception("Cannot add %s; already have %s" %
                                ((a, b, c), t))

        # TODO: should add to edges_lookup after legalization??
        if self._iscounterclockwise(a, b, c):
            assert (a, b) not in self._edges_lookup
            assert (b, c) not in self._edges_lookup
            assert (c, a) not in self._edges_lookup
            self._edges_lookup[(a, b)] = c
            self._edges_lookup[(b, c)] = a
            self._edges_lookup[(c, a)] = b
        else:
            assert (b, a) not in self._edges_lookup
            assert (c, b) not in self._edges_lookup
            assert (a, c) not in self._edges_lookup
            self._edges_lookup[(b, a)] = c
            self._edges_lookup[(c, b)] = a
            self._edges_lookup[(a, c)] = b

        tri = (a, b, c)

        self.tris[tri] = None

    def _remove_tri(self, a, b, c):
        for k in permutations((a, b, c)):
            if k in self.tris:
                break
        del self.tris[k]
        (a, b, c) = k

        if self._edges_lookup.get((a, b), -1) == c:
            del self._edges_lookup[(a, b)]
            del self._edges_lookup[(b, c)]
            del self._edges_lookup[(c, a)]
        elif self._edges_lookup.get((b, a), -1) == c:
            del self._edges_lookup[(b, a)]
            del self._edges_lookup[(a, c)]
            del self._edges_lookup[(c, b)]
        else:
            raise RuntimeError("Lost edges_lookup for tri (%d, %d, %d)" %
                               (a, b, c))

        return k


def _triangulate_python(vertices_2d, segments):
    segments = segments.reshape(len(segments) // 2, 2)
    T = Triangulation(vertices_2d, segments)
    T.triangulate()
    vertices_2d = T.pts
    triangles = T.tris.ravel()
    return vertices_2d, triangles


def _triangulate_cpp(vertices_2d, segments):
    import triangle
    T = triangle.triangulate({'vertices': vertices_2d,
                              'segments': segments}, "p")
    vertices_2d = T["vertices"]
    triangles = T["triangles"]
    return vertices_2d, triangles


def triangulate(vertices):
    """Triangulate a set of vertices.

    This uses a pure Python implementation based on [1]_.

    If `Triangle` by Jonathan R. Shewchuk [2]_ and the Python bindings `triangle` [3]_
    are installed, this will be used instead. Users need to acknowledge and adhere to
    the licensing terms of these packages.

    In the VisPy `PolygonCollection Example` [4]_ a speedup of 97% using
    `Triangle`/`triangle` can be achieved compared to the pure Python implementation.

    Parameters
    ----------
    vertices : array-like
        The vertices.

    Returns
    -------
    vertices : array-like
        The vertices.
    triangles : array-like
        The triangles.

    References
    ----------
    .. [1] Domiter, V. and Žalik, B. Sweep‐line algorithm for constrained
       Delaunay triangulation
    .. [2] Shewchuk J.R. (1996) Triangle: Engineering a 2D quality mesh generator and
       Delaunay triangulator. In: Lin M.C., Manocha D. (eds) Applied Computational
       Geometry Towards Geometric Engineering. WACG 1996. Lecture Notes in Computer
       Science, vol 1148. Springer, Berlin, Heidelberg.
       https://doi.org/10.1007/BFb0014497
    .. [3] https://rufat.be/triangle/
    .. [4] https://github.com/vispy/vispy/blob/main/examples/collections/polygon_collection.py
    """
    n = len(vertices)
    vertices = np.asarray(vertices)
    zmean = vertices[:, 2].mean()
    vertices_2d = vertices[:, :2]
    segments = np.repeat(np.arange(n + 1), 2)[1:-1]
    segments[-2:] = n - 1, 0

    try:
        import triangle  # noqa: F401
    except (ImportError, AssertionError):
        vertices_2d, triangles = _triangulate_python(vertices_2d, segments)
    else:
        segments_2d = segments.reshape((-1, 2))
        vertices_2d, triangles = _triangulate_cpp(vertices_2d, segments_2d)

    vertices = np.empty((len(vertices_2d), 3))
    vertices[:, :2] = vertices_2d
    vertices[:, 2] = zmean
    return vertices, triangles
