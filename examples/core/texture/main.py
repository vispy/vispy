"""Demonstrate's PyGLy's texture loading algorithms.
Loads textures from examples/data/textures/*
(assuming they have an accepted extension) and
renders them to a Quad.
Left and Right arrows switch textures.
"""
import os
import math
from time import time

from PIL import Image
import numpy
import pyglet

# disable the shadow window
# this uses a legacy profile and causes issues
# on OS-X
pyglet.options['shadow_window'] = False

from pyglet.gl import *

import pygly.window
import pygly.gl
from pygly.scene_node import SceneNode
from pygly.camera_node import CameraNode
from pygly.orthogonal_view_matrix import OrthogonalViewMatrix
import pygly.texture
from pygly.texture import Texture
from pyrr import matrix44

# patch pyglet's OpenGL legacy code out
import pygly.gl.core
pygly.gl.core.patch_window()

from examples.core.application import CoreApplication
from examples.core.simple.main import SimpleApplication
import examples.core.quad as quad


class TextureApplication( SimpleApplication ):

    def setup_viewports( self ):
        super( TextureApplication, self ).setup_viewports()

        # change our clear colour
        self.colours[ 0 ] = ( 0.5, 0.5, 0.5, 1.0 )

    def setup_scene( self ):
        """Creates the scene to be rendered.
        Creates our camera, scene graph, 
        """
        CoreApplication.setup_scene( self )

        # register our key press listener
        self.window.push_handlers(
            on_key_press = self.on_key_press
            )

        # setup our GL state
        # enable z buffer
        glEnable( GL_DEPTH_TEST )

        # enable back face culling
        glEnable( GL_CULL_FACE )
        glCullFace( GL_BACK )

        # enable alpha blending
        glEnable( GL_BLEND )
        glBlendFunc(
            GL_ONE,
            GL_ONE_MINUS_SRC_ALPHA
            )

        # create our cube renderable
        quad.create()

        # create our quad
        self.node = SceneNode( 'quad' )
        self.scene_node.add_child( self.node )

        # the quad is from -1:+1, so scale down to -0.5:+0.5
        self.node.world_transform.scale = [0.5, 0.5, 0.5]

        # load our textures
        self.textures = []
        self.current_texture = 0
        self.load_textures( 'examples/data/textures' )
        self.load_random_data()
        self.print_texture_name()

    def load_textures( self, directory ):
        print 'Loading images from', directory

        extensions = [
            '.png',
            '.jpg',
            '.jpeg',
            '.tif',
            '.bmp',
            '.exr',
            ]

        for filename in os.listdir( directory ):
            name, extension = os.path.splitext( filename )
            if extension not in extensions:
                continue

            try:
                print filename,
                full_path = '%s/%s' % (directory, filename)

                image = Image.open( full_path )
                if image.verify() == False:
                    print 'image damaged', filename
                    continue

                image = Image.open( full_path )
                print image.format, image.mode, image.getbands()

                texture = Texture( GL_TEXTURE_2D )
                texture.bind()
                texture.set_min_mag_filter(
                    min = GL_NEAREST,
                    mag = GL_NEAREST
                    )
                pygly.texture.set_pil_texture_2d( image )
                texture.unbind()

                self.textures.append( (filename, texture) )
            except IOError as e:
                print 'Exception:', e

    def load_random_data( self ):
        # create a random RGB texture
        data = numpy.random.random_integers( 120, 255, (32,32,3) )
        texture = Texture( GL_TEXTURE_2D )
        texture.bind()
        pygly.texture.set_raw_texture_2d( data.astype('uint8') )
        texture.set_min_mag_filter(
            min = GL_NEAREST,
            mag = GL_NEAREST
            )
        texture.unbind()

        self.textures.append( ('Random RGB',texture) )

        # create a random luminance texture
        data = numpy.random.random_integers( 120, 255, (32,32,1) )
        texture = Texture( GL_TEXTURE_2D )
        texture.bind()
        texture.set_swizzle( (GL_RED, GL_RED, GL_RED, GL_ONE) )
        pygly.texture.set_raw_texture_2d(
            data.astype('uint8'),
            format = GL_RED,
            internal_format = GL_RGBA,
            )
        texture.set_min_mag_filter(
            min = GL_NEAREST,
            mag = GL_NEAREST
            )
        texture.unbind()

        self.textures.append( ('Random Luminance',texture) )

    def setup_camera( self ):
        # over-ride SimpleApplication's camera
        CoreApplication.setup_camera( self )

        # change our view matrix to an orthogonal one
        self.cameras[ 0 ].view_matrix = OrthogonalViewMatrix(
            pygly.window.aspect_ratio( self.viewports[ 0 ] ),
            scale = [1.0, 1.0],
            near_clip = 1.0,
            far_clip = 200.0
            )

        # move the camera so we're not inside
        # the root scene node's debug cube
        self.cameras[ 0 ].transform.object.translate(
            [ 0.0, 0.0, 35.0 ]
            )
    
    def step( self, dt ):
        """Updates our scene and triggers the on_draw event.
        This is scheduled in our __init__ method and
        called periodically by pyglet's event callbacks.
        We need to manually call 'on_draw' as we patched
        it our of pyglets event loop when we patched it
        out with pygly.monkey_patch.
        Because we called 'on_draw', we also need to
        perform the buffer flip at the end.
        """
        CoreApplication.step( self, dt )

    def on_key_press( self, symbol, modifiers ):
        # change textures
        if symbol == pyglet.window.key.LEFT:
            self.current_texture -= 1
            if self.current_texture < 0:
                self.current_texture = len(self.textures) - 1
            self.print_texture_name()
        elif symbol == pyglet.window.key.RIGHT:
            self.current_texture += 1
            if self.current_texture >= len(self.textures):
                self.current_texture = 0
            self.print_texture_name()

    def print_texture_name( self ):
        print 'Current texture:', self.textures[ self.current_texture ][ 0 ]

    def render_scene( self, camera ):
        """Renders each renderable in the scene
        using the current projection and model
        view matrix.
        The original GL state will be restored
        upon leaving this function.
        """
        projection = camera.view_matrix.matrix
        model_view = camera.model_view

        # calculate a new model view
        world_matrix = self.node.world_transform.matrix
        current_mv = matrix44.multiply(
            world_matrix,
            model_view
            )

        # bind our texture
        texture = self.textures[ self.current_texture ][ 1 ]
        texture.bind()

        # render a cube
        quad.draw( projection, current_mv )

        texture.unbind()
    

def main():
    """Main function entry point.
    Simple creates the Application and
    calls 'run'.
    Also ensures the window is closed at the end.
    """
    # create app
    app = TextureApplication()
    app.run()
    app.window.close()


if __name__ == "__main__":
    main()

