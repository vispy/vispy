# !/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 30

from vispy import app, gloo
from vispy.scene.visuals import Text
from vispy.scene.transforms import STTransform


class Canvas(scene.SceneCanvas):
    def __init__(self, **kwarg):
        scene.SceneCanvas.__init__(self, close_keys='escape', title='Glyphs', **kwarg)
        self.scale = 200.

    def on_initialize(self, event):
        self.text = Text('Hello world!', bold=True)
        # We need to give a transform to our visual
        self.transform = STTransform()
        self.text._program.vert['transform'] = self.transform.shader_map()
        self.apply_zoom()

    def on_draw(self, event):
        gloo.clear(color='white')
        self.text.draw()
        self.update()

    def on_mouse_wheel(self, event):
        """Use the mouse wheel to zoom."""
        self.scale *= 1.25 if event.delta[1] > 0 else 0.8
        self.scale = max(min(self.scale, 2000.), 10.)
        self.apply_zoom()

    def on_resize(self, event):
        self.apply_zoom()

    def apply_zoom(self):
        gloo.set_viewport(0, 0, *self.size)
        self.transform.scale = (self.scale / self.size[0],
                                self.scale / self.size[1], 1.)
        self.update()

if __name__ == '__main__':
    c = Canvas()
    c.show()
    c.update()
    c.app.run()
