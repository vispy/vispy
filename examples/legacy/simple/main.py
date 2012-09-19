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

# over-ride the default pyglet idle loop
import pygly.monkey_patch
pygly.monkey_patch.patch_idle_loop()

import examples.cube


class Application( object ):
    
    def __init__( self ):
        """Sets up the core functionality we need
        to begin rendering.
        This includes the OpenGL configuration, the
        window, the viewport, the event handler
        and update loop registration.
        """
        super( Application, self ).__init__()
        
        # setup our opengl requirements
        config = pyglet.gl.Config(
            depth_size = 16,
            double_buffer = True,
            )

        # create our window
        self.window = pyglet.window.Window(
            fullscreen = False,
            width = 1024,
            height = 768,
            resizable = True,
            vsync = False,
            config = config,
            )

        # create a viewport that spans
        # the entire screen
        self.viewport = pygly.window.create_rectangle(
            self.window
            )

        # setup our scene
        self.setup_scene()

        # listen for events from pyglet events
        self.window.push_handlers(
            on_draw = self.on_draw,
            on_resize = self.on_resize,
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

        # print some debug info
        pygly.gl.print_gl_info()

    def setup_scene( self ):
        """Creates the scene to be rendered.
        Creates our camera, scene graph, 
        """
        # create our cube renderable
        examples.cube.create()

        # create an fps display
        self.fps_display = pyglet.clock.ClockDisplay()

        # create a scene
        # we'll create the scene as a tree
        # to demonstrate the depth-first iteration
        # technique we will use to render it
        self.scene_node = SceneNode( 'root' )

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

        # create a camera and a view matrix
        self.view_matrix = ProjectionViewMatrix(
            pygly.window.aspect_ratio( self.viewport ),
            fov = 45.0,
            near_clip = 1.0,
            far_clip = 200.0
            )
        self.camera = CameraNode('camera', self.view_matrix )
        self.scene_node.add_child( self.camera )

        # move the camera so we're not inside
        # the root scene node's debug cube
        self.camera.transform.object.translate(
            [ 0.0, 30.0, 35.0 ]
            )

        # tilt the camera downward
        self.camera.transform.object.rotate_x(-math.pi / 4.0 )

    def run( self ):
        """Begins the Pyglet main loop.
        """
        pyglet.app.run()

    def on_resize( self, width, height ):
        """Called when the window is resized.
        Pyglet fires an on_resize event and this
        is where we handle it.
        We need to update our view matrix with respect
        to our viewport size, or the content will become
        skewed.
        """
        # update the viewport size
        self.viewport = pygly.window.create_rectangle(
            self.window
            )

        # update the view matrix aspect ratio
        self.camera.view_matrix.aspect_ratio = pygly.window.aspect_ratio(
            self.viewport
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
        # setup the scene
        # rotate the scene nodes about their vertical axis
        self.a1.transform.object.rotate_y( dt )
        self.b1.transform.object.rotate_y( dt )
        self.b2.transform.object.rotate_y( dt )
        self.c1.transform.object.rotate_y( dt )
        self.c2.transform.object.rotate_y( dt )
        self.c3.transform.object.rotate_y( dt )

        # manually dispatch the on_draw event
        # as we patched it out of the idle loop
        self.window.dispatch_event( 'on_draw' )

        # display the frame buffer
        self.window.flip()

    def on_draw( self ):
        """Triggered by the pyglet 'on_draw' event.
        Causes the scene to be rendered.
        """
        self.render()

        # render the fps
        self.fps_display.draw()

    def set_gl_state( self ):
        """Called during rendering to set our
        viewports GL state.
        This sets up things like depth testing,
        smooth shading and back face culling.
        """
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
        """Sets the active window and triggers
        the rendering of the scene to the viewport.
        """
        # set our window
        self.window.switch_to()

        # render the scene with our primary viewport
        # pass in our camera's model view matrix
        self.render_viewport(
            self.viewport,
            self.camera.view_matrix.matrix,
            self.camera.model_view
            )

    def render_viewport( self, viewport, projection, model_view ):
        # setup our viewport
        with pygly.gl.legacy.attributes( GL_ALL_ATTRIB_BITS ):
            # activate our viewport
            pygly.gl.set_viewport( viewport )
            # scissor to our viewport
            pygly.gl.set_scissor( viewport )
            # set our gl attributes
            self.set_gl_state()

            # clear our frame buffer and depth buffer
            glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

            # apply our view matrix
            # we can't mix these or we will pop the wrong
            # matrix
            with legacy.matrix_mode( GL_PROJECTION ):
                with legacy.load_matrix( projection ):
                    with legacy.matrix_mode( GL_MODELVIEW ):
                        with legacy.load_matrix( model_view ):
                            self.render_scene()


    def render_scene( self ):
        """Renders each renderable in the scene
        using the current projection and model
        view matrix.
        The original GL state will be restored
        upon leaving this function.
        """
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
                examples.cube.draw()


def main():
    """Main function entry point.
    Simple creates the Application and
    calls 'run'.
    Also ensures the window is closed at the end.
    """
    # create app
    app = Application()
    app.run()
    app.window.close()


if __name__ == "__main__":
    main()

