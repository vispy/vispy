# -*- coding: utf-8 -*-
# vispy: gallery 1
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Demonstration of Line visual with arbitrary transforms.

Several Line visuals are displayed that all have the same vertex position
information, but different transformations.
"""

import numpy as np
from vispy import app, visuals
from vispy.visuals.transforms import STTransform
from vispy.visuals.filters import Clipper, Alpha, ColorFilter
from vispy.visuals.shaders import Function
from vispy.geometry import Rect

# vertex positions of data to draw
N = 400
pos = np.zeros((N, 2), dtype=np.float32)
pos[:, 0] = np.linspace(0, 350, N)
pos[:, 1] = np.random.normal(size=N, scale=20, loc=0)


class Canvas(app.Canvas):
    def __init__(self):

        # Define several Line visuals that use the same position data
        self.lines = [visuals.LineVisual(pos=pos)
                      for i in range(6)]

        self.lines[0].transform = STTransform(translate=(0, 50))
        
        # Clipping filter (requires update when window is resized) 
        self.lines[1].transform = STTransform(translate=(400, 50))
        self.clipper = Clipper()
        self.lines[1].attach(self.clipper)
        
        # Opacity filter
        self.lines[2].transform = STTransform(translate=(0, 150))
        self.lines[2].attach(Alpha(0.4))
        
        # Color filter (for anaglyph stereo)
        self.lines[3].transform = STTransform(translate=(400, 150))
        self.lines[3].attach(ColorFilter([1, 0, 0, 1]))
        
        # A custom filter
        class Hatching(object):
            def __init__(self):
                self.shader = Function("""
                    void screen_filter() {
                        float f = gl_FragCoord.x * 0.4 + gl_FragCoord.y;
                        f = mod(f, 20);
                        
                        if( f < 5.0 ) {
                            discard;
                        }
                        
                        if( f < 20.0 ) {
                            gl_FragColor.g = gl_FragColor.g + 0.05 * (20-f);
                        }
                    }
                """)
            
            def _attach(self, visual):
                visual._get_hook('frag', 'post').add(self.shader())

        self.lines[4].transform = STTransform(translate=(0, 250))
        self.lines[4].attach(Hatching())
        
        # Mixing filters
        self.lines[5].transform = STTransform(translate=(400, 250))
        self.lines[5].attach(ColorFilter([1, 0, 0, 1]))
        self.lines[5].attach(Hatching())
        
        app.Canvas.__init__(self, keys='interactive', size=(800, 800))
        self.show(True)

    def on_draw(self, ev):
        self.context.clear('black', depth=True)
        for line in self.lines:
            line.draw()

    def on_resize(self, event):
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        for line in self.lines:
            line.transforms.configure(canvas=self, viewport=vp)

        # Need to update clipping boundaries if the window resizes.
        tr = self.lines[1].transforms.get_transform('visual', 'framebuffer')
        self.clipper.bounds = tr.map(Rect(100, -20, 200, 40))


if __name__ == '__main__':
    win = Canvas()
    import sys
    if sys.flags.interactive != 1:
        app.run()
