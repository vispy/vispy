"""Demonstrates PyGLy's functionality.
Renders a simple scene graph and controls
a viewport.
Viewport is provided without any high level
wrappers and is entirely managed through events.
"""
# import this first
from examples.core.simple.main import SimpleApplication

import math

import numpy
import pyglet
from pyglet.gl import *

from pygly.scene_node import SceneNode
import pygly.sorter
from pyrr import matrix44

from examples.core.application import CoreApplication
import examples.core.colour_cube as cube


class SortingApplication( SimpleApplication ):

    def setup_scene( self ):
        """Creates the scene to be rendered.
        Creates our camera, scene graph, 
        """
        # don't call 'SimpleApplication's setup_scene
        CoreApplication.setup_scene( self )

        # setup our GL state
        # disable z buffer
        glDisable( GL_DEPTH_TEST )

        # enable back face culling
        glEnable( GL_CULL_FACE )
        glCullFace( GL_BACK )

        # enable alpha testing
        glEnable( GL_BLEND )
        glBlendFunc( GL_ONE, GL_ONE_MINUS_SRC_ALPHA )

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

        # create a range of colours from 0.1 -> 0.5
        self.cube_colours = numpy.linspace( 0.1, 0.5, len(positions) )
        # make them consistent for RGBA
        self.cube_colours = self.cube_colours.repeat( 4 )
        self.cube_colours.shape = -1, 4
        # replace the alpha value
        self.cube_colours[:,2] = 0.5
        self.cube_colours[:,3] = 0.5

    def setup_camera( self ):
        CoreApplication.setup_camera( self )

        # move the camera so we're not inside
        # the root scene node's debug cube
        self.cameras[ 0 ].transform.object.translate(
            [ 0.0, 10.0, 15.0 ]
            )

        # tilt the camera downward
        self.cameras[ 0 ].transform.object.rotate_x(-math.pi / 4.0 )

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
        self.grid_root.transform.object.rotate_y( dt * 0.2 )

        # this will trigger the draw event and buffer flip
        super( SimpleApplication, self ).step( dt )

    def render_scene( self, camera ):
        """Renders each renderable in the scene
        using the current projection and model
        view matrix.
        The original GL state will be restored
        upon leaving this function.
        """
        projection = camera.view_matrix.matrix
        model_view = camera.model_view

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

        # begin iterating through our scene graph
        # as we iterate over each node, we will set
        # our model view matrix as the node's world
        # matrix and render a cube at that location.
        # we can iterate using any method, but we'll
        # use depth first here
        for node, colour in zip(sorted, self.cube_colours):
            # bind our model view matrix to the shader
            world_matrix = node.world_transform.matrix
            # calculate a new model view
            current_mv = matrix44.multiply(
                world_matrix,
                model_view
                )

            # render the cube
            cube.draw( projection, current_mv, colour )
    

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

