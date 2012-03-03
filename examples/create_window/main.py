'''
Created on 15/06/2011

@author: adam

TODO: use resource locations
http://www.pyglet.org/doc/programming_guide/loading_resources.html
'''

from pyglet.gl import *
import pyglet

# over-ride the default pyglet idle loop
import renderer.idle
from renderer.window import Window


class Application( object ):
    
    def __init__( self ):
        super( Application, self ).__init__()
        
        # setup our opengl requirements
        config = pyglet.gl.Config(
            depth_size = 16,
            double_buffer = True
            )

        # create our window
        self.window = Window(
            pyglet.window.Window(
                fullscreen = False,
                width = 1024,
                height = 768,
                config = config
                )
            )
        
        # setup our update loop the app
        frequency = 60.0
        self.update_delta = 1.0 / frequency
        pyglet.clock.schedule_interval( self.step, self.update_delta )
        print "Rendering at %iHz" % int(frequency)
    
    def run( self ):
        pyglet.app.run()
    
    def step( self, dt ):
        # update the scene
        self.window.render( [] )

        # display the frame buffer
        self.window.flip()
    

def main():
    # create app
    app = Application()
    app.run()
    app.window.close()


if __name__ == "__main__":
    main()

