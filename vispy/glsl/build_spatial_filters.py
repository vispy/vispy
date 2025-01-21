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
"""
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
  - Linear (radius 1)
  - Hanning (radius 1)
  - Hamming (radius 1)
  - Hermite (radius 1)
  - Kaiser (radius 1)
  - Quadric (radius 1.5)
  - Cubic (radius 2)
  - CatRom (radius 2)
  - Mitchell (radius 2)
  - Spline16 (radius 2)
  - Spline36 (radius 4)
  - Gaussian (radius 2)
  - Bessel (radius 3.2383)
  - Sinc (radius 4)
  - Lanczos (radius 4)
  - Blackman (radius 4)


Note::

  Weights code has been translated from the antigrain geometry library
  available at http://www.antigrain.com/
"""


import math
import numpy as np
from inspect import cleandoc
from itertools import product


class SpatialFilter:
    def __init__(self, radius=1):
        self.radius = math.ceil(radius)

    def weight(self, x):
        """
        Return filter weight for a distance x.

        :Parameters:
            ``x`` : 0 < float < ceil(self.radius)
                Distance to be used to compute weight.
        """
        raise NotImplementedError

    def kernel(self, size=4 * 512):
        samples = int(size / self.radius)
        n = size  # r*samples
        kernel = np.zeros(n)
        X = np.linspace(0, self.radius, n)
        for i in range(n):
            kernel[i] = self.weight(X[i])
        N = np.zeros(samples)
        for i in range(self.radius):
            N += kernel[::+1][i * samples:(i + 1) * samples]
            N += kernel[::-1][i * samples:(i + 1) * samples]
        for i in range(self.radius):
            kernel[i * samples:(i + 1) * samples] /= N
        return kernel

    def call_code(self, index):
        code = cleandoc(f'''
            vec4 {self.__class__.__name__}2D(sampler2D texture, vec2 shape, vec2 uv) {{
                return filter2D_radius{self.radius}(texture, u_kernel, {index}, uv, 1 / shape);
            }}

            vec4 {self.__class__.__name__}3D(sampler3D texture, vec3 shape, vec3 uv) {{
                return filter3D_radius{self.radius}(texture, u_kernel, {index}, uv, 1 / shape);
            }}
        ''')

        return code


class Linear(SpatialFilter):
    """
    Linear filter (radius = 1).

    Weight function::

      w(x) = 1 - x

    """

    def weight(self, x):
        return 1 - x


class Hanning(SpatialFilter):
    """
    Hanning filter (radius = 1).

    Weight function::

      w(x) = 0.5 + 0.5 * cos(pi * x)

    """

    def weight(self, x):
        return 0.5 + 0.5 * math.cos(math.pi * x)


class Hamming(SpatialFilter):
    """
    Hamming filter (radius = 1).

    Weight function::

      w(x) = 0.54 + 0.46 * cos(pi * x)

    """

    def weight(self, x):
        return 0.54 + 0.46 * math.cos(math.pi * x)


class Hermite(SpatialFilter):
    """Hermite filter (radius = 1).

    Weight function::

      w(x) = (2*x-3)*x^2 + 1

    """

    def weight(self, x):
        return (2 * x - 3) * x**2 + 1


class Quadric(SpatialFilter):
    """
    Quadric filter (radius = 1.5).

    Weight function::

             |  0 ≤ x < 0.5: 0.75 - x*x
      w(x) = |  0.5 ≤ x < 1.5: 0.5 - (x-1.5)^2
             |  1.5 ≤ x      : 0

    """

    def __init__(self):
        super().__init__(radius=1.5)

    def weight(self, x):
        if x < 0.75:
            return 0.75 - x**2
        elif x < 1.5:
            t = x - 1.5
            return 0.5 * t**2
        return 0


class Cubic(SpatialFilter):
    """
    Cubic filter (radius = 2).

    Weight function::

      w(x) = 1/6((x+2)^3 - 4*(x+1)^3 + 6*x^3 -4*(x-1)^3)
    """

    def __init__(self):
        super().__init__(radius=2)

    def weight(self, x):
        return (1 / 6) * (
            (x + 2)**3
            - 4 * (x + 1)**3
            + 6 * x**3
            - 4 * (x - 1)**3
        )


class Kaiser(SpatialFilter):
    """
    Kaiser filter (radius = 1).


    Weight function::

      w(x) = bessel_i0(a sqrt(1-x^2)* 1/bessel_i0(b)

    """

    def __init__(self, b=6.33):
        self.a = b
        self.epsilon = 1e-12
        self.i0a = 1 / self.bessel_i0(b)
        super().__init__(radius=1)

    def bessel_i0(self, x):
        s = 1
        y = x**2 / 4
        t = y
        i = 2
        while t > self.epsilon:
            s += t
            t *= float(y) / i**2
            i += 1
        return s

    def weight(self, x):
        if x > 1:
            return 0
        return self.bessel_i0(self.a * math.sqrt(1 - x**2)) * self.i0a


class CatRom(SpatialFilter):
    """
    Catmull-Rom filter (radius = 2).

    Weight function::

             |  0 ≤ x < 1: 0.5*(2 + x^2*(-5+x*3))
      w(x) = |  1 ≤ x < 2: 0.5*(4 + x*(-8+x*(5-x)))
             |  2 ≤ x    : 0

    """

    def __init__(self):
        super().__init__(radius=2)

    def weight(self, x):
        if x < 1:
            return 0.5 * (2 + x**2 * (-5 + x * 3))
        elif x < 2:
            return 0.5 * (4 + x * (-8 + x * (5 - x)))
        else:
            return 0


class Mitchell(SpatialFilter):
    """
    Mitchell-Netravali filter (radius = 2).

    Weight function::

             |  0 ≤ x < 1: p0 + x^2*(p2 + x*p3)
      w(x) = |  1 ≤ x < 2: q0 + x*(q1 + x*(q2 + x*q3))
             |  2 ≤ x    : 0

    """

    def __init__(self, b=1/3, c=1/3):
        self.p0 = (6 - 2 * b) / 6
        self.p2 = (-18 + 12 * b + 6 * c) / 6
        self.p3 = (12 - 9 * b - 6 * c) / 6
        self.q0 = (8 * b + 24 * c) / 6
        self.q1 = (-12 * b - 48 * c) / 6
        self.q2 = (6 * b + 30 * c) / 6
        self.q3 = (-b - 6 * c) / 6
        super().__init__(radius=2)

    def weight(self, x):
        if x < 1:
            return self.p0 + x**2 * (self.p2 + x * self.p3)
        elif x < 2:
            return self.q0 + x * (self.q1 + x * (self.q2 + x * self.q3))
        else:
            return 0


class Spline16(SpatialFilter):
    """
    Spline16 filter (radius = 2).

    Weight function::

             |  0 ≤ x < 1: ((x-9/5)*x - 1/5)*x + 1
      w(x) = |
             |  1 ≤ x < 2: ((-1/3*(x-1) + 4/5)*(x-1) - 7/15 )*(x-1)

    """

    def __init__(self):
        super().__init__(radius=2)

    def weight(self, x):
        if x < 1:
            return ((x - 9/5) * x - 1/5) * x + 1
        else:
            return ((-1/3 * (x - 1) + 4/5) * (x - 1) - 7/15) * (x - 1)


class Spline36(SpatialFilter):
    """
    Spline36 filter (radius = 3).

    Weight function::

             |  0 ≤ x < 1: ((13/11*x - 453/209)*x -3/209)*x +1
      w(x) = |  1 ≤ x < 2: ((-6/11*(x-1) - 270/209)*(x-1) -156/209)*(x-1)
             |  2 ≤ x < 3: (( 1/11*(x-2) - 45/209)*(x-2) + 26/209)*(x-2)
    """

    def __init__(self):
        super().__init__(radius=3)

    def weight(self, x):
        if x < 1:
            return ((13/11 * x - 453/209) * x - 3/209) * x + 1
        elif x < 2:
            return ((-6/11 * (x - 1) + 270/209) * (x - 1) - 156 / 209) * (x - 1)
        else:
            return ((1/11 * (x - 2) - 45/209) * (x - 2) + 26/209) * (x - 2)


class Gaussian(SpatialFilter):
    """
    Gaussian filter (radius = 2).

    Weight function::

      w(x) = exp(-2x^2) * sqrt(2/pi)

    Note::

      This filter does not seem to be correct since:

        x = np.linspace(0, 1, 100 )
        f = weight
        z = f(x+1)+f(x)+f(1-x)+f(2-x)

        z should be 1 everywhere but it is not the case and it produces "grid
        effects".
    """

    def __init__(self):
        super().__init__(radius=2)

    def weight(self, x):
        return math.exp(-2 * x**2) * math.sqrt(2 / math.pi)


class Bessel(SpatialFilter):
    """Bessel filter (radius = 3.2383)."""

    def __init__(self):
        super().__init__(radius=3.2383)

    def besj(self, x, n):
        """Function BESJ calculates Bessel function of first kind of order n.

        Parameters
        ----------
        x: int
            value at which the Bessel function is required
        n : int
            an integer (>=0), the order

        Notes
        -----
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

        Adapted for use in AGG library by
                    Andy Wilk (castor.vulgaris@gmail.com)
        Adapted for use in vispy library by
                    Nicolas P. Rougier (Nicolas.Rougier@inria.fr)

        """
        if n < 0:
            return 0
        x = float(x)  # force float type

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

        # Apply recurrence down from current max order
        while True:
            c3 = 0
            c2 = 1e-30
            c4 = 0
            m8 = 1
            if m2 // 2 * 2 == m2:
                m8 = -1

            imax = m2 - 2
            for i in range(1, imax + 1):
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
        if x == 0:
            return math.pi / 4
        else:
            return self.besj(math.pi * x, 1) / (2 * x)


class Sinc(SpatialFilter):
    """Sinc filter (radius = 4)."""

    def __init__(self):
        super().__init__(radius=4)

    def weight(self, x):
        if x == 0:
            return 1
        x *= math.pi
        return (math.sin(x) / x)


class Lanczos(SpatialFilter):
    """Lanczos filter (radius = 4)."""

    def __init__(self):
        super().__init__(radius=4)

    def weight(self, x):
        if x == 0:
            return 1
        elif x > self.radius:
            return 0
        x *= math.pi
        xr = x / self.radius
        return (math.sin(x) / x) * (math.sin(xr) / xr)


class Blackman(SpatialFilter):
    """Blackman filter (radius = 4)."""

    def __init__(self):
        super().__init__(radius=4)

    def weight(self, x):
        if x == 0:
            return 1
        elif x > self.radius:
            return 0
        x *= math.pi
        xr = x / self.radius
        return (math.sin(x) / x) * (0.42 + 0.5 * math.cos(xr) + 0.08 * math.cos(2 * xr))


def generate_filter_code(radius):
    n = int(math.ceil(radius))

    nl = '\n'  # cannot use backslash in fstring
    code = cleandoc(f'''
    vec4 filter1D_radius{n}(sampler2D kernel, float index, float x{''.join(f', vec4 c{i}' for i in range(n * 2))}) {{
        float w, w_sum = 0;
        vec4 r = vec4(0);
        {''.join(f"""
        w = unpack_interpolate(kernel, vec2({1 - (i + 1) / n} + (x / {n}), index));
        w = w * kernel_scale + kernel_bias;
        r += c{i} * w;
        w = unpack_interpolate(kernel, vec2({(i + 1) / n} - (x / {n}), index));
        w = w * kernel_scale + kernel_bias;
        r += c{i + n} * w;"""
        for i in range(n))}
        return r;
    }}

    vec4 filter2D_radius{n}(sampler2D texture, sampler2D kernel, float index, vec2 uv, vec2 pixel) {{
        vec2 texel = uv / pixel - vec2(0.5);
        vec2 f = fract(texel);
        texel = (texel - fract(texel) + vec2(0.001)) * pixel;
        {''.join(f"""
        vec4 t{i} = filter1D_radius{n}(kernel, index, f.x{f''.join(
            f',{nl}            texture2D(texture, texel + vec2({-n + 1 + j}, {-n + 1 + i}) * pixel)'
            for j in range(n * 2))});"""
        for i in range(n * 2))}
        return filter1D_radius{n}(kernel, index, f.y{''.join(f', t{i}' for i in range(2*n))});
    }}

    vec4 filter3D_radius{n}(sampler3D texture, sampler2D kernel, float index, vec3 uv, vec3 pixel) {{
        vec3 texel = uv / pixel - vec3(0.5);
        vec3 f = fract(texel);
        texel = (texel - fract(texel) + vec3(0.001)) * pixel;
        {''.join(f"""
        vec4 t{i}{j} = filter1D_radius{n}(kernel, index, f.x{f''.join(
            f',{nl}            texture3D(texture, texel + vec3({-n + 1 + k}, {-n + 1 + j}, {-n + 1 + i}) * pixel)'
            for k in range(n * 2))});"""
        for i, j in product(range(n * 2), range(n * 2)))}
        {f''.join(f"""
        vec4 t{i} = filter1D_radius{n}(kernel, index, f.y{"".join(
            f", t{i}{j}" for j in range(n * 2))});"""
        for i in range(n * 2))}
        return filter1D_radius{n}(kernel, index, f.z{''.join(f', t{i}' for i in range(2*n))});
    }}
    ''')

    return code


def main():
    # Generate kernels texture (16 x 1024)
    filters = [Linear(), Hanning(), Hamming(), Hermite(), Kaiser(), Quadric(),
               Cubic(), CatRom(), Mitchell(), Spline16(), Spline36(), Gaussian(),
               Bessel(), Sinc(), Lanczos(), Blackman()]

    n = 1024
    K = np.zeros((len(filters), n))
    for i, f in enumerate(filters):
        K[i] = f.kernel(n)

    bias = K.min()
    scale = K.max() - K.min()
    K = (K - bias) / scale
    np.save("spatial-filters.npy", K.astype(np.float32))

    code = cleandoc(f'''
        // ------------------------------------
        // Automatically generated, do not edit
        // ------------------------------------
        const float kernel_bias  = {bias};
        const float kernel_scale = {scale};
        const float kernel_size = {n};
        const vec4 bits = vec4(1, {1 / 256}, {1 / (256 * 256)}, {1 / (256 * 256 * 256)});
        uniform sampler2D u_kernel;
    ''')

    # add basic unpack functions
    code += '\n\n' + cleandoc('''
        float unpack_unit(vec4 rgba) {
            // return rgba.r;  // uncomment this for r32f debugging
            return dot(rgba, bits);
        }

        float unpack_ieee(vec4 rgba) {
            // return rgba.r;  // uncomment this for r32f debugging
            rgba.rgba = rgba.abgr * 255;
            float sign = 1 - step(128 , rgba[0]) * 2;
            float exponent = 2 * mod(rgba[0] , 128) + step(128 , rgba[1]) - 127;
            float mantissa = mod(rgba[1] , 128) * 65536 + rgba[2] * 256 + rgba[3] + float(0x800000);
            return sign * exp2(exponent) * (mantissa * exp2(-23.));
        }


        float unpack_interpolate(sampler2D kernel, vec2 uv) {
            // return texture2D(kernel, uv).r;  //uncomment this for r32f debug without interpolation
            float kpixel = 1. / kernel_size;
            float u = uv.x / kpixel;
            float v = uv.y;
            float uf = fract(u);
            u = (u - uf) * kpixel;
            float d0 = unpack_unit(texture2D(kernel, vec2(u, v)));
            float d1 = unpack_unit(texture2D(kernel, vec2(u + 1. * kpixel, v)));
            return mix(d0, d1, uf);
        }
    ''')

    # add 1d, 2d and 3d filter code
    for radius in range(4):
        code += '\n\n' + generate_filter_code(radius + 1)

    # add call functions for 2D and 3D filters
    # special case for nearest
    code += '\n\n' + cleandoc('''
        vec4 Nearest2D(sampler2D texture, vec2 shape, vec2 uv) {
            return texture2D(texture, uv);
        }

        vec4 Nearest3D(sampler3D texture, vec3 shape, vec3 uv) {
            return texture3D(texture, uv);
        }
    ''')

    for i, f in enumerate(filters):
        code += '\n\n' + f.call_code((i + 0.5) / 16)

    print(code)


if __name__ == "__main__":
    import sys
    sys.exit(main())
