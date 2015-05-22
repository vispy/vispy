# -*- coding: utf-8 -*-
# vispy: gallery 200
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author:   Nicolas P .Rougier
# Date:     06/03/2014
# Abstract: GPU computing using the framebuffer
# Keywords: framebuffer, GPU computing, cellular automata
# -----------------------------------------------------------------------------
"""
Conway game of life.
"""

import numpy as np
from vispy.gloo import (Program, FrameBuffer, RenderBuffer,
                        clear, set_viewport, set_state)
from vispy import app


render_vertex = """
attribute vec2 position;
attribute vec2 texcoord;
varying vec2 v_texcoord;
void main()
{
    gl_Position = vec4(position, 0.0, 1.0);
    v_texcoord = texcoord;
}
"""

render_fragment = """
uniform int pingpong;
uniform sampler2D texture;
varying vec2 v_texcoord;
void main()
{
    float v;
    v = texture2D(texture, v_texcoord)[pingpong];
    gl_FragColor = vec4(1.0-v, 1.0-v, 1.0-v, 1.0);
}
"""

compute_vertex = """
attribute vec2 position;
attribute vec2 texcoord;
varying vec2 v_texcoord;
void main()
{
    gl_Position = vec4(position, 0.0, 1.0);
    v_texcoord = texcoord;
}
"""

compute_fragment = """
uniform int pingpong;
uniform sampler2D texture;
uniform float dx;          // horizontal distance between texels
uniform float dy;          // vertical distance between texels
varying vec2 v_texcoord;
void main(void)
{
    vec2  p = v_texcoord;
    float old_state, new_state, count;

    old_state = texture2D(texture, p)[pingpong];
    count = texture2D(texture, p + vec2(-dx,-dy))[pingpong]
            + texture2D(texture, p + vec2( dx,-dy))[pingpong]
            + texture2D(texture, p + vec2(-dx, dy))[pingpong]
            + texture2D(texture, p + vec2( dx, dy))[pingpong]
            + texture2D(texture, p + vec2(-dx, 0.0))[pingpong]
            + texture2D(texture, p + vec2( dx, 0.0))[pingpong]
            + texture2D(texture, p + vec2(0.0,-dy))[pingpong]
            + texture2D(texture, p + vec2(0.0, dy))[pingpong];

    new_state = old_state;
    if( old_state > 0.5 ) {
        // Any live cell with fewer than two live neighbours dies
        // as if caused by under-population.
        if( count  < 1.5 )
            new_state = 0.0;

        // Any live cell with two or three live neighbours
        // lives on to the next generation.

        // Any live cell with more than three live neighbours dies,
        //  as if by overcrowding.
        else if( count > 3.5 )
            new_state = 0.0;
    } else {
        // Any dead cell with exactly three live neighbours becomes
        //  a live cell, as if by reproduction.
       if( (count > 2.5) && (count < 3.5) )
           new_state = 1.0;
    }

    if( pingpong == 0) {
        gl_FragColor[1] = new_state;
        gl_FragColor[0] = old_state;
    } else {
        gl_FragColor[1] = old_state;
        gl_FragColor[0] = new_state;
    }
}
"""


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, title="Conway game of life",
                            size=(512, 512), keys='interactive')

        # Build programs
        # --------------
        self.comp_size = self.size
        size = self.comp_size + (4,)
        Z = np.zeros(size, dtype=np.float32)
        Z[...] = np.random.randint(0, 2, size)
        Z[:256, :256, :] = 0
        gun = """
        ........................O...........
        ......................O.O...........
        ............OO......OO............OO
        ...........O...O....OO............OO
        OO........O.....O...OO..............
        OO........O...O.OO....O.O...........
        ..........O.....O.......O...........
        ...........O...O....................
        ............OO......................"""
        x, y = 0, 0
        for i in range(len(gun)):
            if gun[i] == '\n':
                y += 1
                x = 0
            elif gun[i] == 'O':
                Z[y, x] = 1
            x += 1

        self.pingpong = 1
        self.compute = Program(compute_vertex, compute_fragment, 4)
        self.compute["texture"] = Z
        self.compute["position"] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
        self.compute["texcoord"] = [(0, 0), (0, 1), (1, 0), (1, 1)]
        self.compute['dx'] = 1.0 / size[1]
        self.compute['dy'] = 1.0 / size[0]
        self.compute['pingpong'] = self.pingpong

        self.render = Program(render_vertex, render_fragment, 4)
        self.render["position"] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
        self.render["texcoord"] = [(0, 0), (0, 1), (1, 0), (1, 1)]
        self.render["texture"] = self.compute["texture"]
        self.render['pingpong'] = self.pingpong

        self.fbo = FrameBuffer(self.compute["texture"],
                               RenderBuffer(self.comp_size))
        set_state(depth_test=False, clear_color='black')

        self._timer = app.Timer('auto', connect=self.update, start=True)

        self.show()

    def on_draw(self, event):
        with self.fbo:
            set_viewport(0, 0, *self.comp_size)
            self.compute["texture"].interpolation = 'nearest'
            self.compute.draw('triangle_strip')
        clear()
        set_viewport(0, 0, *self.physical_size)
        self.render["texture"].interpolation = 'linear'
        self.render.draw('triangle_strip')
        self.pingpong = 1 - self.pingpong
        self.compute["pingpong"] = self.pingpong
        self.render["pingpong"] = self.pingpong


if __name__ == '__main__':
    canvas = Canvas()
    app.run()
