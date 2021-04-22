# -*- coding: utf-8 -*-

import gc

from vispy.testing import (assert_in, run_tests_if_main, assert_raises,
                           assert_equal, assert_not_equal)

from vispy import gloo
from vispy.gloo import (GLContext, get_default_config)


class DummyCanvas(object):

    @property
    def glir(self):
        return self

    def command(self, *args):
        pass


class DummyCanvasBackend(object):

    def __init__(self):
        self.set_current = False
        self._vispy_canvas = DummyCanvas()

    def _vispy_set_current(self):
        self.set_current = True


def test_context_config():
    """Test GLContext handling of config dict"""
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

    # Capabilites are passed on
    assert 'gl_version' in c.capabilities


def test_context_taking():
    """Test GLContext ownership and taking"""
    def get_canvas(c):
        return c.shared.ref

    cb = DummyCanvasBackend()
    c = GLContext()

    # Context is not taken and cannot get backend_canvas
    assert c.shared.name is None
    assert_raises(RuntimeError, get_canvas, c)
    assert_in('None backend', repr(c.shared))

    # Take it
    c.shared.add_ref('test-foo', cb)
    assert c.shared.ref is cb
    assert_in('test-foo backend', repr(c.shared))

    # Now we can take it again
    c.shared.add_ref('test-foo', cb)
    assert len(c.shared._refs) == 2
    # assert_raises(RuntimeError, c.take, 'test', cb)

    # Canvas backend can delete (we use a weak ref)
    cb = DummyCanvasBackend()  # overwrite old object
    gc.collect()

    # No more refs
    assert_raises(RuntimeError, get_canvas, c)


def test_gloo_without_app():
    """Test gloo without vispy.app (with FakeCanvas)"""
    # Create dummy parser
    class DummyParser(gloo.glir.BaseGlirParser):
        def __init__(self):
            self.commands = []

        def parse(self, commands):
            self.commands.extend(commands)

    p = DummyParser()

    # Create fake canvas and attach our parser
    c = gloo.context.FakeCanvas()
    c.context.shared.parser = p

    # Do some commands
    gloo.clear()
    c.flush()
    gloo.clear()
    c.flush()

    assert len(p.commands) in (2, 3)  # there may be a CURRENT command
    assert p.commands[-1][1] == 'glClear'


run_tests_if_main()
