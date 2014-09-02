# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Demonstrate the use of the vispy console. Note how the console size is
independent of the canvas scaling.
"""

from vispy import scene, app
from vispy.scene.widgets import Console
from vispy.scene.visuals import Text

canvas = scene.SceneCanvas(keys='interactive', size=(300, 300))
vb = scene.widgets.ViewBox(parent=canvas.scene, border_color='b')
vb.camera.rect = -1, -1, 2, 2
text = Text('Starting timer...', color='w', font_size=24, parent=vb.scene)

console = Console(text_color='g', text_scale=2, border_color='g')

grid = canvas.central_widget.add_grid()
grid.add_widget(vb, row=0, col=0)
grid.add_widget(console, row=1, col=0)


def on_timer(event):
    text.text = 'Tick #%s' % event.iteration
    if event.iteration % 10 == 0:
        console.clear()
    console.write('Elapsed: %s' % event.elapsed)
    canvas.update()

timer = app.Timer(1.0, connect=on_timer, start=True)

canvas.show()
canvas.app.run()
