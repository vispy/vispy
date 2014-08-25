# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from vispy import scene, gloo
from vispy.scene.visuals import Text


class Canvas(scene.SceneCanvas):
    def __init__(self):
        scene.SceneCanvas.__init__(self, title='Glyphs', keys='interactive')
        self.font_size = 48.
        self.text = Text('', bold=True)
        self.apply_zoom()

    def on_draw(self, event):
        gloo.clear(color='white')
        self.draw_visual(self.text)

    def on_mouse_wheel(self, event):
        """Use the mouse wheel to zoom."""
        self.font_size *= 1.25 if event.delta[1] > 0 else 0.8
        self.font_size = max(min(self.font_size, 160.), 6.)
        self.apply_zoom()

    def on_resize(self, event):
        self.apply_zoom()

    def apply_zoom(self):
        self.text.text = '%s pt' % round(self.font_size, 1)
        self.text.font_size = self.font_size
        self.text.pos = self.size[0] // 2, self.size[1] // 2
        self.update()

if __name__ == '__main__':
    c = Canvas()
    c.show()
    c.app.run()
