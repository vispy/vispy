from ...util.ordereddict import OrderedDict

from .component import VisualComponent  # noqa
from .vertex import *  # noqa
from .color import *  # noqa
from .normal import *  # noqa
from .material import *  # noqa
from .texture import *  # noqa



components = OrderedDict  # maps {'type': {'name': ComponentClass, ...}, ...}


def register_components(type, classes):
    for component in classes:
        components.setdefault(type, OrderedDict())[component.name] = component

def create_component(type, name, *args, **kwds):
    return components[type][name](*args, **kwds)

register_components('material', [ShadingComponent, GridContourComponent])

