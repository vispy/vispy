# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Tutorial: Creating Visuals
==========================

05. Camera location
-------------------

In this tutorial we will demonstrate how to determine the direction from which
a Visual is being viewed.
"""

from vispy import app, gloo, visuals, scene, io


vertex_shader = """
varying vec4 color;
void main() {
    vec4 visual_pos = vec4($position, 1);
    vec4 doc_pos = $visual_to_doc(visual_pos);
    gl_Position = $doc_to_render(doc_pos);
    
    vec4 visual_pos2 = $doc_to_visual(doc_pos + vec4(0, 0, -1, 0));
    vec4 view_direction = (visual_pos2 / visual_pos2.w) - visual_pos;
    view_direction = vec4(normalize(view_direction.xyz), 0);
    
    color = vec4(view_direction.rgb, 1);
}
"""

fragment_shader = """
varying vec4 color;
void main() {
    gl_FragColor = color;
}
"""


class MyMeshVisual(visuals.Visual):
    """
    """

    def __init__(self):
        visuals.Visual.__init__(self, vertex_shader, fragment_shader)

        # Create an interesting mesh shape for demonstration.
        fname = io.load_data_file('orig/triceratops.obj.gz')
        vertices, faces, normals, tex = io.read_mesh(fname)

        self._ibo = gloo.IndexBuffer(faces)

        self.shared_program.vert['position'] = gloo.VertexBuffer(vertices)
        # self.program.vert['normal'] = gloo.VertexBuffer(normals)
        self.set_gl_state('additive', cull_face=False)
        self._draw_mode = 'triangles'
        self._index_buffer = self._ibo

    def _prepare_transforms(self, view):
        # Note we use the "additive" GL blending settings so that we do not
        # have to sort the mesh triangles back-to-front before each draw.
        tr = view.transforms
        view_vert = view.view_program.vert
        view_vert['visual_to_doc'] = tr.get_transform('visual', 'document')
        view_vert['doc_to_visual'] = tr.get_transform('document', 'visual')
        view_vert['doc_to_render'] = tr.get_transform('document', 'render')


# Auto-generate a Visual+Node class for use in the scenegraph.
MyMesh = scene.visuals.create_visual_node(MyMeshVisual)


# Finally we will test the visual by displaying in a scene.

canvas = scene.SceneCanvas(keys='interactive', show=True)

# Add a ViewBox to let the user zoom/rotate
view = canvas.central_widget.add_view()
view.camera = 'turntable'
view.camera.fov = 50
view.camera.distance = 2

mesh = MyMesh(parent=view.scene)
mesh.transform = visuals.transforms.MatrixTransform()
# mesh.transform.translate([-25, -25, -25])
mesh.transform.rotate(90, (1, 0, 0))

axis = scene.visuals.XYZAxis(parent=view.scene)

# ..and optionally start the event loop
if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        app.run()
