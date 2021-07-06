# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""Displays PolarImage.

   Use keys "d" - direction, "o" - origin, "l" - location and "p" - on/off
"""


import numpy as np
import vispy.app
from vispy import gloo
from vispy import visuals
from vispy.visuals.transforms import STTransform


directions = ["cw", "ccw"]
dir_index = 0

locations = ['N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE']
loc_index = 0

origins = ["UL", "UR", "LR", "LL"]
ori_index = 0

polar = [True, False]
pol_index = 0


def cycle_state(states, index):
    new_index = (index + 1) % len(states)
    return states[new_index], new_index


class Canvas(vispy.app.Canvas):
    def __init__(self):
        csize = 1000
        print(csize)

        vispy.app.Canvas.__init__(self, keys='interactive', size=(csize, csize))

        # Create image
        xmax = 500
        xres = xmax / 360
        ymax = 500
        yres = ymax / 100

        image = np.ones((xmax, ymax, 3), dtype=np.uint8)
        grad = np.linspace(0, 255, ymax, dtype=np.uint8)[None, :, None]
        image *= grad
        bl_y1_start, bl_y1_stop = int(yres * 80), int(yres * 90)
        bl_y2_start, bl_y2_stop = int(yres * 95), int(yres * 100)
        wt_y1_start, wt_y1_stop = int(yres * 5), int(yres * 10)
        wt_y2_start, wt_y2_stop = int(yres * 90), int(yres * 95)

        image[:, wt_y1_start:wt_y1_stop, :] = 255
        image[:, wt_y2_start:wt_y2_stop, :] = 255
        image[:, bl_y1_start:bl_y1_stop, :] = 0
        image[:, bl_y2_start:bl_y2_stop, :] = 0
        image[int(xres*10):int(xres*80)] = 255
        image[int(xres*340):int(xres*350)] = 255
        image2 = image

        self.image = visuals.ImageVisual(image,
                                         polar=("cw", "N", "UL"),
                                         interpolation="nearest",
                                         method='impostor')
        self.image2 = visuals.ImageVisual(image2, method='impostor')

        tr1 = (STTransform(scale=(1.0, 1.0, 1), translate=(csize/2, csize/2, 0))
        )
        self.image.transform = tr1

        self.visuals = [self.image, self.image2]
        self.show()

    def on_draw(self, ev):
        gloo.clear(color='w', depth=True)
        for vis in self.visuals:
            vis.draw()

    def on_resize(self, event):
        # Set canvas viewport and reconfigure visual transforms to match.
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        for vis in self.visuals:
            vis.transforms.configure(canvas=self, viewport=vp)

    def on_key_press(self, event):
        global dir_index, loc_index, ori_index, pol_index
        if event.key == 'd':
            dir0, dir_index = cycle_state(directions, dir_index)
        elif event.key == 'l':
            loc0, loc_index = cycle_state(locations, loc_index)
        elif event.key == 'o':
            ori0, ori_index = cycle_state(origins, ori_index)
        elif event.key == "p":
            pol0, pol_index = cycle_state(polar, pol_index)
        else:
            pass
        if polar[pol_index]:
            self.visuals[0].polar = (directions[dir_index], locations[loc_index], origins[ori_index])
        else:
            self.visuals[0].polar = False
        self.update()


if __name__ == '__main__':
    win = Canvas()
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()