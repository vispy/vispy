import argparse

from vispy import app, scene
from vispy.io import read_mesh, load_data_file
from vispy.scene.visuals import Mesh
from vispy.visuals.filters import ShadingFilter, WireframeFilter


parser = argparse.ArgumentParser()
default_mesh = load_data_file('orig/triceratops.obj.gz')
parser.add_argument('--mesh', default=default_mesh)
parser.add_argument('--shininess', default=100)
parser.add_argument('--wireframe-width', default=1)
args = parser.parse_args()

vertices, faces, normals, texcoords = read_mesh(args.mesh)

canvas = scene.SceneCanvas(keys='interactive', bgcolor='white')
view = canvas.central_widget.add_view()

view.camera = 'arcball'
view.camera.depth_value = 1e3

mesh = Mesh(vertices, faces, color=(.5, .7, .5, 1))
view.add(mesh)

shading_filter = ShadingFilter(shininess=args.shininess)
mesh.attach(shading_filter)
wireframe_filter = WireframeFilter(width=args.wireframe_width)
mesh.attach(wireframe_filter)


def attach_headlight(view):
    light_dir = (0, -1, 0, 0)
    shading_filter.light_dir = light_dir[:3]
    initial_light_dir = view.camera.transform.imap(light_dir)

    @view.scene.transform.changed.connect
    def on_transform_change(event):
        transform = view.camera.transform
        shading_filter.light_dir = transform.map(initial_light_dir)[:3]


attach_headlight(view)
shadings = [None, 'flat', 'smooth']
shading_index = shadings.index(shading_filter.shading)


@canvas.events.key_press.connect
def on_key_press(event):
    global shading_index
    if event.key == 's':
        shading_index = (shading_index + 1) % len(shadings)
        shading = shadings[shading_index]
        shading_filter.shading = shading
        mesh.update()
    elif event.key == 'w':
        wireframe_filter.enabled = not wireframe_filter.enabled
        mesh.update()


canvas.show()

if __name__ == "__main__":
    app.run()
