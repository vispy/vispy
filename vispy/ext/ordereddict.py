# -*- coding: utf-8 -*-
from sys import version_info

if version_info >= (2, 7):
    from collections import OrderedDict
else:
    from ._bundled.ordereddict import OrderedDict  # noqa
