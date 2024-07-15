# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 2

"""
Volume Rendering with a Depth Color Transfer Function
================

This example demonstrates how to use a transfer function to color the volume based on the depth of
the maximum value.

Controls:

* 1  - Show attenuated MIP, colored by depth of max value
* 2  - Show attenuated MIP
* - / = - Decrease/increase depth color scale
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
mri_data = (mri_data - mri_data.min()) / mri_data.ptp()

# Prepare canvas
canvas = scene.SceneCanvas(keys='interactive', size=(768, 768), show=True)
canvas.measure_fps()
view = canvas.central_widget.add_view()


class DepthColorTF(BaseTransferFunction):
    """Transfer function that colors the volume based on the depth of the maximum value."""

    glsl_tf = """\
    uniform float u_depth_color_scale;
    vec4 applyTransferFunction(vec4 color, vec3 loc, vec3 start_loc, vec3 step, float max_depth) {
        vec3 d = loc - start_loc;
        float depth = u_depth_color_scale * length(d) / max_depth;
        depth = smoothstep(0.0, 1.0, depth);
        depth = depth * (clim.y - clim.x) + clim.x;
        vec4 hue = applyColormap(depth);
        vec4 final_color = vec4(color.r * hue.rgb, 1.0);
        return final_color;
    }
    """

    def __init__(self):
        super().__init__()
        self._depth_color_scale = 1.0

    @property
    def depth_color_scale(self):
        return self._depth_color_scale

    @depth_color_scale.setter
    def depth_color_scale(self, value):
        self._depth_color_scale = value

    def get_uniforms(self):
        return {"u_depth_color_scale": self.depth_color_scale}


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
cam = scene.cameras.TurntableCamera(parent=view.scene, fov=60, name='Turntable', scale_factor=320.0)
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
        if not hasattr(vol.transfer_function, "depth_color_scale"):
            return
        if event.text == "-":
            vol.transfer_function.depth_color_scale *= 0.9
        elif event.text == "=":
            vol.transfer_function.depth_color_scale *= 1.1
        vol._need_tf_update = True
        print("depth_color_scale:", vol.transfer_function.depth_color_scale)
        vol.update()

    if event.text in "[]":
        if event.text == "[":
            vol.attenuation *= 0.9
        elif event.text == "]":
            vol.attenuation *= 1.1
        print("relative step size:", vol.relative_step_size)
        vol.update()


if __name__ == '__main__':
    print(__doc__)
    app.run()
