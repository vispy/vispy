#! /usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from vispy import app, gloo
from vispy.geometry import Triangulation
from vispy.visuals.collections import TriangleCollection

canvas = app.Canvas(size=(800,800), show=True, keys='interactive')
gloo.set_viewport(0, 0, canvas.size[0], canvas.size[1])
gloo.set_state("translucent", depth_test=True)

def triangulate(P):
    n = len(P)
    S = np.repeat(np.arange(n+1),2)[1:-1]
    S[-2:] = n-1,0
    S = S.reshape(len(S)/2,2)
    T = Triangulation(P[:,:2], S)
    T.triangulate()
    points = T.pts
    triangles = T.tris.ravel()
    P = np.zeros((len(points),3),dtype=np.float32)
    P[:,:2] = points
    return P, triangles

def star(inner=0.5, outer=1.0, n=5):
    R = np.array( [inner,outer]*n)
    T = np.linspace(0,2*np.pi,2*n,endpoint=False)
    P = np.zeros((2*n,3))
    P[:,0]= R*np.cos(T)
    P[:,1]= R*np.sin(T)
    return P


triangles = TriangleCollection("raw", color='shared')

P,I = triangulate(star())

n = 200
for i in range(n):
    c = i/float(n)
    x,y = np.random.uniform(-1,+1,2)
    s = 25/800.0
    triangles.append(P*s+(x,y,0), I, color=(0,0,0,.5))

print triangles[0].vertices

@canvas.connect
def on_draw(e):
    gloo.clear('white')
    triangles.draw()

@canvas.connect
def on_resize(event):
    width, height = event.size
    gloo.set_viewport(0, 0, width, height)

app.run()
