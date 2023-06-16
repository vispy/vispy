# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Picking Markers
===============

Demonstrates how to identify (pick) markers. Hover markers to change their
symbol and color.

Controls:
* p  - Toggle picking view - shows the colors encoding marker ID
* r  - Reset marker symbols and colors
"""
import random
import time
import numpy as np
from scipy.constants import golden as GOLDEN

from vispy import app, scene
from vispy.scene.visuals import Markers
from vispy.visuals.filters import MarkerPickingFilter

canvas = scene.SceneCanvas(keys='interactive', bgcolor='black')
view = canvas.central_widget.add_view(camera="panzoom")
view.camera.rect = (-1, -1, 2, 2)

# floret pattern
n = 10_000
radius = np.linspace(0, 0.9, n)**0.6  # prevent extreme density at center
theta = np.arange(n) * GOLDEN
pos = np.column_stack([radius * np.cos(theta), radius * np.sin(theta)])

COLORS = [
    (1, 0, 0, 1),  # red
    (1, 0.5, 0, 1),  # orange
    (1, 1, 0, 1),  # yellow
    (0, 1, 0, 1),  # green
    (0, 0, 1, 1),  # blue
    (0.29, 0, 0.51, 1),  # indigo
    (0.93, 0.51, 0.93, 1),  # violet
]

colors = np.zeros((n, 4), dtype=np.float32)
colors[:, 0] = 1  # red
colors[:, -1] = 1  # alpha
_colors = colors.copy()

symbols = list(Markers._symbol_shader_values.keys())
symbols_ring = dict(zip(symbols, symbols[1:]))
symbols_ring[symbols[-1]] = symbols[0]

EDGE_COLOR = "white"
MARKER_SIZE = 0.0125
EDGE_WDITH = MARKER_SIZE / 10

markers = Markers(
    pos=pos,
    edge_color=EDGE_COLOR,
    face_color=colors,
    size=MARKER_SIZE,
    edge_width=EDGE_WDITH,
    scaling="scene",
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


throttle = time.monotonic()


@canvas.events.mouse_move.connect
def on_mouse_move(event):
    global throttle
    # throttle mouse events to 50ms
    if time.monotonic() - throttle < 0.05:
        return
    throttle = time.monotonic()

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
    marker_idx = (picking_render.view(np.uint32) - 1)[2, 2, 0]

    if marker_idx >= 0 and marker_idx < len(pos):
        new_symbols = list(markers.symbol)
        new_symbol = symbols_ring[new_symbols[marker_idx]]
        new_symbols[marker_idx] = new_symbol

        colors[marker_idx] = random.choice(COLORS)
        markers.set_data(
            pos=pos,
            edge_color=EDGE_COLOR,
            face_color=colors,
            size=MARKER_SIZE,
            edge_width=EDGE_WDITH,
            symbol=new_symbols,
        )


@canvas.events.key_press.connect
def on_key_press(event):
    global colors
    if event.key == 'p':
        # toggle face picking view
        picking_filter.enabled = not picking_filter.enabled
        markers.update_gl_state(blend=not picking_filter.enabled)
        markers.update()
    if event.key == 'r':
        # reset marker symbols
        colors = _colors.copy()
        markers.set_data(
            pos=pos,
            edge_color=EDGE_COLOR,
            face_color=colors,
            size=MARKER_SIZE,
            edge_width=EDGE_WDITH,
        )


canvas.show()


if __name__ == "__main__":
    print(__doc__)
    app.run()
