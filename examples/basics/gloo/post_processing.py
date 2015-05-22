# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author:   Nicolas P .Rougier
# Date:     04/03/2014
# Abstract: Show post-processing technique using framebuffer
# Keywords: framebuffer, gloo, cube, post-processing
# -----------------------------------------------------------------------------

import numpy as np
from vispy import app

from vispy.geometry import create_cube
from vispy.util.transforms import perspective, translate, rotate
from vispy.gloo import (Program, VertexBuffer, IndexBuffer, Texture2D, clear,
                        FrameBuffer, RenderBuffer, set_viewport, set_state)


cube_vertex = """
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
attribute vec3 position;
attribute vec2 texcoord;
attribute vec3 normal;  // not used in this example
attribute vec4 color;  // not used in this example
varying vec2 v_texcoord;
void main()
{
    gl_Position = projection * view * model * vec4(position,1.0);
    v_texcoord = texcoord;
}
"""

cube_fragment = """
uniform sampler2D texture;
varying vec2 v_texcoord;
void main()
{
    float r = texture2D(texture, v_texcoord).r;
    gl_FragColor = vec4(r,r,r,1);
}
"""

quad_vertex = """
attribute vec2 position;
attribute vec2 texcoord;
varying vec2 v_texcoord;
void main()
{
    gl_Position = vec4(position, 0.0, 1.0);
    v_texcoord = texcoord;
}
"""

quad_fragment = """
uniform sampler2D texture;
varying vec2 v_texcoord;
void main()
{
    vec2 d = 5.0 * vec2(sin(v_texcoord.y*50.0),0)/512.0;

    // Inverse video
    if( v_texcoord.x > 0.5 ) {
        gl_FragColor.rgb = 1.0-texture2D(texture, v_texcoord+d).rgb;
    } else {
        gl_FragColor = texture2D(texture, v_texcoord);
    }
}
"""


def checkerboard(grid_num=8, grid_size=32):
    row_even = grid_num // 2 * [0, 1]
    row_odd = grid_num // 2 * [1, 0]
    Z = np.row_stack(grid_num // 2 * (row_even, row_odd)).astype(np.uint8)
    return 255 * Z.repeat(grid_size, axis=0).repeat(grid_size, axis=1)


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, title='Framebuffer post-processing',
                            keys='interactive', size=(512, 512))

        # Build cube data
        # --------------------------------------
        vertices, indices, _ = create_cube()
        vertices = VertexBuffer(vertices)
        self.indices = IndexBuffer(indices)

        # Build program
        # --------------------------------------
        view = translate((0, 0, -7))
        self.phi, self.theta = 60, 20
        model = rotate(self.theta, (0, 0, 1)).dot(rotate(self.phi, (0, 1, 0)))

        self.cube = Program(cube_vertex, cube_fragment)
        self.cube.bind(vertices)
        self.cube["texture"] = checkerboard()
        self.cube["texture"].interpolation = 'linear'
        self.cube['model'] = model
        self.cube['view'] = view

        color = Texture2D((512, 512, 3), interpolation='linear')
        self.framebuffer = FrameBuffer(color, RenderBuffer((512, 512)))

        self.quad = Program(quad_vertex, quad_fragment, count=4)
        self.quad['texcoord'] = [(0, 0), (0, 1), (1, 0), (1, 1)]
        self.quad['position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
        self.quad['texture'] = color

        # OpenGL and Timer initalization
        # --------------------------------------
        set_state(clear_color=(.3, .3, .35, 1), depth_test=True)
        self.timer = app.Timer('auto', connect=self.on_timer, start=True)
        self._set_projection(self.physical_size)

        self.show()

    def on_draw(self, event):
        with self.framebuffer:
            set_viewport(0, 0, 512, 512)
            clear(color=True, depth=True)
            set_state(depth_test=True)
            self.cube.draw('triangles', self.indices)
        set_viewport(0, 0, *self.physical_size)
        clear(color=True)
        set_state(depth_test=False)
        self.quad.draw('triangle_strip')

    def on_resize(self, event):
        self._set_projection(event.physical_size)

    def _set_projection(self, size):
        width, height = size
        set_viewport(0, 0, width, height)
        projection = perspective(30.0, width / float(height), 2.0, 10.0)
        self.cube['projection'] = projection

    def on_timer(self, event):
        self.theta += .5
        self.phi += .5
        model = rotate(self.theta, (0, 0, 1)).dot(rotate(self.phi, (0, 1, 0)))
        self.cube['model'] = model
        self.update()

if __name__ == '__main__':
    c = Canvas()
    c.app.run()
