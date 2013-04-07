# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

"""
Pyvis - https://github.com/pyvis

The pyvis consists of multiple subpackages that need to be imported
separately before use. These are:

  * ... todo

"""

__version__ = '0.0.dev'

#from pyvis import opengl Needs explicit import
from pyvis.event import EventHandler


## used for application-global settings.

class Config(object):
    def __init__(self):
        self.events = EventHandler(source=self,
                                   changed=None,)
        self._config = {}
    
    def __getitem__(self, item):
        return self._config[item]
    
    def __setitem__(self, item, val):
        self._config[item] = val
        ## inform any listeners that a configuration option has changed
        self.events.changed(item=item, value=val)
        
    def update(self, **kwds):
        for k,v in kwds.items():
            self[k] = v


config = Config()
config['default_backend'] = 'qt'
config['qt_lib'] = 'any'  # options are 'pyqt', 'pyside', or 'any'


