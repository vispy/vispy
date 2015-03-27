# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Plot various views of a structural MRI.
"""

import sys
import numpy as np

from vispy import io, plot as vp

fig = vp.Fig(bgcolor='k', show=False, size=(800, 800))

vol_data = np.load(io.load_data_file('brain/mri.npz'))['data']
vol_data = np.flipud(np.rollaxis(vol_data, 1))

vol_pw = fig[0, 0]
vol_pw.volume(vol_data)
vol_pw.camera.elevation = 30
vol_pw.camera.azimuth = 30
vol_pw.camera.scale_factor /= 1.5

clim = [0, 255.]
fig[1, 0].image(vol_data[:, :, vol_data.shape[2] // 2], cmap='grays')
fig[0, 1].image(vol_data[:, vol_data.shape[1] // 2, :], cmap='grays')
fig[1, 1].image(vol_data[vol_data.shape[0] // 2, :, :].T, cmap='grays')

if __name__ == '__main__':
    fig.show()
    if sys.flags.interactive == 0:
        fig.app.run()
