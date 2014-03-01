#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Author: Jérôme KIEFFER
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""
Demo showing the sharing of a OpenGL texture <--> OpenCL image
"""

import os, sys, time
import numpy
from vispy import app
from vispy import gloo
from vispy import opencl
import pyopencl.array
N = 2048


src = """
__kernel void buf_to_tex( global const float *ary,
                          int width,
                          int height,
                          global const float *mini,
                          global const float *maxi,
                          const int logscale,
                          write_only image2d_t texture)
{
    int x = get_global_id(0);
    int y = get_global_id(1);
    if ((x>=width)||(y>=height)) return;
    float data;
    if (maxi[0]==mini[0])
        data = (ary[x+width*y] - mini[0]);
    else
        data = (ary[x+width*y] - mini[0])/(maxi[0]-mini[0]);
    if (logscale)
        data = log(data*(M_E_F-1.0f)+1.0f);
    write_imagef( texture, (int2)(x,y), data);
}
__kernel void
u16_to_float(global unsigned short  *array_int,
             global float *array_float,
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
# //uniform sampler1D u_colormap;

fragment = """ // texture fragment shader
uniform sampler2D u_texture1;
uniform sampler2D u_colormap;
varying vec2 v_texcoord;
void main()
{   float data = texture2D(u_texture1, v_texcoord).r;
    gl_FragColor = vec4(texture2D(u_colormap,vec2(1.0f,data)).rgb, 1.0f);
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
        self.last_img = None
        self.logscale = 0
        print('Press "L" to switch to log scale, "B" to benchmark and "Q" to quit')



    def init_gl(self):
        # Create program
        self.gl_program = gloo.Program(vertex, fragment)
        self.gl_tex = opencl.Texture2D(numpy.zeros((self.tex_size, self.tex_size), dtype=numpy.float32) + 0.5)  # initial color: plain gray
        # Set uniforms and samplers
        positions = numpy.array([[-1.0, -1.0, 0.0], [+1.0, -1.0, 0.0],
                          [-1.0, +1.0, 0.0], [+1.0, +1.0, 0.0, ]], numpy.float32)
        texcoords = numpy.array([[1.0, 1.0], [0.0, 1.0],
                          [1.0, 0.0], [0.0, 0.0]], numpy.float32)
        self.colormap = numpy.array([[0, 0, 0],
                                     [1, 0, 0],
                                     [1, 1, 0],
                                     [1, 1, 1]], dtype=numpy.float32)

        self.gl_program['u_texture1'] = self.gl_tex
        self.gl_program['position'] = gloo.VertexBuffer(positions)
        self.gl_program['texcoord'] = gloo.VertexBuffer(texcoords)
        gl_colormap = gloo.Texture2D(self.colormap.reshape((self.colormap.shape[0], 1, 3)))
        self.gl_program['u_colormap'] = gl_colormap


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


    def init_openCL(self, platform=None, device=None):
        self.gl_program.draw(gloo.gl.GL_TRIANGLE_STRIP)
        self.ctx = opencl.OpenCL.get_context(platform, device)
        d = self.ctx.devices[0]
        print("OpenCL context on device: %s" % d.name)
        wg_float = min(d.max_work_group_size, self.tex_size)
        self.red_size = 2 ** (int(numpy.ceil(numpy.log2(wg_float))))
        self.queue = pyopencl.CommandQueue(self.ctx)
        self.ocl_prg = pyopencl.Program(self.ctx, src).build()
        reduction_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "reductions.cl")).read()
        self.ocl_red = pyopencl.Program(self.ctx, reduction_src).build("-D WORKGROUP_SIZE=%s" % self.red_size)
        self.ary_float = pyopencl.array.empty(self.queue, shape=(self.tex_size, self.tex_size), dtype=numpy.float32)
        self.maxi_mini = pyopencl.array.empty(self.queue, (self.red_size, 2), dtype=numpy.float32)
        self.mini = pyopencl.array.empty(self.queue, (1), dtype=numpy.float32)
        self.maxi = pyopencl.array.empty(self.queue, (1), dtype=numpy.float32)
        self.cl_colormap = pyopencl.array.to_device(self.queue, self.colormap)
        self.ocl_tex = self.gl_tex.get_ocl(self.ctx)
        img = numpy.random.randint(0, 65000, self.tex_size ** 2).reshape((self.tex_size, self.tex_size)).astype(numpy.uint16)
        self.ocl_ary = pyopencl.array.to_device(self.queue, img)
        self.new_image(img)

    def new_image(self, img=None):
        if img is not None:
            self.last_img = img
        else:
            img = self.last_img
        if self.ocl_prg is None:
            self.init_openCL()
        pyopencl.enqueue_copy(self.queue, self.ocl_ary.data, img)
        self.ocl_prg.u16_to_float(self.queue, (self.tex_size, self.tex_size), (8, 4),
                                self.ocl_ary.data,
                                self.ary_float.data,
                                numpy.int32(self.tex_size),
                                numpy.int32(self.tex_size))
        self.ocl_red.max_min_global_stage1(self.queue, (self.red_size * self.red_size,), (self.red_size,),
                                                                   self.ary_float.data,
                                                                   self.maxi_mini.data,
                                                                   numpy.uint32(self.tex_size * self.tex_size))
        self.ocl_red.max_min_global_stage2(self.queue, (self.red_size,), (self.red_size,),
                                                                   self.maxi_mini.data,
                                                                   self.maxi.data,
                                                                   self.mini.data)

        pyopencl.enqueue_acquire_gl_objects(self.queue, [self.ocl_tex]).wait()
        self.ocl_prg.buf_to_tex(self.queue, (self.tex_size, self.tex_size), (8, 4),
                                  self.ary_float.data, numpy.int32(self.tex_size), numpy.int32(self.tex_size),
                                  self.mini.data, self.maxi.data, numpy.int32(self.logscale),
                                  self.ocl_tex)
        pyopencl.enqueue_release_gl_objects(self.queue, [self.ocl_tex]).wait()
        self.on_paint(None)

    def benchmark(self):
        """
        This is run after clicking on the picture ... to let the application initialize
        """
        print("Starting benchmark")
        y, x = numpy.ogrid[:self.tex_size, :self.tex_size]
        imgs = [numpy.zeros((self.tex_size, self.tex_size), dtype=numpy.uint16),
                numpy.dot(y, numpy.ones(self.tex_size, dtype=numpy.uint16).reshape(1, -1)).astype(numpy.uint16),
                numpy.dot(numpy.ones(self.tex_size, dtype=numpy.uint16).reshape(-1, 1), x).astype(numpy.uint16),
                numpy.dot(self.tex_size - y, numpy.ones(self.tex_size, dtype=numpy.uint16).reshape(1, -1)).astype(numpy.uint16),
                numpy.dot(numpy.ones(self.tex_size, dtype=numpy.uint16).reshape(-1, 1), self.tex_size - x).astype(numpy.uint16),
                (numpy.dot(y, x) / self.tex_size).astype(numpy.uint16),
                (numpy.dot(self.tex_size - y, self.tex_size - x) / self.tex_size).astype(numpy.uint16),
                (numpy.dot(y, x) // self.tex_size).astype(numpy.uint16),
                (numpy.dot(self.tex_size - y, self.tex_size - x) / self.tex_size).astype(numpy.uint16),
                numpy.random.randint(0, 65000, N ** 2).reshape((N, N)).astype(numpy.uint16)]

        number = len(imgs)
        t1 = time.time()
        for i in range(10):
            t0 = t1
            for i in imgs:
                c.new_image(i)
            t1 = time.time()
            print("Rendering at %4.2f fps (average of %i)" % (number / (t1 - t0), number))


    def on_key_release(self, ev):
        if ev.key.name == "L":
            self.logscale = 1 - self.logscale
            print("Switching logscale: %s" % self.logscale)
            self.new_image()
        elif ev.key.name == "B":
            self.benchmark()
        elif ev.key.name == "Q":
            self.app.quit()

if __name__ == '__main__':
    if len(sys.argv) == 3:
        platform = int(sys.argv[1])
        device = int(sys.argv[2])
    else:
        platform = None
        device = None
    c = Canvas(N)
    c.show()
    c.init_gl()
    c.show()
    c.init_openCL(platform, device)
    app.run()
