import argparse

from vispy import app, scene
from vispy.io import read_mesh
from vispy.scene.visuals import Mesh
from vispy.visuals.filters import ShadingFilter


parser = argparse.ArgumentParser()
parser.add_argument('mesh')
args = parser.parse_args()

vertices, faces, normals, texcoords = read_mesh(args.mesh)

canvas = scene.SceneCanvas(keys='interactive', bgcolor='white',
                           size=(800, 600))
view = canvas.central_widget.add_view()

view.camera = 'arcball'

mesh = Mesh(vertices, faces)
mesh.set_gl_state('translucent', depth_test=True, cull_face=True)
view.add(mesh)

shading_filter = ShadingFilter()
shading_filter.shininess = 1e-3
mesh.attach(shading_filter)

shading_filter.light_dir = (0, -1, 0)
initial_light_dir = view.camera.transform.imap(shading_filter.light_dir)[:3]
mesh.update()


# Make the mesh light follow the direction of the camera.
@canvas.events.mouse_move.connect
def on_mouse_move(event):
    transform = view.camera.transform
    shading_filter.light_dir = transform.map(initial_light_dir)[:3]
    mesh.update()


shading_index = 0
shadings = [None, 'flat', 'smooth']


@canvas.events.key_press.connect
def on_key_press(event):
    global shading_index
    if event.key == 's':
        shading_index = (shading_index + 1) % len(shadings)
        shading = shadings[shading_index]
        shading_filter.shading = shading
        shading_filter.enabled = shading is not None
        mesh.update()


canvas.show()

if __name__ == "__main__":
    app.run()
