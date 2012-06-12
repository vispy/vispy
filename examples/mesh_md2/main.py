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
import pygly.gl
from pygly.ratio_viewport import RatioViewport
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
            resizable = True,
            config = config
            )

        # create a viewport
        self.viewport = RatioViewport(
            self.window,
            [ [0.0, 0.0], [1.0, 1.0] ]
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
        self.renderables = []

        # create a scene
        self.scene_node = SceneNode( 'root' )

        # load the md2 and create a renderer object
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
                md2_rotator_node.transform.object.rotate_x( -math.pi / 2.0 )

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
                mesh_node.transform.inertial.translate(
                    [
                        (x * distance) - offset,
                        0.0,
                        (z * distance) + offset
                        ]
                    )

                # add to our list
                self.meshes.append( (mesh, mesh_node) )

                # add to our list of renderables
                self.renderables.append( render_node )
        
        # create a camera and a view matrix
        self.view_matrix = ProjectionViewMatrix(
            self.viewport.aspect_ratio,
            fov = 45.0,
            near_clip = 1.0,
            far_clip = 500.0
            )
        # create a camera
        self.camera = CameraNode(
            'camera',
            self.view_matrix
            )
        self.scene_node.add_child( self.camera )

        # move the camera so we can see the models
        self.camera.transform.object.translate(
            [ 0.0, 75.0, 350.0 ]
            )
        self.camera.transform.object.rotate_x( -math.pi / 4.0 )

        # use a variable for accumulating time
        # for animating the mesh
        self.animation_time = 0.0

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
            mesh_node.transform.object.rotate_y( dt )

        self.render()
        
        # render the fps
        self.fps_display.draw()
        
        # display the frame buffer
        self.window.flip()
            
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

        # enable texturing
        glEnable( self.texture.target )
        glBindTexture( self.texture.target, self.texture.id )

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

        # pyglet has issues with rectangular textures
        # it scales them up to be square powers of 2
        # but it doesn't change the texture coordinates and
        # our textures end up being TOTALLY wrong.
        # so here, we need to get the texture width and height
        # and apply that to our texture matrix
        # instead of being from 0->1, the texture is now from
        # 0->original width
        glMatrixMode( GL_TEXTURE )
        glPushMatrix()

        # texture coords are printed as X,Y,Z triples
        # in the order of:
        # bottom left, bottom right, top right, top left
        glScalef(
            self.texture.tex_coords[ 3 ],
            self.texture.tex_coords[ 7 ],
            1.0
            )
        glMatrixMode( GL_MODELVIEW )

        # clear our frame buffer and depth buffer
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
        
        # render the scene
        for renderable in self.renderables:
            renderable.render()

        # reset the texture matrix because of what we did
        # otherwise any textures following this will be incorrect
        glMatrixMode( GL_TEXTURE )
        glPopMatrix()
        glMatrixMode( GL_MODELVIEW )

        # render the texture on the screen
        texture_y_offset = 80.0
        self.texture.blit( 0.0, texture_y_offset )

        # render the tc's ontop of the texture
        self.meshes[ 0 ][ 0 ].render_tcs(
            (0.0, texture_y_offset),
            (self.texture.width, self.texture.height)
            )

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

