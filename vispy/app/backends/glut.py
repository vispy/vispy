"""
vispy backend for glut.
"""

from __future__ import print_function, division, absolute_import

from vispy.event import Event
from vispy import app

import vispy

import OpenGL.GLUT as glut


class ApplicationBackend(app.ApplicationBackend):
    
    def __init__(self):
        app.ApplicationBackend.__init__(self)
        self._inizialized = False
    
    def _vispy_get_backend_name(self):
        return 'Glut'
    
    def _vispy_process_events(self):
        pass # not possible?
    
    def _vispy_run(self):
        self._vispy_get_native_app() # Force exist
        return glut.glutMainLoop()
    
    def _vispy_quit(self):
        pass # not possible?
    
    def _vispy_get_native_app(self):
        if not self._inizialized:
            glut.glutInit() # todo: maybe allow user to give args?
            self._inizialized = True
        return glut



class CanvasBackend(app.CanvasBackend):
    """ Pyglet backend for Canvas abstract class."""
    
    def __init__(self, vispy_canvas, name='glut window', *args, **kwargs):
        app.CanvasBackend.__init__(self, vispy_canvas)
        self._id = glut.glutCreateWindow(name)
        
        # Register callbacks
        glut.glutDisplayFunc(self.on_draw)
        glut.glutReshapeFunc(self.on_resize)
        #glut.glutVisibilityFunc(self.on_show)
        glut.glutKeyboardFunc(self.on_key_press)
        glut.glutKeyboardUpFunc(self.on_key_release)
        glut.glutMouseFunc(self.on_mouse_action)
        glut.glutMotionFunc(self.on_mouse_motion)
        #glut.glutFunc(self.on_)
        
        self._initialized = False
        
    
    def _vispy_set_current(self):  
        # Make this the current context
        glut.glutSetWindow(self._id)
    
    def _vispy_swap_buffers(self):  
        # Swap front and back buffer
        glut.glutSetWindow(self._id)
        glut.glutSwapBuffers()
    
    def _vispy_set_title(self, title):  
        # Set the window title. Has no effect for widgets
        glut.glutSetWindow(self._id)
        glut.glutSetWindowTitle(title)
    
    def _vispy_set_size(self, w, h):
        # Set size of the widget or window
        glut.glutSetWindow(self._id)
        glut.glutReshapeWindow(w, h)
    
    def _vispy_set_location(self, x, y):
        # Set location of the widget or window. May have no effect for widgets
        glut.glutSetWindow(self._id)
        glut.glutPositionWindow(x, y)
    
    def _vispy_set_visible(self, visible):
        # Show or hide the window or widget
        glut.glutSetWindow(self._id)
        if visible:
            glut.glutShowWindow()
        else:
            glut.glutHideWindow()
    
    def _vispy_update(self):
        # Invoke a redraw
        glut.glutSetWindow(self._id)
        glut.glutPostRedisplay()
    
    def _vispy_close(self):
        # Force the window or widget to shut down
        glut.glutDestroyWindow(self._id)
    
    def _vispy_get_geometry(self):
        # Should return widget (x, y, w, h)
        glut.glutSetWindow(self._id)
        x = glut.glutGet(glut.GLUT_WINDOW_X)
        y = glut.glutGet(glut.GLUT_WINDOW_Y)
        w = glut.glutGet(glut.GLUT_WINDOW_WIDTH)
        h = glut.glutGet(glut.GLUT_WINDOW_HEIGHT)
        return x, y, w, h
    
    
    def on_resize(self, w, h):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.resize(size=(w,h))
        

    def on_draw(self, dummy=None):
        if self._vispy_canvas is None:
            return
        # Initialize?
        if not self._initialized:
            self._initialized = True
            self._vispy_canvas.events.initialize()
        
        w = glut.glutGet(glut.GLUT_WINDOW_WIDTH)
        h = glut.glutGet(glut.GLUT_WINDOW_HEIGHT)
        self._vispy_canvas.events.paint(region=(0, 0, w, h))
    
    def on_mouse_action(self, button, state, x, y):
        if self._vispy_canvas is None:
            return
        action = {glut.GLUT_UP:'release', glut.GLUT_DOWN:'press'}[state]
        
        if button < 3:
            # Mouse click event
            button = {glut.GLUT_LEFT_BUTTON:0, glut.GLUT_RIGHT_BUTTON:1}.get(button, button)
            if action == 'press':
                self._vispy_canvas.events.mouse_press(pos=(x,y), button=button)
            else:
                self._vispy_canvas.events.mouse_release(pos=(x,y), button=button)
        
        elif button in (3, 4):
            # Wheel event
            self._vispy_canvas.events.mouse_wheel(
                pos=(x, y),
                delta=(120 if button==3 else -120),  # Follow Qt stepsize
                )
    
    
    def on_mouse_motion(self, x, y):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.mouse_move(
            pos=(x, y),
            button=None,  # todo: self._buttons_pressed,
            modifiers=None # todo: modifiers
            )
    
    
    def on_key_press(self, key, x, y):
        key = ord(key)
        key = KEYMAP.get(key, key)
        try:
            text = chr(key)
        except Exception:
            text = ''
        # todo: modifiers
        self._vispy_canvas.events.key_press(key=key, text=text)
    
    def on_key_release(self, key, x, y):
        key = ord(key)
        key = KEYMAP.get(key, key)
        try:
            text = chr(key)
        except Exception:
            text = ''
        # todo: modifiers
        self._vispy_canvas.events.key_release(key=key, text=text)
    

# todo: map pyglet keys to vispy constants
KEYMAP = {}

import weakref

def _glut_callback(id):
    # Get weakref wrapper for timer
    timer = TimerBackend._timers.get(id, None)
    if timer is None:
        return
    # Get timer object
    timer = timer()
    if timer is None:
        return
    # Kick it!
    if timer._vispy_timer._running:
        timer._vispy_timer._timeout()
        ms = int(timer._vispy_timer._interval*1000)
        glut.glutTimerFunc(ms, _glut_callback, timer._id)


class TimerBackend(app.TimerBackend):
    _counter = 0
    _timers = {}
    
    def __init__(self, vispy_timer):
        app.TimerBackend.__init__(self, vispy_timer)
        # Give this timer a unique id
        TimerBackend._counter += 1
        self._id = TimerBackend._counter
        # Store this timer (using a weak ref)
        self._timers[self._id] = weakref.ref(self)
    
    @classmethod
    def _glut_callback(cls, id):
        # Get weakref wrapper for timer
        timer = cls._timers.get(id, None)
        if timer is None:
            return
        # Get timer object
        timer = timer()
        if timer is None:
            return
        # Kick it!
        if timer._vispy_timer._running:
            timer._vispy_timer._timeout()
            ms = int(timer._vispy_timer._interval*1000)
            glut.glutTimerFunc(ms, TimerBackend._glut_callback, timer._id)
    
    def _vispy_start(self, interval):
        #glut.glutTimerFunc(int(interval*1000), TimerBackend._glut_callback, self._id)
        glut.glutTimerFunc(int(interval*1000), _glut_callback, self._id)
    
    def _vispy_stop(self):
        pass
    
    def _vispy_get_native_timer(self):
        return glut # or self?
