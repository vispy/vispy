import argparse

from vispy import app, scene
from vispy.io import read_mesh, load_data_file
from vispy.scene.visuals import Mesh
from vispy.visuals.filters import WireframeFilter


parser = argparse.ArgumentParser()
default_mesh = load_data_file('orig/triceratops.obj.gz')
parser.add_argument('--mesh', default=default_mesh)
parser.add_argument('--shininess', default=None)
parser.add_argument('--width', default=1)
args = parser.parse_args()

vertices, faces, normals, texcoords = read_mesh(args.mesh)

canvas = scene.SceneCanvas(keys='interactive', bgcolor='white')
view = canvas.central_widget.add_view()

view.camera = 'arcball'
view.camera.depth_value = 1e3

mesh = Mesh(vertices, faces, shading="smooth", color=(.5, .7, .5, 1))
if args.shininess is not None:
    mesh.shading_filter.shininess = args.shininess
mesh.set_gl_state('translucent', depth_test=True, cull_face=True)
view.add(mesh)

w = WireframeFilter(width=args.width)
mesh.attach(w)


def attach_headlight(mesh, view, canvas):
    light_dir = (0, -1, 0, 0)
    mesh.shading_filter.light_dir = light_dir[:3]
    initial_light_dir = view.camera.transform.imap(light_dir)

    @view.scene.transform.changed.connect
    def on_transform_change(event):
        transform = view.camera.transform
        mesh.shading_filter.light_dir = transform.map(initial_light_dir)[:3]


attach_headlight(mesh, view, canvas)


shadings = [None, 'flat', 'smooth']
shading_index = shadings.index(mesh.shading_filter.shading)


@canvas.events.key_press.connect
def on_key_press(event):
    global shading_index
    if event.key == 's':
        shading_index = (shading_index + 1) % len(shadings)
        shading = shadings[shading_index]
        mesh.shading_filter.shading = shading
        # mesh.shading_filter.enabled = shading is not None
        mesh.update()
    elif event.key == 'w':
        if w._attached:
            mesh.detach(w)
        else:
            mesh.attach(w)


canvas.show()


if __name__ == "__main__":
    app.run()
