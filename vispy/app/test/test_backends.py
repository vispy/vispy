""" Tests to quickly see if the backends look good.
"""

from vispy import keys

class ModuleTest:
    def __init__(self, module):
        self._module = module
    
    def test_keymap(self):
        keymap = self._module.KEYMAP
        vispy_keys = keymap.values()
        for keyname in dir(keys):
            if keyname.upper() != keyname:
                continue
            key = getattr(keys, keyname)
            assert key in vispy_keys



if __name__ == '__main__':
    
    from vispy.app.backends import qt, pyglet, glut
    for mod in [qt, pyglet, glut]:
        test = ModuleTest(mod)
        test.test_keymap()
        print('ok %s' % mod.__name__)
    
    