"""Demonstrates PyGLy's functionality.
Renders a simple scene graph and controls
a viewport.
Viewport is provided without any high level
wrappers and is entirely managed through events.
"""
import math

from pyglet.gl import *
import pyglet

import pygly.window
import pygly.gl
from pygly.gl import legacy
from pygly.projection_view_matrix import ProjectionViewMatrix
from pygly.scene_node import SceneNode
from pygly.camera_node import CameraNode

from examples.application import Application
import examples.legacy.cube as cube


class SimpleApplication( Application ):
    
    def __init__( self ):
        """Sets up the core functionality we need
        to begin rendering.
        This includes the OpenGL configuration, the
        window, the viewport, the event handler
        and update loop registration.
        """
        # setup our opengl requirements
        config = pyglet.gl.Config(
            depth_size = 16,
            double_buffer = True,
            )

        super( SimpleApplication, self ).__init__( config )

    def setup_scene( self ):
        """Creates the scene to be rendered.
        Creates our camera, scene graph, 
        """
        super( SimpleApplication, self ).setup_scene()

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

        # create our cube renderable
        cube.create()

        # create an fps display
        self.fps_display = pyglet.clock.ClockDisplay()

        # the letter indicates the tier the node
        # is on, a = tier 1, b = tier 2, etc.
        self.a1 = SceneNode( 'a1' )
        self.b1 = SceneNode( 'b1' )
        self.b2 = SceneNode( 'b2' )
        self.c1 = SceneNode( 'c1' )
        self.c2 = SceneNode( 'c2' )
        self.c3 = SceneNode( 'c3' )

        # the tree looks as follows
        #                / c1
        #           / b1 - c2
        # root - a1
        #           \ b2 - c3
        self.scene_node.add_child( self.a1 )
        self.a1.add_child( self.b1 )
        self.a1.add_child( self.b2 )
        self.b1.add_child( self.c1 )
        self.b1.add_child( self.c2 )
        self.b2.add_child( self.c3 )

        # if we set the nodes local scale (transform)
        # it will be affected by the parent's scale.
        # by setting the world scale (world_transform)
        # we are ignoring the parent's scale.
        # re-attaching the node would invalidate this.
        self.a1.world_transform.scale = [2.0, 2.0, 2.0]
        self.b1.world_transform.scale = [1.0, 1.0, 1.0]
        self.b2.world_transform.scale = [1.0, 1.0, 1.0]
        self.c1.world_transform.scale = [0.8, 0.8, 0.8]
        self.c2.world_transform.scale = [0.8, 0.8, 0.8]
        self.c3.world_transform.scale = [0.8, 0.8, 0.8]

        # move our scene nodes
        # leave a1 at the centre
        self.b1.transform.object.translate( [10.0, 0.0, 0.0 ] )
        self.b2.transform.object.translate([-10.0, 0.0, 0.0 ] )
        self.c1.transform.object.translate( [ 5.0, 0.0, 0.0 ] )
        self.c2.transform.object.translate( [-5.0, 0.0, 0.0 ] )
        self.c3.transform.object.translate( [ 5.0, 0.0, 0.0 ] )

        # rotate the our b nodes so they tilting forward
        self.b1.transform.object.rotate_x( math.pi / 4.0 )
        self.b2.transform.object.rotate_x( math.pi / 4.0 )

    def setup_camera( self ):
        super( SimpleApplication, self ).setup_camera()

        # move the camera so we're not inside
        # the root scene node's debug cube
        self.cameras[ 0 ].transform.object.translate(
            [ 0.0, 30.0, 35.0 ]
            )

        # tilt the camera downward
        self.cameras[ 0 ].transform.object.rotate_x(-math.pi / 4.0 )

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
        # setup the scene
        # rotate the scene nodes about their vertical axis
        self.a1.transform.object.rotate_y( dt )
        self.b1.transform.object.rotate_y( dt )
        self.b2.transform.object.rotate_y( dt )
        self.c1.transform.object.rotate_y( dt )
        self.c2.transform.object.rotate_y( dt )
        self.c3.transform.object.rotate_y( dt )

        # this will trigger the draw event and buffer flip
        super( SimpleApplication, self ).step( dt )

    def render( self ):
        """Sets the active window and triggers
        the rendering of the scene to the viewport.
        """
        super( SimpleApplication, self ).render()

        # render the fps
        self.fps_display.draw()

    def render_scene( self, projection, model_view ):
        """Renders each renderable in the scene
        using the current projection and model
        view matrix.
        The original GL state will be restored
        upon leaving this function.
        """
        # apply our view matrix
        # we can't nest these due python not
        # closing context managers in reverse order
        # if we nest these, it will first pop the projection
        # matrix mode, then try and pop the projection matrix
        # from the model view stack!
        with legacy.matrix_mode( GL_PROJECTION ):
            with legacy.load_matrix( projection ):
                with legacy.matrix_mode( GL_MODELVIEW ):
                    with legacy.load_matrix( model_view ):
                        self.render_scene_graph()

    def render_scene_graph( self ):
        # begin iterating through our scene graph
        # as we iterate over each node, we will set
        # our model view matrix as the node's world
        # matrix and render a cube at that location.
        # we can iterate using any method, but we'll
        # use depth first here
        for node in self.scene_node.dfs():
            if isinstance( node, CameraNode ):
                continue

            model_matrix = node.world_transform.matrix

            # multiply the existing model view matrix
            # by the model's world matrix
            # then render a cube
            with legacy.multiply_matrix( model_matrix ):
                cube.draw()


def main():
    """Main function entry point.
    Simple creates the Application and
    calls 'run'.
    Also ensures the window is closed at the end.
    """
    # create app
    app = SimpleApplication()
    app.run()
    app.window.close()


if __name__ == "__main__":
    main()

