# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 2

"""
Volume Rendering with a Depth Color Transfer Function
=====================================================

This example demonstrates how to use a transfer function to color the volume based on the depth of
the maximum value.

Controls:

* 1  - Show attenuated MIP, colored by depth of max value
* 2  - Show attenuated MIP
* - / = - Decrease/increase gamma (change how depth affects color)
* [ / ] - Decrease/increase attenuation

"""
import numpy as np
from vispy import app, scene, io
from vispy.color import BaseTransferFunction

try:
    import matplotlib
    mip_colormap = "turbo"
except ImportError:
    matplotlib = None
    mip_colormap = "viridis"

# Read and normalize volume data
mri_data = np.load(io.load_data_file('brain/mri.npz'))['data']
mri_data = np.flipud(np.rollaxis(mri_data, 1)).astype(np.float32)
mri_data = (mri_data - mri_data.min()) / np.ptp(mri_data)

# Prepare canvas
canvas = scene.SceneCanvas(keys='interactive', size=(768, 768), show=True)
canvas.measure_fps()
view = canvas.central_widget.add_view()


class DepthColorTF(BaseTransferFunction):
    """Transfer function that colors the volume based on the depth of the maximum value."""

    glsl_tf = """\
    vec4 applyTransferFunction(vec4 color, vec3 loc, vec3 step, vec3 depth_origin, vec3
                               depth_plane_normal, float max_depth) {
        float depth = dot(loc - depth_origin, depth_plane_normal);
        depth = smoothstep(0.0, 1.0, depth / max_depth);
        depth = depth * (clim.y - clim.x) + clim.x;
        vec4 hue = applyColormap(depth);
        vec4 final_color = vec4(color.r * hue.rgb, 1.0);
        return final_color;
    }
    """


# basic volume rendering visual
vol = scene.visuals.Volume(
    mri_data,
    parent=view.scene,
    attenuation=0.015,
    method="attenuated_mip",
    cmap=mip_colormap,
    relative_step_size=0.5,
    transfer_function=DepthColorTF(),
)

cam = scene.cameras.ArcballCamera(parent=view.scene, fov=60, name='Turntable', scale_factor=320.0)
view.camera = cam
view.camera.scale_factor = 320.0


@canvas.events.key_press.connect
def on_key_press(event):
    global lut_og
    if event.text == "1":
        vol.method = "attenuated_mip"
        vol.cmap = mip_colormap
        vol.transfer_function = DepthColorTF()
        print("attenuated_mip, depth color transfer function")
        vol.update()

    elif event.text == "2":
        vol.method = "attenuated_mip"
        print("attenuated_mip, base transfer function")
        vol.update()

    if event.text in "-=":
        if event.text == "-":
            vol.gamma *= 0.9
        elif event.text == "=":
            vol.gamma *= 1.1
        print("gamma:", vol.gamma)
        vol.update()

    if event.text in "[]":
        if event.text == "[":
            vol.attenuation *= 0.9
        elif event.text == "]":
            vol.attenuation *= 1.1
        print("attenutation:", vol.attenuation)
        vol.update()

    if event.text == "f":
        if view.camera.fov == 60:
            view.camera.fov = 0
        else:
            view.camera.fov = 60
        print("fov:", view.camera.fov)


if __name__ == '__main__':
    print(__doc__)
    app.run()
