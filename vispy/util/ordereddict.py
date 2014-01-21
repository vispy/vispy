# -*- coding: utf-8 -*-
from sys import version_info

if version_info[0] > 2 or version_info[1] >= 7:
    from collections import OrderedDict
else:
    from ._py24_ordereddict import OrderedDict  # noqa
