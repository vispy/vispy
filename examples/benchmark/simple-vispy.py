#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# VisPy - Copyright (c) 2013, Vispy Development Team All rights reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import time
from vispy import app, gl

app.use('qt')
# app.use('glut')
# app.use('pyglet')

canvas = app.Canvas(size=(512,512), title = "Do nothing benchmark (vispy)")

@canvas.connect
def on_paint(event):
    global t, t0, frames
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
    t = time.time()
    frames = frames + 1
    elapsed = (t-t0) # seconds
    if elapsed > 2.5:
        print( "FPS : %.2f (%d frames in %.2f second)"
               % (frames/elapsed, frames, elapsed))
        t0, frames = t,0
    canvas.update()

t0, frames, t = time.time(),0,0
canvas.show()
app.run()
