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
import numpy

import maths.vector
import maths.quaternion
import maths.matrix33
import renderer.idle
import renderer.window
from renderer.viewport import Viewport
from renderer.projection_view_matrix import ProjectionViewMatrix
from scene.scene_node import SceneNode
from scene.camera_node import CameraNode
from scene.render_callback_node import RenderCallbackNode
from scene.fps_controller import FPS_Controller
from input.keyboard import Keyboard
from input.mouse import Mouse

from examples.render_callbacks import grid

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

        # create our input devices
        self.keyboard = Keyboard( self.window )
        self.mouse = Mouse( self.window )

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
        # enable debug so we can see the ndoes
        SceneNode.debug = True

        # create a scene
        self.scene_node = SceneNode( '/root' )

        self.grid_node = RenderCallbackNode(
            '/grid',
            grid.initialise_grid,
            grid.render_grid
            )
        self.scene_node.add_child( self.grid_node )

        # move the grid backward so we can see it
        # and move it down so we start above it
        self.grid_node.translate_object_z( -80.0 )

        # create a node that we'll move around
        self.test_node = SceneNode( '/test' )
        self.scene_node.add_child( self.test_node )

        # create a fps controller for the node
        self.node_controller = FPS_Controller()
        self.node_controller.scene_node = self.test_node
        
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
        
        # assign a camera controller
        # we'll use the FPS camera for this one
        self.camera_controller = FPS_Controller()
        self.camera_controller.scene_node = self.camera
        
        # set the viewports camera
        self.viewport.set_camera( self.scene_node, self.camera )

        self.pitch_time = 0.0
        self.pitch_change = math.pi / 4.0
        self.yaw_change = math.pi / 4.0
        
    def run( self ):
        pyglet.app.run()
    
    def step( self, dt ):
        # update the Camera
        camera_speed = 40.0
        
        # handle input
        # this looks complex, but all we're doing
        # is checking for WASD / Arrows
        # and then sending forward, backward, etc
        # to the camera controller with an amount that
        # is scaled by the current time delta

        # move forward
        if self.keyboard[ self.keyboard.keys.W ] or self.keyboard[ self.keyboard.keys.UP ]:
            self.camera_controller.translate_forward( camera_speed * dt )

        # move backward
        if self.keyboard[ self.keyboard.keys.S ] or self.keyboard[ self.keyboard.keys.DOWN ]:
            self.camera_controller.translate_backward( camera_speed * dt )

        # move right
        if self.keyboard[ self.keyboard.keys.D ] or self.keyboard[ self.keyboard.keys.RIGHT ]:
            self.camera_controller.translate_right( camera_speed * dt )

        # move right
        if self.keyboard[ self.keyboard.keys.A ] or self.keyboard[ self.keyboard.keys.LEFT ]:
            self.camera_controller.translate_left( camera_speed * dt )

        # move up
        if self.keyboard[ self.keyboard.keys.SPACE ]:
            self.camera_controller.translate_up( camera_speed * dt )

        # move up
        if self.keyboard[ self.keyboard.keys.LSHIFT ]:
            self.camera_controller.translate_down( camera_speed * dt )
        
        # handle camera rotation
        # get the relative movement of the mouse
        # since the last frame
        mouse_relative = self.mouse.relative_position

        # the base movement speed we use for
        # scaling with the mouse movements
        # this value just feels about right
        mouse_speed = 0.006
        
        # scale the mouse movement by the relative value
        # DON'T multiply by the time delta here
        # think about it, it's not what you want!
        frame_pitch = math.pi * mouse_speed * mouse_relative[ 1 ]
        frame_yaw = -math.pi * mouse_speed * mouse_relative[ 0 ]
        
        # check for mouse inverts, for us freaks...
        # WE HAVE RIGHTS TOO!
        invert_y = True
        if invert_y == True:
            frame_pitch = -frame_pitch
        
        # pass the mouse movement to the camera controller
        self.camera_controller.orient( pitch = frame_pitch, yaw = frame_yaw )
        
        # reset our mouse relative position
        # we should do this each time we take a reading
        # or the delta will continue to accumulate
        self.mouse.clear_delta()

        # move the test node
        self.pitch_time += dt
        if self.pitch_time > 5.0:
            self.pitch_change *= -1.0
            self.pitch_time = 0.0
        self.node_controller.translate_forward( math.pi * dt )
        self.node_controller.orient( self.pitch_change * dt, self.yaw_change * dt )

        # clear our frame buffer and depth buffer
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
        
        # render the scene
        viewports = [ self.viewport ]
        renderer.window.render( self.window, viewports )

        # render the fps
        self.fps_display.draw()
        
        # display the frame buffer
        self.window.flip()


def main():
    # create app
    app = Application()
    app.run()
    app.window.close()


if __name__ == "__main__":
    main()

