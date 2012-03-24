'''
Created on 15/06/2011

@author: adam

TODO: use resource locations
http://www.pyglet.org/doc/programming_guide/loading_resources.html
'''

import math
import time
import random

from pyglet.gl import *
import pyglet

import renderer.idle
import renderer.window
from renderer.viewport import Viewport
from renderer.projection_view_matrix import ProjectionViewMatrix
from scene.scene_node import SceneNode
from scene.camera_node import CameraNode
from scene.render_callback_node import RenderCallbackNode
from mesh.obj_mesh import OBJ_Mesh
import maths.quaternion


class Application( object ):
    
    def __init__( self ):
        super( Application, self ).__init__()
        
        # setup our opengl requirements
        config = pyglet.gl.Config(
            depth_size = 16,
            double_buffer = True
            )

        # create our window
        self.window = pyglet.window.Window(
            fullscreen = False,
            width = 1024,
            height = 768,
            config = config
            )

        # create a viewport
        self.viewport = Viewport(
            [ 0.0, 0.0, 1.0, 1.0 ]
            )

        # over-ride the viewports setup method
        # so we can set some opengl states
        self.viewport.setup_viewport = self.setup_viewport
        self.viewport.tear_down_viewport = self.tear_down_viewport
        
        # setup our scene
        self.setup_scene()
        
        # setup our update loop the app
        # we'll render at 60 fps
        frequency = 60.0
        self.update_delta = 1.0 / frequency
        # use a pyglet callback for our render loop
        pyglet.clock.schedule_interval(
            self.step,
            self.update_delta
            )
        
        print "Rendering at %iHz" % int(frequency)

    def setup_scene( self ):
        # create a scene
        self.scene_node = SceneNode( '/root' )

        #self.mesh = OBJ_Mesh( 'examples/data/obj/humanoid_tri.obj' )
        #self.mesh = OBJ_Mesh( 'examples/data/obj/humanoid_quad.obj' )
        self.mesh = OBJ_Mesh( 'examples/data/obj/cessna.obj' )
        #self.mesh = OBJ_Mesh( 'examples/data/obj/cube.obj' )
        #self.mesh = OBJ_Mesh( 'examples/data/obj/cube_offsets.obj' )

        # add a grid so we can see wtf we're doing
        self.mesh_node = RenderCallbackNode(
            '/obj/rendernode',
            self.initialise_mesh,
            self.render_mesh
            )
        self.scene_node.add_child( self.mesh_node )

        # move the mesh so we can see it
        self.mesh_node.translate(
            [ 0.0, 0.0, -80.0 ]
            )
        
        # create a camera and a view matrix
        self.view_matrix = ProjectionViewMatrix(
            fov = 60.0,
            near_clip = 1.0,
            far_clip = 200.0
            )
        # create a camera
        self.camera = CameraNode(
            '/camera',
            self.view_matrix
            )
        self.scene_node.add_child( self.camera )
        
        # set the viewports camera
        self.viewport.set_camera( self.scene_node, self.camera )
        
        # the md2 is oriented at 90 degrees about X
        # re-orient the mesh
        quat = maths.quaternion.set_to_rotation_about_x( -math.pi / 2.0 )
        self.mesh_node.rotate_quaternion( quat )
        
    def setup_viewport( self ):
        # use the z-buffer when drawing
        glEnable( GL_DEPTH_TEST )

        # normalise any normals for us
        glEnable( GL_NORMALIZE )

        # enable smooth shading
        # instead of flat shading
        glShadeModel( GL_SMOOTH )
            
        # setup lighting for our viewport
        glEnable( GL_LIGHTING )

        # set our ambient lighting
        glAmbient = glLightModelfv(
            GL_LIGHT_MODEL_AMBIENT,
            (GLfloat * 4)( *[ 0.8, 0.8, 0.8, 1.0 ] )
            )

        # create a light
        glEnable( GL_LIGHT0 )
        glLightfv(
            GL_LIGHT0,
            GL_POSITION,
            (GLfloat * 4)( *[-10.0, 0.0, 0.0, 1.0] )
            )
        glLightfv(
            GL_LIGHT0,
            GL_AMBIENT,
            (GLfloat * 4)( *[0.5, 0.5, 0.5, 1.0] )
            )
        glLightfv(
            GL_LIGHT0,
            GL_DIFFUSE,
            (GLfloat * 4)( *[1.0, 1.0, 1.0, 1.0] )
            )
    
    def tear_down_viewport( self ):
        glDisable( GL_LIGHT0 )
        glDisable( GL_LIGHTING )
        glDisable( GL_NORMALIZE )
        glDisable( GL_DEPTH_TEST )

    def run( self ):
        pyglet.app.run()
    
    def step( self, dt ):
        # rotate the mesh about it's own vertical axis
        self.mesh_node.yaw( dt )
        
        # render the scene
        viewports = [ self.viewport ]
        renderer.window.render( self.window, viewports )
        
        # display the frame buffer
        self.window.flip()

    def initialise_mesh( self ):
        # load the obj mesh from the file
        self.mesh.load()

    def render_mesh( self ):
        # render the mesh
        self.mesh.render()


def main():
    # create app
    app = Application()
    app.run()
    app.window.close()


if __name__ == "__main__":
    main()

