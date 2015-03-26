# -*- coding: utf-8 -*-
# vispy: gallery 30
# vispy: testskip - because this example sometimes sets inactive attributes
"""Computing a Voronoi diagram on the GPU. Shows how to use uniform arrays.

Original version by Xavier Olive (xoolive).

"""

import numpy as np

from vispy import app
from vispy import gloo


# Voronoi shaders.
VS_voronoi = """
attribute vec2 a_position;

void main() {
    gl_Position = vec4(a_position, 0., 1.);
}
"""

FS_voronoi = """
uniform vec2 u_seeds[32];
uniform vec3 u_colors[32];
uniform vec2 u_screen;

void main() {
    float dist = distance(u_screen * u_seeds[0], gl_FragCoord.xy);
    vec3 color = u_colors[0];
    for (int i = 1; i < 32; i++) {
        float current = distance(u_screen * u_seeds[i], gl_FragCoord.xy);
        if (current < dist) {
            color = u_colors[i];
            dist = current;
        }
    }
    gl_FragColor = vec4(color, 1.0);
}
"""


# Seed point shaders.
VS_seeds = """
attribute vec2 a_position;
uniform float u_ps;

void main() {
    gl_Position = vec4(2. * a_position - 1., 0., 1.);
    gl_PointSize = 10. * u_ps;
}
"""

FS_seeds = """
varying vec3 v_color;
void main() {
    gl_FragColor = vec4(1., 1., 1., 1.);
}
"""


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, size=(600, 600), title='Voronoi diagram',
                            keys='interactive')

        self.ps = self.pixel_scale

        self.seeds = np.random.uniform(0, 1.0*self.ps,
                                       size=(32, 2)).astype(np.float32)
        self.colors = np.random.uniform(0.3, 0.8,
                                        size=(32, 3)).astype(np.float32)

        # Set Voronoi program.
        self.program_v = gloo.Program(VS_voronoi, FS_voronoi)
        self.program_v['a_position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
        # HACK: work-around a bug related to uniform arrays until
        # issue #345 is solved.
        for i in range(32):
            self.program_v['u_seeds[%d]' % i] = self.seeds[i, :]
            self.program_v['u_colors[%d]' % i] = self.colors[i, :]

        # Set seed points program.
        self.program_s = gloo.Program(VS_seeds, FS_seeds)
        self.program_s['a_position'] = self.seeds
        self.program_s['u_ps'] = self.ps

        self.activate_zoom()

        self.show()

    def on_draw(self, event):
        gloo.clear()
        self.program_v.draw('triangle_strip')
        self.program_s.draw('points')

    def on_resize(self, event):
        self.activate_zoom()

    def activate_zoom(self):
        self.width, self.height = self.size
        gloo.set_viewport(0, 0, *self.physical_size)
        self.program_v['u_screen'] = (self.width, self.height)

    def on_mouse_move(self, event):
        x, y = event.pos
        x, y = x/float(self.width), 1-y/float(self.height)
        self.program_v['u_seeds[0]'] = x*self.ps, y*self.ps
        # TODO: just update the first line in the VBO instead of uploading the
        # whole array of seed points.
        self.seeds[0, :] = x, y
        self.program_s['a_position'].set_data(self.seeds)
        self.update()

if __name__ == "__main__":
    c = Canvas()
    app.run()
