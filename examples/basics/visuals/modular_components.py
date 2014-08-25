# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Demonstrates plugging custom shaders in to a ModularLine visual.

This allows to modify the appearance of the visual without modifying or
subclassing the original ModularLine class.
"""

import numpy as np
import vispy.app
import vispy.gloo as gloo
from vispy.scene.visuals.modular_line import ModularLine
from vispy.scene.transforms import BaseTransform, STTransform, arg_to_array
from vispy.scene.components import (VisualComponent, VertexColorComponent,
                                    XYPosComponent)
from vispy.scene.shaders import Varying

# vertex positions of data to draw
N = 50
pos = np.zeros((N, 2), dtype=np.float32)
pos[:, 0] = np.linspace(-0.9, 0.9, N)
pos[:, 1] = np.random.normal(size=N, scale=0.2).astype(np.float32)

# One array of colors
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]


# A custom Transform
class SineTransform(BaseTransform):
    """
    Add sine wave to y-value for wavy effect.
    """
    glsl_map = """
        vec4 sineTransform(vec4 pos) {
            return vec4(pos.x, pos.y + sin(pos.x), pos.z, 1);
        }"""

    @arg_to_array
    def map(self, coords):
        ret = coords.copy()
        ret[..., 1] += np.sin(ret[..., 0])
        return ret

    @arg_to_array
    def imap(self, coords):
        ret = coords.copy()
        ret[..., 1] -= np.sin(ret[..., 0])
        return ret


# Custom color component
class DashComponent(VisualComponent):
    """
    VisualComponent that adds dashing to an attached LineVisual.
    """

    SHADERS = dict(
        frag_color="""
            vec4 dash(vec4 color) {
                float mod = $distance / $dash_len;
                mod = mod - float(int(mod));
                color.a = 0.5 * sin(mod*3.141593*2.) + 0.5;
                return color;
            }
        """,
        vert_post_hook="""
            void dashSup() {
                $output_dist = $distance_attr;
            }
        """)

    def __init__(self, pos):
        super(DashComponent, self).__init__()
        self._vbo = None
        self.pos = pos

    def _make_vbo(self):
        if self._vbo is None:
            # measure distance along line
            # TODO: this should be recomputed if the line data changes.
            pixel_tr = self.visual.transform
            pixel_pos = pixel_tr.map(self.pos)
            dist = np.empty(pos.shape[0], dtype=np.float32)
            diff = ((pixel_pos[1:] - pixel_pos[:-1]) ** 2).sum(axis=1) ** 0.5
            dist[0] = 0.0
            dist[1:] = np.cumsum(diff)
            self._vbo = gloo.VertexBuffer(dist)
        return self._vbo

    def activate(self, program, mode):
        vf = self._funcs['vert_post_hook']
        ff = self._funcs['frag_color']
        vf['distance_attr'] = self._make_vbo()  # attribute float
        vf['output_dist'] = Varying('output_dist', dtype='float')
        ff['dash_len'] = 20.
        ff['distance'] = vf['output_dist']

    @property
    def supported_draw_modes(self):
        return set((self.DRAW_PRE_INDEXED,))


# custom position component
class WobbleComponent(VisualComponent):
    """
    Give all vertices a wobble with random phase.
    """
    SHADERS = dict(
        local_position="""
            vec4 wobble(vec4 pos) {
                float x = pos.x + 0.01 * cos($theta + $phase);
                float y = pos.y + 0.01 * sin($theta + $phase);
                return vec4(x, y, pos.z, pos.w);
            }
        """)

    def __init__(self, pos):
        super(WobbleComponent, self).__init__()
        self._vbo = None
        self.pos = pos
        self.theta = (np.random.random(size=pos.shape[:-1]).astype(np.float32)
                      * (2. * np.pi))
        self.phase = 0

    def activate(self, program, mode):
        if self._vbo is None:
            self._vbo = gloo.VertexBuffer(self.theta)

        pf = self._funcs['local_position']
        pf['theta'] = self._vbo
        pf['phase'] = self.phase

        # TODO: make this automatic
        self._visual._program._need_build = True


class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):

        self.line = ModularLine()
        self.line.transform = (STTransform(scale=(40, 100), 
                                           translate=(400, 400)) *
                               SineTransform() *
                               STTransform(scale=(10, 3)))
        self.wobbler = WobbleComponent(pos)
        self.line.pos_components = [XYPosComponent(pos), self.wobbler]
        dasher = DashComponent(pos)
        self.line.color_components = [VertexColorComponent(color), dasher]

        vispy.scene.SceneCanvas.__init__(self, keys='interactive')
        self.size = (800, 800)
        self.show()

        self.timer = vispy.app.Timer(connect=self.wobble,
                                     interval=0.02,
                                     start=True)

    def on_draw(self, ev):
        gloo.set_clear_color('black')
        gloo.clear(color=True, depth=True)

        self.draw_visual(self.line)

    def wobble(self, ev):
        self.wobbler.phase += 0.1
        self.update()


if __name__ == '__main__':
    win = Canvas()
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
