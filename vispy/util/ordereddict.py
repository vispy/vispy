import sys

if sys.version_info >= (2, 7):
    from collections import OrderedDict
else:
    from ._py24_ordereddict import OrderedDict
