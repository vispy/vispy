"""
Pyvis backend for pyglet.
"""

from pyvis.event import Event
from pyvis.canvas import CanvasBackend, AppBackend
from pyvis.timer import TimerBackend

import pyvis

import pyglet.window
import pyglet.app
import pyglet.clock


# From pygly
def idle( self ):
    """An alternate idle loop than Pyglet's default.
 
    By default, pyglet calls on_draw after EVERY batch of events
    which without hooking into, causes ghosting
    and if we do hook into it, it means we render after every event
    which is REALLY REALLY BAD
 
http://www.pyglet.org/doc/programming_guide/the_application_event_loop.html
 
    """
    pyglet.clock.tick( poll = True )
    # don't call on_draw
    return pyglet.clock.get_sleep_time( sleep_idle = True )
 
def patch_idle_loop():
    """Replaces the default Pyglet idle look with the :py:func:`idle` function in this module.
    """
    # check that the event loop has been over-ridden
    if pyglet.app.EventLoop.idle != idle:
        # over-ride the default event loop
        pyglet.app.EventLoop.idle = idle

patch_idle_loop()


class PygletAppBackend(AppBackend):
    
    def __init__(self):
        AppBackend.__init__(self)
    
    def _pyvis_get_backend_name(self):
        return 'Pyglet'
    
    def _pyvis_process_events(self):
        return pyglet.app.platform_event_loop.step(0.0)
    
    def _pyvis_run(self):
        return pyglet.app.run()
    
    def _pyvis_quit(self):
        return pyglet.app.exit()
    
    def _pyvis_get_native_app(self):
        return pyglet.app



class PygletCanvasBackend(pyglet.window.Window, CanvasBackend):
    """ Pyglet backend for Canvas abstract class."""
    
    def __init__(self, parent=None):
        # before creating widget, make sure we have an app
        pyvis.canvas.app.native_app
        
        CanvasBackend.__init__(self)
        pyglet.window.Window.__init__(self, parent)
        
    
    @property
    def _pyvis_geometry(self):
        xy = self.get_location()
        wh = self.get_size()
        return xy + wh
    
    def _pyvis_resize(self, w, h):
        self.set_size(w, h)
        
    def _pyvis_show(self):
        self.set_visible(True)
        
    def _pyvis_update(self):
        pyglet.clock.schedule_once(self.on_draw, 0.0)
    
    def swapBuffers(self):
        # todo: should probably be _pyvis_swap_buffers
        self.flip()
    
    def on_show(self):
        if self._pyvis_canvas is None:
            return
        self._pyvis_canvas.events.initialize()
        pyglet.clock.schedule_once(self.on_draw, 0.0)
    
    def on_resize(self, w, h):
        if self._pyvis_canvas is None:
            return
        ev = Event(size=(w,h))
        self._pyvis_canvas.events.resize(ev)

    def on_draw(self, dummy=None):
        if self._pyvis_canvas is None:
            return
        ev = Event(region=(0, 0, self.width, self.height))
        self._pyvis_canvas.events.paint(ev)
    
    def on_mouse_press(self, x, y, button, modifiers):
        if self._pyvis_canvas is None:
            return
        ev2 = Event(
            action='press', 
            pos=(x, y),
            button=button,
            )
        # todo: capture mouse when pressed down
        self._pyvis_canvas.events.mouse_press(ev2)
    
    def on_mouse_release(self, x, y, button, modifiers):
        if self._pyvis_canvas is None:
            return
        ev2 = Event(
            action='release', 
            pos=(x, y),
            button=button,
            )
        self._pyvis_canvas.events.mouse_release(ev2)
    
    def on_mouse_motion(self, x, y, dx, dy):
        if self._pyvis_canvas is None:
            return
        ev2 = Event(
            action='move', 
            pos=(x, y),
            )
        self._pyvis_canvas.events.mouse_move(ev2)
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self._pyvis_canvas is None:
            return
        ev2 = Event( 
            action='wheel', 
            delta=scroll_y,
            pos=(x, y),
            )
        self._pyvis_canvas.events.mouse_wheel(ev2)
    
    
    def on_key_press(self, key, modifiers):      
        key = self._processKey(key)
        try:
            text = chr(key)
        except Exception:
            text = ''
        #self.figure._GenerateKeyEvent('keydown', key, text, modifiers(event))
        # todo: modifiers
        self._pyvis_canvas.events.key_press(action='press', key=key, text=text)
    
    def on_key_release(self, key, modifiers):
        key = self._processKey(key)
        try:
            text = chr(key)
        except Exception:
            text = ''
        #self.figure._GenerateKeyEvent('keydown', key, text, modifiers(event))
        # todo: modifiers
        self._pyvis_canvas.events.key_release(action='release', key=key, text=text)
    
    def _processKey(self, key):
        # special cases for shift control and alt -> map to 17 18 19
        if key in KEYMAP:
            return KEYMAP[key]
        else:
            return key 
    
    

# todo: map pyglet keys to pyvis constants
KEYMAP = {}


class PyGletTimerBackend(TimerBackend):
    def __init__(self, timer):
        TimerBackend.__init__(self, timer)
    
    def _pyvis_start(self, interval):
        interval = self._pyvis_timer._interval
        if self._pyvis_timer.max_iterations == 1:
            pyglet.clock.schedule_once(self._pyvis_timer._timeout, interval)
        else:
            pyglet.clock.schedule_interval(self._pyvis_timer._timeout, interval)
    
    def _pyvis_stop(self):
        pyglet.clock.unschedule(self._pyvis_timer._timeout)
    
    def _pyvis_timeout(self):
        self._pyvis_timer._timeout()
    
#     def _pyvis_run(self):
#         return QtGui.QApplication.exec_()
# 
#     def _pyvis_quit(self):
#         return QtGui.QApplication.quit()
