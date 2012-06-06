'''
Created on 03/03/2012

@author: adam
'''

import math

import numpy
from pyglet.gl import *
import pyglet

from pyrr import rectangle

import pygly.window
import pygly.gl
from pygly.ratio_viewport import RatioViewport
from pygly.projection_view_matrix import ProjectionViewMatrix
from pygly.scene_node import SceneNode
from pygly.render_callback_node import RenderCallbackNode
from pygly.camera_node import CameraNode

from examples.render_callbacks import grid

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
            config = config
            )

        # create a viewport that spans
        # the entire screen
        self.viewport = RatioViewport(
            self.window,
            [ [0.0, 0.0], [1.0, 1.0] ]
            )

        # make a second viewport
        # this viewport will be 1/10th the size
        self.floating_viewport = RatioViewport(
            self.window,
            [ [0.0, 0.0], [0.1, 0.1] ]
            )

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
        # create a list of renderables
        self.renderables = []

        # create a scene
        self.scene_node = SceneNode( 'root' )

        self.grid_node = SceneNode( 'grid' )
        self.scene_node.add_child( self.grid_node )

        # create a grid to render
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

        # move the camera backward so we can see the mesh
        self.camera.translate_inertial(
            [ 0.0, 20.0, 80.0 ]
            )

        # rotate the camera so it is tilting downward
        self.camera.rotate_object_x( -math.pi / 4.0 )

        # create a list of viewports and cameras
        self.viewports = [
            (self.viewport, self.camera),
            (self.floating_viewport, self.camera)
            ]

        # we will use this as a vector to move the viewport
        # around the window
        self.velocity = numpy.array(
            [ 500, 500 ],
            dtype = numpy.int
            )
    
    def run( self ):
        pyglet.app.run()
    
    def step( self, dt ):
        # move the viewport around the screen
        frame_velocity = self.velocity * dt
        self.floating_viewport.rect[ 0 ] += frame_velocity

        # see if we've gone over the window's bounds
        if self.floating_viewport.left < 0:
            if self.velocity[ 0 ] < 0:
                self.velocity[ 0 ] = -self.velocity[ 0 ]
        if self.floating_viewport.right > self.window.width:
            if self.velocity[ 0 ] > 0:
                self.velocity[ 0 ] = -self.velocity[ 0 ]
        if self.floating_viewport.bottom < 0:
            if self.velocity[ 1 ] < 0:
                self.velocity[ 1 ] = -self.velocity[ 1 ]
        if self.floating_viewport.top > self.window.height:
            if self.velocity[ 1 ] > 0:
                self.velocity[ 1 ] = -self.velocity[ 1 ]

        # rotate the mesh about it's own vertical axis
        self.grid_node.rotate_object_y( dt )

        # render the scene
        self.render()

        # render the fps
        self.fps_display.draw()

        # display the frame buffer
        self.window.flip()

    def set_gl_state( self ):
        glEnable( GL_DEPTH_TEST )
        glShadeModel( GL_SMOOTH )
        glEnable( GL_RESCALE_NORMAL )
        glEnable( GL_SCISSOR_TEST )

    def render( self ):
        # set our window
        self.window.switch_to()

        # render the viewport
        for viewport, camera in self.viewports:
            self.render_viewport( viewport, camera )

        # set our viewport to the entire
        # window
        pygly.gl.set_scissor(
            pygly.window.create_rectangle( self.window )
            )
        pygly.gl.set_viewport(
            pygly.window.create_rectangle( self.window )
            )

    def render_viewport( self, viewport, camera ):
        #
        # setup
        #
    
        # activate our viewport
        viewport.switch_to()

        # scissor to our viewport
        viewport.scissor_to_viewport()

        # setup our viewport properties
        glPushAttrib( GL_ALL_ATTRIB_BITS )
        self.set_gl_state()

        # update the camera's view matrix for our
        # viewports aspect ratio
        camera.view_matrix.aspect_ratio = viewport.aspect_ratio

        # apply our view matrix and camera translation
        camera.view_matrix.push_view_matrix()
        camera.push_model_view()

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
        camera.pop_model_view()
        camera.view_matrix.pop_view_matrix()

        # pop our viewport attributes
        glPopAttrib()


def main():
    # create app
    app = Application()
    app.run()
    app.window.close()


if __name__ == "__main__":
    main()

