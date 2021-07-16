# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from .base_filter import Filter
from ..shaders import Function, Varying
from ...color import colormap, Color


class IsolineFilter(Filter):
    FRAG_SHADER = """
        void isoline() {
            if ($isolevel <= 0. || $isowidth <= 0.) {
                return;
            }

            // function taken from glumpy/examples/isocurves.py
            // and extended to have level, width, color and antialiasing
            // as parameters

            // Extract data value
            // this accounts for perception,
            // have to decide, which one to use or make this a uniform
            const vec3 w = vec3(0.299, 0.587, 0.114);
            //const vec3 w = vec3(0.2126, 0.7152, 0.0722);
            float value = dot(gl_FragColor.rgb, w);

            // setup lw, aa
            float linewidth = $isowidth + $antialias;

            // "middle" contour(s) dividing upper and lower half
            // but only if isolevel is even
            if( mod($isolevel,2.0) == 0.0 ) {
                if( length(value - 0.5) < 0.5 / $isolevel)
                    linewidth = linewidth * 2;
            }

            // Trace contour isoline
            float v  = $isolevel * value - 0.5;
            float dv = linewidth/2.0 * fwidth(v);
            float f = abs(fract(v) - 0.5);
            float d = smoothstep(-dv, +dv, f);
            float t = linewidth/2.0 - $antialias;
            d = abs(d)*linewidth/2.0 - t;

            if( d < - linewidth ) {
                d = 1.0;
            } else  {
                 d /= $antialias;
            }

            // setup foreground
            vec4 fc = $isocolor;

            // mix with background
            if (d < 1.) {
                gl_FragColor = mix(gl_FragColor, fc, 1-d);
            }

        }
    """

    def __init__(self, level=2., width=2.0, antialias=1.0, color='black', **kwargs):
        super(IsolineFilter, self).__init__(fcode=self.FRAG_SHADER, **kwargs)

        self.level = level
        self.width = width
        self.color = color
        self.antialias = antialias

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, lev):
        if lev <= 0:
            lev = 0
        self._level = lev
        self.fshader['isolevel'] = float(lev)

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, w):
        self._width = w
        self.fshader['isowidth'] = float(w)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, c):
        self._color = c
        self.fshader['isocolor'] = Color(c).rgba

    @property
    def antialias(self):
        return self._antialias

    @antialias.setter
    def antialias(self, a):
        self._antialias = a
        self.fshader['antialias'] = float(a)


class Alpha(Filter):
    FRAG_SHADER = """
        void apply_alpha() {
            gl_FragColor.a = gl_FragColor.a * $alpha;
        }
    """

    def __init__(self, alpha=1.0, **kwargs):
        super(Alpha, self).__init__(fcode=self.FRAG_SHADER, **kwargs)

        self.alpha = alpha

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, a):
        self._alpha = a
        self.fshader['alpha'] = float(a)


class ColorFilter(Filter):
    FRAG_SHADER = """
        void apply_color_filter() {
            gl_FragColor = gl_FragColor * $filter;
        }
    """

    def __init__(self, filter=(1., 1., 1., 1.), fpos=8, **kwargs):
        super(ColorFilter, self).__init__(fcode=self.FRAG_SHADER, fpos=fpos, **kwargs)

        self.filter = filter

    @property
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, f):
        self._filter = tuple(f)
        self.fshader['filter'] = self._filter


class ZColormapFilter(Filter):
    FRAG_SHADER = """
        void z_colormap_support() {
            $zval = $position.z;
        }
    """
    VERT_SHADER = """
        void apply_z_colormap() {
            gl_FragColor = $cmap(($zval - $zrange.x) /
                                 ($zrange.y - $zrange.x));
        }
    """

    def __init__(self, cmap, zrange=(0., 1.), fpos=3, vpos=9, **kwargs):
        super(ZColormapFilter, self).__init__(fcode=self.FRAG_SHADER, fpos=fpos,
                                              vcode=self.VERT_SHADER, vpos=vpos, **kwargs)

        if isinstance(cmap, str):
            cmap = colormap.get_colormap(cmap)
        self.cmap = Function(cmap.glsl_map)
        self.fshader['cmap'] = self.cmap
        self.fshader['zrange'] = zrange
        self.vshader['zval'] = Varying('v_zval', dtype='float')
        self.fshader['zval'] = self.vshader['zval']

    def _attach(self, visual):
        super(ZColormapFilter, self)._attach(visual)
        self.vshader['position'] = visual.shared_program.vert['position']
