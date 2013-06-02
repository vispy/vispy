"""
vispy backend for pyglet.
"""

# absolute import is important here, since this module is called pyglet :)
from __future__ import print_function, division, absolute_import

from vispy.event import Event
from vispy import app
from vispy import keys
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
# todo: this does not seem enough. Perhaps use the framerate limiter from plot_lines?

# Map native keys to vispy keys
KEYMAP = {
    pyglet.window.key.LSHIFT: keys.SHIFT,
    pyglet.window.key.RSHIFT: keys.SHIFT,
    pyglet.window.key.LCTRL: keys.CONTROL,
    pyglet.window.key.RCTRL: keys.CONTROL,
    pyglet.window.key.LALT: keys.ALT,
    pyglet.window.key.RALT: keys.ALT,
    pyglet.window.key.LMETA: keys.META,
    pyglet.window.key.RMETA: keys.META,
    
    pyglet.window.key.LEFT: keys.LEFT,
    pyglet.window.key.UP: keys.UP,
    pyglet.window.key.RIGHT: keys.RIGHT,
    pyglet.window.key.DOWN: keys.DOWN,
    pyglet.window.key.PAGEUP: keys.PAGEUP,
    pyglet.window.key.PAGEDOWN: keys.PAGEDOWN,
    
    pyglet.window.key.INSERT: keys.INSERT,
    pyglet.window.key.DELETE: keys.DELETE,
    pyglet.window.key.HOME: keys.HOME,
    pyglet.window.key.END: keys.END,
    
    pyglet.window.key.ESCAPE: keys.ESCAPE,
    pyglet.window.key.BACKSPACE: keys.BACKSPACE,
    
    pyglet.window.key.F1: keys.F1,
    pyglet.window.key.F2: keys.F2,
    pyglet.window.key.F3: keys.F3,
    pyglet.window.key.F4: keys.F4,
    pyglet.window.key.F5: keys.F5,
    pyglet.window.key.F6: keys.F6,
    pyglet.window.key.F7: keys.F7,
    pyglet.window.key.F8: keys.F8,
    pyglet.window.key.F9: keys.F9,
    pyglet.window.key.F10: keys.F10,
    pyglet.window.key.F11: keys.F11,
    pyglet.window.key.F12: keys.F12,
    
    pyglet.window.key.SPACE: keys.SPACE,
    pyglet.window.key.ENTER: keys.ENTER, # == pyglet.window.key.RETURN
    pyglet.window.key.NUM_ENTER: keys.ENTER,
    pyglet.window.key.TAB: keys.TAB,
}


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
        app.CanvasBackend.__init__(self, vispy_canvas)
        # Initialize native widget, but default hidden and resizable
        kwargs['visible'] = kwargs.get('visible', False)
        kwargs['resizable'] = kwargs.get('resizable', True) 
        pyglet.window.Window.__init__(self, *args, **kwargs)
        
        self._buttons_pressed = 0
        self._buttons_accepted = 0
        self._mouse_pos = None
        self._draw_ok = False  # whether it is ok to draw yet
        self._pending_location = None
        
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
    
    def _vispy_set_location(self, x, y):
        # Set location of the widget or window. May have no effect for widgets
        if self._draw_ok:
            self.set_location(x, y)
        else:
            self._pending_location = x, y
    
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
        
        # Set location now if we must. For some reason we get weird 
        # offsets in viewport if set_location is called before the
        # widget is shown.
        if self._pending_location:
            xy, self._pending_location = self._pending_location, None
            self.set_location(*xy)
    
    def on_close(self):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.close()
        self.close() # Or the window wont close
    
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
        self._vispy_canvas.events.paint(region=None)#(0, 0, self.width, self.height))
        
        
            
    def on_mouse_press(self, x, y, button, modifiers):
        if self._vispy_canvas is None:
            return
        self._buttons_pressed |= button
        ev2 = self._vispy_canvas.events.mouse_press(
            pos=(x, self.get_size()[1] - y),
            button=button,
            modifiers=self._modifiers(modifiers)
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
                modifiers=self._modifiers(modifiers)
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
                modifiers=self._modifiers(modifiers)
                )
        
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.mouse_wheel(
            delta=scroll_y*120, # Follow Qt stepsize
            pos=(x, y),
            )
    
    
    def on_key_press(self, key, modifiers):      
        try:
            text = chr(key)
        except Exception:
            text = ''
        print(key)
        self._vispy_canvas.events.key_press(
                key=self._processKey(key), 
                text=text,
                modifiers=self._modifiers(modifiers)
            )
    
    def on_key_release(self, key, modifiers):
        try:
            text = chr(key)
        except Exception:
            text = ''
        self._vispy_canvas.events.key_release(
                key= self._processKey(key), 
                text=text,
                modifiers=self._modifiers(modifiers)
            )
    
    def _processKey(self, key):
        if 97 <= key <= 122:
            key -= 32
        if key in KEYMAP:
            return KEYMAP[key]
        elif key>=32 and key <= 127:
            return keys.Key(chr(key))
        else:
            return None 
    
    def _modifiers(self, pygletmod):
        mod = ()
        if pygletmod & pyglet.window.key.MOD_SHIFT:
            mod += keys.SHIFT,
        if pygletmod & pyglet.window.key.MOD_CTRL:
            mod += keys.CONTROL,
        if pygletmod & pyglet.window.key.MOD_ALT:
            mod += keys.ALT,
        return mod



class TimerBackend(app.TimerBackend):
    
    def _vispy_start(self, interval):
        interval = self._vispy_timer._interval
        if self._vispy_timer.max_iterations == 1:
            pyglet.clock.schedule_once(self._vispy_timer._timeout, interval)
        else:
            # seems pyglet does not give the expected behavior when interval==0
            if interval == 0:
                interval = 1e-9
            pyglet.clock.schedule_interval(self._vispy_timer._timeout, interval)
    
    def _vispy_stop(self):
        pyglet.clock.unschedule(self._vispy_timer._timeout)
    
    def _vispy_get_native_timer(self):
        return pyglet.clock
