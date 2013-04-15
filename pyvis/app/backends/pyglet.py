"""
vispy backend for pyglet.
"""

# absolute import is important here, since this module is called pyglet :)
from __future__ import print_function, division, absolute_import

from vispy.event import Event
from vispy import app

import vispy

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


class ApplicationBackend(app.ApplicationBackend):
    
    def __init__(self):
        app.ApplicationBackend.__init__(self)
    
    def _vispy_get_backend_name(self):
        return 'Pyglet'
    
    def _vispy_process_events(self):
        return pyglet.app.platform_event_loop.step(0.0)
    
    def _vispy_run(self):
        return pyglet.app.run()
    
    def _vispy_quit(self):
        return pyglet.app.exit()
    
    def _vispy_get_native_app(self):
        return pyglet.app



class CanvasBackend(pyglet.window.Window, app.CanvasBackend):
    """ Pyglet backend for Canvas abstract class."""
    
    def __init__(self, parent=None):
        # before creating widget, make sure we have an app
        vispy.app.default_app.native
        # todo: it would be more correct to do this on the app instance 
        # associated with the Canvas (but we dont have a reference to it yet)
        
        app.CanvasBackend.__init__(self)
        pyglet.window.Window.__init__(self, parent)
        
        self._buttons_pressed = 0
        self._buttons_accepted = 0
        self._mouse_pos = None
        self._draw_ok = False  # whether it is ok to draw yet
    
    @property
    def _vispy_geometry(self):
        xy = self.get_location()
        wh = self.get_size()
        return xy + wh
    
    def _vispy_resize(self, w, h):
        self.set_size(w, h)
        
    def _vispy_show(self):
        self.set_visible(True)
        
    def _vispy_update(self):
        pyglet.clock.schedule_once(self.on_draw, 0.0)
    
    def swapBuffers(self):
        # todo: should probably be _vispy_swap_buffers
        self.flip()
    
    def on_show(self):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.initialize()
        pyglet.clock.schedule_once(self.on_draw, 0.0)
    
    def on_resize(self, w, h):
        if self._vispy_canvas is None:
            return
        ev = Event(size=(w,h))
        self._vispy_canvas.events.resize(ev)
        
        # might need to send a paint event as well
        if self._draw_ok:
            self.on_draw()

    def on_draw(self, dummy=None):
        self._draw_ok = True
        if self._vispy_canvas is None:
            return
        ev = Event(region=(0, 0, self.width, self.height))
        self._vispy_canvas.events.paint(ev)
    
    def on_mouse_press(self, x, y, button, modifiers):
        if self._vispy_canvas is None:
            return
        ev2 = Event(
            action='press', 
            pos=(x, self.get_size()[1] - y),
            button=button,
            )
        self._buttons_pressed |= button
        self._vispy_canvas.events.mouse_press(ev2)
        if ev2.accepted:
            self._buttons_accepted |= button
    
    def on_mouse_release(self, x, y, button, modifiers):
        if self._vispy_canvas is None:
            return
        ev2 = Event(
            action='release', 
            pos=(x, self.get_size()[1] - y),
            button=button,
            )
        self._buttons_pressed &= ~button
        if (button & self._buttons_accepted) > 0:
            self._vispy_canvas.events.mouse_release(ev2)
            self._buttons_accepted &= ~button
    
    def on_mouse_motion(self, x, y, dx, dy):
        if self._vispy_canvas is None:
            return
        ev2 = Event(
            action='move', 
            pos=(x, self.get_size()[1] - y),
            buttons=self._buttons_pressed,
            modifiers=None
            )
        self._mouse_pos = (x, y)
        # todo: re-enable with flag
        #self._vispy_canvas.events.mouse_move(ev2)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self._vispy_canvas is None:
            return
        ev2 = Event(
            action='move', 
            pos=(x, self.get_size()[1] - y),
            buttons=buttons,
            modifiers=modifiers
            )
        self._mouse_pos = (x, y)
        if self._buttons_accepted > 0:
            self._vispy_canvas.events.mouse_move(ev2)
        
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self._vispy_canvas is None:
            return
        ev2 = Event( 
            action='wheel', 
            delta=scroll_y*120, # Follow Qt stepsize
            pos=(x, y),
            )
        self._vispy_canvas.events.mouse_wheel(ev2)
    
    
    def on_key_press(self, key, modifiers):      
        key = self._processKey(key)
        try:
            text = chr(key)
        except Exception:
            text = ''
        #self.figure._GenerateKeyEvent('keydown', key, text, modifiers(event))
        # todo: modifiers
        self._vispy_canvas.events.key_press(action='press', key=key, text=text)
    
    def on_key_release(self, key, modifiers):
        key = self._processKey(key)
        try:
            text = chr(key)
        except Exception:
            text = ''
        #self.figure._GenerateKeyEvent('keydown', key, text, modifiers(event))
        # todo: modifiers
        self._vispy_canvas.events.key_release(action='release', key=key, text=text)
    
    def _processKey(self, key):
        # special cases for shift control and alt -> map to 17 18 19
        if key in KEYMAP:
            return KEYMAP[key]
        else:
            return key 
    
    

# todo: map pyglet keys to vispy constants
KEYMAP = {}


class TimerBackend(app.TimerBackend):
    def __init__(self, timer):
        app.TimerBackend.__init__(self, timer)
    
    def _vispy_start(self, interval):
        interval = self._vispy_timer._interval
        if self._vispy_timer.max_iterations == 1:
            pyglet.clock.schedule_once(self._vispy_timer._timeout, interval)
        else:
            pyglet.clock.schedule_interval(self._vispy_timer._timeout, interval)
    
    def _vispy_stop(self):
        pyglet.clock.unschedule(self._vispy_timer._timeout)
    
#     def _vispy_timeout(self):
#         self._vispy_timer._timeout()
    
#     def _vispy_run(self):
#         return QtGui.QApplication.exec_()
# 
#     def _vispy_quit(self):
#         return QtGui.QApplication.quit()
