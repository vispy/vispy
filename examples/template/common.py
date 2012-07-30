import math
import time
import random

from pyglet.gl import *
import pyglet
import numpy

import pygly.window
import pygly.gl
from pygly.ratio_viewport import RatioViewport
from pygly.projection_view_matrix import ProjectionViewMatrix
from pygly.scene_node import SceneNode
from pygly.camera_node import CameraNode
from pygly.render_callback_node import RenderCallbackNode
from pygly.input.keyboard import Keyboard
from pygly.input.mouse import Mouse

import pyrr

# over-ride the default pyglet idle loop
import pygly.monkey_patch
pygly.monkey_patch.patch_idle_loop()


class BaseApplication( object ):
    
    def __init__( self ):
        super( BaseApplication, self ).__init__()

        self.setup()

    def setup( self ):
        self.setup_window()
        self.setup_input()
        self.setup_ui()
        self.setup_scene_root()
        self.setup_camera()
        self.setup_scene()
        self.setup_events()
        
    def setup_window( self ):
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

        # listen for on_draw events
        self.window.push_handlers(
            on_draw = self.on_draw
            )

        # create a viewport
        self.viewport = RatioViewport(
            self.window,
            [ [0.0, 0.0], [1.0, 1.0] ]
            )

    def setup_input( self ):
        # create our keyboard device
        self.keyboard = Keyboard( self.window )

        # register for keypresses
        self.keyboard.digital.push_handlers(
            on_digital_input = self.on_key_event
            )

        # create our mouse device
        self.mouse = Mouse( self.window )

    def setup_events( self ):
        # setup our update loop the app
        # we'll render at 60 fps
        frequency = 60.0
        self.update_delta = 1.0 / frequency

        # use a pyglet callback for our render loop
        pyglet.clock.schedule_interval(
            self.step,
            self.update_delta
            )

    def setup_ui( self ):
        # create an fps display
        self.fps_display = pyglet.clock.ClockDisplay()

    def setup_scene_root( self ):
        # create a list of renderables
        self.renderables = []

        # create a scene
        self.scene_node = SceneNode( 'root' ) 
        
    def setup_camera( self ):
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

    def setup_scene( self ):
        # CREATE SCENE HERE
        pass

    def run( self ):
        pyglet.app.run()
    
    def step( self, dt ):
        # update our mouse
        self.update_mouse( dt )

        # update the scene here
        self.update_scene( dt )

        # manually dispatch the on_draw event
        # as we patched it out of the idle loop
        self.window.dispatch_event( 'on_draw' )
        
        # display the frame buffer
        self.window.flip()

    def update_mouse( self, dt ):
        # USE MOUSE VALUES HERE
        pass

        # reset the relative position of the mouse
        self.mouse.clear_delta()

    def on_key_event( self, digital, event, key ):
        # HANDLE KEYBOARD INPUT HERE
        pass

    def update_scene( self, dt ):
        # UPDATE SCENE HERE
        pass

    def on_draw( self ):
        # render the scene
        self.render()

        # render the fps
        self.fps_display.draw()

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

        self.render_3d()

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

        #
        # render 2d
        #

        self.render_2d()

    def render_2d( self ):
        # render the fps
        self.fps_display.draw()

