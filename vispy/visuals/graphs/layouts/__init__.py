import inspect

from .random import random
from .circular import circular
from .force_directed import fruchterman_reingold


_layout_map = {
    'random': random,
    'circular': circular,
    'force_directed': fruchterman_reingold
}


def get(name, *args, **kwargs):
    if name not in _layout_map:
        raise KeyError("Graph layout '{}' not found.".format(name))

    layout = _layout_map[name]

    if inspect.isclass(layout):
        layout = layout(*args, **kwargs)

    return layout
