'''
Created on 15/06/2011

@author: adam

TODO: use resource locations
http://www.pyglet.org/doc/programming_guide/loading_resources.html
'''

import math
import time
import random

import numpy
import pyglet
from pyglet.gl import *

import pygly.window
from pygly.viewport import Viewport
from pygly.projection_view_matrix import ProjectionViewMatrix
from pygly.scene_node import SceneNode
from pygly.camera_node import CameraNode
from pygly.render_callback_node import RenderCallbackNode
from pygly.mesh.md2_mesh import MD2_Mesh
from pygly.mesh.md2_renderer import MD2_Renderer

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

        # create a viewport
        self.viewport = Viewport(
            pygly.window.create_rectangle(
                self.window
                )
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
        self.scene_node = SceneNode( 'root' )

        # load the md2 and create a renderer object
        # for it
        self.md2_renderer = MD2_Renderer(
            'examples/data/md2/sydney.md2',
            interpolate = 0
            )
        self.image = None
        self.texture = None

        self.meshes = []
        distance = 50.0
        num_meshes = 5
        offset = distance * (float(num_meshes - 1.0) / 2.0)

        values = numpy.arange( num_meshes )
        for x in values:
            for z in values:
                # create a scene node
                # so we can control the location and
                # orientation of the mesh
                mesh_node = SceneNode( 'mesh' )
                self.scene_node.add_child( mesh_node )

                # the md2 is oriented at 90 degrees about X
                # re-orient the mesh
                md2_rotator_node = SceneNode( 'md2_rotate' )
                mesh_node.add_child( md2_rotator_node )
                md2_rotator_node.rotate_object_x( -math.pi / 2.0 )

                # create a mesh
                mesh = MD2_Mesh(
                    self.md2_renderer
                    )
                # set the frame to a random value
                mesh.frame = random.random() * float(mesh.num_frames)

                # create a render node for the mesh
                render_node = RenderCallbackNode(
                    'mesh',
                    self.initialise_mesh,
                    mesh.render
                    )
                md2_rotator_node.add_child( render_node )

                # move the mesh so we can see it
                mesh_node.translate_inertial(
                    [
                        (x * distance) - offset,
                        0.0,
                        (z * distance) + offset
                        ]
                    )

                # add to our list
                self.meshes.append( (mesh, mesh_node) )
        
        # create a camera and a view matrix
        self.view_matrix = ProjectionViewMatrix(
            self.viewport.aspect_ratio,
            fov = 60.0,
            near_clip = 1.0,
            far_clip = 500.0
            )
        # create a camera
        self.camera = CameraNode(
            'camera',
            self.view_matrix
            )
        self.scene_node.add_child( self.camera )

        self.camera.translate_object(
            [ 0.0, 75.0, 350.0 ]
            )
        self.camera.rotate_object_x( -math.pi / 4.0 )
        
        # set the viewports camera
        self.viewport.set_camera( self.scene_node, self.camera )

        # use a variable for accumulating time
        # for animating the mesh
        self.animation_time = 0.0

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

        
    def setup_viewport( self ):
        # use the z-buffer when drawing
        glEnable( GL_DEPTH_TEST )

        # normalise any normals for us
        glEnable( GL_RESCALE_NORMAL )

        # enable us to clear viewports independently
        glEnable( GL_SCISSOR_TEST )

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

    def initialise_mesh( self ):
        # load the mesh
        if self.md2_renderer.num_frames == 0:
            self.md2_renderer.load()

        if self.image == None:
            # load our texture
            # use the PIL decoder as the pyglet one is broken
            # and loads most images as greyscale
            self.image = pyglet.image.load(
                'examples/data/md2/sydney_h.bmp',
                decoder=pyglet.image.codecs.pil.PILImageDecoder()
                )
        if self.texture == None:
            self.texture = self.image.get_texture( rectangle = True )

    def render_mesh( self ):
        self.mesh.render()

    def run( self ):
        pyglet.app.run()
    
    def step( self, dt ):
        # add the current time to the animation
        self.animation_time += dt * 10.0

        for mesh, mesh_node in self.meshes:
            # check if we should move to the next frame
            # 10 fps
            fnum_frames = float( mesh.num_frames )
            mesh.frame = math.fmod(
                mesh.frame + dt * 10.0,
                fnum_frames - 1.0
                )

            # rotate the mesh about it's own vertical axis
            mesh_node.rotate_object_y( dt )

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
        pygly.window.render( self.window, viewports )

        # reset the texture matrix because of what we did
        # otherwise any textures following this will be incorrect
        glMatrixMode( GL_TEXTURE )
        glLoadIdentity()
        glMatrixMode( GL_MODELVIEW )

        # render the texture on the screen
        texture_y_offset = 80.0
        self.texture.blit( 0.0, texture_y_offset )

        # render the tc's ontop of the texture
        self.meshes[ 0 ][ 0 ].render_tcs(
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

