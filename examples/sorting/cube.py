'''
Created on 29/06/2011

@author: adam
'''

from pyglet.gl import *
from pyglet.graphics import Batch


batch = None

def initialise():
    global batch
    batch = Batch()

    batch.add(
        24,
        GL_QUADS,
        None,
        (
            'v3f/static',
            (
                 1.0, 1.0,-1.0,
                -1.0, 1.0,-1.0,
                -1.0, 1.0, 1.0,
                 1.0, 1.0, 1.0,
                
                 1.0,-1.0, 1.0,
                -1.0,-1.0, 1.0,
                -1.0,-1.0,-1.0,
                 1.0,-1.0,-1.0,
                
                 1.0, 1.0, 1.0,
                -1.0, 1.0, 1.0,
                -1.0,-1.0, 1.0,
                 1.0,-1.0, 1.0,
                
                 1.0,-1.0,-1.0,
                -1.0,-1.0,-1.0,
                -1.0, 1.0,-1.0,
                 1.0, 1.0,-1.0,
                
                -1.0, 1.0, 1.0,
                -1.0, 1.0,-1.0,
                -1.0,-1.0,-1.0,
                -1.0,-1.0, 1.0,
                
                 1.0, 1.0,-1.0,
                 1.0, 1.0, 1.0,
                 1.0,-1.0, 1.0,
                 1.0,-1.0,-1.0
                )
            )
        )

def render():
    global batch

    if batch == None:
        initialise()

    # enable back face culling
    glPushAttrib( GL_ALL_ATTRIB_BITS )
    glEnable( GL_CULL_FACE )
    glCullFace( GL_BACK )

    batch.draw()

    glPopAttrib()

