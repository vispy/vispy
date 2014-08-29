# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Marker Visual and shader definitions.
"""

import numpy as np

from ...color import Color
from ...gloo import set_state, VertexBuffer, _check_valid
from ..shaders import ModularProgram, Function, Variable
from .visual import Visual


vert = """
uniform mat4 u_projection;
uniform float u_antialias;

attribute vec3  a_position;
attribute vec4  a_fg_color;
attribute vec4  a_bg_color;
attribute float a_edgewidth;
attribute float a_size;

varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_edgewidth;
varying float v_antialias;

void main (void) {
    $v_size = a_size;
    v_edgewidth = a_edgewidth;
    v_antialias = u_antialias;
    v_fg_color  = a_fg_color;
    v_bg_color  = a_bg_color;
    gl_Position = $transform(vec4(a_position,1.0));
    gl_PointSize = $v_size + 2*(v_edgewidth + 1.5*v_antialias);
}
"""


frag = """
varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_edgewidth;
varying float v_antialias;

void main()
{
    float size = $v_size +2*(v_edgewidth + 1.5*v_antialias);
    float t = v_edgewidth/2.0-v_antialias;

    // The marker function needs to be linked with this shader
    float r = $marker(gl_PointCoord, size);

    float d = abs(r) - t;
    if( r > (v_edgewidth/2.0+v_antialias))
    {
        discard;
    }
    else if( d < 0.0 )
    {
       gl_FragColor = v_fg_color;
    }
    else
    {
        float alpha = d/v_antialias;
        alpha = exp(-alpha*alpha);
        if (r > 0)
            gl_FragColor = vec4(v_fg_color.rgb, alpha*v_fg_color.a);
        else
            gl_FragColor = mix(v_bg_color, v_fg_color, alpha);
    }
}
"""


disc = """
float disc(vec2 pointcoord, float size)
{
    float r = length((pointcoord.xy - vec2(0.5,0.5))*size);
    r -= $v_size/2;
    return r;
}
"""


arrow = """
float arrow(vec2 pointcoord, float size)
{
    float r1 = abs(pointcoord.x -.50)*size +
               abs(pointcoord.y -.5)*size - $v_size/2;
    float r2 = abs(pointcoord.x -.25)*size +
               abs(pointcoord.y -.5)*size - $v_size/2;
    float r = max(r1,-r2);
    return r;
}
"""


ring = """
float ring(vec2 pointcoord, float size)
{
    float r1 = length((pointcoord.xy - vec2(0.5,0.5))*size) - $v_size/2;
    float r2 = length((pointcoord.xy - vec2(0.5,0.5))*size) - $v_size/4;
    float r = max(r1,-r2);
    return r;
}
"""


clobber = """
float clobber(vec2 pointcoord, float size)
{
    const float PI = 3.14159265358979323846264;
    const float t1 = -PI/2;
    const vec2  c1 = 0.2*vec2(cos(t1),sin(t1));
    const float t2 = t1+2*PI/3;
    const vec2  c2 = 0.2*vec2(cos(t2),sin(t2));
    const float t3 = t2+2*PI/3;
    const vec2  c3 = 0.2*vec2(cos(t3),sin(t3));

    float r1 = length((pointcoord.xy- vec2(0.5,0.5) - c1)*size);
    r1 -= $v_size/3;
    float r2 = length((pointcoord.xy- vec2(0.5,0.5) - c2)*size);
    r2 -= $v_size/3;
    float r3 = length((pointcoord.xy- vec2(0.5,0.5) - c3)*size);
    r3 -= $v_size/3;
    float r = min(min(r1,r2),r3);
    return r;
}
"""


square = """
float square(vec2 pointcoord, float size)
{
    float r = max(abs(pointcoord.x -.5)*size, abs(pointcoord.y -.5)*size);
    r -= $v_size/2;
    return r;
}
"""


x_ = """
float x_(vec2 pointcoord, float size)
{
    vec2 rotcoord = vec2((pointcoord.x + pointcoord.y - 1.) / sqrt(2.),
                         (pointcoord.y - pointcoord.x) / sqrt(2.));
    float r1 = max(abs(rotcoord.x - 0.25)*size,
                   abs(rotcoord.x + 0.25)*size);
    float r2 = max(abs(rotcoord.y - 0.25)*size,
                   abs(rotcoord.y + 0.25)*size);
    float r3 = max(abs(rotcoord.x)*size,
                   abs(rotcoord.y)*size);
    float r = max(min(r1,r2),r3);
    r -= $v_size/2;
    return r;
}
"""


diamond = """
float diamond(vec2 pointcoord, float size)
{
    float r = abs(pointcoord.x -.5)*size + abs(pointcoord.y -.5)*size;
    r -= $v_size/2;
    return r;
}
"""


vbar = """
float vbar(vec2 pointcoord, float size)
{
    float r1 = max(abs(pointcoord.x - 0.75)*size,
                   abs(pointcoord.x - 0.25)*size);
    float r3 = max(abs(pointcoord.x - 0.50)*size,
                   abs(pointcoord.y - 0.50)*size);
    float r = max(r1,r3);
    r -= $v_size/2;
    return r;
}
"""


hbar = """
float hbar(vec2 pointcoord, float size)
{
    float r2 = max(abs(pointcoord.y - 0.75)*size,
                   abs(pointcoord.y - 0.25)*size);
    float r3 = max(abs(pointcoord.x - 0.50)*size,
                   abs(pointcoord.y - 0.50)*size);
    float r = max(r2,r3);
    r -= $v_size/2;
    return r;
}
"""


cross = """
float cross(vec2 pointcoord, float size)
{
    float r1 = max(abs(pointcoord.x - 0.75)*size,
                   abs(pointcoord.x - 0.25)*size);
    float r2 = max(abs(pointcoord.y - 0.75)*size,
                   abs(pointcoord.y - 0.25)*size);
    float r3 = max(abs(pointcoord.x - 0.50)*size,
                   abs(pointcoord.y - 0.50)*size);
    float r = max(min(r1,r2),r3);
    r -= $v_size/2;
    return r;
}
"""

tailed_arrow = """
float tailed_arrow(vec2 pointcoord, float size)
{
    //arrow_right
    float r1 = abs(pointcoord.x -.50)*size +
               abs(pointcoord.y -.5)*size - $v_size/2;
    float r2 = abs(pointcoord.x -.25)*size +
               abs(pointcoord.y -.5)*size - $v_size/2;
    float arrow = max(r1,-r2);

    //hbar
    float r3 = (abs(pointcoord.y-.5)*2+.3)*$v_size-$v_size/2;
    float r4 = (pointcoord.x -.775)*size;
    float r6 = abs(pointcoord.x -.5)*size-$v_size/2;
    float limit = (pointcoord.x -.5)*size +
                  abs(pointcoord.y -.5)*size - $v_size/2;
    float hbar = max(limit,max(max(r3,r4),r6));

    return min(arrow,hbar);
}
"""

_marker_dict = {
    'disc': disc,
    'arrow': arrow,
    'ring': ring,
    'clobber': clobber,
    'square': square,
    'diamond': diamond,
    'vbar': vbar,
    'hbar': hbar,
    'cross': cross,
    'tailed_arrow': tailed_arrow,
    'x': x_,
    # aliases
    'o': disc,
    '+': cross,
    's': square,
    '-': hbar,
    '|': vbar,
    '->': tailed_arrow,
    '>': arrow,
}
marker_types = tuple(sorted(list(_marker_dict.keys())))


class Markers(Visual):
    """ Visual displaying marker symbols. 
    """
    def __init__(self):
        self._program = ModularProgram(vert, frag)
        self._v_size_var = Variable('varying float v_size')
        self._program.vert['v_size'] = self._v_size_var
        self._program.frag['v_size'] = self._v_size_var
        Visual.__init__(self)

    def set_data(self, pos=None, style='o', size=10., edge_width=1.,
                 edge_color='black', face_color='white'):
        """ Set the data used to display this visual.
        
        Parameters
        ----------
        pos : array
            The array of locations to display each symbol.
        style : str
            The style of symbol to draw (see Notes).
        size : float
            The symbol size in px.
        edge_width : float
            The width of the symbol outline in px.
        edge_color : Color
            The color used to draw the symbol outline.
        face_color : Color
            The color used to draw the symbol interior.
            
        Notes
        -----
        
        Allowed style strings are: disc, arrow, ring, clobber, square, diamond,
        vbar, hbar, cross, tailed_arrow, and x.
        """
        assert (isinstance(pos, np.ndarray) and
                pos.ndim == 2 and pos.shape[1] in (2, 3))
        assert edge_width > 0
        self.set_style(style)
        edge_color = Color(edge_color).rgba
        face_color = Color(face_color).rgba
        n = len(pos)
        data = np.zeros(n, dtype=[('a_position', np.float32, 3),
                                  ('a_fg_color', np.float32, 4),
                                  ('a_bg_color', np.float32, 4),
                                  ('a_size', np.float32, 1),
                                  ('a_edgewidth', np.float32, 1)])
        data['a_fg_color'] = edge_color
        data['a_bg_color'] = face_color
        data['a_edgewidth'] = edge_width
        data['a_position'][:, :pos.shape[1]] = pos
        data['a_size'] = size
        self._vbo = VertexBuffer(data)

    def set_style(self, style='o'):
        _check_valid('style', style, marker_types)
        self._marker_fun = Function(_marker_dict[style])
        self._marker_fun['v_size'] = self._v_size_var
        self._program.frag['marker'] = self._marker_fun

    def draw(self, event=None):
        set_state(depth_test=False, blend=True, clear_color='white',
                  blend_func=('src_alpha', 'one_minus_src_alpha'))
        if event is not None:
            xform = event.render_transform.shader_map()
            self._program.vert['transform'] = xform
        self._program.prepare()
        self._program['u_antialias'] = 1
        self._program.bind(self._vbo)
        self._program.draw('points')
