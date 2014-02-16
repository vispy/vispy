""" 
Special script for testing that importing vispy subpackages do not pull
in any more vispy submodules than strictly necessary.

These tests cannot be included with nose, because they require a clean
sys.modules, and explicitly cleaning sys.modules and subsequent reloading
of vispy modules causes problems with coverage measurements.
"""

from __future__ import print_function

import sys
from nose.tools import assert_equal, assert_in



def clear_modules():
    """ Remove all vispy modules from sys.modules.
    """
    for key in loaded_vispy_modules():
        del sys.modules[key]


def loaded_vispy_modules(depth=None):
    """ Get names of loaded vispy modules. If depth is given, only
    modules up to that depth are given (i.e. with depth=2 will only
    return direct subpackages.
    """
    modnames = set()
    for m in sys.modules.keys():
        if m.startswith('vispy') and not '__future__' in m:
            if depth:
                parts = m.split('.')
                m = '.'.join(parts[:depth])
            modnames.add(m)
    return modnames


def test_import_vispy():
    """ Importing vispy should only pull in other vispy.util submodule. """
    
    # Zero measurement
    modnames = loaded_vispy_modules(2)
    assert_equal(len(modnames), 0)
    
    # Import bare vispy
    import vispy
    modnames = loaded_vispy_modules(2)
    assert_equal(len(modnames), 2)
    assert_in('vispy', modnames)
    assert_in('vispy.util', modnames)
    

def test_import_vispy_util():
    """ Importing vispy.util should not pull in other vispy submodules. """
    import vispy.util
    modnames = loaded_vispy_modules(2)
    assert_equal(len(modnames), 2)
    assert_in('vispy', modnames)
    assert_in('vispy.util', modnames)


def test_import_vispy_app():
    """ Importing vispy.app should not pull in other vispy submodules. """
    import vispy.app
    modnames = loaded_vispy_modules(2)
    assert_equal(len(modnames), 3)
    assert_in('vispy', modnames)
    assert_in('vispy.util', modnames)
    assert_in('vispy.app', modnames)
    
    # todo: maybe also test that no backends are imported yet


def test_import_vispy_gloo():
    """ Importing vispy.gloo should not pull in other vispy submodules. """
    import vispy.gloo
    modnames = loaded_vispy_modules(2)
    assert_equal(len(modnames), 3)
    assert_in('vispy', modnames)
    assert_in('vispy.util', modnames)
    assert_in('vispy.gloo', modnames)


if __name__ == '__main__':
    print(sys.version)
    for name in list(globals().keys()):
        if name.startswith('test_'):
            test = globals()[name]
            clear_modules()
            try:
                print('TEST %s' % test.__doc__, end='')
                test()
            except Exception as err:
                print('FAIL')
                print('REASON:', err)
                raise Exception('FAIL: '+test.__doc__)
            else:
                print('OK')
            
