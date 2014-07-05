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


# Distance between points A and B
def distance(A, B):
    n = len(A)
    assert len(B) == n
    return np.linalg.norm(np.array(list(A)) - np.array(list(B)))


# Distance of a set of points from a given line
def distances_from_line(e, points):
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
def cosine(A, B, C):
    a, b, c = distance(B, C), distance(A, C), distance(A, B)
    return (a*a+c*c-b*b)/(2*a*c)


# Cartesian coordinates of the point whose barycentric coordinates
# with respect to the triangle ABC are [p,q,r]
def barycentric(A, B, C, p, q, r):
    n = len(A)
    assert len(B) == len(C) == n
    s = p+q+r
    p, q, r = p/s, q/s, r/s
    return tuple([p*A[i]+q*B[i]+r*C[i] for i in range(n)])


# Cartesian coordinates of the point whose trilinear coordinates
# with respect to the triangle ABC are [alpha,beta,gamma]
def trilinear(A, B, C, alpha, beta, gamma):
    a = distance(B, C)
    b = distance(A, C)
    c = distance(A, B)
    return barycentric(A, B, C, a*alpha, b*beta, c*gamma)

               
# Cartesian coordinates of the circumcenter of triangle ABC
def circuminfo(A, B, C):
    cosA = cosine(C, A, B)
    cosB = cosine(A, B, C)
    cosC = cosine(B, C, A)
    cc = trilinear(A, B, C, cosA, cosB, cosC)
    # returns circumcenter and circumradius
    return cc, distance(cc, A)


# Check if the points lie in counter-clockwise order or not
def iscounterclockwise(a, b, c):
    A = pts[a]
    B = pts[b]
    C = pts[c]
    return np.cross(B-A, C-B) > 0


def intersection(edge1, edge2):
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


def intersects(edge1, edge2):
    global pts
    h = intersection(edge1, edge2)
    return (h >= 0 and h < 1)


def intersection_point(edge1, edge2):
    """Return the point at which two edges intersect, or None if they do not.
    If edges intersect at their endpoints, return None.
    """
    h1 = intersection(edge2, edge1)
    h2 = intersection(edge1, edge2)
    if (0 < h1 < 1) and (0 < h2 < 1):  # intersection at endpoints returns None
        p0 = pts[edge1[0]]
        p1 = pts[edge1[1]]
        return p0 * (1.0 - h1) + p1 * h1
    else:
        return None
    

# check if the point is on which side - substitutes the point in the edge
# equation and returns the value
#def orientation(edge, point):
    #m = float(pts[edge[1]][1]-pts[edge[0]][1])/float(pts[edge[1]][0] -
                                                     #pts[edge[0]][0])
    #return pts[point][1]-pts[edge[0]][1]-m*(pts[point][0]--pts[edge[0]][0])


def orientation(edge, point):
    """Returns positive if edge[0]->point is clockwise from edge[0]->edge[1]"""
    v1 = pts[point] - pts[edge[0]]
    v2 = pts[edge[1]] - pts[edge[0]]
    return np.cross(v1, v2) # positive if v1 is CW from v2


#def int_pt(p1, p2, p3, p4):
    ## for testing intersection:
    #global pts
    #pts = np.array([p1, p2, p3, p4], dtype=float)
    #print("Intersection:", intersection_point([0,1], [2,3]))


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


# Clean up data:   (not discussed in original publication)
# (i) Split intersecting edges
intersections = []
for i in range(len(edges)-1):
    for j in range(i+1, len(edges)):
        pt = intersection_point(edges[i], edges[j])
        if pt is not None:
            intersections.append((i, j, pt))

print "intersections:", intersections

for i, j, pt in intersections:
    k = len(pts)
    pts = np.append(pts, pt.reshape(1,2), axis=0)
    ei1 = edges[i,1]
    ej1 = edges[j,1]
    edges[i] = (edges[i,0], k)
    edges[j] = (edges[j,0], k)
    edges = np.append(edges, [[k, ei1]], axis=0)
    edges = np.append(edges, [[k, ej1]], axis=0)

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


# For each triangle, maps (a, b): c
# This is used to look up the thrid point in a triangle, given any edge. 
# Since each edge has two triangles, they are independently stored as 
# (a, b): c and (b, a): d
edges_lookup = {}


## Initialization (sec. 3.3)

# sort by y, then x
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
tops = edges.max(axis=1)
bottoms = edges.min(axis=1)

# inintialize sweep front
front = [0, 2, 1]
tris = []


# visual debugging: draw edges, front, triangles
import pyqtgraph as pg
import time
app = pg.mkQApp()
win = pg.plot()
#gpts = pts.view(float).reshape(len(pts), 2)
graph = pg.GraphItem(pos=pts, adj=edges, pen={'width': 3,
                                               'color': (0, 100, 0)})
win.addItem(graph)
front_line = pg.PlotCurveItem(pen={'width': 2, 'dash': [5, 5], 'color': 'y'})
win.addItem(front_line)
tri_shapes = {}


def draw_state():
    front_pts = pts[np.array(front)]
    front_line.setData(front_pts[:,0], front_pts[:,1])
    for i in range(10):  # sleep ~1 sec, but keep ui responsive
        app.processEvents()
        time.sleep(0.01)


def draw_tri(tri, color=None):
    tpts = pts[np.array(tri)]
    path = pg.arrayToQPath(tpts[:,0], tpts[:,1])
    shape = pg.QtGui.QGraphicsPathItem(path)
    shape.setPen(pg.mkPen(255, 255, 255, 100))
    if color is None:
        brush = pg.mkBrush(0, 255, 255, 50)
    else:
        brush = pg.mkBrush(color)
    shape.setBrush(brush)
    win.addItem(shape)
    tri_shapes[tri] = shape

def undraw_tri(tri):
    shape = tri_shapes.pop(tri)
    win.removeItem(shape)


draw_state()


## Legalize recursively - incomplete
def legalize(p):
    
    f00, f11, p = p
    return (f00, f11, p)

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


## Sweep (sec. 3.4)
#def add_tri(f0, f1, p):
    ## todo: legalize!
    #global front, tris
    #if iscounterclockwise(front[f0], front[f1], p):
        #edges_lookup[(front[f0], front[f1])] = p
        #edges_lookup[(front[f1], p)] = front[f0]
        #edges_lookup[(p, front[f0])] = front[f1]
    #else:
        #edges_lookup[(front[f1], front[f0])] = p
        #edges_lookup[(p, front[f1])] = front[f0]
        #edges_lookup[(front[f0], p)] = front[f1]
    #tri = legalize((front[f0], front[f1], p))
    #tris.append(tri)


def add_tri(a, b, c, legal=True, color=None):
    global tris
    print("Add:", (a,b,c))
    
    # sanity check
    assert a != b and b != c and c != a
    
    # ignore flat tris
    if np.all(pts[a] == pts[b]) or np.all(pts[b] == pts[c]) or np.all(pts[c] == pts[a]):
        print("   Triangle is flat; refusing to add.")
        return
    
    # check this tri is unique
    for t in permutations((a,b,c)):
        if t in tris:
            raise Exception("Cannot add %s; already have %s" % (tri, t))
    
    
    # TODO: should add to edges_lookup after legalization??
    if iscounterclockwise(a, b, c):
        print("    ", (a,b), (b,c), (c,a))
        edges_lookup[(a, b)] = c
        edges_lookup[(b, c)] = a
        edges_lookup[(c, a)] = b
    else:
        print("    ", (b,a), (c,b), (a,c))
        edges_lookup[(b, a)] = c
        edges_lookup[(c, b)] = a
        edges_lookup[(a, c)] = b
    if legal:
        tri = legalize((a, b, c))
    else:
        tri = (a,b,c)
    tris.append(tri)
    draw_tri(tris[-1], color=color)


def remove_tri(a, b, c):
    global tris
    print("Remove:", (a,b,c))
    
    for k in permutations((a, b, c)):
        if k in tris:
            tris.remove(k)
            break
    (a, b, c) = k

    if edges_lookup.get((a, b), None) == c:
        print("    ", (a,b), (b,c), (c,a))
        del edges_lookup[(a, b)]
        del edges_lookup[(b, c)]
        del edges_lookup[(c, a)]
    else:
        print("    ", (b,a), (c,b), (a,c))
        del edges_lookup[(b, a)]
        del edges_lookup[(a, c)]
        del edges_lookup[(c, b)]

    undraw_tri(k)


# Begin triangulation
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
        
        # First just see whether this edge is already present
        # (this is not in the published algorithm)
        btm = bottoms[tops == i][0]
        print("Point is top of edge (%d, %d)" % (btm, i))
        if (i, btm) in edges_lookup or (btm, i) in edges_lookup:
            print("  edge already added, continuing..")
            continue
        
        
        # Locate the other endpoint
        found = False
        for e in edges:
            if i in e:
                found = True
                endpoint = e[0] if (e[1] == i) else e[1]
                break
        if not found:
            print("  Other end point not located; continuing.")
            continue
        
        print("  Locate first intersected triangle")
        # (i) locate intersected triangles
        """
        If the first intersected triangle contains the top point,
        then start traversal there. Also, if an intersected triangle
        contains the top point, then it has to be the first intersected
        triangle.
        """
        #print("  edges lookup:")
        #print(edges_lookup)
        
        vals = edges_lookup.values()
        edge_intersects = False
        for value in vals:
            if value == i:          # loop over all triangles containing Pi
                current_side = edges_lookup.keys()[vals.index(i)]
                # todo: might be sped up by using cross product as described in fig. 11
                if intersects(current_side, e):
                    edge_intersects = True
                    break

        # (ii) remove intersected triangles
        upper_polygon = []
        lower_polygon = []

        if not edge_intersects:
            # find the closest intersection to point
            h_max = 0
            closest_edge = None
            for edge in edges_lookup.keys():
                h = intersection(edge, e)
                if h >= 0 and h < 1 and h > h_max:
                    h_max = h
                    closest_edge = edge
            if not closest_edge:
                # the edge does not intersect any lines
                # triangulate the points on the front lying between the edge
                start = front.index(i)
                end = front.index(endpoint)
                upper_polygon.append(i)
                lower_polygon.append(i)
                c = -1 if (start > end) else 1
                for k in range(start+c, end, c):
                    if orientation((i, endpoint), front[k]) > 0:
                        upper_polygon.append(front[k])
                    else:
                        lower_polygon.append(front[k])
                        front.pop(k)

        else:
            print("Removed triangle = ")
            print(current_side+(i,))
            remove_tri(*(current_side+(i,)))
            upper_polygon.append(i)
            lower_polygon.append(i)
            if orientation((i, endpoint), current_side[0]) > 0:
                upper_polygon.append(current_side[0])
                lower_polygon.append(current_side[1])
            else:
                upper_polygon.append(current_side[1])
                lower_polygon.append(current_side[0])
            # now traverse and remove all intersecting triangles
            try:
                other_vertex = edges_lookup[current_side[::-1]]
                remove_tri(*(current_side+(other_vertex, )))
            except KeyError:
                other_vertex = endpoint
            while (other_vertex != endpoint):
                # now the edge intersects one of the triangles on either sides
                # of current triangle, we find which one and continue the loop
                side1 = (current_side[0], other_vertex)
                if intersects(side1, e):
                    other_vertex = edges_lookup[side1[::-1]]
                    current_side = side1
                    remove_tri(*(current_side+(other_vertex, )))
                else:
                    side2 = (other_vertex, current_side[1])
                    if intersects(side2, e):
                        other_vertex = edges_lookup[side2[::-1]]
                        current_side = side2
                        remove_tri(*(current_side+(other_vertex, )))
                    else:
                        # edge passes through the other_vertex
                        print("does not intersect any other side, "
                              "need to handle it")
                        break

                if orientation((i, endpoint), current_side[0]) > 0:
                    upper_polygon.append(current_side[0])
                    lower_polygon.append(current_side[1])
                else:
                    upper_polygon.append(current_side[1])
                    lower_polygon.append(current_side[0])

        upper_polygon = list(OrderedDict.fromkeys(upper_polygon))
        lower_polygon = list(OrderedDict.fromkeys(lower_polygon))
        upper_polygon.append(endpoint)
        lower_polygon.append(endpoint)

        # (iii) triangluate empty areas
        
        # triangulate upper area
        upper_dist = distances_from_line(e, upper_polygon)
        while len(upper_polygon) > 2:
            i = np.argmax(upper_dist)
            add_tri(upper_polygon[i], upper_polygon[i-1],
                    upper_polygon[i+1], legal=False)
            upper_polygon.pop(i)
            upper_dist.pop(i)

        lower_dist = distances_from_line(e, lower_polygon)
        while len(lower_polygon) > 2:
            i = np.argmax(lower_dist)
            add_tri(lower_polygon[i], lower_polygon[i-1],
                    lower_polygon[i+1], legal=False)
            lower_polygon.pop(i)
            lower_dist.pop(i)
            


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
    draw_state()


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

# (iii) Remove all edges that have only one triangle and are not a constraint 
#       edge (not described in article)
print "== Remove overzealous triangles"
print(tris)
print(edges)
while True:
    rem = []
    for edge in edges_lookup.keys():
        einv = (edge[1], edge[0])
        if einv in edges_lookup:
            continue
        ok = False
        for e in edge, einv:
            m = edges == e
            m = m[:,0] * m[:,1]
            if np.any(m):
                ok = True
                break

        if ok:
            continue
        print("  edge %s fails" % str(edge))
            
        rem.append((edge[0], edge[1], edges_lookup[edge]))
        
    if len(rem) == 0:
        break
    
    for tri in rem:
        try:
            remove_tri(*tri)
        except KeyError:
            pass

    draw_state()


print(front)
print(tris)
#for tri in tris:
    #draw_tri(tri)
draw_state()
