# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import numpy as np

from .visual import Visual
from .. import gloo


class ScrollingLinesVisual(Visual):
    vertex_code = """
    attribute vec2 index;  // .x=line #, .y=vertex #
    uniform sampler2D position;
    
    uniform vec2 pos_size;
    uniform float offset;
    uniform int columns;
    uniform float dt;
    uniform vec2 cell_size;
    
    varying vec2 v_index;
    
    
    void main() {
        v_index = vec2(mod(index.x + offset, pos_size.x), index.y);
        vec4 pos = vec4(index.x * dt, texture2D(position, v_index / (pos_size-1)).r, 0, 1);
        float col = mod(v_index.y, columns);
        float row = (v_index.y - col) / columns;
        pos = pos + vec4(col * cell_size.x, row * cell_size.y, 0, 0);
        gl_Position = $transform(pos);
    }
    """
    
    fragment_code = """
    varying vec2 v_index;
    
    void main() {
        if (v_index.y - floor(v_index.y) > 0) {
            discard;
        }
        gl_FragColor = vec4(1, 1, 1, 1);
    }
    """
    
    def __init__(self, n_lines, line_size, dt, columns=1, cell_size=(1, 1)):
        """Displays many lines of equal length, with the option to add new
        vertex data to one end of the lines.
        """
        self._pos_data = None
        self._offset = 0
        
        data = np.zeros((n_lines, line_size), dtype='float32')
        self._pos_tex = gloo.Texture2D(data, format='luminance', internalformat='r32f')
        self._index_buf = gloo.VertexBuffer()
        self._data_shape = data.shape
        
        Visual.__init__(self, vcode=self.vertex_code, fcode=self.fragment_code)
        
        self.shared_program['position'] = self._pos_tex
        self.shared_program['index'] = self._index_buf
        self.shared_program['columns'] = columns
        self.shared_program['cell_size'] = cell_size
        self.shared_program['dt'] = dt
        self.shared_program['pos_size'] = data.shape[::-1]
        self.shared_program['offset'] = self._offset
        
        index = np.empty((data.shape[0], data.shape[1], 2), dtype='float32')
        index[..., 1] = np.arange(data.shape[0])[:, np.newaxis]
        index[..., 0] = np.arange(data.shape[1])[np.newaxis, :]
        index = index.reshape((index.shape[0]*index.shape[1], index.shape[2]))
        self._index_buf.set_data(index)
        
        self._draw_mode = 'line_strip'
        self.set_gl_state('translucent', line_width=1)

    def _prepare_transforms(self, view):
        view.view_program.vert['transform'] = view.get_transform().simplified
        
    def _prepare_draw(self, view):
        pass
    
    def _compute_bounds(self, axis, view):
        if self._pos_data is None:
            return None
        return self._pos_data[..., axis].min(), self.pos_data[..., axis].max()
    
    def roll_data(self, data):
        data = data.astype('float32')[..., np.newaxis]
        s1 = self._data_shape[1] - self._offset
        if data.shape[1] > s1:
            self._pos_tex[:, self._offset:] = data[:, :s1]
            self._pos_tex[:, :data.shape[1] - s1] = data[:, s1:]
            self._offset = (self._offset + data.shape[1]) % self._data_shape[1]
        else:
            self._pos_tex[:, self._offset:self._offset+data.shape[1]] = data
            self._offset += data.shape[1]
        self.shared_program['offset'] = self._offset
        self.update()
