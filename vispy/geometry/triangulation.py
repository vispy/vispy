# -*- coding: utf8 -*- 
"""
Constrained delaunay implementation based on 

Domiter, V. and Žalik, B.
Sweep‐line algorithm for constrained Delaunay triangulation

(this implementation is not complete)
"""

import numpy as np
from math import cos
from collections import OrderedDict
from itertools import permutations

# Distance between points A and B
def distance(A, B):
    n = len(A)
    assert len(B) == n
    return sum((A[i]-B[i])**2 for i in xrange(n))**0.5

# Distance of a set of points from a given line
def distances_from_line(e, points):
    e1 = np.array(list(pts[e[0]]))
    e2 = np.array(list(pts[e[1]]))
    distances = []
    # check if e is not just a point
    l2 = float(distance(e1, e2))
    l2 *= l2
    if l2==0:
        for p in points:
            distances.append(distance(e1, pts[p]))

    else:
        for p in points:
            t = float((np.array(list(pts[p])) - e1).dot(e2 - e1))/l2
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
    a,b,c = distance(B,C), distance(A,C), distance(A,B)
    return (a*a+c*c-b*b)/(2*a*c)

# Cartesian coordinates of the point whose barycentric coordinates
# with respect to the triangle ABC are [p,q,r]
def barycentric(A,B,C,p,q,r):
    n = len(A)
    assert len(B) == len(C) == n
    s = p+q+r
    p, q, r = p/s, q/s, r/s
    return tuple([p*A[i]+q*B[i]+r*C[i] for i in xrange(n)])

# Cartesian coordinates of the point whose trilinear coordinates
# with respect to the triangle ABC are [alpha,beta,gamma]
def trilinear(A,B,C,alpha,beta,gamma):
    a = distance(B,C)
    b = distance(A,C)
    c = distance(A,B)
    return barycentric(A,B,C,a*alpha,b*beta,c*gamma)
               
# Cartesian coordinates of the circumcenter of triangle ABC
def circuminfo(A,B,C):
    cosA = cosine(C,A,B)
    cosB = cosine(A,B,C)
    cosC = cosine(B,C,A)
    cc = trilinear(A,B,C,cosA,cosB,cosC)
    # returns circumcenter and circumradius
    return cc, distance(cc, A)

# Check if the points lie in counter-clockwise order or not
def iscounterclockwise(a, b, c):
    A = np.array(list(pts[a]))
    B = np.array(list(pts[b]))
    C = np.array(list(pts[c]))
    return np.cross(B-A, C-B)>0

def intersection(edge1, edge2):
    global pts
    A = np.array(list(pts[edge1[0]]))
    B = np.array(list(pts[edge1[1]]))
    C = np.array(list(pts[edge2[0]]))
    D = np.array(list(pts[edge2[1]]))

    E = B-A
    F = D-C
    P = np.array([-E[1], E[0]])
    f = float(F.dot(P))
    if f==0.:
        return float('Inf')
    h = float((A-C).dot(P))/f
    return h

def isintersects(edge1, edge2):
    global pts
    h = intersection(edge1, edge2)
    return (h>=0 and h<1)

# check if the point is on which side - substitutes the point in the edge
# equation and returns the value
def orientation(edge, point):
    m = float(pts[edge[1]][1]-pts[edge[0]][1])/float(pts[edge[1]][0]-pts[edge[0]][0])
    return pts[point][1]-pts[edge[0]][1]-m*(pts[point][0]--pts[edge[0]][0])

#user input data - points and constraining edges
pts = [(0, 0),
       (10, 0),
       (10, 10),
       (20, 10),
       (20, 20),
       (10, 17),
       (9, 30),
       (5, 25),
       (6, 15),
       (10, 12),
       (0, 5)]
edges = [(4,1), (6,7)]

pts = np.array(pts, dtype=[('x', float), ('y', float)])
edges = np.array(edges, dtype=int)
edges_lookup = {}
## Initialization (sec. 3.3)

# sort by y, then x
order = np.argsort(pts, order=('y', 'x'))
pts = pts[order]
# update display edges to match new point order
invorder = np.argsort(order)
edges = invorder[edges]

# make artificial points P-1 and P-2
xmax = pts['x'].max()
xmin = pts['x'].min()
ymax = pts['y'].max()
ymin = pts['y'].min()
xa = (xmax-xmin) * 0.3
ya = (ymax-ymin) * 0.3
p1 = (pts['x'].min() - xa, pts['y'].min() - ya)
# error in the equation in the paper, should be x_max+delta_x, not -delta_x
p2 = (pts['x'].max() + xa, pts['y'].min() - ya)

# prepend artificial points to point list
newpts = np.empty(len(pts)+2, dtype=pts.dtype)
newpts[0] = p1
newpts[1] = p2
newpts[2:] = pts
pts = newpts
edges += 2

# find topmost point in each edge
tops = set(edges.max(axis=1))

# inintialize sweep front
front = [0, 2, 1]
tris = []


# visual debugging: draw edges, front, triangles
import pyqtgraph as pg
import time
app = pg.mkQApp()
win = pg.plot()
gpts = pts.view(float).reshape(len(pts), 2)
graph = pg.GraphItem(pos=gpts, adj=edges, pen={'width': 3, 'color':(0,100,0)})
win.addItem(graph)
front_line = pg.PlotCurveItem(pen={'width': 2, 'dash': [5, 5], 'color': 'y'})
win.addItem(front_line)
tri_shapes = []
def draw_state():
    front_pts = pts[np.array(front)]
    front_line.setData(front_pts['x'], front_pts['y'])
    for i in range(100):  # sleep ~1 sec, but keep ui responsive
        app.processEvents()
        time.sleep(0.01)
def draw_tri(tri):
    tpts = pts[np.array(tri)]
    path = pg.arrayToQPath(tpts['x'], tpts['y'])
    shape = pg.QtGui.QGraphicsPathItem(path)
    shape.setPen(pg.mkPen(255,255,255,100))
    shape.setBrush(pg.mkBrush(0,255,255,50))
    win.addItem(shape)
    tri_shapes.append(shape)
draw_state()

## Legalize recursively - incomplete
def legalize((f00, f11, p)):
    #print "Legalizing points = {}, {}, {}".format(f00, f11, p)
    a = pts[f00]
    b = pts[f11]
    c = pts[p]
    cc, cr = circuminfo(a, b, c)
    for point in pts:
        if (point==a or point==b or point==c):
            continue
        elif distance(cc, point) < cr:
           print "Illegal point"
           print point

    return (f00, f11, p)


## Sweep (sec. 3.4)

def add_tri(f0, f1, p):
    # todo: legalize!
    global front, tris
    if iscounterclockwise(front[f0], front[f1], p):
        edges_lookup[(front[f0], front[f1])] = p
        edges_lookup[(front[f1], p)] = front[f0]
        edges_lookup[(p, front[f0])] = front[f1]
    else:
        edges_lookup[(front[f1], front[f0])] = p
        edges_lookup[(p, front[f1])] = front[f0]
        edges_lookup[(front[f0], p)] = front[f1]
    tri = legalize((front[f0], front[f1], p))
    tris.append(tri)
    #print "Inserted at position f1={} value p={}".format(f1,p)
    #print "front = {}".format(front)
    # visual debugging
    #draw_tri(tris[-1])

def add_triangle(a, b, c):
    # todo: legalize!
    global tris
    if iscounterclockwise(a, b, c):
        edges_lookup[(a, b)] = c
        edges_lookup[(b, c)] = a
        edges_lookup[(c, a)] = b
    else:
        edges_lookup[(b, a)] = c
        edges_lookup[(c, b)] = a
        edges_lookup[(a, c)] = b
    tri = legalize((a, b, c))
    tris.append(tri)

def remove_tri((a, b, c)):
    global tris
    
    for k in permutations((a, b, c)):
        if k in tris:
            tris.remove(k)
            break

    (a, b, c) = k

    if edges_lookup[(a,b)]==c:
        del edges_lookup[(a,b)]
        del edges_lookup[(b,c)]
        del edges_lookup[(c,a)]
    else:
        del edges_lookup[(b,a)]
        del edges_lookup[(a,c)]
        del edges_lookup[(c,b)]

for i in range(3, len(pts)):
    pi = pts[i]
    # First, triangulate from front to new point
    # This applies to both "point events" (3.4.1) and "edge events" (3.4.2).

    # get index along front that intersects pts[i]
    l = 0
    while pts[front[l+1]]['x'] <= pi['x']:
        l += 1
    pl = pts[front[l]]
    pr = pts[front[l+1]]
    if pi['x'] > pl['x']:  # "(i) middle case"
        # Add a single triangle connecting pi,pl,pr
        add_tri(l, l+1, i)
        front.insert(l+1, i)
    else: # "(ii) left case"
        ps = pts[l-1]
        # Add triangles connecting pi,pl,ps and pi,pl,pr
        add_tri(l, l+1, i)
        front.insert(l+1, i)
        add_tri(l-1, l, i)
        front.insert(l, i)
        front.pop(l+1)
        
    # todo: Continue adding triangles to smooth out front
    # (use heuristics shown in figs. 9, 10)
                    
    if i in tops: # this is an "edge event" (sec. 3.4.2)
        #print "Locate first intersected triangle"
        # Locate the other endpoint
        found = False
        for e in edges:
            if i in e:
                found = True
                endpoint = e[0] if (e[1]==i) else e[1]
                break
        if not found:
            print "Other end point not located"
            continue
        # (i) locate intersected triangles
        """
        If the first intersected triangle contains the top point,
        then start traversal there. Also, if an intersected triangle
        contains the top point, then it has to be the first intersected
        triangleself.
        """
        #print edges_lookup
        vals = edges_lookup.values()
        intersects = False
        for value in vals:
            if value==i:
                current_side = edges_lookup.keys()[vals.index(i)]
                if isintersects(current_side, e):
                    intersects = True
                    break

        # (ii) remove intersected triangles
        # initialize set(to remove redundancy) for upper and lower vertices
        upper_polygon = []
        lower_polygon = []

        if not intersects:
            # find the closest intersection to point
            h_max = 0
            closest_edge = None
            for edge in edges_lookup.keys():
                h = intersection(edge, e)
                if h>=0 and h<1 and h>h_max:
                    h_max = h
                    closest_edge = edge

        else:
            print "Removed triangle = "
            print current_side+(i,)
            remove_tri(current_side+(i,))
            upper_polygon.append(i)
            lower_polygon.append(i)
            if orientation(e, current_side[0])>0:
                upper_polygon.append(current_side[0])
                lower_polygon.append(current_side[1])
            else:
                upper_polygon.append(current_side[1])
                lower_polygon.append(current_side[0])
            # now traverse and remove all intersecting triangles
            other_vertex = edges_lookup[current_side[::-1]]
            remove_tri(current_side+(other_vertex, ))
            while (other_vertex!=endpoint):
                # now the edge intersects one of the triangles on either sides
                # of current triangle, we find which one and continue the loop
                side1 = (current_side[0], other_vertex)
                if isintersects(side1, e):
                    other_vertex = edges_lookup[side1[::-1]]
                    current_side = side1
                    remove_tri(current_side+(other_vertex, ))
                else:
                    side2 = (other_vertex, current_side[1])
                    if isintersects(side2, e):
                        other_vertex = edges_lookup[side2[::-1]]
                        current_side = side2
                        remove_tri(current_side+(other_vertex, ))
                    else:
                        # edge passes through the other_vertex
                        #print "does not intersect any other side, need to handle it"
                        break

                if orientation(e, current_side[0])>0:
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
            print "i = ", i, upper_polygon[i], upper_polygon[i-1], upper_polygon[i+1]
            add_triangle(upper_polygon[i], upper_polygon[i-1], upper_polygon[i+1])  # add_tri does legalization with new triangle
            upper_polygon.pop(i)
            upper_dist.pop(i)

        lower_dist = distances_from_line(e, lower_polygon)
        while len(lower_polygon) > 2:
            i = np.argmax(lower_dist)
            add_triangle(lower_polygon[i], lower_polygon[i-1], lower_polygon[i+1])  # add_tri does legalization with new triangle
            lower_polygon.pop(i)
            lower_dist.pop(i)
    #draw_state()

## Finalize (sec. 3.5)

# (i) Remove all triangles that include at least one artificial point
# (ii) Add bordering triangles to fill hull
##print edges_lookup
print tris
for tri in tris:
    draw_tri(tri)
draw_state()
raw_input()