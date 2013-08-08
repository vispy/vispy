# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Vispy is a collaborative project that has the goal to allow more sharing
of code between visualization projects based on OpenGL. It does this
by providing powerful interfaces to OpenGL, at different levels of
abstraction and generality.

These layers are:
  * vispy.gl: raw OpenGL ES 2.0 API
  * vispy.oogl: Object oriented GL API
  * vispy.visuals: Higher level visualization objects (work in progress)
  * ... more to come

Further, vispy comes with a powerful event system and a small
application framework that works on multiple backends. This allows easy
creation of figures, and enables integrating visualizations in a GUI
application.

For more information see http://vispy.org.

"""

from __future__ import print_function, division, absolute_import

# Definition of the version number
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

    def __repr__(self):
        return repr(self._config)

config = Config()
config.update(
    default_backend='qt',
    qt_lib= 'any',  # options are 'pyqt', 'pyside', or 'any'
    show_warnings=False,
)
# todo: qt_lib is now not used anymore, because app.use accepts 'qt', 'pyside' and 'pyqt4'
# LC: I think qt_lib needs to stay so that the end-user can determine whether 
# pyqt/pyside is used. app.use('qt') should check config['qt_lib'].

import getopt,sys
try:
    opts, args = getopt.getopt(sys.argv[1:], '', ['vispy-backend=', 'vispy-gl-debug'])
except getopt.GetoptError, err:
    pass

for o, a in opts:
    if o.startswith('--vispy'):
        if o == '--vispy-backend':
            config['default_backend'] = a
            print('backend', a)
        elif o == '--vispy-gl-debug':
            config['gl_debug'] = True
        else:
            print("Unsupported vispy flag: %s" % o)


# Create API object for OpenGL ES 2.0
# todo: I don't think this belongs here, since in principle vispy might grow non-opengl backends.
#       maybe it goes in oogl.__init__?
import vispy.glapi
gl = vispy.glapi.GLES2()
gl.ext = vispy.glapi.GLES2ext()

import vispy.util
from vispy.util import keys

