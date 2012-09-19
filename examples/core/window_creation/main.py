import pyglet

# disable the shadow window
# this uses a legacy profile and causes issues
# on OS-X
pyglet.options['shadow_window'] = False

from pyglet.gl import *

import pygly.window

# over-ride the default pyglet idle loop
import pygly.monkey_patch
pygly.monkey_patch.patch_idle_loop()

# patch pyglet's OpenGL legacy code out
import pygly.gl.core
pygly.gl.core.patch_window()



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
        # ensure we ask for at least OpenGL 3.2
        # OS-X only supports legacy and Core 3.2
        config = pyglet.gl.Config(
            depth_size = 24,#16,
            double_buffer = True,
            major_version = 3,
            minor_version = 2,
            #forward_compatible = True,
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

        # listen for on_draw events
        self.window.push_handlers(
            on_draw = self.on_draw
            )
        
        # setup our update loop the app
        # we don't need to do this to get the window
        # up, but it's nice to show the basic application
        # structure in such a simple app
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
    
    def run( self ):
        """Begins the Pyglet main loop.
        """
        pyglet.app.run()
    
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
        # clear our frame buffer and depth buffer
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

        pass
    

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

