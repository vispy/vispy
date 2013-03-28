# -*- coding: utf-8 -*-
# Copyright (C) 2012, Robert Schroll
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" The GTK backend.
"""

import os, sys

import visvis
from visvis import BaseFigure, events, constants
from visvis.core.misc import getResourceDir

import gtk
import gtk.gtkgl
import gobject

import OpenGL.GL as gl

MOUSEMAP = {gtk.gdk.BUTTON_PRESS   : 'down',
            gtk.gdk.BUTTON_RELEASE : 'up',
            gtk.gdk._2BUTTON_PRESS : 'double'}

KEYMAP = {  gtk.keysyms.Shift_L: constants.KEY_SHIFT, 
            gtk.keysyms.Shift_R: constants.KEY_SHIFT,
            gtk.keysyms.Alt_L: constants.KEY_ALT,
            gtk.keysyms.Alt_R: constants.KEY_ALT,
            gtk.keysyms.Control_L: constants.KEY_CONTROL,
            gtk.keysyms.Control_R: constants.KEY_CONTROL,
            gtk.keysyms.Left: constants.KEY_LEFT,
            gtk.keysyms.Up: constants.KEY_UP,
            gtk.keysyms.Right: constants.KEY_RIGHT,
            gtk.keysyms.Down: constants.KEY_DOWN,
            gtk.keysyms.Page_Up: constants.KEY_PAGEUP,
            gtk.keysyms.Page_Down: constants.KEY_PAGEDOWN,
            gtk.keysyms.KP_Enter: constants.KEY_ENTER,
            gtk.keysyms.Return: constants.KEY_ENTER,
            gtk.keysyms.Escape: constants.KEY_ESCAPE,
            gtk.keysyms.Delete: constants.KEY_DELETE,
            }

# Make uppercase letters be lowercase
for i in range(ord('A'), ord('Z')):
    KEYMAP[i] = i+32


def modifiers(event):
    """Convert the GTK state into a tuple of active modifier keys."""
    if not hasattr(event, 'state'):
        return ()
    
    mods = ()
    if event.state & gtk.gdk.SHIFT_MASK:
        mods += constants.KEY_SHIFT,
    if event.state & gtk.gdk.CONTROL_MASK:
        mods += constants.KEY_CONTROL,
    if event.state & gtk.gdk.MOD1_MASK:
        mods += constants.KEY_ALT,
    return mods

class GlCanvas(gtk.gtkgl.DrawingArea):
    
    def __init__(self, figure, *args, **kw):
        gtk.gtkgl.DrawingArea.__init__(self)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.BUTTON_RELEASE_MASK |
                        gtk.gdk.POINTER_MOTION_MASK |
                        gtk.gdk.POINTER_MOTION_HINT_MASK |
                        gtk.gdk.KEY_PRESS_MASK |
                        gtk.gdk.KEY_RELEASE_MASK |
                        gtk.gdk.ENTER_NOTIFY_MASK |
                        gtk.gdk.LEAVE_NOTIFY_MASK |
                        gtk.gdk.FOCUS_CHANGE_MASK)
        self.set_property('can-focus', True)
        
        self.figure = figure
        
        # Configure OpenGL framebuffer.
        # Try to get a double-buffered framebuffer configuration,
        # if not successful then try to get a single-buffered one.
        display_mode = (gtk.gdkgl.MODE_RGB    |
                        gtk.gdkgl.MODE_DEPTH  |
                        gtk.gdkgl.MODE_DOUBLE)
        try:
            glconfig = gtk.gdkgl.Config(mode=display_mode)
        except gtk.gdkgl.NoMatches:
            display_mode &= ~gtk.gdkgl.MODE_DOUBLE
            glconfig = gtk.gdkgl.Config(mode=display_mode)
        self.set_gl_capability(glconfig)
        
        # Connect the relevant signals.
        self.connect('configure_event', self._on_configure_event)
        self.connect('expose_event',    self._on_expose_event)
        self.connect('delete_event', self._on_delete_event)
        self.connect('motion_notify_event', self._on_motion_notify_event)
        self.connect('button_press_event', self._on_button_event)
        self.connect('button_release_event', self._on_button_event)
        self.connect('scroll_event', self._on_scroll_event)
        self.connect('key_press_event', self._on_key_press_event)
        self.connect('key_release_event', self._on_key_release_event)
        self.connect('enter_notify_event', self._on_enter_notify_event)
        self.connect('leave_notify_event', self._on_leave_notify_event)
        self.connect('focus_in_event', self._on_focus_in_event)
        
    def _on_configure_event(self, *args):
        if self.figure:
            self.figure._OnResize()
        return False
        
    def _on_delete_event(self, *args):
        if self.figure:
            self.figure.Destroy()
        return True # Let figure.Destoy() destroy this widget
    
    def _on_motion_notify_event(self, widget, event):
        if event.is_hint:
            x, y, state = event.window.get_pointer()
        else:
            x, y, state = event.x, event.y, event.state
        if self.figure:
            self.figure._GenerateMouseEvent('motion', x, y, 0, modifiers(event))
    
    def _on_button_event(self, widget, event):
        button = {1:1, 3:2}.get(event.button, 0)
        self.figure._GenerateMouseEvent(MOUSEMAP[event.type], event.x, event.y, button, modifiers(event))
    
    def _on_scroll_event(self, widget, event):
        horizontal = {gtk.gdk.SCROLL_LEFT: 1.0, gtk.gdk.SCROLL_RIGHT: -1.0}.get(event.direction, 0)
        vertical = {gtk.gdk.SCROLL_UP: 1.0, gtk.gdk.SCROLL_DOWN: -1.0}.get(event.direction, 0)
        if horizontal or vertical:
            self.figure._GenerateMouseEvent('scroll', event.x, event.y, horizontal, vertical, modifiers(event))
    
    def _on_key_press_event(self, widget, event):
        self.figure._GenerateKeyEvent('keydown', KEYMAP.get(event.keyval, event.keyval),
                                      event.string, modifiers(event))
    
    def _on_key_release_event(self, widget, event):
        self.figure._GenerateKeyEvent('keyup', KEYMAP.get(event.keyval, event.keyval),
                                      event.string, modifiers(event))
    
    def _on_enter_notify_event(self, widget, event):
        if self.figure:
            ev = self.figure.eventEnter
            ev.Set(0,0,0)
            ev.Fire()
    
    def _on_leave_notify_event(self, widget, event):
        if self.figure:
            ev = self.figure.eventLeave
            ev.Set(0,0,0)
            ev.Fire()
    
    def _on_focus_in_event(self, widget, event):
        if self.figure:
            BaseFigure._currentNr = self.figure.nr
   
    def _on_expose_event(self, *args):
        # Obtain a reference to the OpenGL drawable
        # and rendering context.
        gldrawable = self.get_gl_drawable()
        glcontext = self.get_gl_context()

        # OpenGL begin
        if not gldrawable.gl_begin(glcontext):
            return False

        self.figure.OnDraw()

        # OpenGL end
        gldrawable.gl_end()
    
    def set_current(self):
        gldrawable = self.get_gl_drawable()
        glcontext = self.get_gl_context()
        
        gldrawable.make_current(glcontext)
    
    def swap_buffers(self):
        gldrawable = self.get_gl_drawable()
        glcontext = self.get_gl_context()

        if gldrawable.is_double_buffered():
            gldrawable.swap_buffers()
        else:
            gl.glFlush()


class Figure(BaseFigure):
    
    def __init__(self, *args, **kw):
        self._widget = None
        self._widget_args = (args, kw)
        if kw.get('create_widget', True):
            self.CreateWidget()
        
        BaseFigure.__init__(self)
    
    def CreateWidget(self):
        """Create the Figure's widget if necessary, and return the
        widget."""
        if self._widget is None:
            # Make sure there is a native app and the timer is started 
            # (also when embedded)
            app.Create()
            
            # create gl widget
            updatePosition = False
            args, kwargs = self._widget_args
            if 'create_widget' in kwargs:
                updatePosition = True
                del(kwargs['create_widget'])
            self._widget = GlCanvas(self, *args, **kwargs)
            if updatePosition:
                self.position._Changed()
        return self._widget
    
    def _SetCurrent(self):
        """Make figure the current OpenGL context."""
        if self._widget and not self._destroyed:
            self._widget.set_current()
    
    def _SwapBuffers(self):
        """Swap the memory and screen buffers."""
        if self._widget and not self._destroyed:
            self._widget.swap_buffers()
    
    def _RedrawGui(self):
        """Make the widget redraw itself."""
        if self._widget:
            self._widget.queue_draw()
    
    def _ProcessGuiEvents(self):
        """Process all events in queue."""
        app.ProcessEvents()
    
    def _SetTitle(self, title):
        """Set the title, when not used in application."""
        if self._widget and not self._destroyed:
            window = self._widget.parent
            if isinstance(window, gtk.Window):
                window.set_title(title)
    
    def _SetPosition(self, x, y, w, h):
        """Set the position and size of the widget.  If it is embedded,
        ignore the x and y coordinates."""
        if self._widget and not self._destroyed:
            self._widget.set_size_request(w, h)
            self._widget.queue_resize()
            window = self._widget.parent
            if isinstance(window, gtk.Window):
                window.move(x, y)
                window.resize(w, h)
    
    def _GetPosition(self):
        """Get the widget's position."""
        if self._widget and not self._destroyed:
            alloc = self._widget.allocation
            x, y = alloc.x, alloc.y
            window = self._widget.parent
            if isinstance(window, gtk.Window):
                x, y = window.get_position()
            return x, y, alloc.width, alloc.height
        return 0, 0, 0, 0
    
    def _Close(self, widget):
        """Close the widget."""
        if widget is None:
            widget = self._widget
        if widget:
            window = widget.parent
            # The destroy() method causes IPython to emit on error on my system
            # the first time it happens (almar)
            if isinstance(window, gtk.Window):
                window.destroy()
            else:
                widget.destroy()
        
        # If no more figures, quit
        # If in script-mode, we nicely quit. If in interactive mode, we won't.
        if len(BaseFigure._figures) == 0:
            app.Quit()


def newFigure():
    """Create a figure and put it in a window."""
    
    figure = Figure()
    window = gtk.Window()
    
    # Set icon
    try:
        iconfile = os.path.join(getResourceDir(), 'visvis_icon_gtk.png')
        window.set_icon_from_file(iconfile)
    except Exception:
        pass
    
    # From GTKGL example
    if sys.platform != 'win32':
        window.set_resize_mode(gtk.RESIZE_IMMEDIATE)
    window.set_reallocate_redraws(True)
    
    window.add(figure._widget)
    size = visvis.settings.figureSize 
    figure._widget.set_size_request(size[0], size[1])
    window.set_geometry_hints(min_width=100, min_height=100)
    window.show_all()
    
    window.connect('delete-event', figure._widget._on_delete_event)
    
    # Initialize OpenGl
    figure.DrawNow()
    return figure


class VisvisEventsTimer:
    """ Timer that can be started and stopped.
    """
    
    def __init__(self):
        self._running = False
    
    def Start(self):
        if not self._running:
            self._running = True
            self._PostTimeout()
    
    def Stop(self):
        self._running = False
    
    def _PostTimeout(self):
        gobject.timeout_add(10, self._Fire)
    
    def _Fire(self):
        if self._running:
            events.processVisvisEvents()
            return True # So called again.
        else:
            return False # Stop timer.


class App(events.App):
    """App()
    
    Application class to wrap the GUI applications in a class
    with a simple interface that is the same for all backends.
    
    This is the GTK implementation.
    
    """
    
    def __init__(self):
        # Create timer
        self._timer = VisvisEventsTimer()
    
    def _GetNativeApp(self):
        """Ensure the GTK app exists."""
        
        # Start timer
        self._timer.Start()
        
        # Prevent quiting when used interactively
        if not hasattr(gtk, 'vv_do_quit'):
            gtk.vv_do_quit = False
        
        # Return singleton gtk object, which represents the gtk application
        return gtk
    
    def _ProcessEvents(self):
        """Process GTK events."""
        gtk.gdk.threads_enter() # enter/leave prevents IPython -gthread to hang
        while gtk.events_pending():
            gtk.main_iteration(False)
        gtk.gdk.threads_leave()
    
    def _Run(self):
        """Enter GTK mainloop."""
        self._GetNativeApp()
        
        if gtk.main_level() == 0:
            # We need to start the mainloop.  This means we will also
            # have to kill the mainloop when the last figure is closed.
            gtk.vv_do_quit = True
            gtk.main()
    
    def Quit(self):
        if gtk.vv_do_quit: # We started the mainloop, so we better kill it.
            gtk.main_quit()

app = App()
