from vispy.testing import run_tests_if_main
from vispy.app import set_interactive
from vispy.ext.ipy_inputhook import inputhook_manager


# Expect the inputhook_manager to set boolean `_in_event_loop`
# on instances of this class when enabled.
class MockApp(object):
    pass


def test_interactive():
    f = MockApp()
    set_interactive(enabled=True, app=f)

    assert inputhook_manager._current_gui == 'vispy'
    assert f._in_event_loop
    assert 'vispy' in inputhook_manager.apps
    assert f == inputhook_manager.apps['vispy']

    set_interactive(enabled=False)

    assert inputhook_manager._current_gui is None
    assert not f._in_event_loop


run_tests_if_main()
