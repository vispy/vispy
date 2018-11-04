import argparse

import numpy as np
from vispy import app, scene
from vispy.io import imread, read_mesh
from vispy.scene.visuals import Mesh
from vispy.visuals.filters import TextureFilter


parser = argparse.ArgumentParser()
parser.add_argument('mesh')
parser.add_argument('--shading', default='smooth',
                    choices=['none', 'flat', 'smooth'])
args = parser.parse_args()

vertices, faces, normals, texcoords = read_mesh(args.mesh)
texture = np.flipud(imread(args.mesh.replace(".obj", ".png")))

canvas = scene.SceneCanvas(keys='interactive', bgcolor='white',
                           size=(800, 600))
view = canvas.central_widget.add_view()

view.camera = 'arcball'
# Adapt the depth to the scale of the mesh to avoid rendering artefacts.
view.camera.depth_value = 10 * (vertices.max() - vertices.min())

shading = None if args.shading == 'none' else args.shading
mesh = Mesh(vertices, faces, shading=shading, color='lightgreen')
mesh.shininess = 1e-3
view.add(mesh)

texture_filter = TextureFilter(texture, texcoords)
mesh.attach(texture_filter)


def attach_headlight(mesh, view, canvas):
    mesh.light_dir = (0, -1, 0)
    initial_light_dir = view.camera.transform.imap(mesh.light_dir)
    initial_light_dir[3] = 0

    @canvas.events.mouse_move.connect
    def on_mouse_move(event):
        transform = view.camera.transform
        mesh.light_dir = transform.map(initial_light_dir)[:3]


attach_headlight(mesh, view, canvas)


canvas.show()

if __name__ == "__main__":
    app.run()
