"""Adds FPS display to the PyGLy example application.
"""
import pyglet

from examples.application import Application


class LegacyApplication( Application ):
    
    def __init__( self, config ):
        """Sets up the core functionality we need
        to begin rendering.
        This includes the OpenGL configuration, the
        window, the viewport, the event handler
        and update loop registration.
        """
        super( LegacyApplication, self ).__init__( config )

    def setup_scene( self ):
        """Creates the scene to be rendered.
        Creates our camera, scene graph, 
        """
        super( LegacyApplication, self ).setup_scene()
        
        # create an fps display
        self.fps_display = pyglet.clock.ClockDisplay()

    def render( self ):
        """Sets the active window and triggers
        the rendering of the scene to the viewport.
        """
        super( LegacyApplication, self ).render()

        # render the fps
        self.fps_display.draw()

