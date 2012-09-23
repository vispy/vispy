"""Demonstrates PyGLy's functionality.
Renders a simple scene graph and controls
a viewport.
Viewport is provided without any high level
wrappers and is entirely managed through events.
"""
import math

import numpy
from pyglet.gl import *

from pygly.scene_node import SceneNode
import pygly.sorter
from pygly.gl import legacy

from examples.legacy.simple.main import SimpleApplication
from examples.legacy.application import LegacyApplication
import examples.legacy.colour_cube as cube


class SortingApplication( SimpleApplication ):
    
    def setup_scene( self ):
        """Creates the scene to be rendered.
        Creates our camera, scene graph, 
        """
        # don't call 'SimpleApplication's setup_scene
        LegacyApplication.setup_scene( self )

        # setup our GL state
        # enable z buffer
        glEnable( GL_DEPTH_TEST )

        # enable back face culling
        glEnable( GL_CULL_FACE )
        glCullFace( GL_BACK )

        # create our cube renderable
        cube.create()

        # create a grid of cubes
        self.grid_root = SceneNode( 'grid_root' )
        self.scene_node.add_child( self.grid_root )

        # create a number of cubes
        # the grid will extend from -5 to +5
        x,z = numpy.mgrid[
            -5:5:11j,
            -5:5:11j
            ]
        x = x.flatten()
        z = z.flatten()

        positions = numpy.vstack(
            (x, numpy.zeros( x.shape ), z )
            )
        positions = positions.T

        # set the distance of the cubes
        # cube is -1 -> 1
        # so distance is 2
        positions *= 2.5

        # store a list of renderables
        self.renderables = []

        for position in positions:
            node = SceneNode( 'node-%s' % position )
            node.transform.inertial.translation = position
            self.grid_root.add_child( node )
            self.renderables.append( node )

        # create a range of colours from 0.0 -> 1.0
        self.colours = numpy.linspace( 0.0, 1.0, len(positions) )
        # make them consistent for RGBA
        self.colours = self.colours.repeat( 4 )
        self.colours.shape = -1, 4
        # replace A with 1.0
        self.colours[:,3] = 1.0

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
        # rotate the grid root node
        # we can't rotate the root scene node because
        # that will rotate the camera too
        self.grid_root.transform.object.rotate_y( dt )

        # this will trigger the draw event and buffer flip
        super( SimpleApplication, self ).step( dt )

    def render_scene_graph( self, camera ):
        # begin iterating through our scene graph
        # as we iterate over each node, we will set
        # our model view matrix as the node's world
        # matrix and render a cube at that location.
        # we can iterate using any method, but we'll
        # use depth first here

        # sort our scene
        # extract the positions of all our renderables
        positions = [
            node.world_transform.translation for node in self.renderables
            ]

        # sort our renderables based on their position
        # from the camera
        # sort based on the -Z axis (the direction the
        # camera faces)
        sorted = pygly.sorter.sort_radius_back_to_front(
            camera.world_transform.translation,
            -(camera.transform.object.z),
            self.renderables,
            positions
            )

        for node, colour in zip(sorted, self.colours):
            model_matrix = node.world_transform.matrix

            # multiply the existing model view matrix
            # by the model's world matrix
            # then render a cube
            with legacy.multiply_matrix( model_matrix ):
                cube.draw( colour )


def main():
    """Main function entry point.
    Simple creates the Application and
    calls 'run'.
    Also ensures the window is closed at the end.
    """
    # create app
    app = SortingApplication()
    app.run()
    app.window.close()


if __name__ == "__main__":
    main()

