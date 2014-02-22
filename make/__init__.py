"""
By putting make.py in a package, we can do "python make" instead of
"python make.py".
"""
from __future__ import print_function, division
from .make import Maker  # noqa
