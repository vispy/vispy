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

import pygly.window
import pygly.gl
from pygly.ratio_viewport import RatioViewport
from pygly.projection_view_matrix import ProjectionViewMatrix
from pygly.scene_node import SceneNode
from pygly.camera_node import CameraNode
from pygly.render_callback_node import RenderCallbackNode
from pygly.mesh.obj_mesh import OBJ_Mesh

# over-ride the default pyglet idle loop
import pygly.monkey_patch
pygly.monkey_patch.patch_idle_loop()


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
            resizable = True,
            vsync = False,
            config = config
            )

        # create a viewport
        self.viewport = RatioViewport(
            self.window,
            [ [0.0, 0.0], [1.0, 1.0] ]
            )
        
        # setup our scene
        self.setup_scene()

        # listen for on_draw events
        self.window.push_handlers(
            on_draw = self.on_draw
            )
        
        # setup our update loop the app
        # we'll render at 60 fps
        frequency = 60.0
        self.update_delta = 1.0 / frequency

        # over-ride the frequency and render at full speed
        self.update_delta = -1

        # use a pyglet callback for our render loop
        pyglet.clock.schedule_interval(
            self.step,
            self.update_delta
            )

    def setup_scene( self ):
        # create an fps display
        self.fps_display = pyglet.clock.ClockDisplay()

        # store a list of our renderables
        self.renderables = []

        # create a scene
        self.scene_node = SceneNode( 'root' )

        self.mesh_node = SceneNode( 'obj' )
        self.scene_node.add_child( self.mesh_node )

        # create a mesh object and render node
        self.mesh = OBJ_Mesh( 'examples/data/obj/cessna.obj' )
        self.mesh_render_node = RenderCallbackNode(
            'mesh',
            self.initialise_mesh,
            self.render_mesh
            )
        self.mesh_node.add_child( self.mesh_render_node )

        # add to our list of renderables
        self.renderables.append( self.mesh_render_node )
        
        # create a camera and a view matrix
        self.view_matrix = ProjectionViewMatrix(
            self.viewport.aspect_ratio,
            fov = 45.0,
            near_clip = 1.0,
            far_clip = 200.0
            )
        # create a camera
        self.camera = CameraNode(
            'camera',
            self.view_matrix
            )
        self.scene_node.add_child( self.camera )

        # move the camera so we can see the model
        self.camera.transform.object.translate(
            [ 0.0, 20.0, 30.0 ]
            )

        # rotate the camera so it is pointing down
        self.camera.transform.object.rotate_x( -math.pi / 4.0 )
        
    def run( self ):
        pyglet.app.run()

    def step( self, dt ):
        # rotate the mesh about it's own vertical axis
        self.mesh_node.transform.object.rotate_y( dt )

        # manually dispatch the on_draw event
        # as we patched it out of the idle loop
        self.window.dispatch_event( 'on_draw' )
        
        # display the frame buffer
        self.window.flip()

    def on_draw( self ):
        # render the scene
        self.render()

        # render the fps
        self.fps_display.draw()

    def initialise_mesh( self ):
        # load the obj mesh from the file
        self.mesh.load()

    def render_mesh( self ):
        # render the mesh
        self.mesh.render()

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

        # setup lighting for our viewport
        glEnable( GL_LIGHTING )

        # set an ambient light level
        glAmbient = glLightModelfv(
            GL_LIGHT_MODEL_AMBIENT,
            (GLfloat * 4)( *[ 0.8, 0.8, 0.8, 1.0 ] )
            )

        # create a light
        glEnable( GL_LIGHT0 )
        glLightfv(
            GL_LIGHT0,
            GL_POSITION,
            (GLfloat * 4)( *[0.0, 20.0, 30.0, 1.0] )
            )
    
    def render( self ):
        #
        # setup
        #

        # set our window
        self.window.switch_to()

        # activate our viewport
        self.viewport.switch_to()

        # scissor to our viewport
        self.viewport.scissor_to_viewport()

        # setup our viewport properties
        glPushAttrib( GL_ALL_ATTRIB_BITS )
        self.set_gl_state()

        # update the view matrix aspect ratio
        self.camera.view_matrix.aspect_ratio = self.viewport.aspect_ratio

        # apply our view matrix and camera translation
        self.camera.view_matrix.push_view_matrix()
        self.camera.push_model_view()

        #
        # render
        #

        # clear our frame buffer and depth buffer
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

        for renderable in self.renderables:
            renderable.render()

        #
        # tear down
        #

        # pop our view matrix and camera translation
        self.camera.pop_model_view()
        self.camera.view_matrix.pop_view_matrix()

        # pop our viewport attributes
        glPopAttrib()

        #
        # reset state
        #

        # set our viewport to the entire window
        pygly.gl.set_scissor(
            pygly.window.create_rectangle( self.window )
            )
        pygly.gl.set_viewport(
            pygly.window.create_rectangle( self.window )
            )


def main():
    # create app
    app = Application()
    app.run()
    app.window.close()


if __name__ == "__main__":
    main()

