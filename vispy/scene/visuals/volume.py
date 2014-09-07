# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np

from ... import gloo
from ...geometry import create_cube
from ...gloo import set_state
from ..transforms import STTransform, NullTransform
from .modular_mesh import ModularMesh
from .cube import Cube
from ..components import (TextureComponent, VertexTextureCoordinateComponent,
                          TextureCoordinateComponent)


class Volume(ModularMesh):
    def __init__(self, **kwds):
        pos = np.asarray([[-1.0, -1.0], [-1.0, 1.0], [1.0, -1.0], [1.0, 1.0]])

        ModularMesh.__init__(self, pos=pos, color=(1.0, 0.0, 0.0, 1.0), **kwds)
        self._primitive = gloo.gl.GL_TRIANGLE_STRIP

        vertices, filled_indices, outline_indices = create_cube()
        self._cube = Cube(vertex_colors = vertices['color'], edge_color='black')

        w, h = 512, 512
        self.start_tex = gloo.Texture2D(shape=((w, h) + (4,)), dtype=np.float32)
        self.start_frame_buf = gloo.FrameBuffer(self.start_tex)

        tex_coord_comp = VertexTextureCoordinateComponent(NullTransform())
        self.color_components = [TextureComponent(self.start_tex, tex_coord_comp)]

    def draw(self, event):
        with self.start_frame_buf:
            gloo.clear('black')
            self._cube.draw(event)

        ModularMesh.draw(self, event)
