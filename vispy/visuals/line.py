from vispy.oogl import ShaderProgram, VertexShader, FragmentShader, VertexBuffer, Texture2D
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


#def b2f(f):
    #b = np.array([f], dtype=np.float32).view(np.uint8)
    #print b
    #s = float(1 - 2 * (b[3] >> 7))
    #e = float(((b[3]&127) << 1) | ((b[2]&128) >> 7)) - 127
    #p = float(b[0] + 256 * b[1] + 65536 * (b[2] & 127))
    #f = s * ((p*1.1920928955078125e-07)+1) * 2**e
    #if f > 5.1e38:
        #return np.nan
    #if f < -5.1e38:
        #return -np.nan
    #return f

XYTexPositionVertexShader = VertexShader("""
    #extension GL_ARB_shader_bit_encoding : enable
    
    // XY position vertex shader using texture and attribute index
    // single-precision float positions are represented as 4-byte RGBA 
    uniform sampler2D in_position;
    uniform int in_position_size;
    
    vec4 read_position(int vert_index) {
        float v_index_clipped = max(0., min(float(in_position_size), float(vert_index)));
        float index = v_index_clipped / float(in_position_size - 1);
        vec4 xv = texture2D(in_position, vec2(0, index));
        vec4 yv = texture2D(in_position, vec2(1, index));
        xv = (xv + 0.002) * 255.;
        yv = (yv + 0.002) * 255.;
        int xi = int(xv.r) + (int(xv.g) * 256) + (int(xv.b) * 65536) + (int(xv.a) * 16777216);
        int yi = int(yv.r) + (int(yv.g) * 256) + (int(yv.b) * 65536) + (int(yv.a) * 16777216);
        float x = intBitsToFloat(xi);
        float y = intBitsToFloat(yi);
        return vec4(x, y, 0.0, 1.0);
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

line_vertex_shader = VertexShader("""
// LineVisual main vertex shader (LINE_STRIP version)

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
""")

line_fragment_shader = FragmentShader("""
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
""")


tri_vertex_shader = VertexShader("""
// LineVisual main vertex shader (TRIANGLE_STRIP version)

// Generic, pluggable shader architecture
// * declares global callbacks that may be redefined by linking different shaders together
// * avoids use of potentially expensive conditionals inside the program

#version 120

// returns vertex position at index as vec4
vec4 read_position(int);

// prototype for the transformation to be customized
vec4 global_transform(vec4);

vec4 global_vertex_color(vec4);

attribute float in_index; // current vertex index

varying vec4 vert_color;
varying vec4 position;
varying vec4 raw_position;

vec2 intersection(vec2 a0, vec2 a1, vec2 b0, vec2 b1) {
    vec2 a = a1 - a0;
    vec2 b = b1 - b0;
    float den = (b.x * a.y - b.y * a.x);
    if (abs(den) > 1e-10) {
        float n = ((b0.y - a0.y) * a.x - (b0.x - a0.x) * a.y) / den;
        return b0 + n * b;
    }
    else {
        return a1;
    }
}

void main(void) 
{
    // All vertex shaders should implement this line to allow
    // customizable transformation.
    //raw_position = global_position();
    
    int v_index = int((in_index+0.5) / 2.0);
    int v_side = int(mod((in_index+0.5), 2.0));
    
    // 3 vertexes in data (raw) coordinate system
    vec4 rpos0 = read_position(v_index-1);
    vec4 rpos1 = read_position(v_index);
    vec4 rpos2 = read_position(v_index+1);
    
    // 3 vertexes in screen coordinate system
    vec4 pos0 = global_transform(rpos0);
    vec4 pos1 = global_transform(rpos1);
    vec4 pos2 = global_transform(rpos2);
    
    // Direction to offset from line segment
    float dir = 1. - (v_side * 2.);
    float width = 5.0 * dir / 800;  // TODO: 800 does not belong here
    
    // Vectors orthogonal to line segments
    vec2 l1 = pos1.xy - pos0.xy;
    vec2 l2 = pos2.xy - pos1.xy;
    vec2 l1_ortho = normalize(vec2(l1.y, -l1.x));
    vec2 l2_ortho = normalize(vec2(l2.y, -l2.x));
    
    // vertexes of offset line segments
    vec2 p0a = pos0.xy + l1_ortho * width;
    vec2 p1a = pos1.xy + l1_ortho * width;
    vec2 p1b = pos1.xy + l2_ortho * width;
    vec2 p2b = pos2.xy + l2_ortho * width;
    
    // Intersection
    vec2 i = intersection(p0a, p1a, p1b, p2b);
    position = vec4(i.x, i.y, pos1.z, 1);
    //position = vec4(pos1.x, pos1.y+width, pos1.z, 1);
    
    gl_Position = position;
    vert_color = global_vertex_color(position);
}
""")

tri_fragment_shader = FragmentShader("""
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
""")
        
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
        #tex = np.zeros((len(self._data), 1, 3), dtype=np.float32)
        #tex[...,:2] = self._data['pos'][:,np.newaxis]
        
        # recast float to RGBA bytes
        d = self._data['pos'].astype(np.float32).view(np.ubyte).reshape(len(self._data), 2, 4)
        self.ptex = Texture2D(d)
        self.ptex.set_filter(gl.GL_NEAREST, gl.GL_NEAREST)
        
        self.indexes = VertexBuffer(data=np.arange(len(self._data)*2, dtype=np.float32))

    def _generate_program(self):
        if self._opts['mode'] == 'fast':
            main_vshader = line_vertex_shader
            main_fshader = line_fragment_shader
            if self._opts['pos'].shape[-1] == 2:
                posShader = XYPositionVertexShader
            else:
                posShader = XYZPositionVertexShader
        else:
            main_vshader = tri_vertex_shader
            main_fshader = tri_fragment_shader
            posShader = XYTexPositionVertexShader
        
        if isinstance(self._opts['color'], tuple):
            colorShader = UniformColorVertexShader
        elif self._opts['color'].shape[-1] == 3:
            colorShader = RGBColorVertexShader
        else:
            colorShader = RGBAColorVertexShader
            
        self._program = ShaderProgram(
            main_vshader, 
            self.transform_chain(),
            main_fshader,
            posShader,
            colorShader,
            NullColorFragmentShader,
            )
            
        #self._program._feedback_vars = ['position']
            
        
    def draw(self):
        Visual.draw(self)
        
        if self._program is None:
            self._generate_program()
        
        with self._program:
            if self._opts['mode'] == 'fast':
                self._program.attributes['in_position'] = self.vbo['pos']
                if self._opts['pos'].shape[-1] == 2:
                    self._program.uniforms['in_z_position'] = 1.0
            else:
                self._program.attributes['in_index'] = self.indexes
                self._program.uniforms['in_position'] = self.ptex
                self._program.uniforms['in_position_size'] = len(self._data)

            if isinstance(self._opts['color'], tuple):
                self._program.uniforms['in_color'] = self._opts['color']
            elif self._opts['color'].shape[-1] == 3:
                self._program.uniforms['in_alpha'] = 1.0;
                self._program.attributes['in_color'] = self.vbo['color']
            else:
                self._program.attributes['in_color'] = self.vbo['color']
                
            if self._opts['mode'] == 'fast':
                #gl.glDrawArrays(gl.GL_LINE_STRIP, 0, self._data.size)
                self._program.draw_arrays(gl.GL_LINE_STRIP)
            else:
                self._program.draw_arrays(gl.GL_TRIANGLE_STRIP)
                
            
            fb = np.zeros((len(self._data), 4), dtype=np.float32)
            #self._program.feedback_arrays(fb, gl.GL_LINE_STRIP)
        
        

