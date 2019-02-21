#Copyright (c) 2009-2016 Nicolas P. Rougier. All rights reserved.
# Distributed under the (new) BSD License.
# -----------------------------------------------------------------------------
import numpy as np
from glumpy import app, gloo, gl, data
from glumpy.transforms import Trackball, Position

vertex = """
    attribute vec3 position;
    attribute vec3 texcoord;
    varying vec3 v_texcoord;
    void main()
    {
        gl_Position = <transform(position)> * vec4(-1,-1,1,1);
        v_texcoord = texcoord;
    }
"""

fragment = """
    uniform samplerCube texture;
    varying vec3 v_texcoord;
    void main()
    {
        gl_FragColor = textureCube(texture, v_texcoord);
    }
"""


window = app.Window(width=1024, height=1024)


@window.event
def on_draw(dt):
    window.clear()
    program.draw(gl.GL_TRIANGLES, indices)


@window.event
def on_init():
    gl.glEnable(gl.GL_DEPTH_TEST)


vertices = np.array([[+1, +1, +1], [-1, +1, +1], [-1, -1, +1], [+1, -1, +1],
                     [+1, -1, -1], [+1, +1, -1], [-1, +1, -1], [-1, -1, -1]])
texcoords = np.array([[+1, +1, +1], [-1, +1, +1], [-1, -1, +1], [+1, -1, +1],
                     [+1, -1, -1], [+1, +1, -1], [-1, +1, -1], [-1, -1, -1]])
faces = np.array([vertices[i] for i in [0, 1, 2, 3, 0, 3, 4, 5, 0, 5, 6, 1,
                                        6, 7, 2, 1, 7, 4, 3, 2, 4, 7, 6, 5]])
indices = np.resize(np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32), 36)
indices += np.repeat(4 * np.arange(6, dtype=np.uint32), 6)
indices = indices.view(gloo.IndexBuffer)
texture = np.zeros((6, 1024, 1024, 3), dtype=np.float32).view(gloo.TextureCube)
texture.interpolation = gl.GL_LINEAR
program = gloo.Program(vertex, fragment, count=24)
program['position'] = faces*10
program['texcoord'] = faces
program['texture'] = texture
program['transform'] = Trackball(Position(), distance=0)

texture[2] = data.get("sky-left.png")/255.
texture[3] = data.get("sky-right.png")/255.
texture[0] = data.get("sky-front.png")/255.
texture[1] = data.get("sky-back.png")/255.
texture[4] = data.get("sky-up.png")/255.
texture[5] = data.get("sky-down.png")/255.
window.attach(program["transform"])
app.run()
