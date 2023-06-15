from vispy.scene import visuals, Node
from vispy.scene.visuals import VisualNode
import vispy.visuals


def test_docstrings():
    # test that docstring insertions worked for all Visual+Node subclasses
    for name in dir(visuals):
        obj = getattr(visuals, name)
        if isinstance(obj, type) and issubclass(obj, Node):
            if obj is Node or obj is VisualNode:
                continue
            assert "This class inherits from visuals." in obj.__doc__
            assert "parent : Node" in obj.__doc__


def test_visual_node_generation():
    # test that all Visual classes also have Visual+Node classes
    visuals = []
    for name in dir(vispy.visuals):
        obj = getattr(vispy.visuals, name)
        if isinstance(obj, type) and issubclass(obj, Node):
            if obj is Node:
                continue
            assert name.endswith('Visual')
            vis_node = getattr(visuals, name[:-6])
            assert issubclass(vis_node, Node)
            assert issubclass(vis_node, obj)


def test_push_pop_gl_state():
    node = vispy.visuals.MeshVisual()
    og_gl_state = node._vshare.gl_state.copy()
    node.push_gl_state(blend=not og_gl_state.get("blend"))
    assert node._vshare.gl_state != og_gl_state
    node.pop_gl_state()
    assert node._vshare.gl_state == og_gl_state


def test_pop_empty_gl_state():
    node = vispy.visuals.MeshVisual()
    assert node._prev_gl_state == []
    og_gl_state = node._vshare.gl_state.copy()
    node.pop_gl_state()
    assert node._vshare.gl_state == og_gl_state


def test_temp_gl_state():
    node = vispy.visuals.MeshVisual()
    og_gl_state = node._vshare.gl_state.copy()
    with node.temp_gl_state(blend=not og_gl_state.get("blend")):
        assert node._vshare.gl_state != og_gl_state
    assert node._vshare.gl_state == og_gl_state


def test_picking_context():
    canvas = vispy.scene.SceneCanvas()
    view = canvas.central_widget.add_view()
    mesh = visuals.Mesh()
    view.add(mesh)

    assert not view.picking
    assert not mesh.picking
    with canvas._scene.picking_context():
        assert view.picking
        assert mesh.picking
    assert not view.picking
    assert not mesh.picking
