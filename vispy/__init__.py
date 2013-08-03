# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Vispy - http://vispy.org

The vispy consists of multiple subpackages that need to be imported
separately before use. These are:

  * ... todo

"""

from __future__ import print_function, division, absolute_import

__version__ = '0.0.dev'


from vispy.event import EmitterGroup, EventEmitter, Event

class ConfigEvent(Event):
    """ Event indicating a configuration change. 
    
    This class has a 'changes' attribute which is a dict of all name:value 
    pairs that have changed in the configuration.
    """
    def __init__(self, changes):
        Event.__init__(self, type='config_change')
        self.changes = changes
        
        
class Config(object):
    """ Container for global settings used application-wide in vispy.
    
    Events:
    -------
    Config.events.changed - Emits ConfigEvent whenever the configuration changes.
    """
    def __init__(self):
        self.events = EmitterGroup(source=self)
        self.events['changed'] = EventEmitter(event_class=ConfigEvent, source=self)
        self._config = {}
    
    def __getitem__(self, item):
        return self._config[item]
    
    def __setitem__(self, item, val):
        self._config[item] = val
        ## inform any listeners that a configuration option has changed
        self.events.changed(changes={item:val})
        
    def update(self, **kwds):
        self._config.update(kwds)
        self.events.changed(changes=kwds)


config = Config()
config.update(
    default_backend='qt',
    qt_lib= 'any',  # options are 'pyqt', 'pyside', or 'any'
    show_warnings=False,
)
# todo: qt_lib is now not used anymore, because app.use accepts 'qt', 'pyside' and 'pyqt4'
# LC: I think qt_lib needs to stay so that the end-user can determine whether 
# pyqt/pyside is used. app.use('qt') should check config['qt_lib'].


# Create API object for OpenGL ES 2.0
# todo: I don't think this belongs here, since in principle vispy might grow non-opengl backends.
#       maybe it goes in oogl.__init__?
import vispy.glapi
gl = vispy.glapi.GLES2()
gl.ext = vispy.glapi.GLES2ext()

import vispy.util
from vispy.util import keys

