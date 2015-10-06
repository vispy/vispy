# -*- coding: utf-8 -*-
# vispy: testskip
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
This is a simple osmesa example that produce an image of a cube

If you have both osmesa and normal (X) OpenGL installed, execute with
something like the following to pickup the OSMesa libraries::

    VISPY_GL_LIB=/opt/osmesa_llvmpipe/lib/libGLESv2.so \
    LD_LIBRARY_PATH=/opt/osmesa_llvmpipe/lib/ \
    OSMESA_LIBRARY=/opt/osmesa_llvmpipe/lib/libOSMesa.so \
    python examples/offscreen/simple_osmesa.py
"""
import vispy
vispy.use(app='osmesa')  # noqa

import numpy as np
import vispy.plot as vp
import vispy.io as io

# Check the application correctly picked up osmesa
assert vispy.app.use_app().backend_name == 'osmesa', 'Not using OSMesa'

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
io.write_png("osmesa.png", img)
