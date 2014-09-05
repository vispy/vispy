# -*- coding: utf-8 -*-
from sys import version_info

if version_info >= (2, 7):
    from collections import OrderedDict
else:
    from .py24_ordereddict import OrderedDict  # noqa
