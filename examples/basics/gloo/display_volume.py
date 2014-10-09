import numpy as np
from vispy import app, gloo
from vispy.util.transforms import perspective, translate, rotate

from vispy.gloo import gl

raw_data = np.load('walnut.npy')

data = np.zeros(raw_data.shape + (3,), np.float32)
data[:, :, :, 0] += (raw_data == 4)
data[:, :, :, 1] += (raw_data == 3)
data[:, :, :, 2] += (raw_data == 1) + (raw_data == 2)


cube_vert = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1],
    [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]], dtype=np.float32)
cube_ind = np.array([1, 5, 7, 7, 3, 1, 0, 2, 6, 6, 4, 0, 0, 1, 3, 3,
    2, 0, 7, 5, 4, 4, 6, 7, 2, 3, 7, 7, 6, 2, 1, 0, 4, 4, 5, 1], dtype=np.uint32)

CUBE_VERT_SHADER = """
// Uniforms
// ------------------------------------
uniform  mat4 u_model;
uniform  mat4 u_view;
uniform  mat4 u_projection;

// Attributes
// ------------------------------------
attribute vec3 a_position;

// Varying
// ------------------------------------
varying vec4 v_color;

void main()
{
    gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
    v_color.rgb = a_position;
}
"""

CUBE_FRAG_SHADER = """
// Varying
// ------------------------------------
varying vec4 v_color;

void main()
{
    gl_FragColor = v_color;
}
"""

W, H = 600, 600
rays_vert = np.array([[-W, -H], [W, -H], [-W, H], [W, H]], dtype=np.float32)

RAYS_VERT_SHADER = """
// Uniforms
// ------------------------------------
uniform  mat4 u_model;
uniform  mat4 u_view;
uniform  mat4 u_projection;

// Attributes
// ------------------------------------
attribute vec2 a_position;

// Varyings
// ------------------------------------
varying vec2 v_texcoord;

void main()
{
    gl_Position = u_projection * u_view * u_model * vec4(a_position, 0.0, 1.0);
    v_texcoord = ((gl_Position.xy/gl_Position.w) + 1.0) / 2.0;
}
"""

RAYS_FRAG_SHADER = """
// Uniforms
// ------------------------------------
uniform sampler3D u_data;
uniform sampler2D u_start;
uniform sampler2D u_stop;

// Varyings
// ------------------------------------
varying vec2 v_texcoord;

void main()
{
    vec4 start = texture2D(u_start, v_texcoord);
    if (start.r == 1.0 && start.g == 1.0 && start.b == 1.0)
    {
        gl_FragColor = vec4(1, 1, 1, 1);
    }
    else
    {
        vec4 stop = texture2D(u_stop, v_texcoord);

        vec3 step = stop.rgb - start.rgb; 
        float dist = length(step);
        step /= dist * 1000.0;

        float step_length = length(step);

        vec3 tex_coord = start.rgb;

        gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
        for (float x = 0.0; x < dist; x += step_length)
        {
            gl_FragColor += texture3D(u_data, tex_coord);

            tex_coord += step;
        }
        gl_FragColor /= 1000.0;
    }
        if (gl_FragColor.r == 0.0 && gl_FragColor.g == 0.0 && gl_FragColor.b == 0.0)
        {
            gl_FragColor = vec4(1, 1, 1, 1);
        }

}
"""


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, keys='interactive')
        self.size = W, H

        self.data_tex = gloo.Texture3D(data)
        self.data_tex.interpolation = 'nearest'
        self.data_tex.wrapping = 'clamp_to_edge'

        shape = self.size[1], self.size[0]

        self.start_tex = gloo.Texture2D(shape=(shape + (4,)), dtype=np.float32)
        self.start_frame_buf = gloo.FrameBuffer(self.start_tex)

        self.stop_tex = gloo.Texture2D(shape=(shape + (4,)), dtype=np.float32)
        self.stop_frame_buf = gloo.FrameBuffer(self.stop_tex)

        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)

        translate(self.view, -0.5, -0.5, -5)

        self.cube_ind_buf = gloo.IndexBuffer(cube_ind)

        self.cube_program = gloo.Program(CUBE_VERT_SHADER, CUBE_FRAG_SHADER)
        self.cube_program['a_position'] = gloo.VertexBuffer(cube_vert)
        self.cube_program['u_model'] = self.model
        self.cube_program['u_view'] = self.view
        self.cube_program['u_projection'] = self.projection

        self.rays_program = gloo.Program(RAYS_VERT_SHADER, RAYS_FRAG_SHADER)
        self.rays_program['a_position'] = gloo.VertexBuffer(rays_vert)
        self.rays_program['u_model'] = self.model
        self.rays_program['u_projection'] = self.projection
        self.rays_program['u_view'] = self.view
        self.rays_program['u_data'] = self.data_tex
        self.rays_program['u_start'] = self.start_tex
        self.rays_program['u_stop'] = self.stop_tex

    def on_initialize(self, event):
        gloo.set_clear_color('white')

    def on_resize(self, event):
        width, height = event.size
        gloo.set_viewport(0, 0, width, height)

        self.projection = perspective(45.0, width / float(height), 2.0, 10.0)
        self.cube_program['u_projection'] = self.projection
        self.rays_program['u_projection'] = self.projection

    def on_mouse_move(self, event):
       if event.is_dragging:
            prev = event.last_event.pos
            curr = event.pos

            if (event.button == 1):
                translate(self.view, (curr[0] - prev[0]) / 1000.0, -(curr[1] - prev[1]) / 1000.0, 0.0)
                self.cube_program['u_view'] = self.view
            elif (event.button == 2):
                rotate(self.model, curr[0] - prev[0], 0, 0, 1)
                rotate(self.model, curr[1] - prev[1], 0, 1, 0)
                self.cube_program['u_model'] = self.model
            self.update()

    def on_draw(self, event):
        gl.glEnable(gl.GL_CULL_FACE)

        with self.start_frame_buf:
            gloo.clear()

            gl.glCullFace(gl.GL_BACK)
            self.cube_program.draw('triangles', self.cube_ind_buf)

        with self.stop_frame_buf:
            gloo.clear()

            gl.glCullFace(gl.GL_FRONT)
            self.cube_program.draw('triangles', self.cube_ind_buf)

        gl.glDisable(gl.GL_CULL_FACE)

        gloo.clear()

        self.rays_program.draw('triangle_strip')

"""
    def on_draw(self, event):
        gl.glEnable(gl.GL_CULL_FACE)

        gloo.clear()

#        gl.glCullFace(gl.GL_FRONT)
        self.cube_program.draw('triangles', self.cube_ind_buf)
"""



if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
