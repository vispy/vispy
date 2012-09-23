import cube
import pyglet.graphics
from pyglet.gl import *

vertex_list = None

def create():
    global vertex_list
    vertex_list = pyglet.graphics.vertex_list(
        24,
        ('v3f/static', (cube.vertices) ),
        )

def draw( colour ):
    global vertex_list
    glColor4f( *colour )
    vertex_list.draw( GL_QUADS )

