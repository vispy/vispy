# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
from __future__ import division
import numpy as np

from vispy import app
from vispy.gloo import VertexBuffer
from vispy.visuals import Visual
from vispy.visuals.transforms import STTransform


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
        Visual.__init__(self, self.VERTEX_SHADER, self.FRAGMENT_SHADER)
        self._pos = pos
        self._color = color
        self._size = size
        self.set_gl_state(blend=True,
                          blend_func=('src_alpha', 'one_minus_src_alpha'))
        self._draw_mode = 'points'

    def _prepare_transforms(self, view=None):
        view.view_program.vert['transform'] = view.transforms.get_transform()

    def _prepare_draw(self, view):
        # attributes / uniforms are not available until program is built
        self.shared_program['a_position'] = VertexBuffer(self._pos)
        self.shared_program['a_color'] = VertexBuffer(self._color)
        self.shared_program['a_size'] = VertexBuffer(self._size)


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive')
        ps = self.pixel_scale

        n = 10000
        pos = 0.25 * np.random.randn(n, 2).astype(np.float32)
        color = np.random.uniform(0, 1, (n, 3)).astype(np.float32)
        size = np.random.uniform(2*ps, 12*ps, (n, 1)).astype(np.float32)

        self.points = MarkerVisual(pos=pos, color=color, size=size)
        w, h = self.size
        self.points.transform = STTransform(scale=(w / 2., h / 2.),
                                            translate=(w / 2., h / 2.))

    def on_mouse_move(self, event):
        if event.is_dragging:
            dxy = event.pos - event.last_event.pos
            button = event.press_event.button

            if button == 1:
                self.points.transform.move(dxy)
            elif button == 2:
                center = event.press_event.pos
                self.points.transform.zoom(np.exp(dxy * (0.01, -0.01)), center)

            self.update()

    def on_resize(self, event):
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        self.points.transforms.configure(canvas=self, viewport=vp)

    def on_draw(self, event):
        self.context.clear('white')
        self.points.draw()

if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
