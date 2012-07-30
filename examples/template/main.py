import math
import time
import random

from pyglet.gl import *
import pyglet
import numpy

import pygly.gl
import pygly.sorter
from pygly.scene_node import SceneNode
from pygly.camera_node import CameraNode

from common import BaseApplication



class Application( BaseApplication ):
    
    def __init__( self ):
        super( Application, self ).__init__()
        
    def setup_camera( self ):
        super( Application, self ).setup_camera()

        # move the camera so we can see the grid
        self.camera.transform.inertial.translate(
            [ 0.0, 10.0, 20.0 ]
            )
        # rotate the camera so it is pointing down
        self.camera.transform.object.rotate_x( -math.pi / 4.0 )

    def setup_ui( self ):
        super( Application, self ).setup_ui()

        self.help_label = pyglet.text.HTMLLabel(
"""
<b>PyGLy Template</b>
""",
        multiline = True,
        x = 10,
        y = 50,
        width = 500,
        anchor_x = 'left',
        anchor_y = 'bottom',
        )
        self.help_label.color = (255,255,255,255)

    def setup_scene( self ):
        super( Application, self ).setup_scene()

        # set our gl clear colour
        glClearColor( 0.2, 0.2, 0.2, 1.0 )

        # CREATE SCENE HERE
        pass

    def update_mouse( self, dt ):
        # USE MOUSE VALUES HERE
        pass

        # reset the relative position of the mouse
        super( Application, self ).update_mouse( dt )

    def on_key_event( self, digital, event, key ):
        # HANDLE KEYBOARD INPUT HERE
        pass

    def update_scene( self, dt ):
        # UPDATE SCENE HERE
        pass

    def render_3d( self ):
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

        # sort our renderables
        positions = [ obj.world_transform.translation for obj in self.renderables ]

        sort_function = pygly.sorter.sort_radius_back_to_front

        sorted_renderables = sort_function(
            self.camera.world_transform.translation,
            -(self.camera.transform.object.z),
            self.renderables,
            positions
            )

        # render each object
        for renderable in sorted_renderables:
            renderable.render()

    def render_2d( self ):
        super( Application, self ).render_2d()

        self.help_label.draw()


def main():
    # create app
    app = Application()
    app.run()
    app.window.close()


if __name__ == "__main__":
    main()

