# !/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 30

from vispy import scene, gloo
from vispy.scene.visuals import Text
from vispy.scene.transforms import STTransform


class Canvas(scene.SceneCanvas):
    def __init__(self):
        scene.SceneCanvas.__init__(self, close_keys='escape', title='Glyphs')
        self.scale = 200.
        self.text = Text('Hello world!', bold=True)
        self.text.transform = STTransform(scale=(100, 100),
                                          translate=(400, 400))
        self.apply_zoom()

    def on_draw(self, event):
        gloo.clear(color='white')
        self.draw_visual(self.text)
        self.update()

    def on_mouse_wheel(self, event):
        """Use the mouse wheel to zoom."""
        self.scale *= 1.25 if event.delta[1] > 0 else 0.8
        self.scale = max(min(self.scale, 2000.), 10.)
        self.apply_zoom()

    def on_resize(self, event):
        self.apply_zoom()

    def apply_zoom(self):
        self.text.transform.scale = (self.scale / self.size[0],
                                     self.scale / self.size[1], 1.)
        self.update()

if __name__ == '__main__':
    c = Canvas()
    c.show()
    c.update()
    c.app.run()
