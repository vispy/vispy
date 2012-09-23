"""Demonstrates PyGLy's functionality.
Renders a simple scene graph and controls
a viewport.
Viewport is provided without any high level
wrappers and is entirely managed through events.
"""
from time import time

import pyglet
from pyglet.gl import *

import pygly.window
import pygly.gl
from pygly.projection_view_matrix import ProjectionViewMatrix
from pygly.scene_node import SceneNode
from pygly.camera_node import CameraNode
from pyrr import matrix44

# over-ride the default pyglet idle loop
import pygly.monkey_patch
pygly.monkey_patch.patch_idle_loop()


class Application( object ):
    
    def __init__( self, gl_config ):
        """Sets up the core functionality we need
        to begin rendering.
        This includes the OpenGL configuration, the
        window, the viewport, the event handler
        and update loop registration.
        """
        super( Application, self ).__init__()

        # create our window
        self.window = pyglet.window.Window(
            fullscreen = False,
            width = 1024,
            height = 768,
            resizable = True,
            vsync = False,
            config = gl_config,
            )

        # listen for on_draw events
        self.window.push_handlers(
            on_draw = self.on_draw,
            on_resize = self.on_resize,
            )
        
        # setup our update loop the app
        # we don't need to do this to get the window
        # up, but it's nice to show the basic application
        # structure in such a simple app
        # render at max speed
        # this also requires vsync to be False or
        # the render loop will be stuck at the monitor
        # frequency
        self.update_delta = -1

        # use a pyglet callback for our render loop
        pyglet.clock.schedule_interval(
            self.step,
            self.update_delta
            )

        # print some debug info
        pygly.gl.print_gl_info()

        # setup our scene
        self.setup()

    def setup( self ):
        self.setup_viewports()
        self.setup_scene()
        self.setup_camera()

    def setup_viewports( self ):
        # create a viewport that spans
        # the entire screen
        # this list is zip'ed with self.cameras
        # to bind the camera to a viewport for rendering.
        self.viewports = [
            pygly.window.create_rectangle(
                self.window
                )
            ]
        self.colours = [
            (0.0, 0.0, 0.0, 1.0)
            ]

    def setup_scene( self ):
        """Creates the scene to be rendered.
        Creates our camera, scene graph, 
        """
        # enable scissoring for viewports
        glEnable( GL_SCISSOR_TEST )

        # create a scene
        # we'll create the scene as a tree
        # to demonstrate the depth-first iteration
        # technique we will use to render it
        self.scene_node = SceneNode( 'root' )

    def setup_camera( self ):
        # create a camera and a view matrix
        view_matrix = ProjectionViewMatrix(
            pygly.window.aspect_ratio( self.viewports[ 0 ] ),
            fov = 45.0,
            near_clip = 1.0,
            far_clip = 200.0
            )
        camera = CameraNode('camera', view_matrix )
        self.scene_node.add_child( camera )

        # store our camera in a list
        # this list is zip'ed with self.viewports
        # to bind the camera to a viewport for rendering.
        # a camera may appear in this array multiple times
        self.cameras = [ camera ]
    
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
        self.viewports[ 0 ] = pygly.window.create_rectangle(
            self.window
            )

        # we would normally update the viewport ratio
        # here, but because we're allowing a single
        # camera to service multiple viewports, we
        # update them each frame
    
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

    def render( self ):
        # set our window
        self.window.switch_to()

        # render each viewport
        for viewport, camera, colour in zip( self.viewports, self.cameras, self.colours ):
            glClearColor( *colour )


            # render the viewport
            self.render_viewport(
                viewport,
                camera,
                )

        # undo our viewport and our scissor
        pygly.gl.set_scissor(
            pygly.window.create_rectangle( self.window )
            )
        pygly.gl.set_viewport(
            pygly.window.create_rectangle( self.window )
            )

    def render_viewport( self, viewport, camera ):
        # activate our viewport
        pygly.gl.set_viewport( viewport )
        # scissor to our viewport
        pygly.gl.set_scissor( viewport )

        # clear our frame buffer and depth buffer
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

        # update the camera's aspect ratio before
        # we render using it
        # we would normally do this in on_resize
        # but because 1 camera could be used to render
        # to multiple viewports in our example, we
        # will do it each frame
        camera.view_matrix.aspect_ratio = pygly.window.aspect_ratio(
            viewport
            )

        self.render_scene( camera )

    def render_scene( self, camera ):
        pass
    

def main():
    """Main function entry point.
    Simple creates the Application and
    calls 'run'.
    Also ensures the window is closed at the end.
    """
    app = Application()
    app.run()
    app.window.close()


if __name__ == "__main__":
    main()

