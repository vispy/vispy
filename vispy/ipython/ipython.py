# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Entry point for vispy's IPython bindings"""

from distutils.version import LooseVersion


def load_ipython_extension(ipython):
    """ Entry point of the IPython extension

    Parameters
    ----------

    IPython : IPython interpreter
        An instance of the IPython interpreter that is handed
        over to the extension
    """
    import IPython

    # don't continue if IPython version is < 3.0
    ipy_version = LooseVersion(IPython.__version__)
    if ipy_version < LooseVersion("3.0.0"):
        ipython.write_err("Your IPython version is older than "
                          "version 3.0.0, the minimum for Vispy's"
                          "IPython backend. Please upgrade your IPython"
                          "version.")
        return

    _load_webgl_backend(ipython)


def _load_webgl_backend(ipython):
    """ Load the webgl backend for the IPython notebook"""

    from .. import app
    app_instance = app.use_app("ipynb_webgl")

    if app_instance.backend_name == "ipynb_webgl":
        ipython.write("Vispy IPython module has loaded successfully")
    else:
        # TODO: Improve this error message
        ipython.write_err("Unable to load webgl backend of Vispy")


def unload_ipython_extension(ipython):
    """ Unload the IPython extension
    """
    pass
