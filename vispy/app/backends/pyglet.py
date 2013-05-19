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
    
    def __init__(self, vispy_canvas, *args, **kwargs):
        pyglet.window.Window.__init__(self, *args, **kwargs)
        app.CanvasBackend.__init__(self, vispy_canvas)
        
        self._buttons_pressed = 0
        self._buttons_accepted = 0
        self._mouse_pos = None
        self._draw_ok = False  # whether it is ok to draw yet
    
    
    def _vispy_set_current(self):  
        # Make this the current context
        self.switch_to()
    
    def _vispy_swap_buffers(self):  
        # Swap front and back buffer
        self.flip()
    
    def _vispy_set_title(self, title):  
        # Set the window title. Has no effect for widgets
        self.set_caption(title)
    
    def _vispy_set_size(self, w, h):
        # Set size of the widget or window
        self.set_size(w, h)
        # todo: when done before shown, get some strange offset in the graphics
    
    def _vispy_set_location(self, x, y):
        # Set location of the widget or window. May have no effect for widgets
        self.set_location(x, y)
    
    def _vispy_set_visible(self, visible):
        # Show or hide the window or widget
        self.set_visible(visible)
    
    def _vispy_update(self):
        # Invoke a redraw
        pyglet.clock.schedule_once(self.on_draw, 0.0)
    
    def _vispy_close(self):
        # Force the window or widget to shut down
        self.close()
    
    def _vispy_get_geometry(self):
        # Should return widget (x, y, w, h)
        xy = self.get_location()
        wh = self.get_size()
        return xy + wh
    
    
    
    def on_show(self):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.initialize()
        pyglet.clock.schedule_once(self.on_draw, 0.0)
    
    def on_resize(self, w, h):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.resize(size=(w,h))
        
        # might need to send a paint event as well
        if self._draw_ok:
            self.on_draw()

    def on_draw(self, dummy=None):
        self._draw_ok = True
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.paint(region=(0, 0, self.width, self.height))
    
    def on_mouse_press(self, x, y, button, modifiers):
        if self._vispy_canvas is None:
            return
        self._buttons_pressed |= button
        ev2 = self._vispy_canvas.events.mouse_press(
            pos=(x, self.get_size()[1] - y),
            button=button,
            )
        if ev2.handled:
            self._buttons_accepted |= button
    
    def on_mouse_release(self, x, y, button, modifiers):
        if self._vispy_canvas is None:
            return
        self._buttons_pressed &= ~button
        if (button & self._buttons_accepted) > 0:
            self._vispy_canvas.events.mouse_release(
                pos=(x, self.get_size()[1] - y),
                button=button,
                )
            self._buttons_accepted &= ~button
    
    def on_mouse_motion(self, x, y, dx, dy):
        if self._vispy_canvas is None:
            return
        self._mouse_pos = (x, y)
        # todo: re-enable with flag
        #self._vispy_canvas.events.mouse_move(
            #action='move', 
            #pos=(x, self.get_size()[1] - y),
            #buttons=self._buttons_pressed,
            #modifiers=None
            #)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if self._vispy_canvas is None:
            return
        self._mouse_pos = (x, y)
        if self._buttons_accepted > 0:
            self._vispy_canvas.events.mouse_move(
                pos=(x, self.get_size()[1] - y),
                button=button,
                #modifiers=modifiers  pyglet modifiers is an int
                )
        
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.mouse_wheel(
            delta=scroll_y*120, # Follow Qt stepsize
            pos=(x, y),
            )
    
    
    def on_key_press(self, key, modifiers):      
        key = self._processKey(key)
        try:
            text = chr(key)
        except Exception:
            text = ''
        #self.figure._GenerateKeyEvent('keydown', key, text, modifiers(event))
        # todo: modifiers
        self._vispy_canvas.events.key_press(key_id=key, text=text)
    
    def on_key_release(self, key, modifiers):
        key = self._processKey(key)
        try:
            text = chr(key)
        except Exception:
            text = ''
        #self.figure._GenerateKeyEvent('keydown', key, text, modifiers(event))
        # todo: modifiers
        self._vispy_canvas.events.key_release(key_id=key, text=text)
    
    def _processKey(self, key):
        if 97 <= key <= 122:
            key -= 32
        # special cases for shift control and alt -> map to 17 18 19
        if key in KEYMAP:
            return KEYMAP[key]
        else:
            return key 
    
    

# todo: map pyglet keys to vispy constants
KEYMAP = {}


class TimerBackend(app.TimerBackend):
    
    def _vispy_start(self, interval):
        interval = self._vispy_timer._interval
        if self._vispy_timer.max_iterations == 1:
            pyglet.clock.schedule_once(self._vispy_timer._timeout, interval)
        else:
            pyglet.clock.schedule_interval(self._vispy_timer._timeout, interval)
    
    def _vispy_stop(self):
        pyglet.clock.unschedule(self._vispy_timer._timeout)
    
    def _vispy_get_native_timer(self):
        return pyglet.clock
