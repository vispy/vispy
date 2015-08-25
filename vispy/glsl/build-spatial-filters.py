#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# glumpy is an OpenGL framework for the fast visualization of numpy arrays.
# Copyright (C) 2009-2011  Nicolas P. Rougier. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY NICOLAS P. ROUGIER ''AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL NICOLAS P. ROUGIER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Nicolas P. Rougier.
# -----------------------------------------------------------------------------
'''
A filter is a shader that transform the current displayed texture. Since
shaders cannot be easily serialized within the GPU, they have to be well
structured on the python side such that we can possibly merge them into a
single source code for both vertex and fragment. Consequently, there is a
default code for both vertex and fragment with specific entry points such that
filter knows where to insert their specific code (declarations, functions and
call (or code) to be inserted in the main function).

Spatial interpolation filter classes for OpenGL textures.

Each filter generates a one-dimensional lookup table (weights value from 0 to
ceil(radius)) that is uploaded to video memory (as a 1d texture) and is then
read by the shader when necessary. It avoids computing weight values for each
pixel. Furthemore, each 2D-convolution filter is separable and can be computed
using 2 1D-convolution with same 1d-kernel (= the lookup table values).

Available filters:

  - Nearest  (radius 0.5)
  - Bilinear (radius 1.0)
  - Hanning (radius 1.0)
  - Hamming (radius 1.0)
  - Hermite (radius 1.0)
  - Kaiser (radius 1.0)
  - Quadric (radius 1.5)
  - Bicubic (radius 2.0)
  - CatRom (radius 2.0)
  - Mitchell (radius 2.0)
  - Spline16 (radius 2.0)
  - Spline36 (radius 4.0)
  - Gaussian (radius 2.0)
  - Bessel (radius 3.2383)
  - Sinc (radius 4.0)
  - Lanczos (radius 4.0)
  - Blackman (radius 4.0)


Note::

  Weights code has been translated from the antigrain geometry library
  available at http://www.antigrain.com/
'''


import math
import numpy as np


class SpatialFilter(object):
    ''' '''

    def __init__(self, radius=1.0):
        self.radius = radius

    def weight(self, x):
        '''
        Return filter weight for a distance x.

        :Parameters:
            ``x`` : 0 < float < ceil(self.radius)
                Distance to be used to compute weight.
        '''
        raise NotImplemented

    def kernel(self, size=4*512):
        radius = self.radius
        r = int(max(1.0, math.ceil(radius)))
        samples = size / r
        n = size  # r*samples
        kernel = np.zeros(n)
        X = np.linspace(0, r, n)
        for i in range(n):
            kernel[i] = self.weight(X[i])
        N = np.zeros(samples)
        for i in range(r):
            N += kernel[::+1][i*samples:(i+1)*samples]
            N += kernel[::-1][i*samples:(i+1)*samples]
        for i in range(r):
            kernel[i*samples:(i+1)*samples:+1] /= N
        return kernel

    def filter_code(self):

        n = int(math.ceil(self.radius))
        filter_1 = 'filter1D_radius%d' % n
        filter_2 = 'filter2D_radius%d' % n

        code = ''
        code += 'vec4\n'
        code += '%s( sampler2D kernel, float index, float x, ' % filter_1
        for i in range(2*n):
            if i == 2*n-1:
                code += 'vec4 c%d )\n' % i
            else:
                code += 'vec4 c%d, ' % i
        code += '{\n'
        code += '    float w, w_sum = 0.0;\n'
        code += '    vec4 r = vec4(0.0,0.0,0.0,0.0);\n'
        for i in range(n):
            code += '    w = unpack_interpolate(kernel, vec2(%f+(x/%.1f), index));\n' % (1.0 - (i + 1) / float(n), n)  # noqa
            code += '    w = w*kernel_scale + kernel_bias;\n'  # noqa
            # code += '   w_sum += w;'
            code += '    r += c%d * w;\n' % i
            code += '    w = unpack_interpolate(kernel, vec2(%f-(x/%.1f), index));\n' % ((i+1)/float(n), n)  # noqa
            code += '    w = w*kernel_scale + kernel_bias;\n'
            # code += '   w_sum += w;'
            code += '    r += c%d * w;\n' % (i + n)
        # code += '    return r/w_sum;\n'
        code += '    return r;\n'
        code += '}\n'
        code += "\n"
        code += 'vec4\n'
        code += '%s' % filter_2
        code += '(sampler2D texture, sampler2D kernel, float index, vec2 uv, vec2 pixel)\n'  # noqa
        code += '{\n'
        code += '    vec2 texel = uv/pixel - vec2(0.5, 0.5) ;\n'
        code += '    vec2 f = fract(texel);\n'
        code += '    texel = (texel-fract(texel) + vec2(0.001, 0.001)) * pixel;\n'  # noqa
        for i in range(2*n):
            code += '    vec4 t%d = %s(kernel, index, f.x,\n' % (i, filter_1)
            for j in range(2*n):
                x, y = (-n+1+j, -n+1+i)
                code += '        texture2D( texture, texel + vec2(%d, %d) * pixel),\n' % (x, y)  # noqa

            # Remove last trailing',' and close function call
            code = code[:-2] + ');\n'

        code += '    return %s(kernel, index, f.y, ' % filter_1
        for i in range(2*n):
            code += 't%d, ' % i

        # Remove last trailing',' and close function call
        code = code[:-2] + ');\n'
        code += '}\n'

        return code

    def call_code(self, index):
        code = ""
        n = int(math.ceil(self.radius))
        filter_1 = 'filter1D_radius%d' % n  # noqa
        filter_2 = 'filter2D_radius%d' % n

        code += 'vec4 %s(sampler2D texture, vec2 shape, vec2 uv)\n' % self.__class__.__name__  # noqa
        code += '{'
        code += ' return %s(texture, u_kernel, %f, uv, 1.0/shape); ' % (filter_2, index)  # noqa
        code += '}\n'
        return code


class Nearest(SpatialFilter):
    '''
    Nearest (=None) filter (radius = 0.5).

    Weight function::

      w(x) = 1

    '''

    def __init__(self):
        SpatialFilter.__init__(self, radius=.5)

    def weight(self, x):
        return 1.0

    def _get_code(self):
        self.build_LUT()
        code = 'vec4\n'
        code += 'interpolate(sampler2D texture, sampler1D kernel, vec2 uv, vec2 pixel)\n'  # noqa
        code += '{\n   return texture2D(texture, uv);\n}\n'
        return code
    code = property(_get_code, doc='''filter functions code''')


class Bilinear(SpatialFilter):
    '''
    Bilinear filter (radius = 1.0).

    Weight function::

      w(x) = 1 - x

    '''

    def __init__(self):
        SpatialFilter.__init__(self, radius=1.0)

    def weight(self, x):
        return 1.0 - x


class Hanning(SpatialFilter):
    '''
    Hanning filter (radius = 1.0).

    Weight function::

      w(x) = 0.5 + 0.5 * cos(pi * x)

    '''

    def __init__(self):
        SpatialFilter.__init__(self, radius=1.0)

    def weight(self, x):
        return 0.5 + 0.5 * math.cos(math.pi * x)


class Hamming(SpatialFilter):
    '''
    Hamming filter (radius = 1.0).

    Weight function::

      w(x) = 0.54 + 0.46 * cos(pi * x)

    '''

    def __init__(self):
        SpatialFilter.__init__(self, radius=1.0)

    def weight(self, x):
        return 0.54 + 0.46 * math.cos(math.pi * x)


class Hermite(SpatialFilter):
    ''' Hermite filter (radius = 1.0).

    Weight function::

      w(x) = (2*x-3)*x^2 + 1

    '''

    def __init__(self):
        SpatialFilter.__init__(self, radius=1.0)

    def weight(self, x):
        return (2.0 * x - 3.0) * x * x + 1.0


class Quadric(SpatialFilter):
    '''
    Quadric filter (radius = 1.5).

    Weight function::

             |  0.0 ≤ x < 0.5: 0.75 - x*x
      w(x) = |  0.5 ≤ x < 1.5: 0.5 - (x-1.5)^2
             |  1.5 ≤ x      : 0

    '''

    def __init__(self):
        SpatialFilter.__init__(self, radius=1.5)

    def weight(self, x):
        if x < 0.75:
            return 0.75 - x * x
        elif x < 1.5:
            t = x - 1.5
            return 0.5 * t * t
        else:
            return 0.0


class Bicubic(SpatialFilter):
    '''
    Bicubic filter (radius = 2.0).

    Weight function::

      w(x) = 1/6((x+2)^3 - 4*(x+1)^3 + 6*x^3 -4*(x-1)^3)
    '''

    def __init__(self):
        SpatialFilter.__init__(self, radius=2.0)

    def pow3(self, x):
        if x <= 0:
            return 0
        else:
            return x * x * x

    def weight(self, x):
        return (1.0/6.0) * (self.pow3(x + 2) -
                            4 * self.pow3(x + 1) +
                            6 * self.pow3(x) -
                            4 * self.pow3(x - 1))


class Kaiser(SpatialFilter):
    '''
    Kaiser filter (radius = 1.0).


    Weight function::

      w(x) = bessel_i0(a sqrt(1-x^2)* 1/bessel_i0(b)

    '''

    def __init__(self, b=6.33):
        self.a = b
        self.epsilon = 1e-12
        self.i0a = 1.0 / self.bessel_i0(b)
        SpatialFilter.__init__(self, radius=1.0)

    def bessel_i0(self, x):
        s = 1.0
        y = x * x / 4.0
        t = y
        i = 2
        while t > self.epsilon:
            s += t
            t *= float(y) / (i * i)
            i += 1
        return s

    def weight(self, x):
        if x > 1:
            return 0
        return self.bessel_i0(self.a * math.sqrt(1.0 - x * x)) * self.i0a


class CatRom(SpatialFilter):
    '''
    Catmull-Rom filter (radius = 2.0).

    Weight function::

             |  0 ≤ x < 1: 0.5*(2 + x^2*(-5+x*3))
      w(x) = |  1 ≤ x < 2: 0.5*(4 + x*(-8+x*(5-x)))
             |  2 ≤ x    : 0

    '''

    def __init__(self, size=256*8):
        SpatialFilter.__init__(self, radius=2.0)

    def weight(self, x):
        if x < 1.0:
            return 0.5 * (2.0 + x * x * (-5.0 + x * 3.0))
        elif x < 2.0:
            return 0.5 * (4.0 + x * (-8.0 + x * (5.0 - x)))
        else:
            return 0.0


class Mitchell(SpatialFilter):
    '''
    Mitchell-Netravali filter (radius = 2.0).

    Weight function::

             |  0 ≤ x < 1: p0 + x^2*(p2 + x*p3)
      w(x) = |  1 ≤ x < 2: q0 + x*(q1 + x*(q2 + x*q3))
             |  2 ≤ x    : 0

    '''

    def __init__(self, b=1.0/3.0, c=1.0/3.0):
        self.p0 = (6.0 - 2.0 * b) / 6.0
        self.p2 = (-18.0 + 12.0 * b + 6.0 * c) / 6.0
        self.p3 = (12.0 - 9.0 * b - 6.0 * c) / 6.0
        self.q0 = (8.0 * b + 24.0 * c) / 6.0
        self.q1 = (-12.0 * b - 48.0 * c) / 6.0
        self.q2 = (6.0 * b + 30.0 * c) / 6.0
        self.q3 = (-b - 6.0 * c) / 6.0
        SpatialFilter.__init__(self, radius=2.0)

    def weight(self, x):
        if x < 1.0:
            return self.p0 + x * x * (self.p2 + x * self.p3)
        elif x < 2.0:
            return self.q0 + x * (self.q1 + x * (self.q2 + x * self.q3))
        else:
            return 0.0


class Spline16(SpatialFilter):
    '''
    Spline16 filter (radius = 2.0).

    Weight function::

             |  0 ≤ x < 1: ((x-9/5)*x - 1/5)*x + 1
      w(x) = |
             |  1 ≤ x < 2: ((-1/3*(x-1) + 4/5)*(x-1) - 7/15 )*(x-1)

    '''

    def __init__(self):
        SpatialFilter.__init__(self, radius=2.0)

    def weight(self, x):
        if x < 1.0:
            return ((x - 9.0/5.0) * x - 1.0/5.0) * x + 1.0
        else:
            return ((-1.0/3.0 * (x-1) + 4.0/5.0) * (x-1) - 7.0/15.0) * (x-1)


class Spline36(SpatialFilter):
    '''
    Spline36 filter (radius = 3.0).

    Weight function::

             |  0 ≤ x < 1: ((13/11*x - 453/209)*x -3/209)*x +1
      w(x) = |  1 ≤ x < 2: ((-6/11*(x-1) - 270/209)*(x-1) -156/209)*(x-1)
             |  2 ≤ x < 3: (( 1/11*(x-2) - 45/209)*(x-2) + 26/209)*(x-2)
    '''

    def __init__(self):
        SpatialFilter.__init__(self, radius=3.0)

    def weight(self, x):
        if x < 1.0:
            return ((13.0/11.0 * x - 453.0/209.0) * x - 3.0/209.0) * x + 1.0
        elif x < 2.0:
            return ((-6.0/11.0 * (x-1) + 270.0/209.0) * (x-1) - 156.0 / 209.0) * (x-1)  # noqa
        else:
            return ((1.0 / 11.0 * (x-2) - 45.0/209.0) * (x - 2) + 26.0/209.0) * (x-2)  # noqa


class Gaussian(SpatialFilter):
    '''
    Gaussian filter (radius = 2.0).

    Weight function::

      w(x) = exp(-2x^2) * sqrt(2/pi)

    Note::

      This filter does not seem to be correct since:

        x = np.linspace(0, 1.0, 100 )
        f = weight
        z = f(x+1)+f(x)+f(1-x)+f(2-x)

        z should be 1 everywhere but it is not the case and it produces "grid
        effects".
    '''
    def __init__(self):
        SpatialFilter.__init__(self, radius=2.0)

    def weight(self, x):
        return math.exp(-2.0 * x * x) * math.sqrt(2.0 / math.pi)


class Bessel(SpatialFilter):
    '''
    Bessel filter (radius = 3.2383).
    '''

    def __init__(self):
        SpatialFilter.__init__(self, radius=3.2383)

    def besj(self, x, n):
        '''
        Function BESJ calculates Bessel function of first kind of order n
        Arguments:
            n - an integer (>=0), the order
            x - value at which the Bessel function is required
        --------------------
        C++ Mathematical Library
        Converted from equivalent FORTRAN library
        Converted by Gareth Walker for use by course 392 computational project
        All functions tested and yield the same results as the corresponding
        FORTRAN versions.

        If you have any problems using these functions please report them to
        M.Muldoon@UMIST.ac.uk

        Documentation available on the web
        http://www.ma.umist.ac.uk/mrm/Teaching/392/libs/392.html
        Version 1.0   8/98
        29 October, 1999
        --------------------
        Adapted for use in AGG library by
                    Andy Wilk (castor.vulgaris@gmail.com)
        Adapted for use in vispy library by
                    Nicolas P. Rougier (Nicolas.Rougier@inria.fr)
        -----------------------------------------------------------------------
        '''
        if n < 0:
            return 0.0

        d = 1e-6
        b = 0
        if math.fabs(x) <= d:
            if n != 0:
                return 0
            return 1

        b1 = 0  # b1 is the value from the previous iteration
        # Set up a starting order for recurrence
        m1 = int(math.fabs(x)) + 6
        if math.fabs(x) > 5:
            m1 = int(math.fabs(1.4 * x + 60 / x))

        m2 = int(n + 2 + math.fabs(x) / 4)
        if m1 > m2:
            m2 = m1

        # Apply recurrence down from curent max order
        while True:
            c3 = 0
            c2 = 1e-30
            c4 = 0
            m8 = 1
            if m2 / 2 * 2 == m2:
                m8 = -1

            imax = m2 - 2
            for i in range(1, imax+1):
                c6 = 2 * (m2 - i) * c2 / x - c3
                c3 = c2
                c2 = c6
                if m2 - i - 1 == n:
                    b = c6
                m8 = -1 * m8
                if m8 > 0:
                    c4 = c4 + 2 * c6

            c6 = 2 * c2 / x - c3
            if n == 0:
                b = c6
            c4 += c6
            b /= c4
            if math.fabs(b - b1) < d:
                return b
            b1 = b
            m2 += 3

    def weight(self, x):
        if x == 0.0:
            return math.pi/4.0
        else:
            return self.besj(math.pi * x, 1) / (2.0 * x)


class Sinc(SpatialFilter):
    '''
    Sinc filter (radius = 4.0).

    Weight function::


    '''

    def __init__(self, size=256, radius=4.0):
        SpatialFilter.__init__(self, radius=max(radius, 2.0))

    def weight(self, x):
        if x == 0.0:
            return 1.0
        x *= math.pi
        return (math.sin(x) / x)


class Lanczos(SpatialFilter):
    '''
    Lanczos filter (radius = 4.0).

    Weight function::


    '''

    def __init__(self, size=256, radius=4.0):
        SpatialFilter.__init__(self, radius=max(radius, 2.0))

    def weight(self, x):
        if x == 0.0:
            return 1.0
        elif x > self.radius:
            return 0.0
        x *= math.pi
        xr = x / self.radius
        return (math.sin(x) / x) * (math.sin(xr)/xr)


class Blackman(SpatialFilter):
    '''
    Blackman filter (radius = 4.0).
    '''

    def __init__(self, size=256, radius=4.0):
        SpatialFilter.__init__(self, radius=max(radius, 2.0))

    def weight(self, x):
        if x == 0.0:
            return 1.0
        elif x > self.radius:
            return 0.0
        x *= math.pi
        xr = x / self.radius
        return (math.sin(x) / x) * (0.42 + 0.5*math.cos(xr) + 0.08*math.cos(2*xr))  # noqa


# Generate kernels texture (16 x 1024)
filters = [Bilinear(), Hanning(),  Hamming(),  Hermite(),
           Kaiser(),   Quadric(),  Bicubic(),  CatRom(),
           Mitchell(), Spline16(), Spline36(), Gaussian(),
           Bessel(),   Sinc(),     Lanczos(),  Blackman()]

n = 1024
K = np.zeros((16, n))
for i, f in enumerate(filters):
    K[i] = f.kernel(n)

bias = K.min()
scale = K.max()-K.min()
K = (K-bias)/scale
np.save("spatial-filters.npy", K.astype(np.float32))

print("// ------------------------------------")
print("// Automatically generated, do not edit")
print("// ------------------------------------")
print("")
print("const float kernel_bias  = %f;" % bias)
print("const float kernel_scale = %f;" % scale)
print("const float kernel_size = %f;" % n)
print("const vec4 bits = vec4(1.0, 1.0/256.0, 1.0/(256.0*256.0), 1.0/(256.0*256.0*256.0));")  # noqa
print("uniform sampler2D u_kernel;")
print("")

code = 'float\n'
code += 'unpack_unit(vec4 rgba)\n'
code += '{\n'
code += '\t// return rgba.r;  // uncomment this for r32f debugging\n'
code += '\treturn dot(rgba, bits);\n'
code += '}\n'
print(code.expandtabs(4))

code = 'float\n'
code += 'unpack_ieee(vec4 rgba)\n'
code += '{\n'
code += '\t// return rgba.r;  // uncomment this for r32f debugging\n'
code += '\trgba.rgba = rgba.abgr * 255;\n'
code += '\tfloat sign = 1.0 - step(128.0,rgba[0])*2.0;\n'
code += '\tfloat exponent = 2.0 * mod(rgba[0],128.0) + ' \
        'step(128.0,rgba[1]) - 127.0;\n'
code += '\tfloat mantissa = mod(rgba[1],128.0)*65536.0 + rgba[2]*256.0 + ' \
        'rgba[3] + float(0x800000);\n'
code += '\treturn sign * exp2(exponent) * (mantissa * exp2(-23));\n'
code += '}\n'
print(code.expandtabs(4))

code = 'float\n'
code += 'unpack_interpolate(sampler2D kernel, vec2 uv)\n'
code += '{\n'
code += '\t// return texture2D(kernel, uv).r; ' \
        '//uncomment this for r32f debug without interpolation\n'
code += '\tfloat kpixel = 1/kernel_size;\n'
code += '\tfloat u = uv.x / kpixel;\n'
code += '\tfloat v = uv.y;\n'
code += '\tfloat uf = fract(u);\n'
code += '\tu = (u - uf) * kpixel;\n'
code += '\n'
code += '\tfloat d0 = unpack_unit(texture2D(kernel, vec2(u, v)));\n'
code += '\tfloat d1 = unpack_unit(texture2D(kernel, vec2(u + 1 * kpixel, v)));\n'  # noqa
code += '\treturn mix(d0, d1, uf);\n'
code += '}\n'
print(code.expandtabs(4))

F = SpatialFilter(1.0)
print(F.filter_code())
F = SpatialFilter(2.0)
print(F.filter_code())
F = SpatialFilter(3.0)
print(F.filter_code())
F = SpatialFilter(4.0)
print(F.filter_code())

# Generate filter functions
# Special case for nearest
print("""vec4 Nearest(sampler2D texture, vec2 shape, vec2 uv)""")
print("""{ return texture2D(texture,uv); }\n""")

for i, f in enumerate(filters):
    print(f.call_code((i+0.5)/16.0))
