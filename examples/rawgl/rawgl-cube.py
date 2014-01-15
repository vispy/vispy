#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This example is equivalent to the spinning cube example,
but does not use vispy.gloo, but the raw GL API.

Show spinning cube using VBO's, transforms and textures.
The use of vertex and element buffer can be turned on or off.

"""

import numpy as np
from vispy.util.transforms import perspective, translate, rotate
from vispy import app, dataio
from vispy.gloo import gl


VERT_CODE = """
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

attribute vec3 a_position;
attribute vec2 a_texcoord;

varying vec2 v_texcoord;

void main()
{
    v_texcoord = a_texcoord;
    gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
}
"""


FRAG_CODE = """
uniform sampler2D u_texture;
varying vec2 v_texcoord;
void main()
{
    float ty = v_texcoord.y;
    float tx = sin(ty*20.0)*0.05 + v_texcoord.x;
    gl_FragColor = texture2D(u_texture, vec2(tx, ty));
}
"""


# Read cube data (replace 'cube.obj' with 'teapot.obj'
positions, faces, normals, texcoords = dataio.read_mesh('cube.obj')
colors = np.random.uniform(0, 1, positions.shape).astype('float32')


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self)
        self.size = 400, 400
        self.init_transforms()

        self.timer = app.Timer(1.0 / 60)
        self.timer.connect(self.update_transforms)
        self.timer.start()

    def on_initialize(self, event):
        gl.glClearColor(1, 1, 1, 1)
        gl.glEnable(gl.GL_DEPTH_TEST)

        # Create shader program
        self._prog_handle = gl.glCreateProgram()

        # Create vertex shader
        shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(shader, VERT_CODE)
        gl.glCompileShader(shader)
        status = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
        if not status:
            # We could show more useful info here, but that takes a few lines
            raise RuntimeError('Vertex shader did not compile.')
        else:
            gl.glAttachShader(self._prog_handle, shader)

        # Create fragment shader
        shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(shader, FRAG_CODE)
        gl.glCompileShader(shader)
        status = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
        if not status:
            # We could show more useful info here, but that takes a few lines
            raise RuntimeError('Fragment shader did not compile.')
        else:
            gl.glAttachShader(self._prog_handle, shader)

        # Link
        gl.glLinkProgram(self._prog_handle)
        status = gl.glGetProgramiv(self._prog_handle, gl.GL_LINK_STATUS)
        if not status:
            # We could show more useful info here, but that takes a few lines
            raise RuntimeError('Program did not link.')

        # Create texture
        im = dataio.crate()
        self._tex_handle = gl.glGenTextures(1)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._tex_handle)
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D,
            0,
            gl.GL_RGB,
            im.shape[1],
            im.shape[0],
            0,
            gl.GL_RGB,
            gl.GL_UNSIGNED_BYTE,
            im)
        gl.glTexParameter(
            gl.GL_TEXTURE_2D,
            gl.GL_TEXTURE_MIN_FILTER,
            gl.GL_LINEAR)
        gl.glTexParameter(
            gl.GL_TEXTURE_2D,
            gl.GL_TEXTURE_MAG_FILTER,
            gl.GL_LINEAR)

        if use_buffers:
            # Create vertex buffer
            self._positions_handle = gl.glGenBuffers(1)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._positions_handle)
            gl.glBufferData(
                gl.GL_ARRAY_BUFFER,
                positions.nbytes,
                positions,
                gl.GL_DYNAMIC_DRAW)
            #
            self._texcoords_handle = gl.glGenBuffers(1)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._texcoords_handle)
            gl.glBufferData(
                gl.GL_ARRAY_BUFFER,
                texcoords.nbytes,
                texcoords,
                gl.GL_DYNAMIC_DRAW)

            # Create buffer for faces
            self._faces_handle = gl.glGenBuffers(1)
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self._faces_handle)
            gl.glBufferData(
                gl.GL_ELEMENT_ARRAY_BUFFER,
                faces.nbytes,
                faces,
                gl.GL_DYNAMIC_DRAW)

    def on_resize(self, event):
        w, h = event.size
        gl.glViewport(0, 0, w, h)
        self.projection = perspective(45.0, w / float(h), 2.0, 10.0)

    def on_paint(self, event):

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Activate program  and texture
        gl.glUseProgram(self._prog_handle)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._tex_handle)

        # Set attributes (again, the loc can be cached)
        loc = gl.glGetAttribLocation(
            self._prog_handle,
            'a_position'.encode('utf-8'))
        gl.glEnableVertexAttribArray(loc)
        if use_buffers:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._positions_handle)
            gl.glVertexAttribPointer(loc, 3, gl.GL_FLOAT, False, 0, None)
        else:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)  # 0 means do not use buffer
            gl.glVertexAttribPointer(loc, 3, gl.GL_FLOAT, False, 0, positions)
        #
        loc = gl.glGetAttribLocation(
            self._prog_handle,
            'a_texcoord'.encode('utf-8'))
        gl.glEnableVertexAttribArray(loc)
        if use_buffers:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._texcoords_handle)
            gl.glVertexAttribPointer(loc, 2, gl.GL_FLOAT, False, 0, None)
        else:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)  # 0 means do not use buffer
            gl.glVertexAttribPointer(loc, 2, gl.GL_FLOAT, False, 0, texcoords)

        # Set uniforms (note that you could cache the locations)
        loc = gl.glGetUniformLocation(
            self._prog_handle,
            'u_view'.encode('utf-8'))
        gl.glUniformMatrix4fv(loc, 1, False, self.view)
        loc = gl.glGetUniformLocation(
            self._prog_handle,
            'u_model'.encode('utf-8'))
        gl.glUniformMatrix4fv(loc, 1, False, self.model)
        loc = gl.glGetUniformLocation(
            self._prog_handle,
            'u_projection'.encode('utf-8'))
        gl.glUniformMatrix4fv(loc, 1, False, self.projection)

        # Draw
        if use_buffers:
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self._faces_handle)
            gl.glDrawElements(
                gl.GL_TRIANGLES,
                faces.size,
                gl.GL_UNSIGNED_INT,
                None)
        else:
            gl.glDrawElements(
                gl.GL_TRIANGLES,
                faces.size,
                gl.GL_UNSIGNED_INT,
                faces)

    def init_transforms(self):
        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)

        self.theta = 0
        self.phi = 0

        translate(self.view, 0, 0, -5)

    def update_transforms(self, event):
        self.theta += .5
        self.phi += .5
        self.model = np.eye(4, dtype=np.float32)
        rotate(self.model, self.theta, 0, 0, 1)
        rotate(self.model, self.phi, 0, 1, 0)

        self.update()


if __name__ == '__main__':
    use_buffers = False

    c = Canvas()
    c.show()
    app.run()
