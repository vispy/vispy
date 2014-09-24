from .. import visuals
from .node import VisualNode


def create_visual_node(subclass):
    # Decide on new class name
    clsname = subclass.__name__
    assert clsname.endswith('Visual')
    clsname = clsname[:-6]
    
    # Generate new docstring
    doc = ("Class inheriting from VisualNode and %s" % 
                   clsname)
    
    # New __init__ method
    def __init__(self, *args, **kwds):
        parent = kwds.pop('parent', None)
        name = kwds.pop('name', None)
        subclass.__init__(self, *args, **kwds)
        VisualNode.__init__(self, parent=parent, name=name)
    
    # Create new class
    cls = type(clsname, (subclass, VisualNode), {'__init__': __init__, 
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
