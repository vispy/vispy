# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""
Show vector field flow
"""

from __future__ import division

from vispy import app, scene, visuals, gloo
from vispy.util import ptime
import numpy as np


class VectorFieldVisual(visuals.Visual):
    vertex = """
    uniform sampler2D field;
    attribute vec2 index;
    uniform vec2 shape;
    uniform vec2 field_shape;
    uniform float spacing;
    varying float dist;  // distance along path for this vertex
    varying vec2 ij;
    uniform sampler2D offset;
    uniform float seg_len;
    uniform int n_iter;  // iterations to integrate along field per vertex
    uniform vec2 attractor;
    varying vec4 base_color;
    uniform sampler2D color;
    
    void main() {
        // distance along one line
        dist = index.y * seg_len;
        
        vec2 local;
        ij = vec2(mod(index.x, shape.x), floor(index.x / shape.x));
        // *off* is a random offset to the starting location, which prevents
        // the appearance of combs in the field 
        vec2 off = texture2D(offset, ij / shape).xy - 0.5;
        local = spacing * (ij + off);
        vec2 uv;
        vec2 dir;
        vec2 da;
        for( int i=0; i<index.y; i+=1 ) {
            for ( int j=0; j<n_iter; j += 1 ) {
                uv = local / field_shape;
                dir = texture2D(field, uv).xy;
                
                // add influence of variable attractor (mouse)
                da = attractor - local;
                float al = 0.1 * length(da);
                da /= 0.5 * (1 + al*al);
                
                dir += da;
                
                // maybe pick a more accurate integration method?
                local += seg_len * dir / n_iter;
            }
        }
        base_color = texture2D(color, uv);
        
        gl_Position = $transform(vec4(local, 0, 1));
    }
    """
    
    fragment = """
    uniform float time;
    uniform float speed;
    varying float dist;
    varying vec2 ij;
    uniform sampler2D offset;
    uniform vec2 shape;
    uniform float nseg;
    uniform float seg_len;
    varying vec4 base_color;
    
    void main() {
        float totlen = nseg * seg_len;
        float phase = texture2D(offset, ij / shape).b;
        float alpha;
        
        // vary alpha along the length of the line to give the appearance of
        // motion
        alpha = mod((dist / totlen) + phase - time * speed, 1);
        
        // add a cosine envelope to fade in and out smoothly at the ends
        alpha *= (1 - cos(2 * 3.141592 * dist / totlen)) * 0.5;
        
        gl_FragColor = vec4(base_color.rgb, base_color.a * alpha);
    }
    """
    
    def __init__(self, field, spacing=10, segments=3, seg_len=0.5,
                 color=(1, 1, 1, 0.3)):
        self._time = 0.0
        self._last_time = ptime.time()
        rows = int(field.shape[0] / spacing)
        cols = int(field.shape[1] / spacing)
        index = np.empty((rows * cols, int(segments) * 2, 2), dtype=np.float32)
        
        # encodes starting position within vector field
        index[:, :, 0] = np.arange(rows * cols)[:, np.newaxis]
        # encodes distance along length of line
        index[:, ::2, 1] = np.arange(segments)[np.newaxis, :]
        index[:, 1::2, 1] = np.arange(segments)[np.newaxis, :] + 1
        self._index = gloo.VertexBuffer(index)
        if not isinstance(color, np.ndarray):
            color = np.array([[list(color)]], dtype='float32')
        self._color = gloo.Texture2D(color)
        
        offset = np.random.uniform(256, size=(rows, cols, 3)).astype(np.ubyte)
        self._offset = gloo.Texture2D(offset, format='rgb')
        self._field = gloo.Texture2D(field, format='rg',
                                     internalformat='rg32f',
                                     interpolation='linear')
        self._field_shape = field.shape[:2]
        
        visuals.Visual.__init__(self, vcode=self.vertex, fcode=self.fragment)
        self.timer = app.Timer(interval='auto', connect=self.update_time,
                               start=False)
        self.freeze()
        
        self.shared_program['field'] = self._field
        self.shared_program['field_shape'] = self._field.shape[:2]
        self.shared_program['shape'] = (rows, cols)
        self.shared_program['index'] = self._index
        self.shared_program['spacing'] = spacing
        self.shared_program['t'] = self._time
        self.shared_program['offset'] = self._offset
        self.shared_program['speed'] = 1
        self.shared_program['color'] = self._color
        self.shared_program['seg_len'] = seg_len
        self.shared_program['nseg'] = segments
        self.shared_program['n_iter'] = 1
        self.shared_program['attractor'] = (0, 0)
        self.shared_program['time'] = 0
        self._draw_mode = 'lines'
        self.set_gl_state('translucent', depth_test=False)
        
        self.timer.start()
        
    def _prepare_transforms(self, view):
        view.view_program.vert['transform'] = view.get_transform()
        
    def _prepare_draw(self, view):
        pass
    
    def _compute_bounds(self, axis, view):
        if axis > 1:
            return (0, 0)
        return (0, self._field_shape[axis])

    def update_time(self, ev):
        t = ptime.time()
        self._time += t - self._last_time
        self._last_time = t
        self.shared_program['time'] = self._time
        self.update()


VectorField = scene.visuals.create_visual_node(VectorFieldVisual)


def fn(y, x):
    dx = x-50
    dy = y-30
    l = (dx**2 + dy**2)**0.5 + 0.01
    return np.array([100 * dy / l**1.7, -100 * dx / l**1.8])

field = np.fromfunction(fn, (100, 100)).transpose(1, 2, 0).astype('float32')
field[..., 0] += 10 * np.cos(np.linspace(0, 2 * 3.1415, 100))

color = np.zeros((100, 100, 4), dtype='float32')
color[..., :2] = (field + 5) / 10.
color[..., 2] = 0.5
color[..., 3] = 0.5

canvas = scene.SceneCanvas(keys='interactive', show=True)
view = canvas.central_widget.add_view(camera='panzoom')

vfield = VectorField(field[..., :2], spacing=0.5, segments=30, seg_len=0.05,
                     parent=view.scene, color=color)
view.camera.set_range()


@canvas.connect
def on_mouse_move(event):
    if 3 in event.buttons:
        tr = canvas.scene.node_transform(vfield)
        vfield.shared_program['attractor'] = tr.map(event.pos)[:2]


if __name__ == '__main__':
    app.run()
