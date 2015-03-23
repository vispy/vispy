# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Compare an optimal plot grid implementation to the same functionality
provided by scenegraph.
"""
from __future__ import division
import numpy as np
import math

from vispy import gloo, app, scene
from vispy.visuals import Visual
from vispy.visuals.shaders import ModularProgram, Function, Variable
from vispy.visuals.transforms import TransformSystem, BaseTransform
from vispy.util.profiler import Profiler



class GridCanvas(app.Canvas):
    def __init__(self, cells, **kwargs):
        super(GridCanvas, self).__init__(keys='interactive',
                                            show=True, **kwargs)
        m, n = (10, 10)
        self.grid_size = (m, n)
        self.cells = cells

    def on_initialize(self, event):
        gloo.set_state(clear_color='black', blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

    def on_mouse_move(self, event):
        if event.is_dragging and not event.modifiers:
            dx = (event.pos - event.last_event.pos) * [1, -1]
            i, j = event.press_event.pos / self.size
            m, n = len(self.cells), len(self.cells[0])
            cell = self.cells[int(i*m)][n - 1 - int(j*n)]
            if event.press_event.button == 1:
                offset = np.array(cell.offset) + (dx / (np.array(self.size) / [m, n])) *  (2 / np.array(cell.scale))
                cell.set_transform(offset, cell.scale)
                
            else:
                cell.set_transform(cell.offset, cell.scale * 1.05 ** dx)
            #x0, y0 = self._normalize(event.press_event.pos)
            #x1, y1 = self._normalize(event.last_event.pos)
            #x, y = self._normalize(event.pos)
            #dx, dy = x - x1, -(y - y1)
            #button = event.press_event.button

            #pan_x, pan_y = self._pz.pan
            #zoom_x, zoom_y = self._pz.zoom

            #if button == 1:
                #self._pz.pan = (pan_x + dx/zoom_x,
                                #pan_y + dy/zoom_y)
            #elif button == 2:
                #zoom_x_new, zoom_y_new = (zoom_x * math.exp(2.5 * dx),
                                          #zoom_y * math.exp(2.5 * dy))
                #self._pz.zoom = (zoom_x_new, zoom_y_new)
                #self._pz.pan = (pan_x - x0 * (1./zoom_x - 1./zoom_x_new),
                                #pan_y + y0 * (1./zoom_y - 1./zoom_y_new))
            self.update()

    def on_draw(self, event):
        prof = Profiler()
        gloo.clear()
        M = len(self.cells)
        N = len(self.cells[0])
        w, h = self.size
        for i in range(M):
            for j in range(N):
                gloo.set_viewport(w*i/M, h*j/N, w/M, h/N)
                self.cells[i][j].draw()


vert = """
attribute vec2 pos;
uniform vec2 offset;
uniform vec2 scale;

void main() {
    gl_Position = vec4((pos + offset) * scale, 0, 1);
}
"""

frag = """
void main() {
    gl_FragColor = vec4(1, 1, 1, 0.5);
}
"""


class Line(object):
    def __init__(self, data, offset, scale):
        self.data = gloo.VertexBuffer(data)
        self.program = gloo.Program(vert, frag)
        self.program['pos'] = self.data
        self.set_transform(offset, scale)
        
    def set_transform(self, offset, scale):
        self.offset = offset
        self.scale = scale
        self.program['offset'] = self.offset
        self.program['scale'] = self.scale
    
    def draw(self):
        self.program.draw('line_strip')


if __name__ == '__main__':
    M, N = (10, 10)
    
    data = np.empty((10000, 2), dtype=np.float32)
    data[:, 0] = np.linspace(0, 100, data.shape[0])
    data[:, 1] = np.random.normal(size=data.shape[0])
    
    
    # Optimized version
    cells = []
    for i in range(M):
        row = []
        cells.append(row)
        for j in range(N):
            row.append(Line(data, offset=(-50, 0), scale=(1.9/100, 2/10)))
    
    gcanvas = GridCanvas(cells, position=(400, 300), size=(800, 600), 
                         title="GridCanvas")
    
    
    # Scenegraph version
    scanvas = scene.SceneCanvas(show=True, keys='interactive', 
                                title="SceneCanvas")
    
    
    scanvas.size = 800, 600
    scanvas.show()
    grid = scanvas.central_widget.add_grid()

    lines = []
    for i in range(10):
        lines.append([])
        for j in range(10):
            vb = grid.add_view(row=i, col=j)
            vb.camera.rect = (0, -5), (100, 10)
            vb.border = (1, 1, 1, 0.4)
            line = scene.visuals.Line(pos=data, color=(1, 1, 1, 0.5), mode='gl')
            vb.add(line)
    
    
    import sys
    if sys.flags.interactive != 1:
        app.run()
