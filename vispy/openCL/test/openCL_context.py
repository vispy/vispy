#!/usr/bin/python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
from vispy import app
from vispy import gloo
from vispy import openCL
import numpy
import time
import pyopencl, pyopencl.array
N = 2048


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
    __kernel void
    u16_to_float(__global unsigned short  *array_int,
    __global float *array_float,
    const int IMAGE_W,
    const int IMAGE_H
    )
    {
    //Global memory guard for padding
    if ((get_global_id(0)<IMAGE_W) && (get_global_id(1) < IMAGE_H)){
    int i = get_global_id(0) + IMAGE_W * get_global_id(1);
    array_float[i]=(float)array_int[i];
    }
    }//end kernel
    """
#//uniform sampler1D u_colormap;

fragment = """ // texture fragment shader
uniform sampler2D u_texture1;
varying vec2 v_texcoord;
void main()
{
    float clr1 = texture2D(u_texture1, v_texcoord).r;
    //vec4 color = vec4(texture1d(u_colormap, clr1).rgb,1.0);
    //gl_FragColor = color;
    gl_FragColor = vec4(vec3(clr1),1.0);
//    if (clr1>0.5)
//        gl_FragColor = vec4(vec3(1.0),1.0);
//    else
//        gl_FragColor = vec4(vec3(0.0),1.0);
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

class Canvas(app.Canvas):
    def __init__(self, tex_size):
        app.Canvas.__init__(self)
        self.tex_size = tex_size
        self.gl_program = None
        self.ocl_prg = None
        self.last_start = 0.0
    
    
    def init_gl(self):
        # Create program
        self.gl_program = gloo.Program(vertex, fragment)
        self.gl_tex =  gloo.Texture2D(numpy.zeros((self.tex_size,self.tex_size),dtype=numpy.float32)+0.5)
        self.gl_tex.activate()
        print("activated")
        # Set uniforms and samplers
        positions = numpy.array([[-1.0, -1.0, 0.0], [+1.0, -1.0, 0.0],
                          [-1.0, +1.0, 0.0], [+1.0, +1.0, 0.0, ]], numpy.float32)
        texcoords = numpy.array([[1.0, 1.0], [0.0, 1.0],
                          [1.0, 0.0], [0.0, 0.0]], numpy.float32)
        self.gl_program['u_texture1'] = self.gl_tex
        self.gl_program['position'] = gloo.VertexBuffer(positions)
        self.gl_program['texcoord'] = gloo.VertexBuffer(texcoords)
    
    def on_initialize(self, event):
        gloo.gl.glClearColor(1, 1, 1, 1)

    def on_resize(self, event):
        width, height = event.size
        gloo.gl.glViewport(0, 0, width, height)

    def on_paint(self, event):

        # Clear
        gloo.gl.glClear(gloo.gl.GL_COLOR_BUFFER_BIT | gloo.gl.GL_DEPTH_BUFFER_BIT)

        # Draw shape with texture, nested context
        if self.gl_program:
            self.gl_program.draw(gloo.gl.GL_TRIANGLE_STRIP)
        self.swap_buffers()


    def init_openCL(self):
        self.gl_program.draw(gloo.gl.GL_TRIANGLE_STRIP)
        self.ocl_ctx = openCL.get_OCL_context()
        print("OpenCL context on device: %s" % self.ocl_ctx.devices[0])
        self.queue = pyopencl.CommandQueue(self.ocl_ctx)
        self.ocl_prg = pyopencl.Program(self.ocl_ctx, src).build()
        self.ary_float = pyopencl.array.empty(self.queue, shape=(self.tex_size,self.tex_size),dtype=numpy.float32)
    
        self.ocl_tex = pyopencl.GLTexture(self.ocl_ctx, pyopencl.mem_flags.READ_WRITE,
                        gloo.gl.GL_TEXTURE_2D, 0, int(self.gl_tex.handle), 2)

        img = numpy.random.randint(0,65000,self.tex_size**2).reshape((self.tex_size,self.tex_size)).astype(numpy.uint16)
        self.ocl_ary = pyopencl.array.to_device(self.queue, img)
    
        self.new_image(img)
    
    def new_image(self, img):
        if self.ocl_prg is None:
            self.init_openCL()
        self.ocl_ary.set(img)
        pyopencl.enqueue_acquire_gl_objects(self.queue, [self.ocl_tex])
        self.ocl_prg.u16_to_float(self.queue, (self.tex_size,self.tex_size), (8,8),
                                self.ocl_ary.data,
                                self.ary_float.data,
                                numpy.int32(self.tex_size),
                                numpy.int32(self.tex_size))
        self.ocl_prg.buf_to_tex(self.queue, (self.tex_size,self.tex_size), (8,8),
                                  self.ocl_ary.data, numpy.int32(self.tex_size), numpy.int32(self.tex_size),
                                  numpy.float32(0.0), numpy.float32(65000.0), self.ocl_tex)
        pyopencl.enqueue_release_gl_objects(self.queue, [self.ocl_tex]).wait()
        t = time.time()
        print("pyopencl program called fps= %.3fs"%(1.0/(t-self.last_start)))
        self.last_start = t
        self.on_paint(None)


if __name__ == '__main__':
    img1 = numpy.random.randint(0,65000,N**2).reshape((N,N)).astype(numpy.uint16)
    img2 = numpy.random.randint(0,65000,N**2).reshape((N,N)).astype(numpy.uint16)
    c = Canvas(N)
    c.measure_fps(1)
    c.show()
    c.init_gl()
    c.show()
    c.init_openCL()
    while True:
        c.new_image(img1)
        c.new_image(img2)
    app.run()
