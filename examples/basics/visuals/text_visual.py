# !/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 30

from vispy import scene, gloo
from vispy.scene.visuals import Text
from vispy.scene.transforms import STTransform


class Canvas(scene.SceneCanvas):
    def __init__(self):
        scene.SceneCanvas.__init__(self, title='Glyphs', keys='interactive')
        self.point_size = 48.
        self.text = Text('', bold=True)
        self.text.transform = STTransform()
        self.apply_zoom()

    def on_draw(self, event):
        gloo.clear(color='white')
        self.draw_visual(self.text)
        #self.update()

    def on_mouse_wheel(self, event):
        """Use the mouse wheel to zoom."""
        self.point_size *= 1.25 if event.delta[1] > 0 else 0.8
        self.point_size = max(min(self.point_size, 160.), 6.)
        self.apply_zoom()

    def on_resize(self, event):
        self.apply_zoom()

    def apply_zoom(self):
        scale = (self.point_size / 72.) * 92.  # Convert from pt to px
        self.text.text = '%s pt' % round(self.point_size, 1)
        self.text.transform.scale = (scale, -scale, 1.)
        self.text.transform.translate = self.size[0] // 2, self.size[1] // 2
        self.update()

if __name__ == '__main__':
    c = Canvas()
    c.show()
    c.app.run()
