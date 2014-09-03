# -*- coding: utf-8 -*-
# vispy: gallery 30
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

canvas = scene.SceneCanvas(keys='interactive', size=(400, 400))
vb = scene.widgets.ViewBox(parent=canvas.scene, border_color='b')
vb.camera.rect = -1, -1, 2, 2
text = Text('Starting timer...', color='w', font_size=24, parent=vb.scene)

console = Console(text_color='g', font_scale=2, border_color='g')

grid = canvas.central_widget.add_grid()
grid.add_widget(vb, row=0, col=0)
grid.add_widget(console, row=1, col=0)


def on_timer(event):
    text.text = 'Tick #%s' % event.iteration
    if event.iteration > 1 and event.iteration % 10 == 0:
        console.clear()
    console.write('Elapsed:\n  %s' % event.elapsed)
    canvas.update()

timer = app.Timer(2.0, connect=on_timer, start=True)

console.write('This is a line that will be wrapped automatically by the'
              'console.\n')
console.write('This line will be truncated ....................,\n'
              'but this next line will survive.\n', wrap=False)

canvas.show()
canvas.app.run()
