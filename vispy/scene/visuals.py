from .. import visuals
from .node import Node

class VisualNode(type):
    # Template class for building Visual/Node combinations
    def __new__(cls, visual_class):
        clsname = visual_class.__name__
        assert clsname.endswith('Visual')
        clsname = clsname[:-6]
        return super(VisualNode, cls).__new__(cls, clsname, 
                                              (visual_class, Node), {})

    def __init__(self, name, bases, attrs):
        self.__visual__class = bases[0]
        self.__init__ = self.__init
        self.__doc__ = ("Class mixing Node and %s" % 
                        self.__visual_class.__name__)

    def __init(self, *args, **kwds):
        parent = kwds.pop('parent', None)
        name = kwds.pop('name', None)
        self.__visual__class.__init__(self, *args, **kwds)
        Node.__init__(self, parent=parent, name=name)


for obj_name in dir(visuals):
    obj = getattr(visuals, obj_name)
    if issubclass(obj, visuals.Visual):
        cls = VisualNode(obj)
        globals()[cls.__name__] = cls



#class LineVisual(LineVisual, Node):
    #def __init__(self, *args, **kwds):
        #parent = kwds.pop('parent', None)
        #name = kwds.pop('name', None)
        #LineVisual.__init__(self, *args, **kwds)
        #Node.__init__(self, parent=parent, name=name)


#class Mesh(MeshVisual, Node):
    #def __init__(self, *args, **kwds):
        #parent = kwds.pop('parent', None)
        #name = kwds.pop('name', None)
        #MeshVisual.__init__(self, *args, **kwds)
        #Node.__init__(self, parent=parent, name=name)


#class Markers(MarkersVisual, Node):
    #def __init__(self, *args, **kwds):
        #parent = kwds.pop('parent', None)
        #name = kwds.pop('name', None)
        #MarkersVisual.__init__(self, *args, **kwds)
        #Node.__init__(self, parent=parent, name=name)


#class Image(ImageVisual, Node):
    #def __init__(self, *args, **kwds):
        #parent = kwds.pop('parent', None)
        #name = kwds.pop('name', None)
        #ImageVisual.__init__(self, *args, **kwds)
        #Node.__init__(self, parent=parent, name=name)


#class GridLines(GridLinesVisual, Node):
    #def __init__(self, *args, **kwds):
        #parent = kwds.pop('parent', None)
        #name = kwds.pop('name', None)
        #GridLinesVisual.__init__(self, *args, **kwds)
        #Node.__init__(self, parent=parent, name=name)


#class XYZAxes(XYZAxesVisual, Node):
    #def __init__(self, *args, **kwds):
        #parent = kwds.pop('parent', None)
        #name = kwds.pop('name', None)
        #XYZAxesVisual.__init__(self, *args, **kwds)
        #Node.__init__(self, parent=parent, name=name)



