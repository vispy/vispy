"""
Demonstrate ViewBox using various clipping methods.

Two boxes are manually positioned on the canvas; they are not updated
when the canvas resizes.

"""
import numpy as np

from vispy import app
from vispy import scene


# Create canvas
canvas = scene.SceneCanvas(size=(800, 600), show=True, keys='interactive')


# Create two ViewBoxes, place side-by-side
# First ViewBox uses a 2D pan/zoom camera
vb1 = scene.widgets.ViewBox(name='vb1', border_color='yellow')
vb1.parent = canvas.scene
vb1.clip_method = 'fbo'
vb1.camera.rect = (-1.2, -2, 2.4, 4)

# Second ViewBox uses a 3D orthographic camera
vb2 = scene.widgets.ViewBox(name='vb2', border_color='blue')
vb2.parent = canvas.scene
vb2.clip_method = 'viewport'
vb2.set_camera('turntable', mode='ortho', elevation=30, azimuth=30)
#vb2.set_camera('turntable', mode='perspective', 
#               distance=10, elevation=0, azimuth=0)

# Move these when the canvas changes size
@canvas.events.resize.connect
def resize(event=None):
    vb1.pos = 20, 20
    vb1.size = canvas.size[0]/2. - 40, canvas.size[1] - 40
    vb2.pos = canvas.size[0]/2. + 20, 20
    vb2.size = canvas.size[0]/2. - 40, canvas.size[1] - 40

resize()


#
# Now add visuals to the viewboxes.
#

# First a plot line:
N = 1000
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]

pos = np.empty((N, 2), np.float32)
pos[:, 0] = np.linspace(-1., 1., N)
pos[:, 1] = np.random.normal(0.0, 0.5, size=N)
pos[:20, 1] = -0.5  # So we can see which side is down

line1 = scene.visuals.Line(pos=pos.copy(), color=color, 
                           name='line1', parent=vb1.scene)
line2 = scene.visuals.Line(pos=pos.copy(), color=color, 
                           name='line2', parent=vb2.scene)


# And some squares:
box = np.array([[0, 0, 0], 
                [0, 1, 0], 
                [1, 1, 0], 
                [1, 0, 0], 
                [0, 0, 0]], dtype=np.float32)
z = np.array([[0, 0, 1]], dtype=np.float32)
box1 = scene.visuals.Line(pos=box, color=(0.7, 0, 0, 1), 
                          name='unit box', parent=vb1.scene)
box2 = scene.visuals.Line(pos=box, color=(0.7, 0, 0, 1), 
                          name='unit box', parent=vb2.scene)

box3 = scene.visuals.Line(pos=(box * 2 - 1),  color=(0, 0.7, 0, 1), 
                          name='nd box', parent=vb1.scene)
box4 = scene.visuals.Line(pos=(box * 2 - 1), color=(0, 0.7, 0, 1), 
                          name='nd box', parent=vb2.scene)

box5 = scene.visuals.Line(pos=box + z, color=(1, 0, 0, 1), 
                          name='unit box', parent=vb2.scene)
box6 = scene.visuals.Line(pos=((box + z) * 2 - 1), color=(0, 1, 0, 1), 
                          name='nd box', parent=vb2.scene)


if __name__ == '__main__':
    print(canvas.scene.describe_tree(with_transform=True))
    app.run()
