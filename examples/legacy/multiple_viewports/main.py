from pygly.ratio_viewport import RatioViewport

from examples.legacy.simple.main import SimpleApplication


class MultipleViewportApplication( SimpleApplication ):
    
    def __init__( self ):
        super( MultipleViewportApplication, self ).__init__()

    def setup_viewports( self ):
        super( MultipleViewportApplication, self ).setup_viewports()

        # make a second viewport
        # this viewport will be 1/10th the size
        self.viewports.append(
            RatioViewport(
                self.window,
                [ [0.7, 0.7], [0.3, 0.3] ]
                )
            )
        self.colours.append(
            (0.3, 0.3, 0.3, 1.0)
            )

    def setup_camera( self ):
        super( MultipleViewportApplication, self ).setup_camera()

        # use the same camera for this viewport
        self.cameras.append( self.cameras[ 0 ] )


def main():
    # create app
    app = MultipleViewportApplication()
    app.run()
    app.window.close()


if __name__ == "__main__":
    main()

