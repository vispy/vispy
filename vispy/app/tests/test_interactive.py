from nose.tools import assert_equal, assert_true, assert_false
from vispy.testing import assert_in, run_tests_if_main

from vispy.app import set_interactive
from vispy.ext.ipy_inputhook import inputhook_manager


# Expect the inputhook_manager to set boolean `_in_event_loop`
# on instances of this class when enabled.
class MockApp(object):
    pass


def test_interactive():
    f = MockApp()
    set_interactive(enabled=True, app=f)

    assert_equal('vispy', inputhook_manager._current_gui)
    assert_true(f._in_event_loop)
    assert_in('vispy', inputhook_manager.apps)
    assert_equal(f, inputhook_manager.apps['vispy'])

    set_interactive(enabled=False)

    assert_equal(None, inputhook_manager._current_gui)
    assert_false(f._in_event_loop)


run_tests_if_main()
