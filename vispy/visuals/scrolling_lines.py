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
    attribute vec2 index;  // .x=line_n, .y=vertex_n
    uniform sampler2D position;
    uniform sampler1D pos_offset;
    uniform sampler1D color;
    
    uniform vec2 pos_size;  // x=n_lines, y=n_verts_per_line
    uniform float offset;  // rolling pointer into vertexes
    uniform float dx;  // x step per sample
    
    varying vec2 v_index;
    varying vec4 v_color;
    
    
    void main() {
        v_index = vec2(mod(index.y + offset, pos_size.y), index.x);
        vec2 uv = (v_index + 0.5) / (pos_size.yx);
        vec4 pos = vec4(index.y * dx, texture2D(position, uv).r, 0, 1);
        
        // fetch starting position from texture lookup:
        pos += vec4(texture1D(pos_offset, (index.x + 0.5) / pos_size.x).rg, 0, 0); 
        
        gl_Position = $transform(pos);
        
        v_color = vec4(1, 1, 1, 1); //texture1D(color, (index.x + 0.5) / pos_size.x);
    }
    """
    
    fragment_code = """
    varying vec2 v_index;
    varying vec4 v_color;
    
    void main() {
        if (v_index.y - floor(v_index.y) > 0) {
            discard;
        }
        gl_FragColor = $color;
    }
    """
    
    def __init__(self, n_lines, line_size, dx, color=None, pos_offset=None,
                 columns=None, cell_size=None):
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
        self.shared_program['dx'] = dx
        self.shared_program['pos_size'] = data.shape
        self.shared_program['offset'] = self._offset
        
        # set an array giving the x/y origin for each plot
        if pos_offset is None:
            # construct positions as a grid 
            rows = np.ceil(n_lines / columns)
            pos_offset = np.empty((rows, columns, 3), dtype='float32')
            pos_offset[..., 0] = np.arange(columns)[np.newaxis, :] * cell_size[0]
            pos_offset[..., 1] = np.arange(rows)[:, np.newaxis] * cell_size[1]
            pos_offset = pos_offset.reshape((rows*columns), 3)
        self._pos_offset = gloo.Texture1D(pos_offset, internalformat='rgb32f',
                                          interpolation='nearest')
        self.shared_program['pos_offset'] = self._pos_offset

        if color is None:
            self.shared_program.frag['color'] = (1, 1, 1, 1)
        else:
            self._color_tex = gloo.Texture1D(color)
            self.shared_program.frag['color'] = 'v_color'
        
        # construct a vertex buffer index containing (plot_n, vertex_n) for
        # each vertex
        index = np.empty((data.shape[0], data.shape[1], 2), dtype='float32')
        index[..., 0] = np.arange(data.shape[0])[:, np.newaxis]
        index[..., 1] = np.arange(data.shape[1])[np.newaxis, :]
        index = index.reshape((index.shape[0]*index.shape[1], index.shape[2]))
        self._index_buf.set_data(index)
        
        self._draw_mode = 'line_strip'
        self.set_gl_state('translucent', line_width=1)

    def set_pos_offset(self, po):
        self._pos_offset.set_data(po)

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

    def set_data(self, index, data):
        self._pos_tex[index] = data
        self.update()
        
                 