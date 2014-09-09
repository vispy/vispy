# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np

from ... import gloo
from ...geometry import create_cube
from ...gloo import set_state, Program, gl
from ..transforms import STTransform, NullTransform
from .modular_mesh import ModularMesh
from .cube import Cube
from ..components import (TextureComponent, VertexTextureCoordinateComponent,
                          TextureCoordinateComponent)
from .visual import Visual
from ..shaders import ModularProgram

W, H = 1.0, 1.0
rays_vert = np.array([[-W, -H], [W, -H], [-W, H], [W, H]], dtype=np.float32)

class Volume(Visual):
    VERTEX_SHADER = """
        attribute vec2 a_position;
        varying vec2 v_texcoord;

        void main(void) {
            gl_Position = vec4(a_position,0.0,1.0);
            v_texcoord = (gl_Position.xy + 1.0) / 2.0;
        }

        """

    FRAGMENT_SHADER = """
        varying vec2 v_texcoord;
        uniform sampler2D u_start;

        void main(void) {
            vec4 start = texture2D(u_start, v_texcoord);

            gl_FragColor = start;
        }
        """

    def __init__(self, **kwds):
        Visual.__init__(self)

        pos = np.asarray([[-1.0, -1.0], [-1.0, 1.0], [1.0, -1.0], [1.0, 1.0]])

        vertices, filled_indices, outline_indices = create_cube()
        self.cube = Cube(vertex_colors = vertices['color'], edge_color='black')

        w, h = 400, 400
        self.start_tex = gloo.Texture2D(shape=((w, h) + (4,)), dtype=np.float32)
        self.start_frame_buf = gloo.FrameBuffer(self.start_tex)

        self._program = Program(self.VERTEX_SHADER, self.FRAGMENT_SHADER)
        self._program['a_position'] = gloo.VertexBuffer(rays_vert)
        self._program['u_start'] = self.start_tex

    def draw(self, event):
        draw_to_screen = False
        if draw_to_screen:
            gloo.clear('white', depth=True)
            self.cube.draw(event)
            return 

        event.push_fbo(self.start_frame_buf, (0, 0), (400, 400))
        event.push_entity(self.cube)

        try:
            gloo.clear('white', depth=True)
            self.cube.draw(event)
        finally:
            event.pop_entity()
            event.pop_fbo()

        gloo.set_state(cull_face=False)
        self._program.draw('triangle_strip')
