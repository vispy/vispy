"""
Demonstration of Tube
"""

import sys
from vispy import scene
from vispy.color import get_colormap

import numpy as np
from scipy.special import sph_harm

canvas = scene.SceneCanvas(keys='interactive')
canvas.view = canvas.central_widget.add_view()

thetas, phis = np.meshgrid(np.linspace(0, np.pi, 100),
                           np.linspace(0, 2*np.pi, 150))

harmonic_values = sph_harm(2, 5, phis, thetas).real
rs = 1. + 0.4*harmonic_values

xs = rs * np.sin(thetas) * np.cos(phis)
ys = rs * np.sin(thetas) * np.sin(phis)
zs = rs * np.cos(thetas)

v_min = np.min(harmonic_values)
v_max = np.max(harmonic_values)
scale = 1. / np.max(np.abs([v_min, v_max]))

length = xs.shape[0] * xs.shape[1]
cm = get_colormap('hot')
col_vals = 0.5 * harmonic_values * scale + 0.5
colors = cm[col_vals.reshape(length)].rgb.reshape((xs.shape[0],
                                                   xs.shape[1],
                                                   3))

mesh = scene.visuals.ImplicitMesh(xs, ys, zs, color=colors)

canvas.view.add(mesh)

canvas.view.set_camera('turntable', mode='perspective',
                       up='z', distance=3.0)
canvas.show()

if __name__ == '__main__':
    if sys.flags.interactive != 1:
        canvas.app.run()
