import pytest

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


def test_push_gl_state():
    node = vispy.visuals.MeshVisual()
    og_gl_state = node._vshare.gl_state.copy()
    node.push_gl_state(blend=False, depth_test=False)
    assert node._vshare.gl_state != og_gl_state
    # preset is always set, unset kwargs should be absent
    assert node._vshare.gl_state == {
        "preset": None,
        "blend": False,
        "depth_test": False,
    }
    node.pop_gl_state()
    assert node._vshare.gl_state == og_gl_state


def test_push_gl_state_update():
    node = vispy.visuals.MeshVisual()
    og_gl_state = node._vshare.gl_state.copy()
    assert "blend" not in og_gl_state
    assert node._vshare.gl_state["depth_test"]

    node.push_gl_state_update(blend=False, depth_test=False)
    assert node._vshare.gl_state != og_gl_state
    assert not node._vshare.gl_state["blend"]
    assert not node._vshare.gl_state["depth_test"]

    node.pop_gl_state()
    assert node._vshare.gl_state == og_gl_state


def test_pop_empty_gl_state():
    node = vispy.visuals.MeshVisual()
    assert node._prev_gl_state == []
    og_gl_state = node._vshare.gl_state.copy()
    node.pop_gl_state()
    assert node._vshare.gl_state == og_gl_state


def test_update_gl_state():
    node = vispy.visuals.MeshVisual()

    og_gl_state = node._vshare.gl_state.copy()
    assert og_gl_state
    og_gl_state["blend"] = False

    node.update_gl_state(blend=True)

    # check that the state was updated
    assert node._vshare.gl_state.pop("blend") != og_gl_state.pop("blend")
    # the rest of the state should be unchanged
    assert node._vshare.gl_state == og_gl_state


def test_update_gl_state_context_manager():
    node = vispy.visuals.MeshVisual()

    node.set_gl_state(blend=False)
    og_gl_state = node._vshare.gl_state.copy()

    with node.update_gl_state(blend=True):
        # check that the state was updated
        assert node._vshare.gl_state == {**og_gl_state, "blend": True}

    # the update should be reverted once out of the context
    assert node._vshare.gl_state == og_gl_state


def test_set_gl_state():
    node = vispy.visuals.MeshVisual()

    node.set_gl_state(blend=False, depth_test=False)
    # preset is always set, unset kwargs should be absent
    assert node._vshare.gl_state == {
        "preset": None,
        "blend": False,
        "depth_test": False,
    }

    node.set_gl_state(blend=False)
    # preset is always set, unset kwargs should be absent
    assert node._vshare.gl_state == {"preset": None, "blend": False}


def test_set_gl_state_context_manager():
    node = vispy.visuals.MeshVisual()

    node.set_gl_state(blend=False)
    og_gl_state = node._vshare.gl_state.copy()

    with node.set_gl_state(blend=True):
        # preset is always set, unset kwargs should be absent
        assert node._vshare.gl_state == {"preset": None, "blend": True}

    # the update should be reverted once out of the context
    assert node._vshare.gl_state == og_gl_state


@pytest.mark.parametrize("enable_picking", [True, False])
def test_picking_context(enable_picking):
    mesh = visuals.Mesh()
    mesh.picking = not enable_picking

    assert mesh.picking != enable_picking

    with mesh.set_picking(picking=enable_picking) as p:
        assert p == enable_picking
        assert mesh.picking == enable_picking

    assert mesh.picking != enable_picking
