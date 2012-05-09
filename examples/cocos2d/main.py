#
# PyGLy code
#

import math

from pygly.projection_view_matrix import ProjectionViewMatrix
from pygly.scene_node import SceneNode
from pygly.render_callback_node import RenderCallbackNode
from pygly.camera_node import CameraNode
from pygly.cocos2d.layer import Layer as PyGLyLayer

import examples.render_callbacks.grid as grid

pygly_layer = None
pygly_node = SceneNode( '/root' )
pygly_camera = None

def setup_pygly_scene():
    global pygly_node
    global pygly_camera
    global pygly_layer

    # this must be done after the
    # director is initialised or the
    # program will crash since the window
    # won't have been created
    pygly_layer = PyGLyLayer()

    grid_node = RenderCallbackNode(
        '/grid',
        grid.initialise_grid,
        grid.render_grid
        )
    pygly_node.add_child( grid_node )

    # rotate the mesh so it is tilting forward
    grid_node.rotate_object_x( math.pi / 4.0 )

    # move the grid backward so we can see it
    grid_node.translate_inertial_z( -80.0 )

    # create a camera and a view matrix
    view_matrix = ProjectionViewMatrix(
        pygly_layer.pygly_viewport.aspect_ratio,
        fov = 60.0,
        near_clip = 1.0,
        far_clip = 200.0
        )
    pygly_camera = CameraNode(
        '/camera',
        view_matrix
        )
    pygly_node.add_child( pygly_camera )

    # set the viewports camera
    pygly_layer.pygly_viewport.set_camera(
        pygly_node,
        pygly_camera
        )


#
# messy cocos2d code, verbatim from their examples, yuck
# http://cocos2d.org
#
# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


import cocos
from cocos.director import director

from pyglet import gl

# Defining a new layer type...
class Square(cocos.layer.Layer):
    """Square (color, c, y, size=50) : A layer drawing a square at (x,y) of
    given color and size"""
    def __init__(self, color, x, y, size=50):
        super( Square, self ).__init__()

        self.x = x
        self.y = y
        self.size = size
        self.layer_color = color
                
    def draw(self):
        super(Square,self).draw()
        gl.glDisable( gl.GL_DEPTH_TEST )

        gl.glColor4f(*self.layer_color)
        x, y = self.x, self.y
        w = x+self.size; h=y+self.size
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f( x, y )
        gl.glVertex2f( x, h )
        gl.glVertex2f( w, h )
        gl.glVertex2f( w, y )
        gl.glEnd()
        gl.glColor4f(1,1,1,1) 

        #gl.glEnable( gl.GL_DEPTH_TEST )
        
if __name__ == "__main__":
    director.init()
    sc = cocos.scene.Scene()

    # Create a large number of layers
    for i in range(5,12):
        colour = (0.03*i,0.03*i,0.03*i,1)
        x = i * 20
        y = i * 20
        sc.add( Square(colour, x, y) )

    # add our pygly scene as a layer
    setup_pygly_scene()
    sc.add( pygly_layer, name="pygly" )

    # add some layers ontop of our pygly scene
    for i in range(15,20):
        colour = (0.03*i,0.03*i,0.03*i,1)
        x = i * 20
        y = i * 20
        sc.add( Square(colour, x, y) )

    #from cocos.actions.interval_actions import MoveBy
    #pygly_layer.do( MoveBy( (50,0), duration=8) )
    #sc.do( MoveBy( (50,0),duration=8) )
    #from cocos.actions.interval_actions import RotateBy
    #sc.do( RotateBy( 360,duration=8) )
    #pygly_layer.anchor_x = 320
    #pygly_layer.anchor_y = 320
    from cocos.actions.interval_actions import ScaleBy
    #pygly_layer.do( ScaleBy( 2,duration=2) )
    #pygly_layer.anchor_x = 0
    #pygly_layer.anchor_y = 0
    #pygly_layer.anchor_x = 320
    #pygly_layer.anchor_y = 240
    #pygly_layer.anchor_x = 640
    #pygly_layer.anchor_y = 480
    #sc.anchor_x = 0
    #sc.anchor_y = 0
    #sc.anchor_x = 320
    #sc.anchor_y = 240
    #sc.anchor_x = 640
    #sc.anchor_y = 480
    sc.do( ScaleBy( 2,duration=2) )
    director.run( sc )

