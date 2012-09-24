"""Demonstrates the interoperability of
PyGLy (or any other OpenGL application)
with Cocos2D.

Requires Cocos2D to be installed.
 pip install cocos2d
"""
#
# PyGLy code
#

import math

from pyglet.gl import *

import pygly.window
from pygly.projection_view_matrix import ProjectionViewMatrix
from pygly.scene_node import SceneNode
from pygly.render_callback_node import RenderCallbackNode
from pygly.camera_node import CameraNode
from pygly.cocos2d.layer import PyGLyLayer

from examples.legacy.simple.main import SimpleApplication


class PyglyScene( SimpleApplication ):

    def __init__( self ):
        # don't call our super constructors

        # store the window for our viewport function
        # to access
        self.window = cocos.director.director.window

        # print some debug info
        pygly.gl.print_gl_info()

        # setup our scene
        self.setup()

        # this must be done after the
        # director is initialised or the
        # program will crash since the window
        # won't have been created
        self.layer = PyGLyLayer(
            camera = self.cameras[ 0 ],
            render_callback = self.render
            )

        # register our on_resize handler
        self.window.push_handlers(
            on_resize = self.on_resize
            )

    def render( self, layer, *args, **kwargs ):
        super( PyglyScene, self ).render()

# the following cocos2d example is from
# the following url
# http://los-cocos.googlecode.com/svn/trunk/samples/hello_world.py

#
# cocos2d
# http://cocos2d.org
#
# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

import cocos

class HelloWorld(cocos.layer.Layer):
    def __init__(self):
        super( HelloWorld, self ).__init__()
        # a cocos.text.Label is a wrapper of pyglet.text.Label
        # with the benefit of being a cocosnode
        label = cocos.text.Label('Hello, World!',
        font_name='Times New Roman',
        font_size=32,
        anchor_x='center', anchor_y='center')

        label.position = 320,240
        self.add( label )

if __name__ == "__main__":
    # director init takes the same arguments as pyglet.window
    cocos.director.director.init()

    # We create a new layer, an instance of HelloWorld
    hello_layer = HelloWorld ()

    # A scene that contains the layer hello_layer
    main_scene = cocos.scene.Scene (hello_layer)

    pygly_scene = PyglyScene()
    main_scene.add( pygly_scene.layer, name = "pygly" )

    # And now, start the application, starting with main_scene
    cocos.director.director.run (main_scene)

    # or you could have written, without so many comments:
    #      director.run( cocos.scene.Scene( HelloWorld() ) )
