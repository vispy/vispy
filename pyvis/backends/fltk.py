# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" The FLTK backend.


"""

import visvis
from visvis import BaseFigure, events, constants
from visvis.core.misc import basestring

import fltk

KEYMAP = {  fltk.FL_SHIFT: constants.KEY_SHIFT, 
            fltk.FL_Shift_L: constants.KEY_SHIFT, 
            fltk.FL_Shift_R: constants.KEY_SHIFT, 
            fltk.FL_ALT : constants.KEY_ALT,
            fltk.FL_Alt_L : constants.KEY_ALT,
            fltk.FL_Alt_R : constants.KEY_ALT,
            fltk.FL_Control_L: constants.KEY_CONTROL,
            fltk.FL_Control_R: constants.KEY_CONTROL,
            fltk.FL_Left: constants.KEY_LEFT,
            fltk.FL_Up: constants.KEY_UP,
            fltk.FL_Right: constants.KEY_RIGHT,
            fltk.FL_Down: constants.KEY_DOWN,
            fltk.FL_Page_Up: constants.KEY_PAGEUP,
            fltk.FL_Page_Down: constants.KEY_PAGEDOWN,
            fltk.FL_Delete: constants.KEY_DELETE
            }

# Make uppercase letters be lowercase
for i in range(ord('A'), ord('Z')):
    KEYMAP[i] = i+32


def modifiers():
    """Convert the fltk modifier state into a tuple of active modifier keys."""
    mod = ()
    fltkmod = fltk.Fl.event_state()
    if fltk.FL_SHIFT & fltkmod:
        mod += constants.KEY_SHIFT,
    if fltk.FL_CTRL & fltkmod:
        mod += constants.KEY_CONTROL,
    if fltk.FL_ALT & fltkmod:
        mod += constants.KEY_ALT,
    return mod


class GLWidget(fltk.Fl_Gl_Window):
    """ Implementation of the GL_window, which passes a number of
    events to the Figure object that wraps it.
    """
    
    def __init__(self, figure, *args, **kwargs):     
        fltk.Fl_Gl_Window.__init__(self, *args, **kwargs)        
        self.figure = figure
        
        # Callback when closed
        self.callback(self.OnClose)
    
    
    def handle(self, event):
        """ All events come in here. """
        if not self.figure:
            return 1
        
        # map fltk buttons to visvis buttons
        buttons = [0,1,0,2,0,0,0]
        
        if event == fltk.FL_PUSH:
            x, y = fltk.Fl.event_x(), fltk.Fl.event_y()
            but = buttons[fltk.Fl.event_button()]
            self.figure._GenerateMouseEvent('down', x, y, but, modifiers())
        
        elif event == fltk.FL_RELEASE:            
            x, y = fltk.Fl.event_x(), fltk.Fl.event_y()
            but = buttons[fltk.Fl.event_button()]
            if fltk.Fl.event_clicks() == 1:
                # double click                
                self.figure._GenerateMouseEvent('double', x, y, but, modifiers())
            else:
                # normal release                
                self.figure._GenerateMouseEvent('up', x, y, but, modifiers())
        
        elif event in [fltk.FL_MOVE, fltk.FL_DRAG]:
            w,h = self.w(), self.h()
            self.OnMotion(None)
        elif event == fltk.FL_MOUSEWHEEL:
            self.OnMouseWheel(None)
        elif event == fltk.FL_ENTER:
            ev = self.figure.eventEnter
            ev.Set(0,0,0)
            ev.Fire()
        elif event == fltk.FL_LEAVE:
            ev = self.figure.eventLeave
            ev.Set(0,0,0)
            ev.Fire()
        elif event == fltk.FL_KEYDOWN:
            self.OnKeyDown(None)
        elif event == fltk.FL_KEYUP:
            self.OnKeyUp(None)
        elif event == fltk.FL_CLOSE:
            self.OnClose(None)
        
        elif event == fltk.FL_FOCUS:
            self.OnFocus(None)        
        else:
            return 1 # maybe someone else knows what to do with it
        return 1 # event was handled.
    
    
    def resize(self, x, y, w, h):
        # Overload resize function to also draw after resizing
        if self.figure:
            fltk.Fl_Gl_Window.resize(self, x, y, w, h)
            self.figure._OnResize()
    
    def draw(self):
        # Do the draw commands now
        self.figure.OnDraw() 
    
    
    def OnMotion(self, event):
        # prepare and fire event
        x, y = fltk.Fl.event_x(), fltk.Fl.event_y()
        self.figure._GenerateMouseEvent('motion', x, y, 0, modifiers())
    
    def OnMouseWheel(self, event):
        # Mpff, I cant event test horizontal scrolling, because if I do, fltk segfaults
        horizontal = -1.0 * fltk.Fl.event_dx() or 0
        vertical = -1.0 * fltk.Fl.event_dy() or 0
        x, y = fltk.Fl.event_x(), fltk.Fl.event_y()
        self.figure._GenerateMouseEvent('scroll', x, y, horizontal, vertical, modifiers())
    
    def OnKeyDown(self, event):
        key, text = self._ProcessKey()
        self.figure._GenerateKeyEvent('keydown', key, text, modifiers())
    
    def OnKeyUp(self, event):        
        key, text = self._ProcessKey()        
        self.figure._GenerateKeyEvent('keyup', key, text, modifiers())
    
    def _ProcessKey(self):
        """ evaluates the keycode of fltk, and transform to visvis key.
        Also produce text version.
        return key, text. """
        key = fltk.Fl.event_key()
        if isinstance(key, basestring):
            key = ord(key)
        # special cases for shift control and alt -> map to 17 18 19
        if key in KEYMAP:
            return KEYMAP[key], ''
        else:
            # other key, try producing text            
            #print(key, self._shiftDown)
            if (97 <= key <= 122) and fltk.Fl.event_shift():
                key -= 32                
            try:
                return key, chr(key)
            except ValueError:
                return key, ''
    
    
    def OnClose(self, event=None):    
        if self.figure:
            self.figure.Destroy()
        self.hide()        
    
    
    def OnFocus(self, event):
        BaseFigure._currentNr = self.figure.nr


class Figure(BaseFigure):
    """ This is the fltk implementation of the figure class.
    
    A Figure represents the OpenGl context and is the root
    of the visualization tree; a Figure Wibject does not have a parent.
    
    A Figure can be created with the function vv.figure() or vv.gcf().
    """
    
    def __init__(self, *args, **kwargs):
        
        self._widget = None
        self._widget_args = (args, kwargs)
        if kwargs.get('create_widget', True):
            self.CreateWidget()
        
        # call original init AFTER we created the widget
        BaseFigure.__init__(self)
    
    def CreateWidget(self):
        """ Create the Figure's widget if necessary, and return the
        widget. """
        if self._widget is None:
            # Make sure there is a native app and the timer is started 
            # (also when embedded)
            app.Create()
            
            # create widget
            updatePosition = False
            args, kwargs = self._widget_args
            if 'create_widget' in kwargs:
                updatePosition = True
                del(kwargs['create_widget'])
            self._widget = GLWidget(self, *args, **kwargs)
            if updatePosition:
                self.position._Changed()
        return self._widget
    
    def _SetCurrent(self):
        """ make this scene the current context """
        if self._widget:
            self._widget.make_current()
        
        
    def _SwapBuffers(self):
        """ Swap the memory and screen buffer such that
        what we rendered appears on the screen """
        if self._widget:
            self._widget.swap_buffers()

    def _SetTitle(self, title):
        """ Set the title of the figure... """
        if self._widget:
            window = self._widget
            if hasattr(window,'label'):
                window.label(title)
    
    def _SetPosition(self, x, y, w, h):
        """ Set the position of the widget. """
        if self._widget:
            # select widget to resize. If it 
            widget = self._widget       
            # apply
            widget.position(x,y)
            widget.size(w, h)

    def _GetPosition(self):
        """ Get the position of the widget. """
        if self._widget:
            # select widget to resize. If it 
            widget = self._widget        
            # get and return        
            return widget.x(), widget.y(), widget.w(), widget.h()
        return 0, 0, 0, 0
    
    def _RedrawGui(self):
        if self._widget:
            self._widget.redraw()
    
    def _ProcessGuiEvents(self):
        fltk.Fl.wait(0) 
    
    def _Close(self, widget=None):
        if widget is None:
            widget = self._widget
        if widget:
            widget.OnClose()        
    

def newFigure():
    """ Create a window with a figure widget.
    """
    
    # Create figure
    size = visvis.settings.figureSize
    figure = Figure(size[0], size[1], "Figure")    
    figure._widget.size_range(100,100,0,0,0,0)
    figure._widget.show() # Show AFTER canvas is added    
    
    # Make OpenGl Initialize and return
    # Also call draw(), otherwise it will not really draw and crash on Linux
    figure.DrawNow()
    figure._widget.draw()
    return figure




class VisvisEventsTimer:
    """ Timer that can be started and stopped.
    """
    def __init__(self):
        self._running = False
    def Start(self):
        if not self._running:
            self._running = True
            self._PostOneShot()
    def Stop(self):
        self._running = False
    def _PostOneShot(self):
        fltk.Fl.add_timeout(0.01, self._Fire)
    def _Fire(self):
        if self._running:
            events.processVisvisEvents()
            self._PostOneShot() # Repost


class App(events.App):
    """ App()
    
    Application class to wrap the GUI applications in a class
    with a simple interface that is the same for all backends.
    
    This is the fltk implementation.
    
    """
    
    def __init__(self):
        # Init timer
        self._timer = VisvisEventsTimer()
    
    def _GetNativeApp(self):
        self._timer.Start()
        return fltk.Fl
    
    def _ProcessEvents(self):
        app = self._GetNativeApp()
        app.wait(0) 
    
    def _Run(self):
        app = self._GetNativeApp()
        if hasattr(app, '_in_event_loop') and app._in_event_loop:
            pass # Already in event loop
        else:
            app.run()

# Create application instance now
app = App()
