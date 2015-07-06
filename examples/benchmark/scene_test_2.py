# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Compare an optimal plot grid implementation to the same functionality
provided by scenegraph.

Use --vispy-cprofile to see an overview of time spent in all functions.
Use util.profiler and --vispy-profile=ClassName.method_name for more directed
profiling measurements.
"""
from __future__ import division
import numpy as np

from vispy import gloo, app, scene, visuals
from vispy.util.profiler import Profiler


class GridCanvas(app.Canvas):
    def __init__(self, cells, **kwargs):
        m, n = (10, 10)
        self.grid_size = (m, n)
        self.cells = cells
        super(GridCanvas, self).__init__(keys='interactive',
                                         show=True, **kwargs)

    def on_initialize(self, event):
        self.context.set_state(clear_color='black', blend=True,
                               blend_func=('src_alpha', 'one_minus_src_alpha'))

    def on_mouse_move(self, event):
        if event.is_dragging and not event.modifiers:
            dx = (event.pos - event.last_event.pos) * [1, -1]
            i, j = event.press_event.pos / self.size
            m, n = len(self.cells), len(self.cells[0])
            cell = self.cells[int(i*m)][n - 1 - int(j*n)]
            if event.press_event.button == 1:
                offset = (np.array(cell.offset) + 
                          (dx / (np.array(self.size) / [m, n])) *  
                          (2 / np.array(cell.scale)))
                cell.set_transform(offset, cell.scale)
                
            else:
                cell.set_transform(cell.offset, cell.scale * 1.05 ** dx)
            self.update()

    def on_draw(self, event):
        prof = Profiler()  # noqa
        self.context.clear()
        M = len(self.cells)
        N = len(self.cells[0])
        w, h = self.size
        for i in range(M):
            for j in range(N):
                self.context.set_viewport(w*i/M, h*j/N, w/M, h/N)
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


scales = np.array((1.9 / 100., 2. / 10.))


class VisualCanvas(app.Canvas):
    def __init__(self, vis, **kwargs):
        super(VisualCanvas, self).__init__(keys='interactive',
                                           show=True, **kwargs)
        m, n = (10, 10)
        self.grid_size = (m, n)
        self.visuals = vis

    def on_initialize(self, event):
        self.context.set_state(clear_color='black', blend=True,
                               blend_func=('src_alpha', 'one_minus_src_alpha'))

    def on_mouse_move(self, event):
        if event.is_dragging and not event.modifiers:
            dx = np.array(event.pos - event.last_event.pos)
            x, y = event.press_event.pos / self.size
            m, n = self.grid_size
            i, j = int(x*m), n - 1 - int(y*n)
            v = self.visuals[i][j]
            tr = v.transform
            if event.press_event.button == 1:
                tr.translate = np.array(tr.translate)[:2] + \
                    dx * scales * (1, -1)

            else:
                tr.scale = tr.scale[:2] * 1.05 ** (dx * (1, -1))
            self.update()

    def on_draw(self, event):
        prof = Profiler()  # noqa
        self.context.clear()
        M, N = self.grid_size
        w, h = self.size
        for i in range(M):
            for j in range(N):
                self.context.set_viewport(w*i/M, h*j/N, w/M, h/N)
                self.visuals[i][j].draw()


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
            row.append(Line(data, offset=(-50, 0), scale=scales))

    gcanvas = GridCanvas(cells, position=(400, 300), size=(800, 600),
                         title="GridCanvas")

    # Visual version
    vlines = []
    for i in range(M):
        row = []
        vlines.append(row)
        for j in range(N):
            v = visuals.LineVisual(pos=data, color='w', method='gl')
            v.transform = visuals.transforms.STTransform(
                translate=(-1, 0), scale=scales)
            row.append(v)

    vcanvas = VisualCanvas(vlines, position=(400, 300), size=(800, 600), 
                           title="VisualCanvas")

    # Scenegraph version
    scanvas = scene.SceneCanvas(show=True, keys='interactive', 
                                title="SceneCanvas")
    
    scanvas.size = 800, 600
    grid = scanvas.central_widget.add_grid(margin=0)

    lines = []
    for i in range(10):
        lines.append([])
        for j in range(10):
            vb = grid.add_view(camera='panzoom', row=i, col=j)
            vb.camera.set_range([0, 100], [-5, 5], margin=0)
            line = scene.visuals.Line(pos=data, color='w', method='gl')
            vb.add(line)
    scanvas.show()

    import sys
    if sys.flags.interactive != 1:
        app.run()
