'''
Created on 24/06/2011

@author: adam
'''

from pyglet.gl import *
import pyglet.window.key


class Keyboard( object ):
    # allow access to pyglet.window.key
    keys = pyglet.window.key
    
    def __init__( self ):
        super( Keyboard, self ).__init__()
        
        self.keyState = pyglet.window.key.KeyStateHandler()
    
    def attachToWindow( self, window ):
        window.push_handlers( self, self.keyState )
    
    def detachFromWindow( self, window ):
        window.remove_handlers( self, self.keyState )
    
    def isKeyDown( self, key ):
        return self.keyState[ key ]
    
    def __getitem__( self, k ):
        # Handles [] operator
        # redirect to our keyboard handler
        return self.keyState[ k ]
    
    def registerHandler( self, handler ):
        pass
    
    def unregisterHandler( self, handler ):
        pass
    
    def on_key_press( self, symbol, modifiers ):
        """
        Pyglet event handler method.
        """
        print "Keypress"
        pass
    
    def on_key_release( self, symbol, modifiers ):
        """
        Pyglet event handler method.
        """
        print "Keyrelease"
        pass


if __name__ == "__main__":
    from pyglet.gl import *
    
    keyboard = Keyboard()
    
    window = pyglet.window.Window( fullscreen = False )
    
    keyboard.attachToWindow( window )
    
    def update( dt ):
        global keyboard
        if keyboard[ keyboard.keys.SPACE ]:
            print "SPACE is down"
        #else:
        #    print "SPACE is NOT down"
    
    pyglet.clock.schedule_interval( update, (1.0 / 60.0) )
    pyglet.app.run()
    
    keyboard.detachFromWindow( window )
    
    

