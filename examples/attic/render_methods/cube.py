'''
Created on 29/06/2011

@author: adam
'''

from pyglet.gl import *
from pyglet.graphics import Batch


def render_triangles():
    glBegin( GL_QUADS )
    glVertex3f( 1.0, 1.0,-1.0 )
    glVertex3f(-1.0, 1.0,-1.0 )
    glVertex3f(-1.0, 1.0, 1.0 )
    glVertex3f( 1.0, 1.0, 1.0 )

    glVertex3f( 1.0,-1.0, 1.0 )
    glVertex3f(-1.0,-1.0, 1.0 )
    glVertex3f(-1.0,-1.0,-1.0 )
    glVertex3f( 1.0,-1.0,-1.0 )

    glVertex3f( 1.0, 1.0, 1.0 )
    glVertex3f(-1.0, 1.0, 1.0 )
    glVertex3f(-1.0,-1.0, 1.0 )
    glVertex3f( 1.0,-1.0, 1.0 )

    glVertex3f( 1.0,-1.0,-1.0 )
    glVertex3f(-1.0,-1.0,-1.0 )
    glVertex3f(-1.0, 1.0,-1.0 )
    glVertex3f( 1.0, 1.0,-1.0 )

    glVertex3f(-1.0, 1.0, 1.0 )
    glVertex3f(-1.0, 1.0,-1.0 )
    glVertex3f(-1.0,-1.0,-1.0 )
    glVertex3f(-1.0,-1.0, 1.0 )

    glVertex3f( 1.0, 1.0,-1.0 )
    glVertex3f( 1.0, 1.0, 1.0 )
    glVertex3f( 1.0,-1.0, 1.0 )
    glVertex3f( 1.0,-1.0,-1.0 )
    glEnd()

def render_immediate_mode():
    # enable back face culling
    glPushAttrib( GL_ALL_ATTRIB_BITS )
    glEnable( GL_CULL_FACE )
    glCullFace( GL_BACK )

    render_triangles()

    glPopAttrib()

display_list = None

def initialise_display_list():
    global display_list
    display_list = glGenLists( 1 );
    glNewList( display_list, GL_COMPILE )

    render_triangles()

    glEndList()

def render_display_list():
    global display_list
    glCallList( display_list )

batch = None

def initialise_batch():
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

def render_batch():
    global batch

    if batch == None:
        initialise()

    # enable back face culling
    glPushAttrib( GL_ALL_ATTRIB_BITS )
    glEnable( GL_CULL_FACE )
    glCullFace( GL_BACK )

    batch.draw()

    glPopAttrib()

