# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Picking Instance of InstancedMeshes
===================================

Demonstrates how to identify (pick) individual instanced meshes.

"""

import numpy as np

from vispy import app, scene, use
from vispy.io import read_mesh, load_data_file
from vispy.scene.visuals import InstancedMesh
from vispy.scene import transforms
from scipy.spatial.transform import Rotation

#Necessary to use InstancedMesh
use(gl='gl+')

canvas = scene.SceneCanvas(keys='interactive', bgcolor='white')
view = canvas.central_widget.add_view()

view.camera = 'turntable'
view.camera.depth_value = 1e3

#Load an mesh file
mesh_path = load_data_file('spot/spot.obj.gz')

n_instances = 8
vertices, faces, normals, texcoords = read_mesh(mesh_path)
instance_colors = np.random.rand(n_instances, 3).astype(np.float32)
instance_positions = [[0,2,0], [2,0,0], [6,0,0], [3,4,1], [5,3,2], [6,2,1], [8,4,6], [1,2,6]]
instance_transforms = Rotation.identity(n_instances).as_matrix().astype(np.float32)

# Create a colored `MeshVisual`.
mesh = InstancedMesh(
    vertices,
    faces,
    instance_colors=instance_colors,
    instance_positions=instance_positions,
    instance_transforms=instance_transforms,
    parent=view.scene,
)

scene.visuals.XYZAxis(parent=view.scene)
mesh.interactive = True

@canvas.events.mouse_press.connect
def on_mouse_press(event):
    clicked_mesh = canvas.visual_at(event.pos)
    if isinstance(clicked_mesh, InstancedMesh):
        pos1, min, min_pos = get_view_axis_in_scene_coordinates(
            event.pos, clicked_mesh
        )
        instance_pos = clicked_mesh.instance_positions[min_pos]
        print(f"visual at : {clicked_mesh}")
        print(f"event.pos : {event.pos}")
        print(f"min distance : {min} and min_pos : {instance_pos}")
       


def get_view_axis_in_scene_coordinates(pos, mesh):
    event_pos = np.array([pos[0], pos[1], 0, 1])  
    instances_on_canvas = []
    # Translate each position to corresponding 2d canvas coordinates
    for instance in mesh.instance_positions:
        on_canvas = mesh.get_transform(map_from="visual", map_to="canvas").map(instance)
        on_canvas /= on_canvas[3:]
        instances_on_canvas.append(on_canvas)

    min = 10000
    min_pos = None
    # Find the closest position to the clicked position
    for i, instance_pos in enumerate(instances_on_canvas):
        # Not minding z axis
        temp_min = np.linalg.norm(
            np.array(event_pos[:2]) - np.array(instance_pos[:2])
        )
        if temp_min < min:
            min = temp_min
            min_pos = i

    return instances_on_canvas, min, min_pos

canvas.show()


if __name__ == "__main__":
    print(__doc__)
    app.run()
