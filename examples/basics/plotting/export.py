# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Demonstrates rendering a canvas to an image at higher resolution than the
original display.
"""

import sys
import vispy.plot as vp

# Create a canvas showing plot data
canvas = vp.plot([1, 6, 2, 4, 3, 8, 5, 7, 6, 3])

# Render the canvas scene to a numpy array image with higher resolution 
# than the original canvas
scale = 4
image = canvas.render(size=(canvas.size[0]*scale, canvas.size[1]*scale))

# Display the data in the array, sub-sampled down to the original canvas
# resolution
image = image[::scale, ::scale]
canvas2 = vp.image(image)

# By default, the view adds some padding when setting its range.
# We'll remove that padding so the image looks exactly like the original 
# canvas:
canvas2.view.camera.auto_zoom(canvas2.image, padding=0)

if __name__ == '__main__' and sys.flags.interactive == 0:
    canvas.app.run()
