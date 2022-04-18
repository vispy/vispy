# -*- coding: utf-8 -*-
# vispy: testskip
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
This is a simple egl example that produces 2d plot.

Was tested on Linux with Nvidia drivers.

Requires libEGLso.1 to be found in the system.
"""
import vispy
import numpy as np
import vispy.plot as vp
import vispy.io as io
vispy.use(app='egl')

# Check the application correctly picked up egl 
assert vispy.app.use_app().backend_name == 'egl', 'Not using EGL'

if __name__ == '__main__':

    data = np.load(io.load_data_file('electrophys/iv_curve.npz'))['arr_0']
    time = np.arange(0, data.shape[1], 1e-4)

    fig = vp.Fig(size=(800, 800), show=False)

    x = np.linspace(0, 10, 20)
    y = np.cos(x)
    line = fig[0, 0].plot((x, y), symbol='o', width=3, title='I/V Curve',
                          xlabel='Current (pA)', ylabel='Membrane Potential (mV)')
    grid = vp.visuals.GridLines(color=(0, 0, 0, 0.5))
    grid.set_gl_state('translucent')
    fig[0, 0].view.add(grid)

    fig.show()

    img = fig.render()
    io.write_png("egl.png", img)
