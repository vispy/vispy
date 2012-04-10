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
            [ [0.0, 0.0], [1.0, 1.0] ]
            )

        # over-ride the viewports setup method
        # so we can set some opengl states
        self.viewport.setup_viewport = self.setup_viewport
        
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

        # display the current FPS
        self.fps_display = pyglet.clock.ClockDisplay()
        
        print "Rendering at %iHz" % int(frequency)

    def setup_scene( self ):
        # create a scene
        self.scene_node = SceneNode( '/root' )

        # create a mesh object
        self.mesh = OBJ_Mesh( 'examples/data/obj/cessna.obj' )

        # create our render node with callbacks to
        # render our mesh
        self.mesh_node = RenderCallbackNode(
            '/obj/rendernode',
            self.initialise_mesh,
            self.render_mesh
            )
        self.scene_node.add_child( self.mesh_node )

        # move the mesh so we can see it
        self.mesh_node.translate_object_z( -30.0 )
        
        # rotate the mesh so we can see it
        self.mesh_node.rotate_object_x( math.pi / 4.0 )
        
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

        # create a light
        glEnable( GL_LIGHT0 )
        glLightfv(
            GL_LIGHT0,
            GL_POSITION,
            (GLfloat * 4)( *[0.0, 0.0, 0.0, 1.0] )
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
        
    def setup_viewport( self ):
        # use the z-buffer when drawing
        glEnable( GL_DEPTH_TEST )

        # normalise any normals for us
        glEnable( GL_RESCALE_NORMAL )

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
    
    def run( self ):
        pyglet.app.run()
    
    def step( self, dt ):
        # rotate the mesh about it's own vertical axis
        self.mesh_node.rotate_object_y( dt )

        # clear our frame buffer and depth buffer
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

        # render the scene
        viewports = [ self.viewport ]
        renderer.window.render( self.window, viewports )

        # render the fps
        self.fps_display.draw()
        
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

