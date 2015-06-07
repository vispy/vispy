# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

# This file acts as the main entry point for vispy's
# iPython bindings


# Entry Point
# when an iPython extension is loaded, this function is called
# with the ipython parameter being the actual iPython interpreter
# object.
def load_ipython_extension(ipython):
    print("the iPython vispy extension has been loaded.")
    _load_webgl_backend()


# setup ipython mode for vispy
def _load_webgl_backend():
    from vispy import app
    app.use_app("ipynb_webgl")
    print("Vispy iPython module has loaded successfully")


# if we need to unload things, then we need this.
# for now, this is empty.
def unload_ipython_extension(ipython):
    pass
