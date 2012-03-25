'''
Created on 15/06/2011

@author: adam
'''

from pyglet.gl import *
import pyglet

# over-ride the default pyglet idle loop
import renderer.idle
import renderer.window


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
        
        # setup our update loop the app
        # we don't need to do this to get the window
        # up, but it's nice to show the basic application
        # structure in such a simple app
        # we'll render at 60 fps
        frequency = 60.0
        self.update_delta = 1.0 / frequency
        self.fps_display = pyglet.clock.ClockDisplay()
        # use a pyglet callback for our render loop
        pyglet.clock.schedule_interval(
            self.step,
            self.update_delta
            )

        print "Rendering at %iHz" % int(frequency)
    
    def run( self ):
        pyglet.app.run()
    
    def step( self, dt ):
        # render the scene
        viewports = []
        renderer.window.render( self.window, viewports )

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

