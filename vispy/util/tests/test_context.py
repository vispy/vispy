# -*- coding: utf-8 -*-

import gc

from nose.tools import assert_raises, assert_equal, assert_not_equal
from vispy.testing import assert_in

from vispy.util.context import (GLContext, get_current_context, 
                                get_default_config)


class DummyCanvasBackend(object):
    
    def __init__(self):
        self.set_current = False
    
    def _vispy_set_current(self):
        self.set_current = True


def test_context_config():
    """ Test GLContext handling of config dict
    """
    default_config = get_default_config()
    
    # Pass default config unchanged
    c = GLContext(default_config)
    assert_equal(c.config, default_config)
    # Must be deep copy
    c.config['double_buffer'] = False
    assert_not_equal(c.config, default_config)
    
    # Passing nothing should yield default config
    c = GLContext()
    assert_equal(c.config, default_config)
    # Must be deep copy
    c.config['double_buffer'] = False
    assert_not_equal(c.config, default_config)
    
    # This should work
    c = GLContext({'red_size': 4, 'double_buffer': False})
    assert_equal(c.config.keys(), default_config.keys())
    
    # Passing crap should raise
    assert_raises(KeyError, GLContext, {'foo': 3})
    assert_raises(TypeError, GLContext, {'double_buffer': 'not_bool'})
    

def test_context_taking():
    """ Test GLContext ownership and taking
    """
    def get_canvas(c):
        return c.backend_canvas
    
    cb = DummyCanvasBackend()
    c = GLContext()
    
    # Context is not taken and cannot get backend_canvas
    assert not c.istaken
    assert_raises(RuntimeError, get_canvas, c)
    assert_in('no backend', repr(c))
    
    # Take it
    c.take('test-foo', cb)
    assert c.backend_canvas is cb
    assert_in('test-foo backend', repr(c))
    
    # Now we cannot take it again
    assert_raises(RuntimeError, c.take, 'test', cb)
    
    # Canvas backend can delete (we use a weak ref)
    cb = DummyCanvasBackend()  # overwrite old object
    gc.collect()
    
    # Still cannot take it, but backend is invalid
    assert_raises(RuntimeError, c.take, 'test', cb)
    assert_raises(RuntimeError, get_canvas, c)


def test_context_activating():
    """ Test GLContext activation and obtaining current context
    """
    c1 = GLContext()
    c2 = GLContext()
    
    assert get_current_context() is None
    
    # Need backend to make current
    assert_raises(RuntimeError, c1.set_current)
    
    # Unless we do this
    c1.set_current(False)
    assert get_current_context() is c1
    
    # Switch
    c2.set_current(False)
    assert get_current_context() is c2
    
    # Now try with backend
    cb1 = DummyCanvasBackend()
    c1.take('test', cb1)
    assert cb1.set_current is False
    assert get_current_context() is c2
    c1.set_current()
    assert get_current_context() is c1
    assert cb1.set_current is True


if __name__ == '__main__':
    test_context_config()
    test_context_taking()
    test_context_activating()
