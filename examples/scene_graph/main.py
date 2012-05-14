'''
Created on 03/03/2012

@author: adam
'''

import math

from pyglet.gl import *
import pyglet

import pygly.window
from pygly.viewport import Viewport
from pygly.projection_view_matrix import ProjectionViewMatrix
from pygly.scene_node import SceneNode
from pygly.render_callback_node import RenderCallbackNode
from pygly.camera_node import CameraNode

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
            config = config
            )

        # create a viewport that spans
        # the entire screen
        self.viewport = Viewport(
            pygly.window.create_rectangle(
                self.window
                )
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
        # turn scene node debugging on
        SceneNode.debug = True

        # create a scene
        self.scene_node = SceneNode( 'root' )

        self.sn1 = SceneNode( 'sn1' )
        self.sn2 = SceneNode( 'sn2' )
        self.sn3 = SceneNode( 'sn3' )
        self.scene_node.add_child( self.sn1 )
        self.sn1.add_child( self.sn2 )
        self.sn2.add_child( self.sn3 )

        self.sn1.set_scale( [2.0, 2.0, 2.0] )
        self.sn2.set_scale( [0.5, 0.5, 0.5] )
        self.sn3.set_scale( [2.0, 2.0, 2.0] )

        # move our scene nodes
        self.sn1.translate_object(
            [ 0.0,10.0, 0.0 ]
            )
        self.sn2.translate_object(
            [10.0, 0.0, 0.0 ]
            )
        self.sn3.translate_object(
            [ 5.0, 0.0, 0.0 ]
            )

        # rotate the scene so it is tilting forward
        self.sn1.rotate_object_x( math.pi / 4.0 )

        # create a camera and a view matrix
        self.view_matrix = ProjectionViewMatrix(
            self.viewport.aspect_ratio,
            fov = 60.0,
            near_clip = 1.0,
            far_clip = 200.0
            )
        self.camera = CameraNode(
            'camera',
            self.view_matrix
            )
        self.scene_node.add_child( self.camera )

        # move the camera so we're not inside
        # the root scene node's debug cube
        self.camera.translate_object(
            [ 0.0, 20.0, 40.0 ]
            )

        # set the viewports camera
        self.viewport.set_camera( self.scene_node, self.camera )

        glEnable( GL_DEPTH_TEST )
    
    def run( self ):
        pyglet.app.run()
    
    def step( self, dt ):
        # rotate the scene nodes about their vertical axis
        self.sn1.rotate_object_y( dt )
        self.sn2.rotate_object_y( dt )

        # clear our frame buffer and depth buffer
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

        # render the scene
        viewports = [ self.viewport ]
        pygly.window.render( self.window, viewports )

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

