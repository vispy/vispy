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
uniform sampler1D u_colormap;
varying vec2 v_texcoord;
void main()
{
    float clr1 = texture2D(u_texture1, v_texcoord).r;
    vec4 color = vec4(texture1d(u_colormap, value).rgb,1.0);
    gl_FragColor = color;
    //vec4(vec3(clr1),1.0);
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
    
    def init_gl(self):
        # Create program
        self.gl_program = gloo.Program(vertex, fragment)
        self.gl_tex =  gloo.Texture2D(numpy.zeros((self.tex_size,self.tex_size),dtype=numpy.float32))
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
        colormap = numpy.empty((512,3),dtype=numpy.float32)
        colormap[:,0] = numpy.interp(numpy.arange(512),
                              [0, 171, 342, 512],
                              [0,1,1,1])
        colormap[:,1] = numpy.interp(numpy.arange(512),
                              [0, 171, 342, 512],
                              [0,0,1,1])
        colormap[:,2] = numpy.interp(numpy.arange(512),
                              [0, 171, 342, 512],
                              [0,0,0,1])
        self.gl_program['u_colormap'] = colormap
    
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
        
#canvas = app.Canvas(size=(512, 512), title="VisPy - OpenCL")
#canvas.show()

        self.gl_program.draw(gloo.gl.GL_TRIANGLE_STRIP)
#vbo = gloo.VertexBuffer(
        self.ocl_ctx = openCL.get_OCL_context()
        print("OpenCL context on device: %s" % self.ocl_ctx.devices[0])
        self.queue = pyopencl.CommandQueue(self.ocl_ctx)
        self.ocl_prg = pyopencl.Program(self.ocl_ctx, src).build()
#print(ctx)

        img = numpy.random.randint(0, 65000, N*N).astype(numpy.float32).reshape((N,N))
        self.ocl_ary = pyopencl.array.to_device(self.queue, img)
        #print ary
        #mf = pyopencl.mem_flags
        #fmt = pyopencl.ImageFormat(pyopencl.channel_order.INTENSITY, pyopencl.channel_type.FLOAT)
        #img2d = pyopencl.Image(ctx, mf.WRITE_ONLY, fmt, shape=(N,N), buffer=ary.data)
        #img2d = pyopencl.image_from_array(ctx, img, num_channels=None, mode="w", norm_int=True)
        #print img2d
        self.ocl_tex = pyopencl.GLTexture(self.ocl_ctx, pyopencl.mem_flags.READ_WRITE,
                        gloo.gl.GL_TEXTURE_2D, 0, int(self.gl_tex.handle), 2)
        #print clTex
        #pyopencl.enqueue_acquire_gl_objects(queue, [clTex], wait_for=True)
        e=self.ocl_prg.buf_to_tex(self.queue, (N,N), (8,8),
                                self.ocl_ary.data, numpy.int32(N), numpy.int32(N),
                                numpy.float32(0.0), numpy.float32(65500), self.ocl_tex)
        e.wait()

        #clTex = pyopencl.GLTexture(ctx,img2d, dims=2)
        #pyopencl.GLBuffer(ctx, pyopencl.mem_flags.READ_WRITE, int(vbo._handle))
        self.gl_program.draw(gloo.gl.GL_TRIANGLE_STRIP)



if __name__ == '__main__':
    c = Canvas(N)
    c.show()
    c.init_gl()
    c.init_openCL()
    print c.ocl_ary.get()
    app.run()
