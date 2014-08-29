# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
"""

import numpy as np
import vispy.app
from vispy import gloo
from vispy.scene import visuals
from vispy.scene.transforms import STTransform, BaseTransform, arg_to_array

image = np.random.normal(size=(100, 100, 3), loc=128,
                         scale=50).astype(np.ubyte)

"""
y = x + x / (x^2 + 1)
  = x (1 + 1 / (x^2 + 1))
  = x (x^2 + 2 / x^2 + 1)
  
  
"""



class MagnifyTransform(BaseTransform):
    """
    """
    glsl_map = """
        vec4 sineTransform(vec4 pos) {
            vec2 d = vec2(pos.x - $center.x, pos.y - $center.y);
            float dist = length(d);
            vec2 dir = d / dist;
            
            dist = dist + dist / (dist*dist + 1);

            d = $center + dir * dist;
            return vec4(d, pos.z, 1);
        }"""

    glsl_imap = """
        vec4 sineTransform(vec4 pos) {
            vec2 d = vec2(pos.x - $center.x, pos.y - $center.y);
            float dist = length(d);
            vec2 dir = d / dist;
            
            dist = dist + dist / (dist*dist + 1);

            d = $center + dir * dist;
            return vec4(d, pos.z, 1);
        }"""

    Linear = False
    
    def __init__(self):
        self._center = (0, 0)
        super(MagnifyTransform, self).__init__()
        
    @property
    def center(self):
        return self._center
    
    @center.setter
    def center(self, center):
        self._center = center
        self.shader_map()
        self.shader_imap()

    def shader_map(self):
        fn = super(MagnifyTransform, self).shader_map()
        fn['center'] = self._center  # uniform vec2
        return fn

    def shader_imap(self):
        fn = super(MagnifyTransform, self).shader_imap()
        fn['center'] = self._center  # uniform vec2
        return fn

    @arg_to_array
    def map(self, coords):
        ret = coords.copy()
        #ret[..., 1] += np.sin(ret[..., 0])
        return ret

    @arg_to_array
    def imap(self, coords):
        ret = coords.copy()
        #ret[..., 1] -= np.sin(ret[..., 0])
        return ret


class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):
        self.image = visuals.Image(image, method='impostor')
        self.mag = MagnifyTransform()
        self._pos = (0, 0)
        self.image.transform = (STTransform(scale=(7, 7), translate=(50, 50)) *
                                self.mag)
        vispy.scene.SceneCanvas.__init__(self, keys='interactive')
        self.size = (800, 800)
        self.show()

    def on_mouse_move(self, event):
        self._pos = event.pos[:2]
        self.update()

    def on_draw(self, ev):
        gloo.clear(color='black', depth=True)
        self.push_viewport((0, 0) + self.size)
        
        self.mag.center = self.image.transform.imap(self._pos)[:2]
        self.draw_visual(self.image)


if __name__ == '__main__':
    win = Canvas()
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
