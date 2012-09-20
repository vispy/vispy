#
# PyGLy code
#

import math

from pyglet.gl import *

import pygly.window
from pygly.projection_view_matrix import ProjectionViewMatrix
from pygly.scene_node import SceneNode
from pygly.render_callback_node import RenderCallbackNode
from pygly.camera_node import CameraNode
from pygly.cocos2d.layer import Layer as PyGLyLayer

import examples.render_callbacks.grid as grid


class PyglyScene( object ):

    def __init__( self ):
        super( PyglyScene, self ).__init__()

        # store a list of renderables
        self.renderables = []

        # create a scene
        self.scene_node = SceneNode( 'root' )

        # create a node for the grid
        self.grid_node = SceneNode( 'grid' )
        self.scene_node.add_child( self.grid_node )

        # create a render node for the grid
        self.grid_render_node = RenderCallbackNode(
            'mesh',
            grid.initialise_grid,
            grid.render_grid
            )
        self.grid_node.add_child( self.grid_render_node )

        # add to our list of renderables
        self.renderables.append( self.grid_render_node )

        # create a camera and a view matrix
        # set a temporary aspect ratio as we haven't created
        # the viewport yet
        self.view_matrix = ProjectionViewMatrix(
            aspect_ratio = 4.0 / 3.0,
            fov = 45.0,
            near_clip = 1.0,
            far_clip = 200.0
            )
        self.camera = CameraNode(
            'camera',
            self.view_matrix
            )
        self.scene_node.add_child( self.camera )

        # move the camera
        self.camera.transform.object.translate(
            [ 0.0, 20.0, 40.0 ]
            )

        # rotate the camera so it is tilting forward
        self.camera.transform.object.rotate_x( -math.pi / 4.0 )

        # this must be done after the
        # director is initialised or the
        # program will crash since the window
        # won't have been created
        self.layer = PyGLyLayer(
            camera = self.camera,
            render_callback = self.render_layer
            )

        # update the aspect ratio
        self.camera.view_matrix.aspect_ratio = pygly.window.aspect_ratio(
            self.layer.pygly_viewport
            )

        # register our on_resize handler
        director.window.push_handlers(
            on_resize = self.on_resize
            )

    def on_resize( self, width, height ):
        # update the viewport size
        self.layer.pygly_viewport = pygly.window.create_rectangle(
            director.window
            )

        # update the view matrix aspect ratio
        self.camera.view_matrix.aspect_ratio = pygly.window.aspect_ratio(
            self.layer.pygly_viewport
            )

    def set_gl_state( self ):
        # enable z buffer
        glEnable( GL_DEPTH_TEST )

        # enable smooth shading
        glShadeModel( GL_SMOOTH )

        # rescale only normals for lighting
        glEnable( GL_RESCALE_NORMAL )

        # enable scissoring for viewports
        glEnable( GL_SCISSOR_TEST )

        # enable back face culling
        glEnable( GL_CULL_FACE )
        glCullFace( GL_BACK )

    def render_layer( self, layer ):
        #
        # setup
        #

        # activate our viewport
        pygly.gl.set_viewport( layer.pygly_viewport )
        # scissor to our viewport
        pygly.gl.set_scissor( layer.pygly_viewport )

        # setup our viewport properties
        glPushAttrib( GL_ALL_ATTRIB_BITS )
        self.set_gl_state()

        # apply our view matrix and camera transform
        layer.pygly_camera.view_matrix.push_view_matrix()
        layer.pygly_camera.push_model_view()

        #
        # render
        #

        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

        self.scene_node.render_debug()

        for renderable in self.renderables:
            renderable.render()

        #
        # tear down
        #

        # pop our view matrix and camera transform
        layer.pygly_camera.pop_model_view()
        layer.pygly_camera.view_matrix.pop_view_matrix()

        # reset our gl state
        glPopAttrib()

        # reset the viewport state
        pygly.gl.set_viewport(
            pygly.window.create_rectangle( director.window )
            )
        pygly.gl.set_scissor(
            pygly.window.create_rectangle( director.window )
            )

        # ensure the matrix mode is set back to GL_MODELVIEW
        glMatrixMode( GL_MODELVIEW )


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
    pygly_scene = PyglyScene()
    sc.add( pygly_scene.layer, name = "pygly" )

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

