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

import pygly.window
import pygly.gl
from pygly.ratio_viewport import RatioViewport
from pygly.projection_view_matrix import ProjectionViewMatrix
from pygly.scene_node import SceneNode
from pygly.camera_node import CameraNode
from pygly.render_callback_node import RenderCallbackNode
from pygly.input.keyboard import Keyboard

import pyrr

import cube

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

        # create a viewport
        self.viewport = RatioViewport(
            self.window,
            [ [0.0, 0.0], [1.0, 1.0] ]
            )

        # create our input devices
        self.keyboard = Keyboard( self.window )

        # register for keypresses
        self.keyboard.digital.push_handlers(
            on_digital_input = self.on_key_event
            )

        # setup our scene
        self.setup_scene()

        # setup our text
        self.setup_text()
        
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
        # set our gl clear colour
        glClearColor( 0.2, 0.2, 0.2, 1.0 )

        # start by rendering using immediate mode
        self.render_mode = 0

        # create a list of renderables
        self.renderables = []

        # create a scene
        self.scene_node = SceneNode( 'root' ) 
        
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

        # move the camera so we can see the grid
        self.camera.transform.inertial.translate(
            [ 0.0, 10.0, 20.0 ]
            )
        # rotate the camera so it is pointing down
        self.camera.transform.object.rotate_x( -math.pi / 4.0 )

        # create a single node that is parent to all
        # of our cubes
        self.cube_root = SceneNode( 'cube_root' )
        self.scene_node.add_child( self.cube_root )

        # create a number of cubes
        x,z = numpy.mgrid[
            -5:5:11j,
            -5:5:11j
            ]
        x = x.flatten()
        z = z.flatten()

        positions = numpy.vstack(
            (x, numpy.zeros( x.shape ), z )
            )
        positions = positions.T

        # set the distance of the cubes
        # cube is -1 -> 1
        # so distance is 2
        positions *= 2.5

        for position in positions:
            node = RenderCallbackNode(
                'cube',
                self.initialise_cube,
                self.render_cube
                )
            node.transform.inertial.translation = position
            self.cube_root.add_child( node )
            self.renderables.append( node )

        # sort our renderables
        positions = [ obj.world_transform.translation for obj in self.renderables ]

        renderables = pygly.sorter.sort_radius_back_to_front(
            self.camera.world_transform.translation,
            -(self.camera.transform.object.z),
            self.renderables,
            positions
            )

    def setup_text( self ):
        self.help_label = pyglet.text.HTMLLabel(
"""
<b>Render Method demo</b>
<ul>
<li>E: Toggle render mode</li>
</ul>
""",
        multiline = True,
        x = 0,
        y = 50,
        width = 500,
        anchor_x = 'left',
        anchor_y = 'bottom',
        )
        self.help_label.color = (255,255,255,255)

    def setup_status_text( self ):
        if self.render_mode == 0:
            render_text = "OpenGL Immediate Mode"
        elif self.render_mode == 1:
            render_text = "OpenGL display list"
        elif self.render_mode == 2:
            render_text = "Pyglet Batch"

        self.status_label = pyglet.text.HTMLLabel(
"""
Rendering: %i transparent cubes<br>
Render method: %s<br>
""" % (len(self.renderables), render_text),
        multiline = True,
        x = 500,
        y = 50,
        width = 500,
        anchor_x = 'left',
        anchor_y = 'bottom',
        )
        self.status_label.color = (255,255,255,255)

    def run( self ):
        pyglet.app.run()
    
    def step( self, dt ):
        # render the scene
        self.render()

        # render the fps
        self.fps_display.draw()

        # render our help text
        self.help_label.draw()

        # update our status text
        self.setup_status_text()
        # render it
        self.status_label.draw()
        
        # display the frame buffer
        self.window.flip()

    def on_key_event( self, digital, event, key ):
        if event == Keyboard.up:
            # check for switching of sorting
            if key[ 0 ] == self.keyboard.keys.E:
                self.render_mode += 1
                if self.render_mode >= 3:
                    self.render_mode = 0

    def initialise_cube( self ):
        # initialise all render methods
        cube.initialise_display_list()
        cube.initialise_batch()

    def render_cube( self ):
        if self.render_mode == 0:
            cube.render_immediate_mode()
        elif self.render_mode == 1:
            cube.render_display_list()
        elif self.render_mode == 2:
            cube.render_batch()

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

        # enable alpha rendering
        glEnable( GL_BLEND )
        glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )

        glColor4f( 0.5, 0.5, 0.5, 0.5 )

        # render each object
        for renderable in self.renderables:
            # render the object
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

