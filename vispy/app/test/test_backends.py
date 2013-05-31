""" Tests to quickly see if the backends look good.
"""

import vispy
from vispy import keys

class ModuleTest:
    def __init__(self, module):
        self._module = module
    
    def test_keymap(self):
        """ Test that the keymap contains all keys supported by vispy.
        """
        keymap = self._module.KEYMAP
        vispy_keys = keymap.values()
        for keyname in dir(keys):
            if keyname.upper() != keyname:
                continue
            key = getattr(keys, keyname)
            assert key in vispy_keys
    
    
    def test_methods(self):
        """ Test that all _vispy_x methods are there.
        """
        exceptions = '_vispy_get_native_canvas', '_vispy_get_native_timer', '_vispy_get_native_app'
        
        Klass = self._module.CanvasBackend
        KlassRef = vispy.app.canvas.CanvasBackend
        for key in dir(KlassRef):
            if not key.startswith('__'):
                method = getattr(Klass, key)
                if key not in exceptions:
                    if hasattr(method, '__module__'): 
                        assert method.__module__ == self._module.__name__ # Py3k
                    else:
                        assert method.im_func.__module__ == self._module.__name__
        
        Klass = self._module.TimerBackend
        KlassRef = vispy.app.timer.TimerBackend
        for key in dir(KlassRef):
            if not key.startswith('__'):
                method = getattr(Klass, key)
                if key not in exceptions:
                    if hasattr(method, '__module__'): 
                        assert method.__module__ == self._module.__name__ # Py3k
                    else:
                        assert method.im_func.__module__ == self._module.__name__
        
        Klass = self._module.ApplicationBackend
        KlassRef = vispy.app.application.ApplicationBackend
        for key in dir(KlassRef):
            if not key.startswith('__'):
                method = getattr(Klass, key)
                if key not in exceptions:
                    if hasattr(method, '__module__'): 
                        assert method.__module__ == self._module.__name__ # Py3k
                    else:
                        assert method.im_func.__module__ == self._module.__name__
    
    
    def test_events(self):
        """ Test that all events seem to be emitted.
        """
        # Get text
        fname = self._module.__file__.strip('c')
        text = open(fname, 'rb').read().decode('utf-8')
        
        canvas = vispy.app.Canvas(create_native=False)
        eventNames = set(canvas.events._emitters.keys())
        eventNames.discard('stylus'); eventNames.discard('touch') # Leave this for now
        
        for name in eventNames:
            assert 'events.%s'%name in text
        


if __name__ == '__main__':
    
    from vispy.app.backends import template, qt, pyglet, glut
    
    for mod in [template, qt, pyglet, glut]:
        test = ModuleTest(mod)
        test.test_keymap()
        test.test_methods()
        test.test_events()
        print('ok %s' % mod.__name__)
        
    
    