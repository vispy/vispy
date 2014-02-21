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
import numpy
import pyopencl, pyopencl.array
N = 1024

canvas = app.Canvas(size=(512, 512), title="VisPy - OpenCL")

#data = np.zeros(N, np.float32)
#vbo = gloo.VertexBuffer(data)

# Question: How do I actually send this to the GPU ?
#vbo.activate()
#print(dir(vbo))
#print(vbo._handle, type(vbo._handle))


src = """
__kernel void buf_to_tex( global float *ary,
                          int width,
                          int height,
                          float mini,
                          float maxi,
                          write_only image2d_t texture)
{
  int x = get_global_id(0);
  int y = get_global_id(1);
  float data = (ary[x+width*y] - mini)/(maxi-mini); 
  if ((x>=width)||(y>=height)) return;
  write_imagef( texture, (int2)(x,y), data);
}
"""

fragment = """ // texture fragment shader
uniform sampler2D u_texture1;
varying vec2 v_texcoord;
void main()
{
            vec4 clr1 = texture2D(u_texture1, v_texcoord);
            gl_FragColor = vec4(vec3(clr1.a),1.0) ;
            }
"""
vertex = """
attribute vec3 position;
attribute vec2 texcoord;

varying vec2 v_texcoord;
void main()
{
            v_texcoord = texcoord;
            gl_Position = vec4(position, 1);
}
"""

canvas.show()
glTex =  gloo.Texture2D(numpy.empty((N,N),dtype=numpy.float32))
glTex.activate()
print glTex

positions = numpy.array([[-0.8, -0.8, 0.0], [+0.7, -0.7, 0.0],
                          [-0.7, +0.7, 0.0], [+0.8, +0.8, 0.0, ]], numpy.float32)
texcoords = numpy.array([[1.0, 1.0], [0.0, 1.0],
                          [1.0, 0.0], [0.0, 0.0]], numpy.float32)

program = gloo.Program(vert=vertex, frag=fragment)
program['u_texture1'] = glTex
program['position'] = gloo.VertexBuffer(positions)
program["texcoord"] = gloo.VertexBuffer(texcoords)
#vbo = gloo.VertexBuffer(
ctx = openCL.get_OCL_context()
print("OpenCL context on device: %s" % ctx.devices[0])
queue = pyopencl.CommandQueue(ctx)
prg = pyopencl.Program(ctx, src).build()
#print(ctx)

img = numpy.random.randint(0, 65000, N*N).astype(numpy.float32).reshape((N,N))
ary = pyopencl.array.to_device(queue, img)
print ary
#mf = pyopencl.mem_flags
#fmt = pyopencl.ImageFormat(pyopencl.channel_order.INTENSITY, pyopencl.channel_type.FLOAT)
#img2d = pyopencl.Image(ctx, mf.WRITE_ONLY, fmt, shape=(N,N), buffer=ary.data)
#img2d = pyopencl.image_from_array(ctx, img, num_channels=None, mode="w", norm_int=True)
#print img2d
clTex = pyopencl.GLTexture(ctx, pyopencl.mem_flags.READ_WRITE,
                gloo.gl.GL_TEXTURE_2D, 0, int(glTex.handle), 2)
print clTex
#pyopencl.enqueue_acquire_gl_objects(queue, [clTex], wait_for=True)
prg.buf_to_tex(queue, (N,N), (8,8), ary.data, numpy.int32(N), numpy.int32(N), numpy.float32(0.0), numpy.float32(65500),
        clTex).wait()

#clTex = pyopencl.GLTexture(ctx,img2d, dims=2)
#pyopencl.GLBuffer(ctx, pyopencl.mem_flags.READ_WRITE, int(vbo._handle))
#program.draw(gloo.gl.GL_TRIANGLE_STRIP)
app.run()

