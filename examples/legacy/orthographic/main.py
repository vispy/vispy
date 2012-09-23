"""Demonstrates PyGLy's functionality.
Renders a simple scene graph and controls
a viewport.
Viewport is provided without any high level
wrappers and is entirely managed through events.
"""
from examples.legacy.simple.main import SimpleApplication
import pygly.window
from pygly.orthogonal_view_matrix import OrthogonalViewMatrix


class OrthographicApplication( SimpleApplication ):

    def setup_camera( self ):
        super( OrthographicApplication, self ).setup_camera()

        # replace the camera's projection view matrix with
        # an orthographic one
        self.cameras[ 0 ].view_matrix = OrthogonalViewMatrix(
            pygly.window.aspect_ratio( self.viewports[ 0 ] ),
            scale = [60.0, 60.0],
            near_clip = 1.0,
            far_clip = 200.0
            )

def main():
    """Main function entry point.
    Simple creates the Application and
    calls 'run'.
    Also ensures the window is closed at the end.
    """
    # create app
    app = OrthographicApplication()
    app.run()
    app.window.close()


if __name__ == "__main__":
    main()

