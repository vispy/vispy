"""
Demonstration of Tube
"""

import sys
from vispy import scene
from vispy.geometry.torusknot import TorusKnot

from colorsys import hsv_to_rgb
import numpy as np


def torus_knot(p=3, q=4, num=100):
    '''
    Returns points in the p, q torus knot.

    Note that not all combinations of p and q give knots;
    some curves may pass through themselves.
    '''
    data = np.zeros((num, 3), dtype=np.float64)
    ts = np.linspace(0, 2*np.pi, num)
    rs = np.cos(q*ts) + 2
    data[:, 0] = rs*np.cos(p*ts)
    data[:, 1] = rs*np.sin(p*ts)
    data[:, 2] = -1*np.sin(q*ts)
    return data

canvas = scene.SceneCanvas(keys='interactive')
canvas.view = canvas.central_widget.add_view()

points1 = TorusKnot(5, 3).first_component[:-1]
points1[:, 0] -= 20.
points1[:, 2] -= 15.

points2 = points1.copy()
points2[:, 2] += 30.

points3 = points1.copy()
points3[:, 0] += 41.
points3[:, 2] += 30

points4 = points1.copy()
points4[:, 0] += 41.

colors = np.linspace(0, 1, len(points1))
colors = np.array([hsv_to_rgb(c, 1, 1) for c in colors])

vertex_colors = np.random.random(8 * len(points1))
vertex_colors = np.array([hsv_to_rgb(c, 1, 1) for c in vertex_colors])

l1 = scene.visuals.Tube(points1,
                        shading='flat',
                        vertex_colors=vertex_colors,
                        tube_points=8)

l2 = scene.visuals.Tube(points2,
                        colors=colors,
                        shading='smooth',
                        tube_points=8)

l3 = scene.visuals.Tube(points3, colors=colors,
                        shading='flat',
                        tube_points=8,
                        closed=True)

l4 = scene.visuals.Tube(points4, colors=colors,
                        shading='flat',
                        tube_points=8,
                        mode='lines')

canvas.view.add(l1)
canvas.view.add(l2)
canvas.view.add(l3)
canvas.view.add(l4)
canvas.view.set_camera('turntable', mode='perspective',
                       up='z', distance=2.9*1.5*np.max(np.max(
                           points1, axis=0)))
canvas.show()

if __name__ == '__main__':
    if sys.flags.interactive != 1:
        canvas.app.run()
