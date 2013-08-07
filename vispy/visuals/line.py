from vispy.oogl import ShaderProgram, VertexShader, FragmentShader, VertexBuffer
import OpenGL.GL as gl
import vispy.shaders.transforms as transforms
import numpy as np
from .visual import Visual

XYPositionVertexShader = VertexShader("""
    // XY position vertex shader
    attribute vec2 in_position;
    uniform float in_z_position;
    
    vec4 global_position() {
        return vec4(in_position, in_z_position, 1);            
    }
""")

XYZPositionVertexShader = VertexShader("""
    // XYZ position vertex shader
    attribute vec3 in_position;
    
    vec4 global_position() {
        return vec4(in_position, 1);            
    }
""")

UniformColorVertexShader = VertexShader("""
    // Uniform color vertex shader
    uniform vec4 in_color;
    
    vec4 global_vertex_color(vec4 pos) {
        return in_color;
    }
""")

RGBColorVertexShader = VertexShader("""
    // RGB color vertex shader
    attribute vec3 in_color;
    uniform float in_alpha;
    
    vec4 global_vertex_color(vec4 pos) {
        return vec4(in_color, in_alpha);            
    }
""")

RGBAColorVertexShader = VertexShader("""
    // RGBA color vertex shader
    attribute vec4 in_color;
    
    vec4 global_vertex_color(vec4 pos) {
        return vec4(in_color);
    }
""")

NullColorFragmentShader = FragmentShader("""
    // Null color fragment shader
    vec4 global_fragment_color(vec4 vert_color, vec4 position) {
        return vert_color;
    }
""")

vertex_shader = """
// LineVisual main vertex shader

// Generic, pluggable shader architecture
// * declares global callbacks that may be redefined by linking different shaders together
// * avoids use of potentially expensive conditionals inside the program

#version 120

// returns current vertex position as vec4
vec4 global_position();

// prototype for the transformation to be customized
vec4 global_transform(vec4);

vec4 global_vertex_color(vec4);


varying vec4 vert_color;
varying vec4 position;
varying vec4 raw_position;

void main(void) 
{
    // All vertex shaders should implement this line to allow
    // customizable transformation.
    raw_position = global_position();
    position = global_transform(raw_position);
    gl_Position = position;
    vert_color = global_vertex_color(position);
}
"""

fragment_shader = """
// LineVisual main fragment shader
#version 120

// Returns fragment color given vertex color and position
// todo: might want access to view, document, and device coordinates here.
vec4 global_fragment_color(vec4, vec4);

varying vec4 vert_color;
varying vec4 position;
varying vec4 raw_position;

void main(void)
{
    gl_FragColor = global_fragment_color(vert_color, position);
}
"""
        
class LineVisual(Visual):
    def __init__(self, **kwds):
        Visual.__init__(self)
        self.set_gl_options({
            gl.GL_LINE_SMOOTH: True,
            gl.GL_BLEND: True,
            'glBlendFunc': (gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA),
            'glHint': (gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST),
            'glLineWidth': (1,),
            })
            
        self._opts = {
            'color': (1, 1, 1, 1),
            'width': 1,
            'mode': 'fast',   # maybe 'fast_update', 'fast_redraw', and 'quality' ?
            }
        #self._program = ShaderProgram(
                            #VertexShader(vertex_shader), 
                            #self._Visual__transform,
                            #FragmentShader(fragment_shader))
        self._program = None
        self.set_data(**kwds)
        
    def update(self):
        self._program = None
        
    def set_data(self, **kwds):
        """
        Keyword arguments:
        pos     (N, 2-3) array
        color   (3-4) or (N, 3-4) array
        width   scalar or (N,) array
        """
        self._opts.update(kwds)
        typ = [('pos', np.float32, self._opts['pos'].shape[-1])]
        if isinstance(self._opts['color'], np.ndarray):
            typ.append(('color', np.float32, self._opts['color'].shape[-1]))
        self._data = np.empty(self._opts['pos'].shape[:-1], typ)
        self._data['pos'] = self._opts['pos']
        if isinstance(self._opts['color'], np.ndarray):
            self._data['color'] = self._opts['color']
        
        self.vbo = VertexBuffer(data=self._data)

    def _generate_program(self):
        if self._opts['pos'].shape[-1] == 2:
            posShader = XYPositionVertexShader
        else:
            posShader = XYZPositionVertexShader
        
        if isinstance(self._opts['color'], tuple):
            colorShader = UniformColorVertexShader
        elif self._opts['color'].shape[-1] == 3:
            colorShader = RGBColorVertexShader
        else:
            colorShader = RGBAColorVertexShader
            
        self._program = ShaderProgram(
            VertexShader(vertex_shader), 
            self._Visual__transform,
            FragmentShader(fragment_shader),
            posShader,
            colorShader,
            NullColorFragmentShader,
            )
            
        
    def draw(self):
        Visual.draw(self)
        
        if self._program is None:
            self._generate_program()
        
        with self._program:
            self._program.attributes['in_position'] = self.vbo['pos']
            if self._opts['pos'].shape[-1] == 2:
                self._program.uniforms['in_z_position'] = 1.0

            if isinstance(self._opts['color'], tuple):
                self._program.uniforms['in_color'] = self._opts['color']
            elif self._opts['color'].shape[-1] == 3:
                self._program.uniforms['in_alpha'] = 1.0;
                self._program.attributes['in_color'] = self.vbo['color']
            else:
                self._program.attributes['in_color'] = self.vbo['color']
                
            gl.glDrawArrays(gl.GL_LINE_STRIP, 0, self._data.size)
        
        

