from vispy import scene
from vispy.testing import requires_application, TestingCanvas


@requires_application()
def test_viewbox_clips_direct_children():
    """Direct children of a viewbox should be clipped."""
    with TestingCanvas(size=(200, 200)) as c:
        grid = c.central_widget.add_grid()
        view = grid.add_view(row=0, col=0)
        view.size = (100, 100)  # simulate grid layout
        ell = scene.Ellipse(center=(0, 0), radius=20, parent=view)

        # the direct child must inherit the ViewBox clipper
        assert view in ell._clippers
        # bounds should track the viewbox rect
        assert ell._clippers[view].bounds is not None
