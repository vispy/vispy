import numpy as np
import math
from vispy import app, gloo
from vispy.gloo import gl
from vispy.io import read_png, load_data_file
from vispy.util.transforms import perspective


def lookAt(eye, target):
    """Computes matrix to put camera looking at look point."""
    eye = np.asarray(eye).astype(np.float32)
    target = np.asarray(target).astype(np.float32)

    up = np.asarray([0, 0, 1]).astype(np.float32)

    vforward = eye - target
    vforward /= np.linalg.norm(vforward)
    vright = np.cross(up, vforward)
    vright /= np.linalg.norm(vright)
    vup = np.cross(vforward, vright)

    view = np.r_[vright, -np.dot(vright, eye),
                 vup, -np.dot(vup, eye),
                 vforward, -np.dot(vforward, eye),
                 [0, 0, 0, 1]].reshape(4, 4, order='F')

    return view


def getView(angle, distance):
    eye = np.array([math.cos(angle), math.sin(angle), 1]) * distance
    origin = [0, 0, 0]
    return lookAt(eye, origin)


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
faces = np.array([vertices[i] for i in [0, 1, 2, 3, 0, 3, 4, 5, 0, 5, 6, 1,
                                        6, 7, 2, 1, 7, 4, 3, 2, 4, 7, 6, 5]])
indices = np.resize(np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32), 36)
indices += np.repeat(4 * np.arange(6, dtype=np.uint32), 6)

texture = np.zeros((6, 1024, 1024, 3), dtype=np.float32)
texture[2] = read_png(load_data_file("skybox/sky-left.png"))/255.
texture[3] = read_png(load_data_file("skybox/sky-right.png"))/255.
texture[0] = read_png(load_data_file("skybox/sky-front.png"))/255.
texture[1] = read_png(load_data_file("skybox/sky-back.png"))/255.
texture[4] = read_png(load_data_file("skybox/sky-up.png"))/255.
texture[5] = read_png(load_data_file("skybox/sky-down.png"))/255.


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, size=(1024, 1024), keys='interactive')
        self.program = gloo.Program(vertex_shader, fragment_shader, count=24)
        self.program['a_position'] = faces*10
        self.program['a_texcoord'] = faces
        self.program.bind(gloo.VertexBuffer(faces))
        self.program['texture'] = gloo.TextureCube(texture, interpolation='linear')

        self.angle = 0
        self.distance = 25
        self.view = getView(self.angle, self.distance)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)

        self.program['u_model'] = self.model
        self.program['u_view'] = self.view
        gloo.set_viewport(0, 0, *self.physical_size)
        self.projection = perspective(60.0, self.size[0] /
                                      float(self.size[1]), 1.0, 100.0)
        self.program['u_projection'] = self.projection

        gl.glEnable(gl.GL_DEPTH_TEST)
        gloo.set_clear_color('black')
        self.show()

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)
        self.program.draw(gl.GL_TRIANGLES, gloo.IndexBuffer(indices))

    def on_mouse_wheel(self, event):
        deltaDistance = event.delta[1]
        self.distance = self.distance - deltaDistance
        if self.distance < 1.0:
            self.distance = 1.0
        if self.distance > 40.0:
            self.distance = 40.0
        self.program['u_view'] = getView(self.angle, self.distance)
        self.update()

    def on_mouse_press(self, event):
        self.mousex = event.pos[0]

    def on_mouse_release(self, event):
        deltaX = event.pos[0]-self.mousex
        deltaAngle = deltaX * (2*math.pi) / self.size[0]
        self.angle = (self.angle - deltaAngle/10.0) % (2*math.pi)
        self.program['u_view'] = getView(self.angle, self.distance)
        self.update()


if __name__ == '__main__':
    c = Canvas()
    app.run()
