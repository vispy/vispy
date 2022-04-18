# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# vispy: gallery 2
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Plot a scaled Image
===================

Demonstrates rendering a canvas to an image at higher resolution than the
original display.

NOTE: This example is currently broken.

"""

import vispy.plot as vp

# Create a canvas showing plot data
fig = vp.Fig()
fig[0, 0].plot([1, 6, 2, 4, 3, 8, 5, 7, 6, 3])

# Render the canvas scene to a numpy array image with higher resolution
# than the original canvas
scale = 4
image = fig.render(size=(fig.size[0]*scale, fig.size[1]*scale))

# Display the data in the array, sub-sampled down to the original canvas
# resolution
fig_2 = vp.Fig()
fig_2[0, 0].image(image[::-scale, ::scale])

# By default, the view adds some padding when setting its range.
# We'll remove that padding so the image looks exactly like the original
# canvas:
fig_2[0, 0].camera.set_range(margin=0)

if __name__ == '__main__':
    fig.app.run()
