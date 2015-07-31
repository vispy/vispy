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
