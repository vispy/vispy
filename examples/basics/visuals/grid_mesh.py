"""
Demonstration of a mesh constructed in a grid about x,y,z coordinates.
"""

import sys
from vispy import scene
from vispy.color import get_colormap

import numpy as np
from scipy.special import sph_harm

canvas = scene.SceneCanvas(keys='interactive')
view = canvas.central_widget.add_view()

thetas, phis = np.meshgrid(np.linspace(0, np.pi, 100),
                           np.linspace(0, 2*np.pi, 150))
shape = thetas.shape
linear_shape = thetas.shape[0] * thetas.shape[1]
cm = get_colormap('hot')

for l in range(3):
    for m in range(l+1):
        harmonic_values = sph_harm(m, l, phis, thetas).real
        rs = 1. + 0.4*harmonic_values

        xs = rs * np.sin(thetas) * np.cos(phis)
        ys = rs * np.sin(thetas) * np.sin(phis)
        zs = rs * np.cos(thetas)

        xs -= 4.5
        zs -= 4.5
        xs += 2.5 * l
        zs += 2.5 * m

        v_min = np.min(harmonic_values)
        v_max = np.max(harmonic_values)
        scale = 1. / np.max(np.abs([v_min, v_max]))

        harmonic_values *= 0.5*scale
        harmonic_values += 0.5
        colors = cm[harmonic_values.reshape(linear_shape)].rgba.reshape(
            (shape[0], shape[1], 4))

        mesh = scene.visuals.GridMesh(xs, ys, zs, colors=colors)

        view.add(mesh)

view.camera = 'turntable'
canvas.show()

if __name__ == '__main__':
    if sys.flags.interactive != 1:
        canvas.app.run()
