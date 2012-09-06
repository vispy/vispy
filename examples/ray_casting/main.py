'''
Created on 15/06/2011

@author: adam
'''

import math
import time
import random

from pyglet.gl import *
import pyglet
import numpy

from pyrr import geometric_tests

import pygly.window
import pygly.gl
from pygly.ratio_viewport import RatioViewport
#from pygly.projection_view_matrix import ProjectionViewMatrix
from pygly.orthogonal_view_matrix import OrthogonalViewMatrix
from pygly.scene_node import SceneNode
from pygly.camera_node import CameraNode
from pygly.render_callback_node import RenderCallbackNode
from pygly import debug_cube
from pygly.mesh.obj_mesh import OBJ_Mesh
from pygly.input.keyboard import Keyboard
from pygly.input.mouse import Mouse

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

        # create our input devices
        self.keyboard = Keyboard( self.window )
        self.mouse = Mouse( self.window )

        # initialise our mouse position to
        # an invalid value
        self.last_mouse_point = [-1, -1]
        
        # setup our scene
        self.setup_scene()

        # setup our text
        self.setup_text()

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

        # create a list of renderables
        self.renderables = []

        # create a scene
        self.scene_node = SceneNode( 'root' )

        self.mesh_node = SceneNode( 'obj' )
        self.scene_node.add_child( self.mesh_node )

        # create our render node with callbacks to
        # render our mesh
        self.mesh_render_node = RenderCallbackNode(
            'mesh',
            None,
            debug_cube.render
            )
        self.mesh_node.add_child( self.mesh_render_node )

        # add to our list of renderables
        self.renderables.append( self.mesh_render_node )

        # rotate the mesh so we can see it
        self.mesh_node.transform.object.rotate_x( math.pi / 4.0 )
        
        # create a camera and a view matrix
        """
        self.view_matrix = ProjectionViewMatrix(
            self.viewport.aspect_ratio,
            aspect_ratio,
            fov = 60.0,
            near_clip = 1.0,
            far_clip = 200.0
            )
        """
        self.view_matrix = OrthogonalViewMatrix(
            self.viewport.aspect_ratio,
            scale = [ 20.0, 20.0 ],
            near_clip = 1.0,
            far_clip = 200.0
            )
        # create a camera
        self.camera = CameraNode(
            '/camera',
            self.view_matrix
            )
        self.scene_node.add_child( self.camera )

        # move the camera so we can see the mesh
        self.mesh_node.transform.inertial.translate(
            [ 0.0, 0.0, 30.0 ]
            )

    def setup_text( self ):
        self.help_label = pyglet.text.HTMLLabel(
"""
<b>Ray Casting demo</b>
<ul>
<li>Mouse: cast ray into the scene</li>
</ul>
""",
            multiline = True,
            x = 0,
            y = 50,
            width = 500,
            anchor_x = 'left',
            anchor_y =
            'bottom',
            )
        self.help_label.color = (255,255,255,255)

    def initialise_mesh( self ):
        # load the mesh
        self.mesh.load()

    def render_mesh( self ):
        self.mesh.render()

    def run( self ):
        pyglet.app.run()

    def move_mesh( self ):
        # we don't need the delta
        # just clear it to stop overflows
        self.mouse.clear_delta()

        # see if the mouse moved
        mouse_pos = self.mouse.absolute_position
        if True == numpy.array_equal(
            mouse_pos,
            self.last_mouse_point
            ):
            return

        # the mouse has moved
        # update our mouse pos
        self.last_mouse_point = mouse_pos

        # even though the mouse moved, we can't be
        # guaranteed that it is within the window.
        # we sometimes get events that include mouse
        # values that are outside the window.
        # so we need to check against this.
        if False == geometric_tests.point_intersect_rectangle(
            mouse_pos,
            self.viewport.rect
            ):
            return

        # make the point relative to the viewport
        # and make it into a percentage value of the size
        relative_point = numpy.array(
            mouse_pos - self.viewport.position,
            dtype = numpy.float
            )
        relative_point /= self.viewport.size

        # cast a ray from the mouse's current position
        mouse_ray = self.camera.create_ray_from_ratio_point(
            relative_point
            )

        # render the mesh somewhere along the ray
        distance = 50.0
        self.mesh_node.transform.inertial.translation = mouse_ray[ 0 ] + (mouse_ray[ 1 ] * distance)
    
    def step( self, dt ):
        # move the mesh to the mouse position
        self.move_mesh()

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

        # render our help text
        self.help_label.draw()

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

    def render( self ):
        #
        # setup
        #

        # activate the window
        self.window.switch_to()

        # activate our viewport
        self.viewport.switch_to()

        # scissor to our viewport
        self.viewport.scissor_to_viewport()

        # setup our viewport properties
        self.viewport.push_viewport_attributes()

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

        # reset our gl state
        self.viewport.pop_viewport_attributes()

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

