from vispy import gloo
from vispy import app
from vispy.gloo import gl
import numpy as np

VERT_SHADER = """
attribute vec3  a_position;
attribute vec3  a_color;
attribute float a_size;

uniform float u_line_width;

uniform vec2 u_pan;
uniform vec2 u_zoom;

varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_radius;
varying float v_linewidth;
varying float v_antialias;

void main (void) {
    v_radius = a_size;
    v_linewidth = u_line_width;
    v_antialias = 1.0;
    v_fg_color  = vec4(0.0,0.0,0.0,1.0);
    v_bg_color  = vec4(a_color,    1.0);

    gl_Position = vec4(u_zoom * (a_position.xy + u_pan), a_position.z, 1.0);
    gl_PointSize = 2.0*(v_radius + v_linewidth + 1.5*v_antialias);
}
"""

FRAG_SHADER = """
varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_radius;
varying float v_linewidth;
varying float v_antialias;
void main()
{    
    float size = 2*(v_radius + v_linewidth + 1.5*v_antialias);
    float t = v_linewidth/2.0-v_antialias;
    float r = length((gl_PointCoord.xy - vec2(0.5,0.5))*size);
    float d = abs(r - v_radius) - t;
    if( d < 0.0 )
        gl_FragColor = v_fg_color;
    else
    {
        float alpha = d/v_antialias;
        alpha = exp(-alpha*alpha);
        if (r > v_radius)
            gl_FragColor = vec4(v_fg_color.rgb, alpha*v_fg_color.a);
        else
            gl_FragColor = mix(v_bg_color, v_fg_color, alpha);
    }
}
"""

class DiscCollection(object):
    def __init__(self):
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        
        self._vbo_position = gloo.VertexBuffer('2f4')
        self._vbo_color = gloo.VertexBuffer('3f4')
        self._vbo_size = gloo.VertexBuffer('f4')
        
        self.program['a_position'] = self._vbo_position
        self.program['a_color'] = self._vbo_color
        self.program['a_size'] = self._vbo_size
        self.program['u_line_width'] = 1.0
        self.program['u_zoom'] = (1.0, 1.0)
        self.program['u_pan'] = (0., 0.)
        
    @property
    def line_width(self):
        return
        
    @line_width.setter
    def line_width(self, value):
        self.program['u_line_width'] = value

        
        
    @property
    def position(self):
        return
    @position.setter
    def position(self, value):
        self._vbo_position.set_data(value)

        
        
    @property
    def color(self):
        return
    @color.setter
    def color(self, value):
        self._vbo_color.set_data(value)

        
        
    @property
    def size(self):
        return
    @size.setter
    def size(self, value):
        self._vbo_size.set_data(value)
    
    
    
    def draw(self):
        self.program.draw(gl.GL_POINTS)
