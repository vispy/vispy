# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 2

"""
Volume Rendering with 2D Transfer Function
==========================================

This example demonstrates how to use higher order transfer functions to control volume rendering.
The transfer function is a 2D texture that is sampled based on the data value and the gradient
magnitude. The transfer function is shown over the 2D histogram of the data below the image. You can
paint on the transfer function to change it.

Controls:

* 1  - Reset to default 1D transfer function
* 2  - Reset to default 2D transfer function
* [ / ] - Decrease/increase relative step size

# Left click and drag to paint the transfer function
# Alt + Left click and drag to erase on the transfer function

"""
import numpy as np
from vispy import app, scene, io
from vispy.color import TextureSamplingTF

# Read and normalize volume data
mri_data = np.load(io.load_data_file('brain/mri.npz'))['data']
mri_data = np.flipud(np.rollaxis(mri_data, 1)).astype(np.float32)
mri_data = (mri_data - mri_data.min()) / np.ptp(mri_data)

# Prepare canvas
canvas = scene.SceneCanvas(keys='interactive', size=(768, 1024), show=True)
canvas.measure_fps()
grid = canvas.central_widget.add_grid()

# Set up a viewbox to display the image
data_view = grid.add_view(row=0, col=0, row_span=2)
# The other view will show the 2D histogram of the data with the TF over it
cmap_view = grid.add_view(row=2, col=0, camera='panzoom')


class GradientMagnitudeTF(TextureSamplingTF):
    """Transfer function that uses the data value and gradient magnitude to
    sample a 2D transfer function.
    """

    glsl_tf = """\
    vec4 applyTransferFunction(vec4 color, vec3 loc, vec3 origin, vec3 step, float max_depth) {
        // calculate normal vector from gradient
        vec3 dstep = 1.5 / u_shape;
        // pass a dummy value for the "maxColor" which we're not going to use
        vec4 _dummy = vec4(0.0);
        vec3 N = calculateGradient(loc, dstep, _dummy);
        // also calculate the gradient magnitude
        float gm = length(N);

        gm = clamp(gm, min(clim.x, clim.y), max(clim.x, clim.y));

        float data = colorToVal(color);
        data = clamp(data, min(clim.x, clim.y), max(clim.x, clim.y));

        vec4 final_color = sampleTFLUT(pow(data, gamma), gm);
        return final_color;
    }
    """


bins = 64
cols = 128
lut = np.empty((bins, cols, 4), dtype=np.float32)
lut[:, :, 0] = 0
lut[:, :, 1] = np.linspace(0, 1, cols)
lut[:, :, 2] = 1
lut[:, :, 3] = np.linspace(0, 0.05, cols)  # alpha
lut_og = lut.copy()
lut_og_1d = lut_og.copy()
lut_og_2d = lut_og.copy()
lut_og_2d[:, :, 3] *= np.linspace(0.1, 1, bins)[:, None] ** 0.5

# basic volume rendering visual
vol = scene.visuals.Volume(
    mri_data,
    parent=data_view.scene,
    attenuation=0.015,
    method="translucent",
    relative_step_size=0.8,
    transfer_function=GradientMagnitudeTF(lut_og_1d),
)
# breakpoint()
cam = scene.cameras.TurntableCamera(parent=data_view.scene, fov=60, name='Turntable')
data_view.camera = cam
data_view.camera.scale_factor = 320.0

# display the 2D histogram of the data with the TF over it
gm = np.linalg.norm(np.gradient(mri_data), axis=0)
hist_data = np.histogram2d(
    gm.ravel(),
    mri_data.ravel(),
    bins=(bins, cols),
    range=((0, 1), (0, 1)),
)[0].astype(np.float32)

hist = scene.visuals.Image(np.log(hist_data + 1e-3), parent=cmap_view.scene, cmap="grays")
cmap = scene.visuals.Image(vol.transfer_function._lut, parent=cmap_view.scene)


def update_cmap_view():
    # multiply by 10 just so it's easier to see, even though it's not correct
    cmap_vis = vol.transfer_function._lut.copy()
    cmap_vis[:, :, 3] *= 10
    cmap.set_data(cmap_vis)
    cmap.set_gl_state('translucent', depth_test=False)
    cmap.update()


cmap_view.camera.rect = (0, 0, cols, bins)
cmap_view.camera.interactive = False
update_cmap_view()


@canvas.events.mouse_move.connect
@canvas.events.mouse_press.connect
def paint_tf(event):
    u, v = lut_og.shape[:2]
    if event.button == 1 and cmap_view.parent is not None:
        x, y = event.pos
        v_ = int(x * v / cmap_view.size[0]) - 1
        u_ = u - int((y - data_view.size[1]) * u / cmap_view.size[1]) - 1
        if u_ < 0 or u_ >= u or v_ < 0 or v_ >= v:
            return
        lut = vol.transfer_function._lut.copy()
        u_min, u_max = max(0, u_ - 1), min(u, u_ + 2)
        v_min, v_max = max(0, v_ - 1), min(v, v_ + 2)
        if "Alt" in event.modifiers:
            # erase
            lut[u_min:u_max, v_min:v_max, :] = lut_og[u_min:u_max, v_min:v_max, :]
        else:
            # draw red
            lut[u_min:u_max, v_min:v_max, 3] *= 1.2
            lut[u_min:u_max, v_min:v_max, 0] = 1.0
            lut[u_min:u_max, v_min:v_max, 1:3] = 0.0
        lut = np.clip(lut, 0, 1.0)
        vol.transfer_function = GradientMagnitudeTF(lut)
        update_cmap_view()
        vol.update()


@canvas.events.key_press.connect
def on_key_press(event):
    global lut_og
    if event.text == "1":
        vol.method = "translucent"
        lut_og = lut_og_1d
        new_lut = lut_og.copy()
        vol.transfer_function = GradientMagnitudeTF(new_lut)
        print("translucent, 1D colormap")
        update_cmap_view()
        vol.update()

    elif event.text == "2":
        vol.method = "translucent"
        lut_og = lut_og_2d
        new_lut = lut_og.copy()
        vol.transfer_function = GradientMagnitudeTF(new_lut)
        print("translucent, 2D colormap")
        update_cmap_view()
        vol.update()

    if event.text in "[]":
        if event.text == "[":
            vol.relative_step_size *= 0.9
        elif event.text == "]":
            vol.relative_step_size *= 1.1
        print("relative step size:", vol.relative_step_size)
        vol.update()


if __name__ == '__main__':
    print(__doc__)
    app.run()
