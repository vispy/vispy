from vispy.oogl import Texture2D, VertexShader, FragmentShader, ShaderProgram
from vispy import app
import OpenGL.GL as gl
import OpenGL.GLU as glu
import numpy as np

im0 = np.zeros((100,100,3), 'float64')
im0[:50,:,0] = 1.0

im1 = np.zeros((100,100,3), 'float64')
im1[:50,:,0] = 1.0
im1[:,:50,1] = 1.0
im1[50:,50:,2] = 1.0

VERT_SHADER = """ // simple vertex shader
void main (void) {
    // Get position
    vec4 vertex = vec4(gl_Vertex);
    
    // Calculate vertex in eye coordinates
    //vertex = vec3(gl_ModelViewMatrix * vertex);
    
    // Pass tex coords
    gl_TexCoord[0] = gl_MultiTexCoord0;
    
    // Calculate projected position
    gl_Position = gl_ModelViewProjectionMatrix * vertex;
}
"""

FRAG_SHADER1 = """ // simples fragment shader
uniform sampler2D texture1;
vec4 get_color();

void main()
{    
    gl_FragColor = get_color() * texture2D(texture1, gl_TexCoord[0].st);
}

"""

FRAG_SHADER2 = """

uniform vec3 color;

vec4 get_color()
{    
    return vec4 (color.r, color.g, color.b, 1.0);
    //return vec4(0.0, 1.0, 0.0, 1.0);
}
"""


class Canvas(app.Canvas):
    
    def __init__(self):
        app.Canvas.__init__(self)
        
        # Create texture 0 (not used)
        self._texture0 = Texture2D()
        self._texture0.set_data(im0)
        
        # Create texture 1
        self._texture1 = Texture2D()
        self._texture1.set_data(im1)
        
        # Create program
        self._program = ShaderProgram(
                VertexShader(VERT_SHADER), 
                FragmentShader(FRAG_SHADER1),
                FragmentShader(FRAG_SHADER2)
                )
        
        # Set uniforms and samplers
        self._program.set_uniform('color', (0.5, 1.0, 0.5))
        self._program.set_uniform('texture1', self._texture1)
    
    
    def on_paint(self, event):
        # 
        # Set viewport and transformations
        gl.glViewport(0, 0, *self.geometry[2:])
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        glu.gluOrtho2D(0.0, 1.0, 0.0, 1.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        # Clear
        gl.glClearColor(1,1,1,1);
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        # Draw shape is a color
        gl.glColor(0.7, 0.0, 0.0)
        self.draw_shape(0,0)
        
        # Draw shape with texture, nested context
        gl.glColor(1.0, 1.0, 1.0)
        with self._texture0(0), self._texture1(1), self._program:
            self.draw_shape(0.5, 0.0)
            self.draw_shape(0.0, 0.5)
            
        # Draw shape again, the texture should not be shown
        gl.glColor(0.0, 0.4, 0.0)
        self.draw_shape(0.5,0.5)
        
        self._backend._vispy_swap_buffers()
    
    def draw_shape(self, x, y):
        # Draw simple shape
        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord(0,0); gl.glVertex(x+0,y+0); 
        gl.glTexCoord(0.1,0.8); gl.glVertex(x+0.1,y+0.3); 
        gl.glTexCoord(0.6,1); gl.glVertex(x+0.4,y+0.5); 
        gl.glTexCoord(1,0.1); gl.glVertex(x+0.5,y+0.2); 
        gl.glEnd()
c = Canvas()
c.show()

app.run()
