# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# Author: Jérôme Kieffer
# -----------------------------------------------------------------------------
import unittest
import numpy
import vispy.opencl
import vispy.app

pyopencl = vispy.opencl.pyopencl

# How can I test if I have OpenCL with GL support but no driver for the GPU ?
# -----------------------------------------------------------------------------

class OpenCLTest(unittest.TestCase):
    def setUp(self):
        self.app = vispy.app.Canvas()
        self.app.show()
        if pyopencl:
            self.default_ctx, self.ids = vispy.opencl._make_context()

    def tearDown(self):
        self.app.close()
#        self.app.show()
        del self.app

    def test_opencl_context_free(self):
        if pyopencl:
            ctx = vispy.opencl.OpenCL.get_context()
            self.assert_(ctx.devices == self.default_ctx.devices)
        else:
            try:
                ctx = vispy.opencl.OpenCL.get_context()
            except:
                pass
            else:
                raise AssertionError


    def test_opencl_buffer(self):
        if not pyopencl: return
        ary = numpy.arange(100).reshape((10, 10)).astype("float32")
        buf = vispy.opencl.VertexBuffer(ary)
        buf.activate()
        cl_buffer = buf.get_ocl()

    def test_opencl_texture(self):
        if not pyopencl: return
        ary = numpy.arange(100).reshape((10, 10)).astype("float32")
        tex = vispy.opencl.Texture2D(ary)
        tex.activate()
        cl_image = tex.get_ocl()
