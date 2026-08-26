from vispy import scene
from vispy.testing import requires_application, TestingCanvas


@requires_application()
def test_viewbox_clips_direct_children_only():
    with TestingCanvas(size=(200, 200)) as c:
        grid = c.central_widget.add_grid()
        view = grid.add_view(row=0, col=0)
        view.size = (100, 100)  # simulate grid layout
        ell = scene.Ellipse(center=(0, 0), radius=20, parent=view)

        assert view in ell._clippers
        assert ell._clippers[view].bounds is not None

        line = scene.Line(pos=[[0, 0], [1, 1]], parent=view.scene)

        assert view._scene in line._clippers
        assert view not in line._clippers
