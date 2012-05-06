'''
Created on 03/03/2012

@author: adam
'''

from pyglet.gl import *

grid_dl = None

def initialise_grid():
    global grid_dl

    if grid_dl == None:
        grid_dl = generate_grid_display_list( (10, 10), (20, 20) )

def render_grid():
    global grid_dl

    # render the display list
    glCallList( grid_dl )

def generate_grid_display_list( cell_size, num_cells ):
    grid_dl = glGenLists( 1 );
    glNewList( grid_dl, GL_COMPILE )

    # disable the lighting
    glDisable( GL_LIGHTING )

    # TODO: use glPointParameter to automatically scale points
    # http://www.opengl.org/sdk/docs/man/xhtml/glPointParameter.xml
    glLineWidth( 1.0 )

    glBegin( GL_LINES )
    draw_grid( cell_size, num_cells )
    glEnd()

    glEndList()
    return grid_dl

def draw_grid( cell_size, num_cells ):
    # draw a white grid
    glColor3f( 1.0, 1.0, 1.0 )

    half_size = (
        (num_cells[ 0 ] / 2) * cell_size[ 0 ],
        (num_cells[ 1 ] / 2) * cell_size[ 1 ]
        )
    # draw our depth lines
    for x in xrange( num_cells[ 0 ] + 1 ):
        x_pos = float( -half_size[ 0 ] + (x * cell_size[ 0 ]) )

        glVertex3f( x_pos, 0.0, -half_size[ 1 ] )
        glVertex3f( x_pos, 0.0, +half_size[ 1 ] )

    # draw our width lines
    for z in xrange( num_cells[ 1 ] + 1 ):
        z_pos = float( -half_size[ 1 ] + (z * cell_size[ 1 ]) )

        glVertex3f( -half_size[ 1 ], 0.0, z_pos )
        glVertex3f( +half_size[ 1 ], 0.0, z_pos )

