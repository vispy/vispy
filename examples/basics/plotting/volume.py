# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# vispy: gallery 1
"""
Plot various views of a structural MRI.
"""

import numpy as np

from vispy import io, plot as vp

fig = vp.Fig(bgcolor='k', size=(800, 800), show=False)

vol_data = np.load(io.load_data_file('brain/mri.npz'))['data']
vol_data = np.flipud(np.rollaxis(vol_data, 1))

clim = [32, 192]
vol_pw = fig[0, 0]
vol_pw.volume(vol_data, clim=clim)
vol_pw.view.camera.elevation = 30
vol_pw.view.camera.azimuth = 30
vol_pw.view.camera.scale_factor /= 1.5

shape = vol_data.shape
fig[1, 0].image(vol_data[:, :, shape[2] // 2], cmap='grays', clim=clim,
                fg_color=(0.5, 0.5, 0.5, 1))
fig[0, 1].image(vol_data[:, shape[1] // 2, :], cmap='grays', clim=clim,
                fg_color=(0.5, 0.5, 0.5, 1))
fig[1, 1].image(vol_data[shape[0] // 2, :, :].T, cmap='grays', clim=clim,
                fg_color=(0.5, 0.5, 0.5, 1))

if __name__ == '__main__':
    fig.show(run=True)
