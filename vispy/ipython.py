# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

# This file acts as the main entry point for vispy's
# iPython bindings


# setup ipython mode for vispy
def vispy_ipython(line):
    from vispy import app
    app.use_app("ipynb_webgl")

    print("Vispy iPython module has loaded successfully")


def load_ipython_extension(ipython):
    print("the iPython vispy extension has been loaded.\n"
          "use %vispy_ipython to embed vispy plots in the notebook")

    ipython.register_magic_function(vispy_ipython, magic_kind="line")


# if we need to unload things, then we need this
def unload_ipython_extension(ipython):
    pass
