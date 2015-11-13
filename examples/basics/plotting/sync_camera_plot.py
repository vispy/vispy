# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# vispy: gallery 1
"""
Example of syngronization of two plots during zooming
"""

import numpy as np

from vispy import plot as vp
from vispy.scene import SyncCamera2D

fig = vp.Fig(size=(1200, 600), bgcolor='#1c1f21', show=False)
fig.title = 'demo - sync 2 plots by X axis'
x = np.linspace(0, 10, 116000)
y1 = np.cos(x) + np.random.randn(len(x))
y2 = np.sin(x) + 0.2 * np.random.randn(len(x))

sp1 = fig[0, 0]
sp2 = fig[1, 0]
line1 = sp1.plot((x, y1), color='#00b4b2', width=1, title='I/V Curve',
    xlabel='Current (pA)', ylabel='Membrane Potential (mV)', face_color='w')
line2 = sp2.plot((x, y2), color='#ff0000')

#note: for complete sync is better connect cameras directly
x_sync_cam = SyncCamera2D(sync_x=True)
sp1.camera.link(x_sync_cam)
sp2.camera.link(x_sync_cam)

if __name__ == '__main__':
    fig.show(run=True)
