# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# 2014, Almar Klein
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------

""" Visualization of traveling through space.
"""

import time

import numpy as np

from vispy import gloo
from vispy import app
from vispy.util.transforms import perspective


vertex = """
#version 120

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform float u_time_offset;
uniform float u_pixel_scale;

attribute vec3  a_position;
attribute float a_offset;

varying float v_pointsize;

void main (void) {

    vec3 pos = a_position;
    pos.z = pos.z - a_offset - u_time_offset;
    vec4 v_eye_position = u_view * u_model * vec4(pos, 1.0);
    gl_Position = u_projection * v_eye_position;

    // stackoverflow.com/questions/8608844/...
    //  ... resizing-point-sprites-based-on-distance-from-the-camera
    float radius = 1;
    vec4 corner = vec4(radius, radius, v_eye_position.z, v_eye_position.w);
    vec4  proj_corner = u_projection * corner;
    gl_PointSize = 100.0 * u_pixel_scale * proj_corner.x / proj_corner.w;
    v_pointsize = gl_PointSize;
}
"""

fragment = """
#version 120
varying float v_pointsize;
void main()
{
    float x = 2.0*gl_PointCoord.x - 1.0;
    float y = 2.0*gl_PointCoord.y - 1.0;
    float a = 0.9 - (x*x + y*y);
    a = a * min(1.0, v_pointsize/1.5);
    gl_FragColor = vec4(1.0, 1.0, 1.0, a);
}
"""

N = 100000  # Number of stars
SIZE = 100
SPEED = 4.0  # time in seconds to go through one block
NBLOCKS = 10


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, title='Spacy', keys='interactive',
                            size=(800, 600))

        self.program = gloo.Program(vertex, fragment)
        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)

        self.activate_zoom()

        self.timer = app.Timer('auto', connect=self.update, start=True)

        # Set uniforms (some are set later)
        self.program['u_model'] = self.model
        self.program['u_view'] = self.view
        self.program['u_pixel_scale'] = self.pixel_scale

        # Set attributes
        self.program['a_position'] = np.zeros((N, 3), np.float32)
        self.program['a_offset'] = np.zeros((N, 1), np.float32)

        # Init
        self._timeout = 0
        self._active_block = 0
        for i in range(NBLOCKS):
            self._generate_stars()
        self._timeout = time.time() + SPEED

        gloo.set_state(clear_color='black', depth_test=False,
                       blend=True, blend_equation='func_add',
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

        self.show()

    def on_key_press(self, event):
        if event.text == ' ':
            if self.timer.running:
                self.timer.stop()
            else:
                self.timer.start()

    def on_resize(self, event):
        self.activate_zoom()

    def activate_zoom(self):
        width, height = self.size
        gloo.set_viewport(0, 0, *self.physical_size)
        far = SIZE*(NBLOCKS-2)
        self.projection = perspective(25.0, width / float(height), 1.0, far)
        self.program['u_projection'] = self.projection

    def on_draw(self, event):
        # Set time offset. Factor runs from 1 to 0
        # the time offset goes from 0 to size
        factor = (self._timeout - time.time()) / SPEED
        self.program['u_time_offset'] = -(1-factor) * SIZE

        # Draw
        gloo.clear()
        self.program.draw('points')

        # Build new starts if the first block is fully behind us
        if factor < 0:
            self._generate_stars()

    def on_close(self, event):
        self.timer.stop()

    def _generate_stars(self):

        # Get number of stars in each block
        blocksize = N // NBLOCKS

        # Update active block
        self._active_block += 1
        if self._active_block >= NBLOCKS:
            self._active_block = 0

        # Create new position data for the active block
        pos = np.zeros((blocksize, 3), 'float32')
        pos[:, :2] = np.random.normal(0.0, SIZE/2, (blocksize, 2))  # x-y
        pos[:, 2] = np.random.uniform(0, SIZE, (blocksize,))  # z
        start_index = self._active_block * blocksize
        self.program['a_position'].set_subdata(pos, offset=start_index)

        #print(start_index)

        # Set offsets - active block gets offset 0
        for i in range(NBLOCKS):
            val = i - self._active_block
            if val < 0:
                val += NBLOCKS
            values = np.ones((blocksize, 1), 'float32') * val * SIZE
            start_index = i*blocksize
            self.program['a_offset'].set_subdata(values, offset=start_index)

        # Reset timer
        self._timeout += SPEED


if __name__ == '__main__':
    c = Canvas()
    app.run()
