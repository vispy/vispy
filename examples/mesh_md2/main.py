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
from mesh.md2_mesh import MD2_Mesh
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
            [ 0.0, 0.0, 1.0, 1.0 ]
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

        self.mesh_node = SceneNode( '/mesh' )
        self.scene_node.add_child( self.mesh_node )

        # create our render node
        # this is seperate to the mesh node because
        # we need to rotate it about it's X axis
        # due to the model being on its side
        self.render_node = RenderCallbackNode(
            '/md2/rendernode',
            self.initialise_mesh,
            self.render_mesh
            )
        self.mesh_node.add_child( self.render_node )

        # the md2 is oriented at 90 degrees about X
        # re-orient the mesh
        self.render_node.rotate_object_x( -math.pi / 2.0 )

        # move the mesh so we can see it
        self.mesh_node.translate_inertial_z( -40.0 )
        
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

        # use a variable for accumulating time
        # for animating the mesh
        self.animation_time = 0.0
        
    def setup_viewport( self ):
        # use the z-buffer when drawing
        glEnable( GL_DEPTH_TEST )

        # enable texturing
        glEnable( self.texture.target )
        glBindTexture( self.texture.target, self.texture.id )

        # enable smooth shading
        # instead of flat shading
        glShadeModel( GL_SMOOTH )
            
        # setup lighting for our viewport
        #glEnable( GL_LIGHTING )

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

    def initialise_mesh( self ):
        self.mesh = MD2_Mesh(
            'examples/data/md2/sydney.md2'
            )
        # load the mesh
        self.mesh.load()

        # load our texture
        # use the PIL decoder as the pyglet one is broken
        # and loads most images as greyscale
        self.image = pyglet.image.load(
            'examples/data/md2/sydney_h.bmp',
            decoder=pyglet.image.codecs.pil.PILImageDecoder()
            )
        self.texture = self.image.get_texture( rectangle = True )

    def render_mesh( self ):
        self.mesh.render()

    def run( self ):
        pyglet.app.run()
    
    def step( self, dt ):
        # add the current time to the animation
        self.animation_time += dt

        # check if we should move to the next frame
        # 10 fps
        self.mesh.frame += dt * 10.0
        if self.mesh.frame > float(len(self.mesh.frames) - 1):
            self.mesh.frame = 0.0

        # rotate the mesh about it's own vertical axis
        self.mesh_node.rotate_object_y( dt )

        # pyglet has issues with rectangular textures
        # it scales them up to be square powers of 2
        # but it doesn't change the texture coordinates and
        # our textures end up being TOTALLY wrong.
        # so here, we need to get the texture width and height
        # and apply that to our texture matrix
        # instead of being from 0->1, the texture is now from
        # 0->original width
        glMatrixMode( GL_TEXTURE )
        glLoadIdentity()
        # texture coords are printed as X,Y,Z triples
        # in the order of, bottom left, bottom right, top right, top left
        glScalef(
            self.texture.tex_coords[ 3 ],
            self.texture.tex_coords[ 7 ],
            1.0
            )
        glMatrixMode( GL_MODELVIEW )

        # clear our frame buffer and depth buffer
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
        
        # render the scene
        viewports = [ self.viewport ]
        renderer.window.render( self.window, viewports )

        # reset the matrix
        glMatrixMode( GL_TEXTURE )
        glLoadIdentity()
        glMatrixMode( GL_MODELVIEW )

        # render the texture on the screen
        texture_y_offset = 80.0
        self.texture.blit( 0.0, texture_y_offset )

        # render the tc's ontop of the texture
        self.mesh.render_tcs(
            (0.0, texture_y_offset),
            (self.texture.width, self.texture.height)
            )
        
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

