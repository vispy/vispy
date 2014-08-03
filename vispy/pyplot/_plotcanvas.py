# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .. import app
from .. import gloo
from ..util.ordereddict import OrderedDict
from ..scene.shaders import ModularProgram
from ..scene.visuals import Visual
from ..scene.transforms import STTransform


class PanZoomTransform(STTransform):
    pan = (0., 0.)

    def move(self, dx, dy):
        """I call this when I want to translate."""
        self.pan = (self.pan[0] + dx/self.scale[0],
                    self.pan[1] + dy/self.scale[1])
        self.translate = (self.pan[0]*self.scale[0],
                          self.pan[1]*self.scale[1])

    def zoom(self, (dx, dy), center=(0., 0.)):
        """I call this when I want to zoom."""
        scale = (self.scale[0] * np.exp(2.5*dx),
                 self.scale[1] * np.exp(2.5*dy))
        tr = self.pan
        self.pan = (tr[0] - center[0] * (1./self.scale[0] - 1./scale[0]),
                    tr[1] + center[1] * (1./self.scale[1] - 1./scale[1]))
        self.scale = scale
        self.translate = (self.pan[0]*self.scale[0],
                          self.pan[1]*self.scale[1])


class MarkerVisual(Visual):
    VERTEX_SHADER = """
        #version 120

        vec4 transform(vec4);

        attribute vec2 a_position;
        attribute vec3 a_color;
        attribute float a_size;

        varying vec4 v_fg_color;
        varying vec4 v_bg_color;
        varying float v_radius;
        varying float v_linewidth;
        varying float v_antialias;

        void main (void) {
            v_radius = a_size;
            v_linewidth = 1.0;
            v_antialias = 1.0;
            v_fg_color  = vec4(0.0,0.0,0.0,0.5);
            v_bg_color  = vec4(a_color, 1.0);
            gl_Position = transform(vec4(a_position, 0., 1.));
            gl_PointSize = 2.0*(v_radius + v_linewidth + 1.5*v_antialias);
        }
    """

    FRAGMENT_SHADER = """
        #version 120
        varying vec4 v_fg_color;
        varying vec4 v_bg_color;
        varying float v_radius;
        varying float v_linewidth;
        varying float v_antialias;
        void main()
        {
            float size = 2.0*(v_radius + v_linewidth + 1.5*v_antialias);
            float t = v_linewidth/2.0-v_antialias;
            float r = length((gl_PointCoord.xy - vec2(0.5,0.5))*size);
            float d = abs(r - v_radius) - t;
            if( d < 0.0 )
                gl_FragColor = v_fg_color;
            else
            {
                float alpha = d/v_antialias;
                alpha = exp(-alpha*alpha);
                if (r > v_radius)
                    gl_FragColor = vec4(v_fg_color.rgb, alpha*v_fg_color.a);
                else
                    gl_FragColor = mix(v_bg_color, v_fg_color, alpha);
            }
        }
    """

    def __init__(self, pos=None, color=None, size=None):
        self._program = ModularProgram(self.VERTEX_SHADER,
                                       self.FRAGMENT_SHADER)
        self.set_data(pos=pos, color=color, size=size)

    def set_options(self):
        gloo.set_state(clear_color=(1, 1, 1, 1), blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

    def set_data(self, pos=None, color=None, size=None):
        self._pos = pos
        self._color = color
        self._size = size

    def draw(self):
        self.set_options()
        self._program.prepare()
        self._program['a_position'] = gloo.VertexBuffer(self._pos)
        self._program['a_color'] = gloo.VertexBuffer(self._color)
        self._program['a_size'] = gloo.VertexBuffer(self._size)
        self._program.draw(gloo.gl.GL_POINTS, 'points')


class LineVisual(Visual):
    VERTEX_SHADER = """
        #version 120
        vec4 transform(vec4);
        attribute vec2 a_position;

        void main (void)
        {
            gl_Position = transform(vec4(a_position, 0., 1.0));
        }
    """

    FRAGMENT_SHADER = """
        #version 120
        uniform vec3 u_color;
        void main()
        {
            gl_FragColor = vec4(u_color.xyz, 1.);
        }
    """

    def __init__(self, pos=None, color=None):
        self._program = ModularProgram(self.VERTEX_SHADER,
                                       self.FRAGMENT_SHADER)
        self.set_data(pos=pos, color=color)

    def set_options(self):
        gloo.set_state(clear_color=(1, 1, 1, 1), blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

    def set_data(self, pos=None, color=None):
        self._pos = pos
        self._color = color

    def draw(self):
        self.set_options()
        self._program.prepare()
        self._program['a_position'] = gloo.VertexBuffer(self._pos)
        self._program['u_color'] = self._color
        self._program.draw(gloo.gl.GL_LINE_STRIP, 'line_strip')


class PlotCanvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, close_keys='escape')
        self._visuals = OrderedDict()
        self.panzoom = PanZoomTransform()

    def _normalize(self, (x, y)):
        w, h = float(self.size[0]), float(self.size[1])
        return x/(w/2.)-1., y/(h/2.)-1.

    def add_visual(self, name, value):
        assert name not in self._visuals
        self._visuals[name] = value
        value._program['transform'] = self.panzoom.shader_map()

    def on_mouse_move(self, event):
        if event.is_dragging:
            x0, y0 = self._normalize(event.press_event.pos)
            x1, y1 = self._normalize(event.last_event.pos)
            x, y = self._normalize(event.pos)
            dxy = ((x - x1), -(y - y1))
            center = (x0, y0)
            button = event.press_event.button

            if button == 1:
                self.panzoom.move(dxy)
            elif button == 2:
                self.panzoom.zoom(dxy, center=center)

            self.update()
            self.panzoom.shader_map()

    def on_mouse_wheel(self, event):
        c = event.delta[1] * .1
        x, y = self._normalize(event.pos)
        self.panzoom.zoom((c, c), center=(x, y))
        self.update()
        self.panzoom.shader_map()

    def on_resize(self, event):
        self.width, self.height = event.size
        gloo.set_viewport(0, 0, self.width, self.height)

    def on_draw(self, event):
        gloo.clear()
        for v in self._visuals.values():
            v.draw()
