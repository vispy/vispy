# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Tutorial: Creating Visuals
==========================

04. Fragment Programs
---------------------

In this tutorial, we will demonstrate the use of the fragment shader as a 
raycaster to draw complex shapes on a simple rectanglular mesh.

Previous tutorials focused on the use of forward transformation functions to 
map vertices from the local coordinate system of the visual to the "render 
coordinates" output of the vertex shader. In this tutorial, we will use inverse
transformation functions in the fragment shader to map backward from the 
current fragment location to the visual's local coordinate system. 
"""
import numpy as np
from vispy import app, gloo, visuals, scene


vertex_shader = """
void main() {
   gl_Position = vec4($position, 0, 1);
}
"""

fragment_shader = """
void main() {
  vec4 pos = $fb_to_visual(gl_FragCoord);
  gl_FragColor = vec4(sin(pos.x / 10.), sin(pos.y / 10.), 0, 1);
}
"""


class MyRectVisual(visuals.Visual):
    """
    """
    
    def __init__(self):
        visuals.Visual.__init__(self, vertex_shader, fragment_shader)
        self.vbo = gloo.VertexBuffer(np.array([
            [-1, -1], [1, -1], [1, 1],
            [-1, -1], [1, 1], [-1, 1]
        ], dtype=np.float32))
        self.shared_program.vert['position'] = self.vbo
        self.set_gl_state(cull_face=False)
        self._draw_mode = 'triangle_fan'

    def _prepare_transforms(self, view):
        view.view_program.frag['fb_to_visual'] = \
            view.transforms.get_transform('framebuffer', 'visual')

# As in the previous tutorial, we auto-generate a Visual+Node class for use
# in the scenegraph.
MyRect = scene.visuals.create_visual_node(MyRectVisual)


# Finally we will test the visual by displaying in a scene.

canvas = scene.SceneCanvas(keys='interactive', show=True)

# This time we add a ViewBox to let the user zoom/pan
view = canvas.central_widget.add_view()
view.camera = 'panzoom'
view.camera.rect = (0, 0, 800, 800)

vis = MyRect()
view.add(vis)

# ..and optionally start the event loop
if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        app.run()
