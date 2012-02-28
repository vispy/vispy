'''
Created on 28/06/2011

@author: adam
'''

import numpy
from pyglet.gl import *
import pyglet.window.mouse

class Mouse( object ):
    buttons = pyglet.window.mouse
    
    def __init__( self ):
        super( Mouse, self ).__init__()
        
        self.mouseAbs = numpy.zeros( (2), dtype = int )
        self.mouseRel = numpy.zeros( (2), dtype = int )
    
    def attachToWindow( self, window ):
        window.push_handlers( self, self )
    
    def detachFromWindow( self, window ):
        window.remove_handlers( self, self )
    
    def on_mouse_motion( self, x, y, dx, dy ):
        self.mouseAbs[:] = [x, y]
        
        # add our relative values
        self.mouseRel[:] = [
            self.mouseRel[ 0 ] + dx,
            self.mouseRel[ 1 ] + dy
            ]
    
    def clearRelativeValue( self ):
        self.mouseRel.fill( 0 )
    


