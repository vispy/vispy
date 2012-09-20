import pyglet.graphics
from pyglet.gl import *
import numpy

from pygly.shader import Shader

from ctypes import *


shader_source = {
    'vert': """
#version 150

in  vec3 in_position;
in  vec3 in_colour;
uniform mat4 model_view;
uniform mat4 projection;

out vec3 ex_colour;

void main(void) 
{
    gl_Position = projection * model_view * vec4(
        in_position,
        1.0
        );

    ex_colour = in_colour;
}
""",

    'frag': """
#version 150

// Video card drivers require this next line to function properly
precision highp float;

in vec3 ex_colour;
out vec4 fragColor;

void main(void) 
{
    //Set colour of each fragment to WHITE
    fragColor = vec4( ex_colour, 1.0 );
}
"""
    }

vao = None
vbo = None

vertices = numpy.array([
     1.0, 1.0,-1.0,
    -1.0, 1.0,-1.0,
     1.0, 1.0, 1.0,
    -1.0, 1.0,-1.0,
    -1.0, 1.0, 1.0,
     1.0, 1.0, 1.0,

     1.0,-1.0, 1.0,
    -1.0,-1.0, 1.0,
     1.0,-1.0,-1.0,
    -1.0,-1.0, 1.0,
    -1.0,-1.0,-1.0,
     1.0,-1.0,-1.0,

     1.0, 1.0, 1.0,
    -1.0, 1.0, 1.0,
     1.0,-1.0, 1.0,
    -1.0, 1.0, 1.0,
    -1.0,-1.0, 1.0,
     1.0,-1.0, 1.0,

     1.0,-1.0,-1.0,
    -1.0,-1.0,-1.0,
     1.0, 1.0,-1.0,
    -1.0,-1.0,-1.0,
    -1.0, 1.0,-1.0,
     1.0, 1.0,-1.0,

    -1.0, 1.0, 1.0,
    -1.0, 1.0,-1.0,
    -1.0,-1.0, 1.0,
    -1.0, 1.0,-1.0,
    -1.0,-1.0,-1.0,
    -1.0,-1.0, 1.0,

     1.0, 1.0,-1.0,
     1.0, 1.0, 1.0,
     1.0,-1.0,-1.0,
     1.0, 1.0, 1.0,
     1.0,-1.0, 1.0,
     1.0,-1.0,-1.0,
     ],
     dtype = 'float32'
     )

colours = numpy.array([
    # green
    0.0, 1.0, 0.0,
    0.0, 1.0, 0.0,
    0.0, 1.0, 0.0,
    0.0, 1.0, 0.0,
    0.0, 1.0, 0.0,
    0.0, 1.0, 0.0,
    # orange
    1.0, 0.5, 0.0,
    1.0, 0.5, 0.0,
    1.0, 0.5, 0.0,
    1.0, 0.5, 0.0,
    1.0, 0.5, 0.0,
    1.0, 0.5, 0.0,
    # blue
    0.0, 0.0, 1.0,
    0.0, 0.0, 1.0,
    0.0, 0.0, 1.0,
    0.0, 0.0, 1.0,
    0.0, 0.0, 1.0,
    0.0, 0.0, 1.0,
    # violet
    1.0, 0.0, 1.0,
    1.0, 0.0, 1.0,
    1.0, 0.0, 1.0,
    1.0, 0.0, 1.0,
    1.0, 0.0, 1.0,
    1.0, 0.0, 1.0,
    # yellow
    1.0, 1.0, 0.0,
    1.0, 1.0, 0.0,
    1.0, 1.0, 0.0,
    1.0, 1.0, 0.0,
    1.0, 1.0, 0.0,
    1.0, 1.0, 0.0,
    # red
    1.0, 0.0, 0.0,
    1.0, 0.0, 0.0,
    1.0, 0.0, 0.0,
    1.0, 0.0, 0.0,
    1.0, 0.0, 0.0,
    1.0, 0.0, 0.0,
    ],
    dtype = 'float32'
    )


def create():
    global vao
    global vbo
    global vertices
    global colours
    global shader
    global shader_source

    shader = Shader(
        vert = shader_source['vert'],
        frag = shader_source['frag']
        )

    vao = (GLuint)()
    glGenVertexArrays( 1, vao )

    vbo = (GLuint * 2)()
    glGenBuffers( 2, vbo )

    # bind our vertex array
    glBindVertexArray( vao )

    # load our vertex positions
    # this will be attribute 0
    glBindBuffer( GL_ARRAY_BUFFER, vbo[ 0 ] )
    glBufferData(
        GL_ARRAY_BUFFER,
        vertices.nbytes,
        (GLfloat * vertices.size)(*vertices),
        GL_STATIC_DRAW
        )
    glVertexAttribPointer( 0, 3, GL_FLOAT, GL_FALSE, 0, 0)
    glEnableVertexAttribArray( 0 )

    # load our vertex colours
    # this will be attribute 1
    glBindBuffer( GL_ARRAY_BUFFER, vbo[ 1 ] )
    glBufferData(
        GL_ARRAY_BUFFER,
        colours.nbytes,
        (GLfloat * colours.size)(*colours),
        GL_STATIC_DRAW
        )
    glVertexAttribPointer( 1, 3, GL_FLOAT, GL_FALSE, 0, 0)
    glEnableVertexAttribArray( 1 )

    # unbind our buffers
    glBindVertexArray( 0 )

    # update our shader
    shader.attribute( 0, 'in_position' )
    shader.attribute( 1, 'in_colour' )
    shader.frag_location( 'fragColor' )

    # link the shader now
    shader.link()

def draw( projection, model_view ):
    global vao
    global vertices
    global shader

    shader.bind()
    shader.uniform_matrixf( 'model_view', model_view.flat )
    shader.uniform_matrixf( 'projection', projection.flat )

    glBindVertexArray( vao )

    glDrawArrays( GL_TRIANGLES, 0, vertices.size / 3 )

    glBindVertexArray( 0 )
    shader.unbind()

