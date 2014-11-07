"""
Example volume rendering
"""

import numpy as np

from vispy import scene, io

# Read volume
vol = np.load(io.load_data_file('brain/mri.npz'))['data']
vol = np.flipud(np.rollaxis(vol, 1))
#import imageio
#vol = imageio.volread('stent.npz')

# Prepare canvas
canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 800, 600
canvas.show()
canvas.measure_fps()

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Create the volume visual
volume = scene.visuals.Volume(vol, parent=view.scene, threshold=0.5)
#volume._program._context.glir.set_verbose('SHADERS')

# Create two cameras (1 for firstperson, 3 for 3d person)
cam1 = scene.cameras.FlyCamera(parent=view.scene)
cam3 = scene.cameras.TurntableCamera(parent=view.scene)
for cam in (cam1, cam3):
    cam.set_range((0, 250), (0, 250), (0, 250))
view.camera = cam3  # Select turntable at first


# Implement key presses
@canvas.events.key_press.connect
def select_camera(event):
    if event.text == '1':
        view.set_camera('fly')
    elif event.text == '3':
        view.set_camera('turntable')
    elif event.text == 'm':
        volume.style = 'mip'
    elif event.text == 'i':
        volume.style = 'iso'
    elif event.text == '[':
        volume.threshold -= 0.1
    elif event.text == ']':
        volume.threshold += 0.1
