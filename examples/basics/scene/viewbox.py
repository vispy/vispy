"""
Demonstrate ViewBox using various clipping methods.

Two boxes are manually positioned on the canvas; they are not updated
when the canvas resizes.

"""
import numpy as np

from vispy import app
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
line_ndc = scene.visuals.Line(pos=pos.copy(), color=color, name='line_ndc')

#pos[:, 0] = np.linspace(50, 350., N)
#pos[:, 1] = 150 + pos[:, 1] * 50
#pos[:20, 1] = 100  # So we can see which side is down
#line_pixels = scene.visuals.Line(pos=pos.copy(), color=color)

# Create canvas
canvas = scene.SceneCanvas(size=(800, 600), show=True, close_keys='escape')

vb1 = scene.widgets.ViewBox(name='vb1', parent=canvas.scene, border=(1, 1, 0, 1))
vb1.clip_method = 'fbo'
vb1.pos = 20, 20
vb1.size = canvas.size[0]/2. - 40, canvas.size[1] - 40
vb1.camera.rect = (-1.2, -2, 2.4, 4)

line_ndc.add_parent(vb1.scene)

vb2 = scene.widgets.ViewBox(name='vb2', parent=canvas.scene, border=(0, 0, 1, 1))
vb2.clip_method = 'viewport'
vb2.pos = canvas.size[0]/2. + 20, 20
vb2.size = canvas.size[0]/2. - 40, canvas.size[1] - 40
vb2.set_camera('turntable', mode='ortho', elevation=30, azimuth=30)
#vb2.set_camera('turntable', mode='perspective', 
#               distance=10, elevation=0, azimuth=0)

line_ndc.add_parent(vb2.scene)

box = np.array([[0, 0, 0], 
                [0, 1, 0], 
                [1, 1, 0], 
                [1, 0, 0], 
                [0, 0, 0]], dtype=np.float32)
z = np.array([[0, 0, 1]], dtype=np.float32)
unit_box1 = scene.visuals.Line(pos=box, 
                               color=(0.7, 0, 0, 1), 
                               name='unit box')
nd_box1 = scene.visuals.Line(pos=(box * 2 - 1), 
                             color=(0, 0.7, 0, 1), 
                             name='nd box')
vb1.add(unit_box1)
vb1.add(nd_box1)

unit_box2 = scene.visuals.Line(pos=box + z, 
                               color=(1, 0, 0, 1), 
                               name='unit box')
nd_box2 = scene.visuals.Line(pos=((box + z) * 2 - 1), 
                             color=(0, 1, 0, 1), 
                             name='nd box')
vb2.add(unit_box1)
vb2.add(nd_box1)
vb2.add(unit_box2)
vb2.add(nd_box2)

if __name__ == '__main__':
    app.run()
