'''
Created on 03/03/2012

@author: adam
'''

import math

from pyglet.gl import *
import pyglet

import pygly.window
from pygly.ratio_viewport import RatioViewport
from pygly.projection_view_matrix import ProjectionViewMatrix
from pygly.scene_node import SceneNode
from pygly.render_callback_node import RenderCallbackNode
from pygly.camera_node import CameraNode

import grid

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

        # create a viewport that spans
        # the entire screen
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

        # store a list of renderables
        self.renderables = []

        # create a scene
        self.scene_node = SceneNode( 'root' )

        # create a grid to render
        self.grid_node = SceneNode( 'grid' )
        self.scene_node.add_child( self.grid_node )

        self.grid_render_node = RenderCallbackNode(
            'mesh',
            grid.initialise_grid,
            grid.render_grid
            )
        self.grid_node.add_child( self.grid_render_node )

        # add to our list of renderables
        self.renderables.append( self.grid_render_node )

        # create a camera and a view matrix
        self.view_matrix = ProjectionViewMatrix(
            self.viewport.aspect_ratio,
            fov = 45.0,
            near_clip = 1.0,
            far_clip = 200.0
            )
        self.camera = CameraNode(
            'camera',
            self.view_matrix
            )
        self.scene_node.add_child( self.camera )

        # move the camera backward so we can see it
        self.camera.transform.inertial.translate(
            [ 0.0, 20.0, 40.0]
            )

        # rotate the camera so it is tilting forward
        self.camera.transform.object.rotate_x( -math.pi / 4.0 )

        # listen for viewport resize events
        self.viewport.push_handlers(
            on_change_aspect_ratio = self.view_matrix.on_change_aspect_ratio
            )

    def setup_viewport( self ):
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
        # enable some default options
        # use the z-buffer when drawing
        glEnable( GL_DEPTH_TEST )

        # enable smooth shading
        glShadeModel( GL_SMOOTH )
    
    def run( self ):
        pyglet.app.run()
    
    def step( self, dt ):
        # rotate the mesh about it's own vertical axis
        self.grid_node.transform.object.rotate_y( dt )

        # manually dispatch the on_draw event
        # as we patched it out of the idle loop
        self.window.dispatch_event( 'on_draw' )

        # display the frame buffer
        self.window.flip()

    def on_draw( self ):
        self.render()

        # render the fps
        self.fps_display.draw()

    def render( self ):
        #
        # setup
        #

        # set our window
        self.window.switch_to()
        # set our viewport
        self.viewport.switch_to()
        self.viewport.scissor_to_viewport()

        # apply our viewport settings
        self.viewport.push_viewport_attributes()

        # update the view matrix aspect ratio
        self.camera.view_matrix.aspect_ratio = self.viewport.aspect_ratio

        # apply our camera
        self.camera.view_matrix.push_view_matrix()
        self.camera.push_model_view()

        #
        # render
        #

        # clear our frame buffer and depth buffer
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

        # render the scene graph for debugging
        self.scene_node.render_debug()

        # render the scene
        for renderable in self.renderables:
            renderable.render()

        #
        # tear down
        #

        # pop our view matrix and camera transforms
        self.camera.pop_model_view()
        self.camera.view_matrix.pop_view_matrix()

        self.viewport.pop_viewport_attributes()

        pygly.gl.set_scissor(
            pygly.window.create_rectangle( self.window )
            )
        pygly.gl.set_viewport(
            pygly.window.create_rectangle( self.window )
            )

        # ensure the matrix mode was last set to
        # GL_MODELVIEW
        glMatrixMode( GL_MODELVIEW )
    

def main():
    # create app
    app = Application()
    app.run()
    app.window.close()


if __name__ == "__main__":
    main()

