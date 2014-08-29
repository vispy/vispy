# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
"""

import numpy as np
import vispy.scene
from vispy import gloo
from vispy.scene import visuals
from vispy.scene.transforms import STTransform, BaseTransform, arg_to_array

class MagnifyTransform(BaseTransform):
    """
    """
    glsl_map = """
        vec4 mag_transform(vec4 pos) {
            vec2 d = vec2(pos.x - $center.x, pos.y - $center.y);
            float dist = length(d);
            if (dist == 0) {
                return pos;
            }
            vec2 dir = d / dist;
            
            // gaussian profile
            float m = 1 / ((dist/$radius)*(dist/$radius) + 1);
            // flatten to make nearly linear in the center
            m = pow(1 - pow((1 - m), 100), 100);
            dist = dist * (1 + ($mag-1) * m);

            d = $center + dir * dist;
            return vec4(d, pos.z, pos.w);
        }"""
    
    glsl_imap = glsl_map
    
    Linear = False
    
    def __init__(self):
        self._center = (0, 0)
        self._mag = 5
        self._radius = 10
        super(MagnifyTransform, self).__init__()
        
    @property
    def center(self):
        return self._center
    
    @center.setter
    def center(self, center):
        self._center = center
        self.shader_map()
        self.shader_imap()

    @property
    def magnification(self):
        return self._mag
    
    @magnification.setter
    def magnification(self, mag):
        self._mag = mag
        self.shader_map()
        self.shader_imap()

    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, radius):
        self._radius = radius
        self.shader_map()
        self.shader_imap()

    def shader_map(self):
        fn = super(MagnifyTransform, self).shader_map()
        fn['center'] = self._center  # uniform vec2
        fn['mag'] = self._mag
        fn['radius'] = self._radius / 4.4
        return fn

    def shader_imap(self):
        fn = super(MagnifyTransform, self).shader_imap()
        fn['center'] = self._center  # uniform vec2
        fn['mag'] = 1. / self._mag
        fn['radius'] = self._radius / 4.4
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


class Magnify1DTransform(MagnifyTransform):
    """
    """
    glsl_map = """
        vec4 mag_transform(vec4 pos) {
            float dist = pos.x - $center.x;
            if (dist == 0) {
                return pos;
            }
            
            // gaussian profile
            float m = 1 / ((dist/$radius)*(dist/$radius) + 1);
            // flatten to make nearly linear in the center
            m = pow(1 - pow((1 - m), 100), 100);
            dist = dist * (1 + ($mag-1) * m);

            return vec4($center.x + dist, pos.y, pos.z, pos.w);
        }"""
    
    glsl_imap = glsl_map


class MagCamera(vispy.scene.cameras.PanZoomCamera):
    def __init__(self, *args, **kwds):
        self.mag = MagnifyTransform()
        self.mag._mag = 3
        super(MagCamera, self).__init__(*args, **kwds)

    def view_mouse_event(self, event):
        self.mag.center = event.pos[:2]
        super(MagCamera, self).view_mouse_event(event)
        self._update_transform()
    
    def _set_scene_transform(self, tr):
        vbs = self.viewbox.size
        self.mag.radius = min(vbs) / 4
        super(MagCamera, self)._set_scene_transform(self.mag * tr)


class Mag1DCamera(MagCamera):
    def __init__(self, *args, **kwds):
        self.mag = Magnify1DTransform()
        self.mag._mag = 3
        super(MagCamera, self).__init__(*args, **kwds)

    def _set_scene_transform(self, tr):
        vbs = self.viewbox.size
        self.mag.radius = vbs[0] / 4
        super(MagCamera, self)._set_scene_transform(self.mag * tr)

canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
grid = canvas.central_widget.add_grid()

vb1 = grid.add_view(row=0, col=0, col_span=2)
vb2 = grid.add_view(row=1, col=0)
vb3 = grid.add_view(row=1, col=1)

# Top viewbox
vb1.camera = Mag1DCamera()
pos = np.empty((100, 2))
pos[:,0] = np.arange(100)
pos[:,1] = np.random.normal(size=100, loc=50, scale=10)
line = visuals.Line(pos, color='white', parent=vb1.scene)
line.transform = STTransform(translate=(0, 0, -0.1))
vb1.camera.rect = 0, 0, 100, 100

grid = visuals.GridLines(parent=vb1.scene)


# bottom-left viewbox
img_data = np.random.normal(size=(100, 100, 3), loc=58,
                            scale=20).astype(np.ubyte)


image = visuals.Image(img_data, method='impostor', grid=(100, 100), parent=vb2.scene)
vb2.camera = MagCamera()
#vb2.camera.auto_zoom(image)
vb2.camera.rect = (-1, -1, image.size[0]+2, image.size[1]+2) 









if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
