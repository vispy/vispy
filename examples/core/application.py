"""Adds FPS counter to the PyGLy example application.
We have to print the Core FPS out because pyglet
labels use OpenGL Legacy code.
"""
from time import time

from examples.application import Application


class CoreApplication( Application ):
    
    def __init__( self, config ):
        """Adds an FPS counter.
        """
        super( CoreApplication, self ).__init__( config )

        # set our start time
        self.time = time()
        self.frame_count = 0
        self.print_time = 2.0
    
    def step( self, dt ):
        """Updates the FPS.
        """
        # this will trigger the draw event and buffer flip
        super( CoreApplication, self ).step( dt )

        # update our FPS
        self.frame_count += 1
        # get the latest time
        new_time = time()
        diff = new_time - self.time
        if diff > self.print_time:
            print "FPS:",float(self.frame_count) / diff
            self.time = new_time
            self.frame_count = 0

