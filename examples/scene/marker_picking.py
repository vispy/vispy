# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Picking Markers
===============

Demonstrates how to identify (pick) markers. Click markers to change their edge
color.

Controls:
* p  - Toggle picking view - shows the colors encoding marker ID
* s  - Cycle marker symbols
* c  - Clear picked markers
"""
import itertools

import numpy as np
from scipy.constants import golden as GOLDEN

from vispy import app, scene
from vispy.scene.visuals import Markers
from vispy.visuals.filters import MarkerPickingFilter

symbols = itertools.cycle(Markers._symbol_shader_values.keys())


MARKER_SIZE = 0.0125
EDGE_WDITH = MARKER_SIZE / 10

canvas = scene.SceneCanvas(keys='interactive', bgcolor='black')
view = canvas.central_widget.add_view(camera="panzoom")
view.camera.rect = (-1, -1, 2, 2)
n = 10_000
radius = np.linspace(0, 0.9, n)**0.6
theta = np.arange(n) * GOLDEN * np.pi
pos = np.column_stack([radius * np.cos(theta), radius * np.sin(theta)])
edge_color = np.ones((len(pos), 4), dtype=np.float32)

markers = Markers(
    pos=pos,
    edge_color=edge_color,
    face_color="red",
    size=MARKER_SIZE,
    edge_width=EDGE_WDITH,
    scaling="scene",
    symbol=next(symbols),
)
markers.update_gl_state(depth_test=True)
view.add(markers)

# Use filters to affect the rendering of the mesh.
picking_filter = MarkerPickingFilter()
markers.attach(picking_filter)


@view.events.connect
def on_viewbox_change(event):
    # workaround for vispy/#2501
    markers.update_gl_state(blend=not picking_filter.enabled)


@canvas.events.mouse_press.connect
def on_mouse_press(event):
    # adjust the event position for hidpi screens
    render_size = tuple(d * canvas.pixel_scale for d in canvas.size)
    x_pos = event.pos[0] * canvas.pixel_scale
    y_pos = render_size[1] - (event.pos[1] * canvas.pixel_scale)

    # render a small patch around the mouse cursor
    restore_state = not picking_filter.enabled
    picking_filter.enabled = True
    markers.update_gl_state(blend=False)
    picking_render = canvas.render(
        crop=(x_pos - 2, y_pos - 2, 5, 5),
        bgcolor=(0, 0, 0, 0),
        alpha=True,
    )
    if restore_state:
        picking_filter.enabled = False
    markers.update_gl_state(blend=not picking_filter.enabled)

    # unpack the face index from the color in the center pixel
    face_idx = (picking_render.view(np.uint32) - 1)[2, 2]

    if face_idx >= 0 and face_idx < len(pos):
        edge_color[face_idx] = (0, 1, 0, 1)
        markers.set_data(
            pos=pos,
            edge_color=edge_color,
            face_color="red",
            size=MARKER_SIZE,
            edge_width=EDGE_WDITH,
            symbol=markers.symbol,
        )


@canvas.events.key_press.connect
def on_key_press(event):
    if event.key == 'c':
        edge_color = np.ones((len(pos), 4), dtype=np.float32)
        markers.set_data(
            pos=pos,
            edge_color=edge_color,
            face_color="red",
            size=MARKER_SIZE,
            edge_width=EDGE_WDITH,
            symbol=markers.symbol,
        )
    if event.key == 'p':
        # toggle face picking view
        picking_filter.enabled = not picking_filter.enabled
        markers.update_gl_state(blend=not picking_filter.enabled)
        markers.update()
    if event.key == 's':
        markers.symbol = next(symbols)
        markers.update()


canvas.show()


if __name__ == "__main__":
    print(__doc__)
    app.run()
