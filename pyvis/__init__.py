import opengl
from event import EventReceiver

## used for application-global settings.

class Config(EventReceiver):
    def __init__(self):
        EventReceiver.__init__(self)
        self._config = {}
    
    def __getitem__(self, item):
        return self._config[item]
    
    def __setitem__(self, item, val):
        self._config[item] = val
        ## inform any listeners that a configuration option has changed
        self.call_event('changed', item=item, value=val)
        
    def update(self, **kwds):
        for k,v in kwds.items():
            self[k] = v


config = Config()
config['default_backend'] = 'qt'
config['qt_lib'] = 'any'  # options are 'pyqt', 'pyside', or 'any'


