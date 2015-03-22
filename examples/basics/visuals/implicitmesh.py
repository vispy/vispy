"""
Demonstration of Tube
"""

import sys
from vispy import scene

import numpy as np
from scipy.special import sph_harm

canvas = scene.SceneCanvas(keys='interactive')
canvas.view = canvas.central_widget.add_view()


thetas, phis = np.meshgrid(np.linspace(0, np.pi, 100),
                           np.linspace(0, 2*np.pi, 150))

rs = 1. + 0.2*sph_harm(2, 5, phis, thetas).real

xs = rs * np.sin(thetas) * np.cos(phis)
ys = rs * np.sin(thetas) * np.sin(phis)
zs = rs * np.cos(thetas)


mesh = scene.visuals.ImplicitMesh(xs, ys, zs)

canvas.view.add(mesh)

canvas.view.set_camera('turntable', mode='perspective',
                       up='z', distance=3.0)
canvas.show()

if __name__ == '__main__':
    if sys.flags.interactive != 1:
        canvas.app.run()
