
import numpy as np

from vispy import app, gloo
from vispy import scene


# Create lines for use in ndc and pixel coordinates
N = 1000
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]
pos = np.empty((N, 2), np.float32)

pos[:, 0] = np.linspace(-1., 1., N)
pos[:, 1] = np.random.normal(0.0, 0.5, size=N)
pos[:20, 1] = -0.5  # So we can see which side is down
line_ndc = scene.visuals.Line(pos=pos.copy(), color=color)

pos[:, 0] = np.linspace(50, 350., N)
pos[:, 1] = 150 + pos[:, 1] * 50
pos[:20, 1] = 100  # So we can see which side is down
line_pixels = scene.visuals.Line(pos=pos.copy(), color=color)

# Create canvas
canvas = scene.SceneCanvas(size=(800, 600), show=True, close_keys='escape')
# null camera; we will operate in the coordinate system provided by
# the canvas.
#canvas.scene.camera = scene.cameras.Camera()  

vb1 = scene.ViewBox(canvas.scene, border=(1, 1, 0, 1))
vb1.preferred_clip_method = 'fbo'
vb1.pos = 20, 20
vb1.size = canvas.size[0]/2. - 40, canvas.size[1] - 40
vb1.scene.camera = scene.cameras.TwoDCamera()

line_ndc.add_parent(vb1.scene)

vb2 = scene.ViewBox(canvas.scene, border=(0, 0, 1, 1))
vb2.preferred_clip_method = 'viewport'
vb2.pos = canvas.size[0]/2. + 20, 20
vb2.size = canvas.size[0]/2. - 40, canvas.size[1] - 40
vb2.scene.camera = scene.cameras.TwoDCamera()

line_ndc.add_parent(vb2.scene)

box = np.array([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]], dtype=np.float32)
unit_box = scene.visuals.Line(pos=box, color=(1, 0, 0, 1), name='unit box')
nd_box = scene.visuals.Line(pos=box*2-1, color=(0, 1, 0, 1), name='nd box')
vb1.add(unit_box)
vb1.add(nd_box)
vb2.add(unit_box)
vb2.add(nd_box)



if __name__ == '__main__':
    app.run()
