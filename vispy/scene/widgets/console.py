# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
""" Fast and failsafe GL console """

# Code translated from glumpy

import numpy as np

from .widget import Widget
from ...visuals import Visual
from ...gloo import VertexBuffer
from ...color import Color
from ...ext.six import string_types


# Translated from
# http://www.piclist.com/tecHREF/datafile/charset/
#     extractor/charset_extractor.htm
__font_6x8__ = np.array([
    (0x00, 0x00, 0x00, 0x00, 0x00, 0x00), (0x10, 0xE3, 0x84, 0x10, 0x01, 0x00),
    (0x6D, 0xB4, 0x80, 0x00, 0x00, 0x00), (0x00, 0xA7, 0xCA, 0x29, 0xF2, 0x80),
    (0x20, 0xE4, 0x0C, 0x09, 0xC1, 0x00), (0x65, 0x90, 0x84, 0x21, 0x34, 0xC0),
    (0x21, 0x45, 0x08, 0x55, 0x23, 0x40), (0x30, 0xC2, 0x00, 0x00, 0x00, 0x00),
    (0x10, 0x82, 0x08, 0x20, 0x81, 0x00), (0x20, 0x41, 0x04, 0x10, 0x42, 0x00),
    (0x00, 0xA3, 0x9F, 0x38, 0xA0, 0x00), (0x00, 0x41, 0x1F, 0x10, 0x40, 0x00),
    (0x00, 0x00, 0x00, 0x00, 0xC3, 0x08), (0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00, 0x00, 0xC3, 0x00), (0x00, 0x10, 0x84, 0x21, 0x00, 0x00),
    (0x39, 0x14, 0xD5, 0x65, 0x13, 0x80), (0x10, 0xC1, 0x04, 0x10, 0x43, 0x80),
    (0x39, 0x10, 0x46, 0x21, 0x07, 0xC0), (0x39, 0x10, 0x4E, 0x05, 0x13, 0x80),
    (0x08, 0x62, 0x92, 0x7C, 0x20, 0x80), (0x7D, 0x04, 0x1E, 0x05, 0x13, 0x80),
    (0x18, 0x84, 0x1E, 0x45, 0x13, 0x80), (0x7C, 0x10, 0x84, 0x20, 0x82, 0x00),
    (0x39, 0x14, 0x4E, 0x45, 0x13, 0x80), (0x39, 0x14, 0x4F, 0x04, 0x23, 0x00),
    (0x00, 0x03, 0x0C, 0x00, 0xC3, 0x00), (0x00, 0x03, 0x0C, 0x00, 0xC3, 0x08),
    (0x08, 0x42, 0x10, 0x20, 0x40, 0x80), (0x00, 0x07, 0xC0, 0x01, 0xF0, 0x00),
    (0x20, 0x40, 0x81, 0x08, 0x42, 0x00), (0x39, 0x10, 0x46, 0x10, 0x01, 0x00),
    (0x39, 0x15, 0xD5, 0x5D, 0x03, 0x80), (0x39, 0x14, 0x51, 0x7D, 0x14, 0x40),
    (0x79, 0x14, 0x5E, 0x45, 0x17, 0x80), (0x39, 0x14, 0x10, 0x41, 0x13, 0x80),
    (0x79, 0x14, 0x51, 0x45, 0x17, 0x80), (0x7D, 0x04, 0x1E, 0x41, 0x07, 0xC0),
    (0x7D, 0x04, 0x1E, 0x41, 0x04, 0x00), (0x39, 0x14, 0x17, 0x45, 0x13, 0xC0),
    (0x45, 0x14, 0x5F, 0x45, 0x14, 0x40), (0x38, 0x41, 0x04, 0x10, 0x43, 0x80),
    (0x04, 0x10, 0x41, 0x45, 0x13, 0x80), (0x45, 0x25, 0x18, 0x51, 0x24, 0x40),
    (0x41, 0x04, 0x10, 0x41, 0x07, 0xC0), (0x45, 0xB5, 0x51, 0x45, 0x14, 0x40),
    (0x45, 0x95, 0x53, 0x45, 0x14, 0x40), (0x39, 0x14, 0x51, 0x45, 0x13, 0x80),
    (0x79, 0x14, 0x5E, 0x41, 0x04, 0x00), (0x39, 0x14, 0x51, 0x55, 0x23, 0x40),
    (0x79, 0x14, 0x5E, 0x49, 0x14, 0x40), (0x39, 0x14, 0x0E, 0x05, 0x13, 0x80),
    (0x7C, 0x41, 0x04, 0x10, 0x41, 0x00), (0x45, 0x14, 0x51, 0x45, 0x13, 0x80),
    (0x45, 0x14, 0x51, 0x44, 0xA1, 0x00), (0x45, 0x15, 0x55, 0x55, 0x52, 0x80),
    (0x45, 0x12, 0x84, 0x29, 0x14, 0x40), (0x45, 0x14, 0x4A, 0x10, 0x41, 0x00),
    (0x78, 0x21, 0x08, 0x41, 0x07, 0x80), (0x38, 0x82, 0x08, 0x20, 0x83, 0x80),
    (0x01, 0x02, 0x04, 0x08, 0x10, 0x00), (0x38, 0x20, 0x82, 0x08, 0x23, 0x80),
    (0x10, 0xA4, 0x40, 0x00, 0x00, 0x00), (0x00, 0x00, 0x00, 0x00, 0x00, 0x3F),
    (0x30, 0xC1, 0x00, 0x00, 0x00, 0x00), (0x00, 0x03, 0x81, 0x3D, 0x13, 0xC0),
    (0x41, 0x07, 0x91, 0x45, 0x17, 0x80), (0x00, 0x03, 0x91, 0x41, 0x13, 0x80),
    (0x04, 0x13, 0xD1, 0x45, 0x13, 0xC0), (0x00, 0x03, 0x91, 0x79, 0x03, 0x80),
    (0x18, 0x82, 0x1E, 0x20, 0x82, 0x00), (0x00, 0x03, 0xD1, 0x44, 0xF0, 0x4E),
    (0x41, 0x07, 0x12, 0x49, 0x24, 0x80), (0x10, 0x01, 0x04, 0x10, 0x41, 0x80),
    (0x08, 0x01, 0x82, 0x08, 0x24, 0x8C), (0x41, 0x04, 0x94, 0x61, 0x44, 0x80),
    (0x10, 0x41, 0x04, 0x10, 0x41, 0x80), (0x00, 0x06, 0x95, 0x55, 0x14, 0x40),
    (0x00, 0x07, 0x12, 0x49, 0x24, 0x80), (0x00, 0x03, 0x91, 0x45, 0x13, 0x80),
    (0x00, 0x07, 0x91, 0x45, 0x17, 0x90), (0x00, 0x03, 0xD1, 0x45, 0x13, 0xC1),
    (0x00, 0x05, 0x89, 0x20, 0x87, 0x00), (0x00, 0x03, 0x90, 0x38, 0x13, 0x80),
    (0x00, 0x87, 0x88, 0x20, 0xA1, 0x00), (0x00, 0x04, 0x92, 0x49, 0x62, 0x80),
    (0x00, 0x04, 0x51, 0x44, 0xA1, 0x00), (0x00, 0x04, 0x51, 0x55, 0xF2, 0x80),
    (0x00, 0x04, 0x92, 0x31, 0x24, 0x80), (0x00, 0x04, 0x92, 0x48, 0xE1, 0x18),
    (0x00, 0x07, 0x82, 0x31, 0x07, 0x80), (0x18, 0x82, 0x18, 0x20, 0x81, 0x80),
    (0x10, 0x41, 0x00, 0x10, 0x41, 0x00), (0x30, 0x20, 0x83, 0x08, 0x23, 0x00),
    (0x29, 0x40, 0x00, 0x00, 0x00, 0x00), (0x10, 0xE6, 0xD1, 0x45, 0xF0, 0x00)
], dtype=np.float32)

VERTEX_SHADER = """
uniform vec2 u_logical_scale;
uniform float u_physical_scale;
uniform vec4 u_color;
uniform vec4 u_origin; 

attribute vec2 a_position;
attribute vec3 a_bytes_012;
attribute vec3 a_bytes_345;

varying vec4 v_color;
varying vec3 v_bytes_012, v_bytes_345;

void main (void)
{
    gl_Position = u_origin + vec4(a_position * u_logical_scale, 0., 0.);
    gl_PointSize = 8.0 * u_physical_scale;
    v_color = u_color;
    v_bytes_012 = a_bytes_012;
    v_bytes_345 = a_bytes_345;
}
"""

FRAGMENT_SHADER = """
float segment(float edge0, float edge1, float x)
{
    return step(edge0,x) * (1.0-step(edge1,x));
}

varying vec4 v_color;
varying vec3 v_bytes_012, v_bytes_345;

vec4 glyph_color(vec2 uv) {
    if(uv.x > 5.0 || uv.y > 7.0)
        return vec4(0, 0, 0, 0);
    else {
        float index  = floor( (uv.y*6.0+uv.x)/8.0 );
        float offset = floor( mod(uv.y*6.0+uv.x,8.0));
        float byte = segment(0.0,1.0,index) * v_bytes_012.x
                   + segment(1.0,2.0,index) * v_bytes_012.y
                   + segment(2.0,3.0,index) * v_bytes_012.z
                   + segment(3.0,4.0,index) * v_bytes_345.x
                   + segment(4.0,5.0,index) * v_bytes_345.y
                   + segment(5.0,6.0,index) * v_bytes_345.z;
        if( floor(mod(byte / (128.0/pow(2.0,offset)), 2.0)) > 0.0 )
            return v_color;
        else
            return vec4(0, 0, 0, 0);
    }
}

void main(void)
{
    vec2 loc = gl_PointCoord.xy * 8.0;
    vec2 uv = floor(loc);
    // use multi-sampling to make the text look nicer
    vec2 dxy = 0.25*(abs(dFdx(loc)) + abs(dFdy(loc)));
    vec4 box = floor(vec4(loc-dxy, loc+dxy));
    vec4 color = glyph_color(floor(loc)) +
                 0.25 * glyph_color(box.xy) +
                 0.25 * glyph_color(box.xw) +
                 0.25 * glyph_color(box.zy) +
                 0.25 * glyph_color(box.zw);
    gl_FragColor = color / 2.;
}
"""


class Console(Widget):
    """Fast and failsafe text console

    Parameters
    ----------
    text_color : instance of Color
        Color to use.
    font_size : float
        Point size to use.
    """
    def __init__(self, text_color='black', font_size=12., **kwargs):
        self._visual = ConsoleVisual(text_color, font_size)
        Widget.__init__(self, **kwargs)
        self.add_subvisual(self._visual)
        
    def on_resize(self, event):
        """Resize event handler

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        self._visual.size = self.size
        
    def clear(self):
        """Clear the console"""
        self._visual.clear()

    def write(self, text='', wrap=True):
        """Write text and scroll

        Parameters
        ----------
        text : str
            Text to write. ``''`` can be used for a blank line, as a newline
            is automatically added to the end of each line.
        wrap : str
            If True, long messages will be wrapped to span multiple lines.
        """
        self._visual.write(text)
        
    @property
    def text_color(self):
        """The color of the text"""
        return self._visual._text_color

    @text_color.setter
    def text_color(self, color):
        self._visual._text_color = Color(color)

    @property
    def font_size(self):
        """The font size (in points) of the text"""
        return self._visual._font_size

    @font_size.setter
    def font_size(self, font_size):
        self._visual._font_size = float(font_size)

        
class ConsoleVisual(Visual):
    def __init__(self, text_color, font_size, **kwargs):
        # Harcoded because of font above and shader program
        self.text_color = text_color
        self.font_size = font_size
        self._char_width = 6
        self._char_height = 10
        self._pending_writes = []
        self._text_lines = []
        self._col = 0
        self._current_sizes = (-1,) * 3
        self._size = (100, 100)
        Visual.__init__(self, VERTEX_SHADER, FRAGMENT_SHADER)
        self._draw_mode = 'points'
        self.set_gl_state(depth_test=False, blend=True,
                          blend_func=('src_alpha', 'one_minus_src_alpha'))

    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self, s):
        self._size = s

    @property
    def text_color(self):
        """The color of the text"""
        return self._text_color

    @text_color.setter
    def text_color(self, color):
        self._text_color = Color(color)

    @property
    def font_size(self):
        """The font size (in points) of the text"""
        return self._font_size

    @font_size.setter
    def font_size(self, font_size):
        self._font_size = float(font_size)

    def _resize_buffers(self, font_scale):
        """Resize buffers only if necessary"""
        new_sizes = (font_scale,) + self.size
        if new_sizes == self._current_sizes:  # don't need resize
            return
        self._n_rows = int(max(self.size[1] /
                               (self._char_height * font_scale), 1))
        self._n_cols = int(max(self.size[0] /
                               (self._char_width * font_scale), 1))
        self._bytes_012 = np.zeros((self._n_rows, self._n_cols, 3), np.float32)
        self._bytes_345 = np.zeros((self._n_rows, self._n_cols, 3), np.float32)
        pos = np.empty((self._n_rows, self._n_cols, 2), np.float32)
        C, R = np.meshgrid(np.arange(self._n_cols), np.arange(self._n_rows))
        # We are in left, top orientation
        x_off = 4.
        y_off = 4 - self.size[1] / font_scale
        pos[..., 0] = x_off + self._char_width * C
        pos[..., 1] = y_off + self._char_height * R
        self._position = VertexBuffer(pos)

        # Restore lines
        for ii, line in enumerate(self._text_lines[:self._n_rows]):
            self._insert_text_buf(line, ii)
        self._current_sizes = new_sizes

    def _prepare_draw(self, view):
        xform = view.get_transform()
        tr = view.get_transform('document', 'render')
        logical_scale = np.diff(tr.map(([0, 1], [1, 0])), axis=0)[0, :2]
        tr = view.get_transform('document', 'framebuffer')
        log_to_phy = np.mean(np.diff(tr.map(([0, 1], [1, 0])), axis=0)[0, :2])
        n_pix = (self.font_size / 72.) * 92.  # num of pixels tall
        # The -2 here is because the char_height has a gap built in
        font_scale = max(n_pix / float((self._char_height-2)), 1)
        self._resize_buffers(font_scale)
        self._do_pending_writes()
        self._program['u_origin'] = xform.map((0, 0, 0, 1))
        self._program['u_logical_scale'] = font_scale * logical_scale
        self._program['u_color'] = self.text_color.rgba
        self._program['u_physical_scale'] = font_scale * log_to_phy
        self._program['a_position'] = self._position
        self._program['a_bytes_012'] = VertexBuffer(self._bytes_012)
        self._program['a_bytes_345'] = VertexBuffer(self._bytes_345)

    def _prepare_transforms(self, view):
        pass

    def clear(self):
        """Clear the console"""
        if hasattr(self, '_bytes_012'):
            self._bytes_012.fill(0)
            self._bytes_345.fill(0)
        self._text_lines = [] * self._n_rows
        self._pending_writes = []

    def write(self, text='', wrap=True):
        """Write text and scroll

        Parameters
        ----------
        text : str
            Text to write. ``''`` can be used for a blank line, as a newline
            is automatically added to the end of each line.
        wrap : str
            If True, long messages will be wrapped to span multiple lines.
        """
        # Clear line
        if not isinstance(text, string_types):
            raise TypeError('text must be a string')
        # ensure we only have ASCII chars
        text = text.encode('utf-8').decode('ascii', errors='replace')
        self._pending_writes.append((text, wrap))
        self.update()

    def _do_pending_writes(self):
        """Do any pending text writes"""
        for text, wrap in self._pending_writes:
            # truncate in case of *really* long messages
            text = text[-self._n_cols*self._n_rows:]
            text = text.split('\n')
            text = [t if len(t) > 0 else '' for t in text]
            nr, nc = self._n_rows, self._n_cols
            for para in text:
                para = para[:nc] if not wrap else para
                lines = [para[ii:(ii+nc)] for ii in range(0, len(para), nc)]
                lines = [''] if len(lines) == 0 else lines
                for line in lines:
                    # Update row and scroll if necessary
                    self._text_lines.insert(0, line)
                    self._text_lines = self._text_lines[:nr]
                    self._bytes_012[1:] = self._bytes_012[:-1]
                    self._bytes_345[1:] = self._bytes_345[:-1]
                    self._insert_text_buf(line, 0)
        self._pending_writes = []

    def _insert_text_buf(self, line, idx):
        """Insert text into bytes buffers"""
        self._bytes_012[idx] = 0
        self._bytes_345[idx] = 0
        # Crop text if necessary
        I = np.array([ord(c) - 32 for c in line[:self._n_cols]])
        I = np.clip(I, 0, len(__font_6x8__)-1)
        if len(I) > 0:
            b = __font_6x8__[I]
            self._bytes_012[idx, :len(I)] = b[:, :3]
            self._bytes_345[idx, :len(I)] = b[:, 3:]
