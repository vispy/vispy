# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of reactive EllipseVisual. 
"""

import vispy
from vispy import gloo, app
from vispy.scene import visuals


class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):
        self.ellipse = visuals.Ellipse(pos=(400, 400, 0), radius=[320, 240],
                                       color=(1, 0, 0, 1),
                                       border_color=(1, 1, 1, 1),
                                       start_angle=180., span_angle=150.)
        
        vispy.scene.SceneCanvas.__init__(self, keys='interactive')
        self.size = (800, 800)
        self.show()
        
        self._timer = app.Timer('auto', connect=self.on_timer, start=True)

    def on_timer(self, event):
        self.ellipse.radius[0] += 1
        self.ellipse.radius[1] += 1.5
        self.ellipse.span_angle += 0.6
        self.update()

    def on_mouse_press(self, event):
        self.ellipse.radius = [320, 240]
        self.ellipse.span_angle = 150.
        self.update()

    def on_draw(self, ev):
        gloo.clear(color='black')
        self.draw_visual(self.ellipse)
        

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
