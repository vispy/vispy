# -*- coding: utf8 -*- 
"""
Constrained delaunay implementation based on 

Domiter, V. and Žalik, B.
Sweep‐line algorithm for constrained Delaunay triangulation

(this implementation is not complete)
"""

import numpy as np
from collections import OrderedDict
from itertools import permutations


class Triangulation(object):
    def __init__(self, pts, edges):
        self.pts = pts
        self.edges = edges
        
        
    def normalize(self):
        # Clean up data   (not discussed in original publication)
        
        # (i) Split intersecting edges
        
        # we can do all intersections at once, but this has excessive memory
        # overhead.
        #int1 = self.intersection_matrix(edges)
        #int2 = int1.T
        
        # measure intersection point between all pairs of edges
        cuts = self.find_edge_intersections()

        
                
        

        # (ii) merge identical points
        dups = []
        for i in range(pts.shape[0]-1):
            if i in dups:
                continue
            for j in range(i+1, pts.shape[0]):
                if np.all(pts[i] == pts[j]):
                    dups.append((i, j))

        for i, j in dups:
            print("========  %d => %d  =============" % (j, i))
            print(pts)
            print(edges)
            # rewrite edges to use i instead of j
            edges[edges == j] = i
            
            # remove j from points
            pts = np.concatenate([pts[:j], pts[j+1:]])
            mask = edges > j
            edges[mask] = edges[mask] - 1
            print(pts)
            print(edges)


    def initialize(self):
        self.normalize()
        
        ## Initialization (sec. 3.3)

        # sort points by y, then x
        pts = pts.reshape(pts.shape[0]*pts.shape[1]).view([('x', float), ('y', float)])
        order = np.argsort(pts, order=('y', 'x'))
        pts = pts[order]
        # update display edges to match new point order
        invorder = np.argsort(order)
        edges = invorder[edges]
        pts = pts.view(float).reshape(len(pts), 2)

        # make artificial points P-1 and P-2
        xmax = pts[:,0].max()
        xmin = pts[:,0].min()
        ymax = pts[:,1].max()
        ymin = pts[:,1].min()
        xa = (xmax-xmin) * 0.3
        ya = (ymax-ymin) * 0.3
        p1 = (pts[:,0].min() - xa, pts[:,1].min() - ya)
        # error in the equation in the paper, should be x_max+delta_x, not -delta_x
        p2 = (pts[:,0].max() + xa, pts[:,1].min() - ya)

        # prepend artificial points to point list
        newpts = np.empty((pts.shape[0]+2, 2), dtype=float)
        newpts[0] = p1
        newpts[1] = p2
        newpts[2:] = pts
        pts = newpts
        edges += 2

        # find topmost point in each edge
        self.tops = edges.max(axis=1)
        self.bottoms = edges.min(axis=1)

        # inintialize sweep front
        self.front = [0, 2, 1]
        
        self.tris = []
        self.pts = pts
        self.edges = edges

        # For each triangle, maps (a, b): c
        # This is used to look up the thrid point in a triangle, given any edge. 
        # Since each edge has two triangles, they are independently stored as 
        # (a, b): c and (b, a): d
        self.edges_lookup = {}


    def triangulate(self):
        self.initialize()
        
        ## Begin sweep (sec. 3.4)
        for i in range(3, pts.shape[0]):
            draw_state()
            
            pi = pts[i]
            print "========== New point %d: %s ==========" % (i, pi)
            
            # First, triangulate from front to new point
            # This applies to both "point events" (3.4.1) and "edge events" (3.4.2).

            # get index along front that intersects pts[i]
            l = 0
            while pts[front[l+1], 0] <= pi[0]:
                l += 1
            pl = pts[front[l]]
            pr = pts[front[l+1]]
            if pi[0] > pl[0]:  # "(i) middle case"
                print("  mid case")
                # Add a single triangle connecting pi,pl,pr
                add_tri(front[l], front[l+1], i)
                front.insert(l+1, i)
            else:  # "(ii) left case"
                print("  left case")
                ps = pts[l-1]
                # Add triangles connecting pi,pl,ps and pi,pl,pr
                add_tri(front[l], front[l+1], i)
                add_tri(front[l-1], front[l], i)
                front[l] = i
                #front.insert(l+1, i)
                #front.insert(l, i)
                #front.pop(l+1)
            print(front)
                
            draw_state()
            
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
                    angle = np.arccos(cosine(pi, p1, p2))
                    
                    # if angle is < pi/2, make new triangle
                    if angle > np.pi/2.:
                        break
                    
                    assert i != front[ind1] and front[ind1] != front[ind2] and front[ind2] != i
                    add_tri(i, front[ind1], front[ind2], color=(0, 255, 0, 50))
                    front.pop(ind1)
            
            draw_state()
            
                            
            if i in tops:  # this is an "edge event" (sec. 3.4.2)
                print "  == edge event =="
                
                for j in bottoms[tops == i]:
                    edge_event(j, i)  # Make sure edge (j, i) is present in mesh
                
                ## First just see whether this edge is already present
                ## (this is not in the published algorithm)
                #btm = bottoms[tops == i][0]
                #print("    Point is top of edge (%d, %d)" % (btm, i))
                #if (i, btm) in edges_lookup or (btm, i) in edges_lookup:
                    #print("    edge already added, continuing..")
                    #continue
                
                
                ## Locate the other endpoint
                #found = False
                #for e in edges:
                    #if i in e:
                        #found = True
                        #endpoint = e[0] if (e[1] == i) else e[1]
                        #break
                #if not found:
                    #print("    Other end point not located; continuing.")
                    #continue
                
                #print("    Locate first intersected triangle")
                ## (i) locate intersected triangles
                #"""
                #If the first intersected triangle contains the top point,
                #then start traversal there. Also, if an intersected triangle
                #contains the top point, then it has to be the first intersected
                #triangle.
                #"""
                ##print("  edges lookup:")
                ##print(edges_lookup)
                
                #vals = edges_lookup.values()
                #edge_intersects = False
                #for value in vals:
                    #if value == i:          # loop over all triangles containing Pi
                        #current_side = edges_lookup.keys()[vals.index(i)]
                        ## todo: might be sped up by using cross product as described in fig. 11
                        #if intersects(current_side, e):
                            #edge_intersects = True
                            #break

                ## (ii) remove intersected triangles
                #upper_polygon = []
                #lower_polygon = []

                #if not edge_intersects:
                    ## find the closest intersection to point
                    #h_max = 0
                    #closest_edge = None
                    #for edge in edges_lookup.keys():
                        #h = intersection(edge, e)
                        #if h >= 0 and h < 1 and h > h_max:
                            #h_max = h
                            #closest_edge = edge
                    #if not closest_edge:
                        ## the edge does not intersect any lines
                        ## triangulate the points on the front lying between the edge
                        #start = front.index(i)
                        #end = front.index(endpoint)
                        #upper_polygon.append(i)
                        #lower_polygon.append(i)
                        #c = -1 if (start > end) else 1
                        #for k in range(start+c, end, c):
                            #if orientation((i, endpoint), front[k]) > 0:
                                #upper_polygon.append(front[k])
                            #else:
                                #lower_polygon.append(front[k])
                                #front.pop(k)

                #else:
                    #remove_tri(*(current_side+(i,)))
                    #upper_polygon.append(i)
                    #lower_polygon.append(i)
                    #if orientation((i, endpoint), current_side[0]) > 0:
                        #upper_polygon.append(current_side[0])
                        #lower_polygon.append(current_side[1])
                    #else:
                        #upper_polygon.append(current_side[1])
                        #lower_polygon.append(current_side[0])
                    ## now traverse and remove all intersecting triangles
                    #try:
                        #other_vertex = edges_lookup[current_side[::-1]]
                        #remove_tri(*(current_side+(other_vertex, )))
                    #except KeyError:
                        #other_vertex = endpoint
                    #while (other_vertex != endpoint):
                        ## now the edge intersects one of the triangles on either sides
                        ## of current triangle, we find which one and continue the loop
                        #side1 = (current_side[0], other_vertex)
                        #if intersects(side1, e):
                            #other_vertex = edges_lookup[side1[::-1]]
                            #current_side = side1
                            #remove_tri(*(current_side+(other_vertex, )))
                        #else:
                            #side2 = (other_vertex, current_side[1])
                            #if intersects(side2, e):
                                #other_vertex = edges_lookup[side2[::-1]]
                                #current_side = side2
                                #remove_tri(*(current_side+(other_vertex, )))
                            #else:
                                ## edge passes through the other_vertex
                                #print("    does not intersect any other side, "
                                    #"need to handle it")
                                #break

                        #if orientation((i, endpoint), current_side[0]) > 0:
                            #upper_polygon.append(current_side[0])
                            #lower_polygon.append(current_side[1])
                        #else:
                            #upper_polygon.append(current_side[1])
                            #lower_polygon.append(current_side[0])

                #upper_polygon = list(OrderedDict.fromkeys(upper_polygon))
                #lower_polygon = list(OrderedDict.fromkeys(lower_polygon))
                #upper_polygon.append(endpoint)
                #lower_polygon.append(endpoint)

                # (iii) triangluate empty areas
                
                # triangulate upper area
                #upper_dist = distances_from_line(e, upper_polygon)
                #while len(upper_polygon) > 2:
                    #i = np.argmax(upper_dist)
                    #add_tri(upper_polygon[i], upper_polygon[i-1],
                            #upper_polygon[i+1], legal=False)
                    #upper_polygon.pop(i)
                    #upper_dist.pop(i)

                #lower_dist = distances_from_line(e, lower_polygon)
                #while len(lower_polygon) > 2:
                    #i = np.argmax(lower_dist)
                    #add_tri(lower_polygon[i], lower_polygon[i-1],
                            #lower_polygon[i+1], legal=False)
                    #lower_polygon.pop(i)
                    #lower_dist.pop(i)
                    
        self.finalize()
        
    def finalize(self):
        ## Finalize (sec. 3.5)

        # (i) Remove all triangles that include at least one artificial point
        print "== Remove artificial triangles"
        # todo: just don't add these in the first place. 
        rem = []
        for tri in tris:
            if 0 in tri or 1 in tri:
                rem.append(tri)
                
        for tri in rem:
            remove_tri(*tri)


        # (ii) Add bordering triangles to fill hull
        print "== Fill hull"
        front = list(OrderedDict.fromkeys(front))

        l = len(front) - 2
        k = 1
        while k < l-1:
            # if edges lie in counterclockwise direction, then signed area is positive
            if iscounterclockwise(front[k], front[k+1], front[k+2]):
                add_tri(front[k], front[k+1], front[k+2], legal=False)
                front.pop(k+1)
                l -= 1
                continue
            k += 1

        # (iii) Remove all triangles not inside the hull (not described in article)
        print "== Remove triangles outside hull"

        # TODO:  Start off by marking all triangles connected to artificial points as
        #        "bad". Two triangles that share a hull edge are marked opposite, and
        #        triangles that share a non-hull edge are marked the same. This should
        #        take care of all artificial and hole triangles.


    def edge_event(self, i, j):
        """
        Force edge (i, j) to be present in mesh. 
        This works by removing intersected triangles and filling holes up to
        the cutting edge.
        """
        # traverse in two different modes:
        #  1. If cutting edge is below front, traverse through triangles. These
        #     must be removed and the resulting hole re-filled. (fig. 12)
        #  2. If cutting edge is above the front, then follow the front until 
        #     crossing under again. (fig. 13)
        # We must be able to switch back and forth between these modes (fig. 14)

        # Collect points that draw the open polygons on either side of the cutting
        # edge. The final front must follow the upp
        upper_polygon = [i]
        lower_polygon = [i]
        
        # Keep track of which section of the front must be replaced
        # and with what it should be replaced
        front_hole = []  # contains start and stop indexes for section of front to remove
        front_patch = []  # contains data that should fill the hole in the front
        
        if edge_below_front:
            mode = 1  # follow triangles
        else:
            mode = 2  # follow front
            
        last_tri = None   # last triangle cut by the edge (already set if in mode 1)
        last_edge = None  # last front edge followed (already set if in mode 2)
                        # or last triangle edge crossed (if in mode 1)
        while True:
            if mode == 1:
                if last_edge in front_edges: # crossing over front
                    mode = 2
                    last_tri = None
                    # update front / polygons
                    continue
                else:
                    next_tri = adjacent_triangle(last_tri, last_edge)
                    if j in next_tri:
                        # reached endpoint! 
                        # update front / polygons
                        break
                    else:
                        tri_edges = edges_in_tri(next_tri)
                        tri_edges.remove(last_edge)
                        # select the edge that is cut
                        next_edge = intersected_edge(tri_edges, (i,j))

                
                
            else:  # mode == 2
                pass

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
            mask1 = (int1 >= 0) & (int1 <= 1)
            mask2 = (int2 >= 0) & (int2 <= 1)
            mask3 = mask1 & mask2  # all intersections
            
            # compute points of intersection
            inds = np.argwhere(mask3)[:, 0]
            if len(inds) == 0:
                continue
            h = int2[inds][:, np.newaxis]
            pts = edges[i, 0][np.newaxis, :] * (1.0 - h) + edges[i, 1][np.newaxis, :] * h
            
            # record for all edges the location of cut points
            edge_cuts = cuts.setdefault(i, [])
            for j,ind in enumerate(inds):
                if 0 < int2[ind] < 1:
                    edge_cuts.append((int2[ind], pts[j]))
                if 0 < int1[ind] < 1:
                    other_cuts = cuts.setdefault(ind+i+1, [])
                    other_cuts.append((int1[ind], pts[j]))
        
        # sort all cut lists by intercept
        for k,v in cuts.items():
            v.sort(key=lambda x: x[0])
            
        return cuts
    
    # Distance between points A and B
    def distance(self, A, B):
        n = len(A)
        assert len(B) == n
        return np.linalg.norm(np.array(list(A)) - np.array(list(B)))


    # Distance of a set of points from a given line
    def distances_from_line(self, e, points):
        e1 = pts[e[0]]
        e2 = pts[e[1]]
        distances = []
        # check if e is not just a point
        l2 = float(distance(e1, e2))
        l2 *= l2
        if l2 == 0:
            for p in points:
                distances.append(distance(e1, pts[p]))

        else:
            for p in points:
                t = float((pts[p] - e1).dot(e2 - e1))/l2
                if (t < 0.0):
                    distances.append(distance(pts[p], e1))
                elif (t > 0.0):
                    distances.append(distance(pts[p], e2))
                else:
                    projection = e1 + t * (e2 - e1)
                    distances.append(distance(pts[p], projection))
        return distances


    # Cosine of angle ABC
    def cosine(self, A, B, C):
        a, b, c = distance(B, C), distance(A, C), distance(A, B)
        return (a*a+c*c-b*b)/(2*a*c)


    # Cartesian coordinates of the point whose barycentric coordinates
    # with respect to the triangle ABC are [p,q,r]
    def barycentric(self, A, B, C, p, q, r):
        n = len(A)
        assert len(B) == len(C) == n
        s = p+q+r
        p, q, r = p/s, q/s, r/s
        return tuple([p*A[i]+q*B[i]+r*C[i] for i in range(n)])


    # Cartesian coordinates of the point whose trilinear coordinates
    # with respect to the triangle ABC are [alpha,beta,gamma]
    def trilinear(self, A, B, C, alpha, beta, gamma):
        a = distance(B, C)
        b = distance(A, C)
        c = distance(A, B)
        return barycentric(A, B, C, a*alpha, b*beta, c*gamma)

                
    # Cartesian coordinates of the circumcenter of triangle ABC
    def circuminfo(self, A, B, C):
        cosA = cosine(C, A, B)
        cosB = cosine(A, B, C)
        cosC = cosine(B, C, A)
        cc = trilinear(A, B, C, cosA, cosB, cosC)
        # returns circumcenter and circumradius
        return cc, distance(cc, A)


    # Check if the points lie in counter-clockwise order or not
    def iscounterclockwise(self, a, b, c):
        A = pts[a]
        B = pts[b]
        C = pts[c]
        return np.cross(B-A, C-B) > 0


    def intersection(self, edge1, edge2):
        """Return the intercept of the line defined by edge1 onto edge2.
        A value of 0 indicates intersection at edge2[0], and i indicates 
        intersection at edge2[1]."""
        global pts
        A = pts[edge1[0]]
        B = pts[edge1[1]]
        C = pts[edge2[0]]
        D = pts[edge2[1]]

        E = B-A
        F = D-C
        P = np.array([-E[1], E[0]])
        f = float(F.dot(P))
        if f == 0.:
            return float('Inf')
        h = float((A-C).dot(P))/f
        return h


    def intersects(self, edge1, edge2):
        global pts
        h = intersection(edge1, edge2)
        return (h >= 0 and h < 1)


    #def intersection_point(self, edge1, edge2):
        #"""Return the point at which two edges intersect, or None if they do not.
        #If edges intersect at their endpoints, return None.
        #"""
        #h1 = intersection(edge2, edge1)
        #h2 = intersection(edge1, edge2)
        #if (0 < h1 < 1) and (0 < h2 < 1):  # intersection at endpoints returns None
            #p0 = pts[edge1[0]]
            #p1 = pts[edge1[1]]
            #return p0 * (1.0 - h1) + p1 * h1
        #else:
            #return None

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
        """Return the intercepts of all lines defined in *lines1* as they intersect
        all lines in *lines2*. 
        
        Arguments are of shape (..., 2, 2), where axes are:
        
        0: number of lines
        1: two points per line
        2: x,y pair per point

        Lines are compared elementwise across the arrays (lines1[i] is compared
        against lines2[i]). If one of the arrays has N=1, then that line is
        compared against all lines in the other array.
        
        Returns an array of shape (N,) where each value indicates the intercept
        relative to the defined line segment. A value of 0 indicates intersection
        at the first endpoint, and a value of 1 indicates intersection at the second
        endpoint. Values between 1 and 0 are on the segment, whereas values outside
        1 and 0 are off of the segment. 
        
        """
        #global pts
        #A = pts[edges1[:,0]]
        #B = pts[edges1[:,1]]
        #C = pts[edges2[:,0]]
        #D = pts[edges2[:,1]]
        
        l1 = lines1[..., 1, :] - lines1[..., 0, :]  # vector for each line in lines1
        l2 = lines2[..., 1, :] - lines2[..., 0, :]  # vector for each line in lines2
        diff = lines1[..., 0, :] - lines2[..., 0, :]  # vector between first point of each line
        #E = B - A
        #F = D - C
        
        p = l1.copy()[..., ::-1]  # vectors perpendicular to l1
        p[...,0] *= -1
        #P = E.copy()[:, ::-1] # perpendicular vectors
        #P[:,0] *= -1
        
        f = (l2 * p).sum(axis=-1)  # l2 dot p
        h = (diff * p).sum(axis=-1) / f  # diff dot p / f
        #h = ((A - C) * P).sum(axis=1) / f  # (A-C) dot P
        return h

    #def orientation(self, edge, point):
        #"""Returns positive if edge[0]->point is clockwise from edge[0]->edge[1]"""
        #v1 = self.pts[point] - self.pts[edge[0]]
        #v2 = self.pts[edge[1]] - self.pts[edge[0]]
        #return np.cross(v1, v2) # positive if v1 is CW from v2

    ## Legalize recursively - incomplete
    def legalize(self, p):
        return p  # disabled for now
    
        f00, f11, p = p

        print("Legalizing points = {}, {}, {}".format(f00, f11, p))
        a = pts[f00]
        b = pts[f11]
        c = pts[p]
        cc, cr = circuminfo(a, b, c)
        for point in pts:
            if np.all(point == a) or np.all(point == b) or np.all(point == c):
                continue
            elif distance(cc, point) < cr:
                print("Illegal point")
                print(point)
                pass

        return (f00, f11, p)

    def add_tri(self, a, b, c, legal=True, source=None):
        # source is just used for debugging
        print("Add triangle:", (a,b,c))
        
        # sanity check
        assert a != b and b != c and c != a
        
        # ignore flat tris
        pa = self.pts[a]
        pb = self.pts[b]
        pc = self.pts[c]
        if np.all(pa == pb) or np.all(pb == pc) or np.all(pc == pa):
            print("   Triangle is flat; refusing to add.")
            return
        
        # check this tri is unique
        for t in permutations((a,b,c)):
            if t in self.tris:
                raise Exception("Cannot add %s; already have %s" % (tri, t))
        
        # TODO: should add to edges_lookup after legalization??
        if self.iscounterclockwise(a, b, c):
            print("    ", (a,b), (b,c), (c,a))
            self.edges_lookup[(a, b)] = c
            self.edges_lookup[(b, c)] = a
            self.edges_lookup[(c, a)] = b
        else:
            print("    ", (b,a), (c,b), (a,c))
            self.edges_lookup[(b, a)] = c
            self.edges_lookup[(c, b)] = a
            self.edges_lookup[(a, c)] = b
        
        if legal:
            tri = self.legalize((a, b, c))
        else:
            tri = (a, b, c)
        
        self.tris.append(tri)


    def remove_tri(self, a, b, c):
        print("Remove triangle:", (a,b,c))
        
        for k in permutations((a, b, c)):
            if k in tris:
                break
        self.tris.remove(k)
        (a, b, c) = k

        if self.edges_lookup.get((a, b), None) == c:
            #print("    ", (a,b), (b,c), (c,a))
            del self.edges_lookup[(a, b)]
            del self.edges_lookup[(b, c)]
            del self.edges_lookup[(c, a)]
        else:
            #print("    ", (b,a), (c,b), (a,c))
            del self.edges_lookup[(b, a)]
            del self.edges_lookup[(a, c)]
            del self.edges_lookup[(c, b)]

        return k



if __name__ == '__main__':
    import pyqtgraph as pg
    import time
    
    app = pg.mkQApp()
    
    class DebugTriangulation(Triangulation):
        """ 
        Visualize triangulation process stepwise to aid in debugging.
        """
        def __init__(self, pts, edges):
            Triangluate.__init__(self, pts, edges)
            
            # visual debugging: draw edges, front, triangles
            self.win = pg.plot()
            self.graph = pg.GraphItem(pos=pts, adj=edges, 
                                      pen={'width': 3, 'color': (0, 100, 0)})
            self.win.addItem(self.graph)
            self.front_line = pg.PlotCurveItem(pen={'width': 2, 
                                                    'dash': [5, 5], 
                                                    'color': 'y'})
            self.win.addItem(self.front_line)
            self.tri_shapes = {}

            self.draw_state()
            
        def draw_state(self):
            global app
            front_pts = self.pts[np.array(self.front)]
            self.front_line.setData(front_pts[:,0], front_pts[:,1])
            for i in range(10):  # sleep ~1 sec, but keep ui responsive
                app.processEvents()
                time.sleep(0.01)

        def draw_tri(self, tri, source=None):
            tpts = self.pts[np.array(tri)]
            path = pg.arrayToQPath(tpts[:,0], tpts[:,1])
            shape = pg.QtGui.QGraphicsPathItem(path)
            shape.setPen(pg.mkPen(255, 255, 255, 100))
            if source is None:
                brush = pg.mkBrush(0, 255, 255, 50)
            else:
                brush = pg.mkBrush(color)
            shape.setBrush(brush)
            self.win.addItem(shape)
            self.tri_shapes[tri] = shape
            self.draw_state()

        def undraw_tri(self, tri):
            shape = self.tri_shapes.pop(tri)
            self.win.removeItem(shape)
            self.draw_state()
            
        def add_tri(self, *args, **kwds):
            Triangulation.add_tri(self, *args, **kwds)
            self.draw_tri(self.tris[-1], source=kwds.get('source', None))
        
        def remove_tri(self, *args, **kwds):
            k = Triangulation.add_tri(self, *args, **kwds)
            undraw_tri(k)
        
        
    #user input data - points and constraining edges
    pts = [(0, 0),
        (10, 0),
        (10, 10),
        (20, 10),
        (20, 20),
        (25, 20),
        (25, 25),
        (20, 25),
        (20, 20),
        (10, 17),
        (5, 25),
        (9, 30),
        (6, 15),
        (15, 12.5),
        (0, 5)]
    l = len(pts)
    edges = [(i, (i+1) % l) for i in range(l)]
    pts += [(21, 21),
            (24, 21),
            (24, 24),
            (21, 24)]
    edges += [(l,   l+1),
              (l+1, l+2),
              (l+2, l+3),
              (l+3, l)]

    pts = np.array(pts, dtype=float)
    edges = np.array(edges, dtype=int)


    triangulation = DebugTriangulation(pts, edges)





