# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
from __future__ import division
import numpy as np

from vispy import app
from vispy import gloo
from vispy.visuals.shaders import ModularProgram
from vispy.visuals import Visual
from vispy.visuals.transforms import (STTransform, LogTransform,
                                      TransformSystem, ChainTransform)


class MarkerVisual(Visual):
    # My full vertex shader, with just a `transform` hook.
    VERTEX_SHADER = """
        #version 120

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
            v_bg_color  = vec4(a_color,    1.0);

            gl_Position = $transform(vec4(a_position,0,1));

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
        """Special function that is used to set the options. Automatically
        called at initialization."""
        gloo.set_state(clear_color=(1, 1, 1, 1), blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

    def set_data(self, pos=None, color=None, size=None):
        """I'm not required to use this function. We could also have a system
        of trait attributes, such that a user doing
        `visual.position = myndarray` results in an automatic update of the
        buffer. Here I just set the buffers manually."""
        self._pos = pos
        self._color = color
        self._size = size

    def draw(self, transforms):
        # attributes / uniforms are not available until program is built
        tr = transforms.get_full_transform()
        self._program.vert['transform'] = tr.shader_map()
        self._program.prepare()  # Force ModularProgram to set shaders
        self._program['a_position'] = gloo.VertexBuffer(self._pos)
        self._program['a_color'] = gloo.VertexBuffer(self._color)
        self._program['a_size'] = gloo.VertexBuffer(self._size)
        self._program.draw('points')


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive')
        ps = self.pixel_scale

        n = 10000
        pos = 0.25 * np.random.randn(n, 2).astype(np.float32)
        color = np.random.uniform(0, 1, (n, 3)).astype(np.float32)
        size = np.random.uniform(2*ps, 12*ps, (n, 1)).astype(np.float32)

        self.points = MarkerVisual(pos=pos, color=color, size=size)

        self.panzoom = STTransform(scale=(1, 0.2), translate=(0, 500))
        w2 = (self.size[0]/2, self.size[1]/2)
        self.transform = ChainTransform([self.panzoom,
                                         STTransform(scale=w2, translate=w2),
                                         LogTransform(base=(0, 2, 0))])

        self.tr_sys = TransformSystem(self)
        self.tr_sys.visual_to_document = self.transform

        gloo.set_state(blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

    def on_mouse_move(self, event):
        if event.is_dragging:
            dxy = event.pos - event.last_event.pos
            button = event.press_event.button

            if button == 1:
                self.panzoom.move(dxy)
            elif button == 2:
                center = event.press_event.pos
                self.panzoom.zoom(np.exp(dxy * (0.01, -0.01)), center)

            self.update()

    def on_resize(self, event):
        self.width, self.height = event.size
        gloo.set_viewport(0, 0, self.width, self.height)

    def on_draw(self, event):
        gloo.clear()
        self.points.draw(self.tr_sys)

if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
