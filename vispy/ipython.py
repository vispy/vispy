# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Entry point for vispy's IPython bindings"""


def load_ipython_extension(ipython):
    """ Entry point of the IPython extension

    Parameters
    ----------

    IPython : IPython interpreter
        An instance of the IPython interpreter that is handed
        over to the extension
    """
    return _load_webgl_backend()


def _load_webgl_backend():
    """ Load the webgl backend for the IPython notebook

    Returns
    -------
    The instance of the "ipynb_webgl" app
    """

    from vispy import app
    app_instance = app.use_app("ipynb_webgl")
    print("Vispy IPython module has loaded successfully")

    return app_instance


def unload_ipython_extension(ipython):
    """ Unload the IPython extension
    """
    pass
