# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 2

"""
Volume Rendering
================

Example volume rendering

"""

import dask.array as da
from dask_image.imread import imread
import numpy as np
from vispy import app, scene, io
from vispy.color import BaseColormap
from skimage.transform import pyramid_reduce
# from vispy.visuals.transforms import STTransform

# Read volume
mri_data = np.load(io.load_data_file('brain/mri.npz'))['data']
mri_data = np.flipud(np.rollaxis(mri_data, 1)).astype(np.float32)
# TODO: generate more illustrative data

# mri_data = imread('/Users/aandersoniii/Data/21316414z-8_scale-4.0_cdim-3_net-4_wmean--2_wstd-0.85_0.tif').compute()
# mri_data = mri_data.reshape((1024, 1024, 1024, 3))[..., 0].astype(np.float32)
mri_data = (mri_data - mri_data.min()) / mri_data.ptp()
# mri_data_small = pyramid_reduce(mri_data, 4)
# mri_data = mri_data_small

print(mri_data.shape, mri_data.min(), mri_data.max())
# print(mri_data.shape, mri_data.dtype)


# Prepare canvas
canvas = scene.SceneCanvas(keys='interactive', size=(768, 1024), show=True)
canvas.measure_fps()
grid = canvas.central_widget.add_grid()

# Set up a viewbox to display the image with interactive pan/zoom
view0 = grid.add_view(row=0, col=0, row_span=2)
view1 = grid.add_view(row=2, col=0, camera="panzoom")
# view0 = canvas.central_widget.add_view()


# create colormaps that work well for translucent and additive volume rendering

n = 2
p = 0.2

class TransFire(BaseColormap):
    glsl_map = f"""
    vec4 translucent_fire(float t) {{
        return vec4(pow(t, 0.5), t, t*t, pow(t, {n}));
    }}
    """

class TransFire2D(BaseColormap):
    glsl_map = f"""
    vec4 translucent_fire(float t, float g) {{
        return vec4(pow(t, {p}), 1 / (1 + t), g*g*g, pow(g, {n}));
    }}
    """


# Create the volume visuals, only one is visible
vol = scene.visuals.Volume(mri_data, parent=view0.scene, method="translucent", cmap=TransFire(), relative_step_size=1.0)
vol.unfreeze()
vol.transfer_function = TransFire2D()
cam = scene.cameras.TurntableCamera(parent=view0.scene, fov=60, name='Turntable')
view0.camera = cam
view0.camera.scale_factor = 320.0

# pre-integrate the volume for direct volume rendering

gm = np.linalg.norm(np.gradient(mri_data), axis=0)
# gm = da.linalg.norm(da.stack(da.gradient(mri_data), axis=-1), axis=-1)
# gm = da.rechunk(gm, chunks=(256, 256, 256))
# print(gm)
hist_data = np.histogram2d(
    np.log(np.clip(gm.ravel(), 1e-2, None)),
    mri_data.ravel(),
    # da.from_array(mri_data, chunks=(256, 256, 256)).ravel(),
    bins=(32, 128),
    # range=((0, 1), (0, 1)),
)[0]
# hist_data = da.log(da.clip(hist_data, 1, None)).compute()
print(hist_data.shape)
t, gm = np.meshgrid(np.linspace(0, 1, 128), np.linspace(0, 1, 32))
r = t ** p
g = 1 / (1 + t)
b = gm**3
a = gm**n
hist_overlay = np.stack((r, g, b, a), axis=-1)
hist = scene.visuals.Image(np.log(hist_data + 1), parent=view1.scene, cmap="gray")
cmap = scene.visuals.Image(hist_overlay, parent=view1.scene)
cmap.set_gl_state('translucent', depth_test=False)
view1.camera.rect = (0, 0, 128, 32)
view1.camera.interactive = False


@canvas.connect
def on_mouse_press(event):
    print(event.button)
    print(event.pos)
    print(view0.size, view1.size)


@canvas.events.key_press.connect
def on_key_press(event):
    global n
    if event.text in ('-', "="):
        if event.text == '-':
            n -= .1
        else:
            n += .1
        n = max(0, n)
        print(n)
        r = t ** p
        g = 1 / (1 + t)
        b = gm**3
        a = gm**n
        hist_overlay = np.stack((r, g, b, a), axis=-1)
        cmap.set_data(hist_overlay)
        cmap.set_gl_state('translucent', depth_test=False)
        cmap.update()

        class TransFire2D(BaseColormap):
            glsl_map = f"""
            vec4 translucent_fire(float t, float g) {{
                return vec4(pow(t, {p}), 1 / (1 + t), g*g*g, pow(g, {n}));
            }}
            """
        vol.transfer_function = TransFire2D()

        class TransFire(BaseColormap):
            glsl_map = f"""
            vec4 translucent_fire(float t) {{
                return vec4(pow(t, 0.5), t, t*t, pow(t, {n}));
            }}
            """
        vol.cmap = TransFire()
        vol.update()

    elif event.text == '2':
        methods = ['translucent', 'translucent_2d']
        method = methods[(methods.index(vol.method) + 1) % len(methods)]
        vol.method = method
        print("Volume render method: %s" % method)

    elif event.text == "[":
        vol.relative_step_size = max(vol.relative_step_size - 0.1, 0.5)
        vol.update()
        print(vol.relative_step_size)

    elif event.text == "]":
        vol.relative_step_size = max(vol.relative_step_size + 0.1, 0.5)
        vol.update()
        print(vol.relative_step_size)


if __name__ == '__main__':
    print(__doc__)
    app.run()
