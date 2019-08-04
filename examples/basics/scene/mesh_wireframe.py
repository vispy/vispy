import argparse

from vispy import app, scene
from vispy.io import read_mesh, load_data_file
from vispy.scene.visuals import Mesh
from vispy.visuals.filters import WireframeFilter


parser = argparse.ArgumentParser()
default_mesh = load_data_file('orig/triceratops.obj.gz')
parser.add_argument('--mesh', default=default_mesh)
args = parser.parse_args()

vertices, faces, normals, texcoords = read_mesh(args.mesh)

canvas = scene.SceneCanvas(keys='interactive', bgcolor='white')
view = canvas.central_widget.add_view()

view.camera = 'arcball'
view.camera.depth_value = 1e3

mesh = Mesh(vertices, faces, color=(.5, .7, .5, 1))
mesh.set_gl_state('translucent', depth_test=True, cull_face=True)
view.add(mesh)

wireframe_filter = WireframeFilter()
mesh.attach(wireframe_filter)


canvas.show()


if __name__ == "__main__":
    app.run()
