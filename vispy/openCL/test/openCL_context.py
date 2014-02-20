#!/usr/bin/python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
from vispy import app
from vispy import gloo
# from vispy.gloo import gl
from vispy import openCL
import numpy as np
import pyopencl
N = 1000

canvas = app.Canvas(size=(512, 512), title="VisPy - OpenCL")


canvas.show()
ctx = openCL.get_OCL_context()
print("OpenCL context on device: %s" % ctx.devices[0])

data = np.zeros(N, np.float32)
vbo = gloo.VertexBuffer(data)

# Question: How do I actually send this to the GPU ?
vbo.activate()
print(dir(vbo))
print(vbo._handle, type(vbo._handle))
pyopencl.GLBuffer(ctx, pyopencl.mem_flags.READ_WRITE, int(vbo._handle))
# app.run()
