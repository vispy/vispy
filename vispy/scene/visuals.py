from .. import visuals
from .node import Node

_doc_template = """Class inheriting from visuals.%sVisual and scene.Node.

Instances of this class may be added to a scenegraph using the methods and
properties defined by Node, and will display the visual output defined by
visuals.%sVisual.

Most VisualNode subclasses are generated automatically from the classes found 
in vispy.visuals. For custom visuals, it is recommended to subclass from
Visual rather than VisualNode.
"""


def create_visual_node(subclass):
    # Decide on new class name
    clsname = subclass.__name__
    assert clsname.endswith('Visual')
    clsname = clsname[:-6]
    
    # Generate new docstring
    doc = _doc_template % (clsname, clsname)
    
    # New __init__ method
    def __init__(self, *args, **kwds):
        parent = kwds.pop('parent', None)
        name = kwds.pop('name', None)
        subclass.__init__(self, *args, **kwds)
        Node.__init__(self, parent=parent, name=name)
    
    # Create new class
    cls = type(clsname, (subclass, Node), {'__init__': __init__, 
                                           '__doc__': doc})
    
    return cls

__all__ = []

for obj_name in dir(visuals):
    obj = getattr(visuals, obj_name)
    if (isinstance(obj, type) and 
       issubclass(obj, visuals.Visual) and 
       obj is not visuals.Visual):
        cls = create_visual_node(obj)
        globals()[cls.__name__] = cls
        __all__.append(cls.__name__)
