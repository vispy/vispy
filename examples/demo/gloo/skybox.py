import numpy as np
from vispy import app, gloo
from vispy.gloo import gl
from vispy.io import read_png
from vispy.util.transforms import perspective, translate, rotate

vertex_shader = """
attribute vec3 a_position;
attribute vec3 a_texcoord;
varying vec3 v_texcoord;
uniform   mat4 u_model;
uniform   mat4 u_view;
uniform   mat4 u_projection;

void main()
{
    v_texcoord = a_texcoord;
    gl_Position = u_projection * u_view * u_model * vec4(a_position, 1.0);
}
"""

fragment_shader = """
uniform samplerCube texture;
varying vec3 v_texcoord;

void main()
{
    gl_FragColor = textureCube(texture, v_texcoord);
}
"""

vertices = np.array([[+1, +1, +1], [-1, +1, +1], [-1, -1, +1], [+1, -1, +1],
                     [+1, -1, -1], [+1, +1, -1], [-1, +1, -1], [-1, -1, -1]]).astype(np.float32)
texcoords = np.array([[+1, +1, +1], [-1, +1, +1], [-1, -1, +1], [+1, -1, +1],
                     [+1, -1, -1], [+1, +1, -1], [-1, +1, -1], [-1, -1, -1]]).astype(np.float32)
faces = np.array([vertices[i] for i in [0, 1, 2, 3, 0, 3, 4, 5, 0, 5, 6, 1,
                                        6, 7, 2, 1, 7, 4, 3, 2, 4, 7, 6, 5]])
indices = np.resize(np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32), 36)
indices += np.repeat(4 * np.arange(6, dtype=np.uint32), 6)

texture = np.zeros((6, 1024, 1024, 3), dtype=np.float32)
texture[2] = read_png("sky-left.png")/255.
texture[3] = read_png("sky-right.png")/255.
texture[0] = read_png("sky-front.png")/255.
texture[1] = read_png("sky-back.png")/255.
texture[4] = read_png("sky-up.png")/255.
texture[5] = read_png("sky-down.png")/255.


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, size=(1024, 1024), keys='interactive')
        self.program = gloo.Program(vertex_shader, fragment_shader, count=24)
        self.program['a_position'] = faces*10
        self.program['a_texcoord'] = faces
        self.program.bind(gloo.VertexBuffer(faces))
        self.program['texture'] = gloo.TextureCube(texture, interpolation='linear')

        self.default_view = np.array([[8.00000012e-01, 2.00000003e-01, -4.79999989e-01, 0.00000000e+00],
                                      [-5.00000000e-01, 3.00000012e-01, -7.79999971e-01, 0.00000000e+00],
                                      [-9.99999978e-03, 8.99999976e-01, -3.00000012e-01, 0.00000000e+00],
                                      [-3.00000000e-01, -2.15000000e+01, -4.76000001e+01, 1.00000000e+00]],
                                     dtype=np.float32)
        self.view = self.default_view
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)

        self.translate = [0, 0, 0]
        self.rotate = [0, 0, 0]

        self.program['u_model'] = self.model
        self.program['u_view'] = self.view

        gl.glEnable(gl.GL_DEPTH_TEST)
        gloo.set_clear_color('black')
        self.show()
        print("canvas.init()")

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)
        self.program.draw(gl.GL_TRIANGLES, gloo.IndexBuffer(indices))

    def on_key_press(self, event):
        """Controls -
        q(Q) - move left
        d(D) - move right
        z(Z) - move up
        s(S) - move down
        j/J - rotate about x-axis cw/anti-cw
        k/K - rotate about y-axis cw/anti-cw
        l/L - rotate about z-axis cw/anti-cw
        space - reset view
        p(P) - print current view
        """
        self.translate = [0, 0, 0]
        self.rotate = [0, 0, 0]

        if(event.text == 'p' or event.text == 'P'):
            print(self.view)
        elif(event.text == 'd' or event.text == 'D'):
            self.translate[0] = 0.3
        elif(event.text == 'q' or event.text == 'Q'):
            self.translate[0] = -0.3
        elif(event.text == 'z' or event.text == 'Z'):
            self.translate[1] = 0.3
        elif(event.text == 's' or event.text == 'S'):
            self.translate[1] = -0.3
        elif(event.text == 'j'):
            self.rotate = [1, 0, 0]
        elif(event.text == 'J'):
            self.rotate = [-1, 0, 0]
        elif(event.text == 'k'):
            self.rotate = [0, 1, 0]
        elif(event.text == 'K'):
            self.rotate = [0, -1, 0]
        elif(event.text == 'l'):
            self.rotate = [0, 0, 1]
        elif(event.text == 'L'):
            self.rotate = [0, 0, -1]
        elif(event.text == ' '):
            self.view = self.default_view

        self.view = self.view.dot(
            translate(-np.array(self.translate)).dot(
                rotate(self.rotate[0], (1, 0, 0)).dot(
                    rotate(self.rotate[1], (0, 1, 0)).dot(
                        rotate(self.rotate[2], (0, 0, 1))))))
        self.program['u_view'] = self.view
        self.update()

    def on_resize(self, event):
        self.activate_zoom()

    def activate_zoom(self):
        gloo.set_viewport(0, 0, *self.physical_size)
        self.projection = perspective(60.0, self.size[0] /
                                      float(self.size[1]), 1.0, 100.0)
        self.program['u_projection'] = self.projection

if __name__ == '__main__':
    c = Canvas()
    app.run()
