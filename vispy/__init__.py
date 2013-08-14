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
__version__ = '0.1.0'


from vispy.event import EmitterGroup, EventEmitter, Event
from vispy.util import keys


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
        # inform any listeners that a configuration option has changed
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
    gl_debug=False,
)


def parse_command_line_arguments():
    """ Transform vispy specific command line args to vispy config.
    Put into a function so that any variables dont leak in the vispy namespace.
    """
    import getopt, sys
    # Get command line args for vispy
    argnames = ['vispy-backend', 'vispy-gl-debug']
    try:
        opts, args = getopt.getopt(sys.argv[1:], '', argnames)
    except getopt.GetoptError:
        opts = []
    # Use them to set the config values
    for o, a in opts:
        if o.startswith('--vispy'):
            if o == '--vispy-backend':
                config['default_backend'] = a
                print('backend', a)
            elif o == '--vispy-gl-debug':
                config['gl_debug'] = True
            else:
                print("Unsupported vispy flag: %s" % o)
parse_command_line_arguments()
