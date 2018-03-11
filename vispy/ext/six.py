# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# This shim has been imported from Astropy.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Handle loading six package from system or from the bundled copy
"""

import importlib
import io
import sys

from distutils.version import StrictVersion


_SIX_MIN_VERSION = StrictVersion('1.8.0')
_SIX_SEARCH_PATH = ['vispy.ext._bundled.six', 'six']


def _import_six(search_path=_SIX_SEARCH_PATH):
    failures = []
    for mod_name in search_path:
        try:
            six_mod = importlib.import_module(mod_name)
        except ImportError as exp:
            failures.append('%s: %s' % (mod_name, exp))
            continue
        try:
            if StrictVersion(six_mod.__version__) >= _SIX_MIN_VERSION:
                break
        except (AttributeError, ValueError) as exp:
            # Attribute error if the six module isn't what it should be and
            # doesn't have a .__version__; ValueError if the version string
            # exists but is somehow bogus/unparseable
            failures.append('%s: %s' % (mod_name, exp))
            continue
    else:
        raise ImportError(
            "Vispy requires the 'six' module of minimum version {0}; "
            "normally this is bundled with the Vispy package so if you get "
            "this warning consult the packager of your Vispy "
            "distribution.\n{1}".format(_SIX_MIN_VERSION, '\n'.join(failures)))

    # Using importlib does not overwrite this shim, so do it ourselves.
    this_module = sys.modules[__name__]
    if not hasattr(this_module, '_importer'):
        # Copy all main six attributes.
        for name, value in six_mod.__dict__.items():
            if name.startswith('__'):
                continue
            this_module.__dict__[name] = value

        # Tell six's importer to accept this shim's name as its own.
        importer = six_mod._importer
        known_modules = list(importer.known_modules.items())
        for name, mod in known_modules:
            this_name = __name__ + name[len(mod_name):]
            importer.known_modules[this_name] = mod

        # Turn this shim into a package just like six does.
        this_module.__path__ = []  # required for PEP 302 and PEP 451
        this_module.__package__ = __name__  # see PEP 366
        if this_module.__dict__.get('__spec__') is not None:
            this_module.__spec__.submodule_search_locations = []  # PEP 451


_import_six()

if PY3:
    file_types = (io.TextIOWrapper, io.BufferedRandom)
else:
    file_types = (file, io.TextIOWrapper, io.BufferedRandom)
