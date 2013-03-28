# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" The WX backend.


"""

# NOTICE: wx has the same general problem with OpenGl being kinda 
# unmanaged and frames not being drawn on Gnome. However, wx seems
# relatively well workable with only applying a Refresh command 
# on each Activate command of the main window.

import os

import visvis
from visvis import BaseFigure, events, constants
from visvis.core.misc import getResourceDir

import wx
from wx.glcanvas import GLCanvas


KEYMAP = {  wx.WXK_SHIFT: constants.KEY_SHIFT, 
            wx.WXK_ALT: constants.KEY_ALT,
            wx.WXK_CONTROL: constants.KEY_CONTROL,
            wx.WXK_LEFT: constants.KEY_LEFT,
            wx.WXK_UP: constants.KEY_UP,
            wx.WXK_RIGHT: constants.KEY_RIGHT,
            wx.WXK_DOWN: constants.KEY_DOWN,
            wx.WXK_PAGEUP: constants.KEY_PAGEUP,
            wx.WXK_PAGEDOWN: constants.KEY_PAGEDOWN,
            wx.WXK_RETURN: constants.KEY_ENTER,
            wx.WXK_ESCAPE: constants.KEY_ESCAPE,
            wx.WXK_DELETE: constants.KEY_DELETE
            }

# Make uppercase letters be lowercase
for i in range(ord('A'), ord('Z')):
    KEYMAP[i] = i+32


def modifiers(event):
    """Convert the WX modifier state into a tuple of active modifier keys."""
    mod = ()
    if event.ShiftDown():
        mod += constants.KEY_SHIFT,
    if event.CmdDown():
        mod += constants.KEY_CONTROL,
    if event.AltDown():
        mod += constants.KEY_ALT,
    return mod


class GLWidget(GLCanvas):
    """ Implementation of the WX GLCanvas, which passes a number of
    events to the Figure object that wraps it.
    """
    
    def __init__(self, figure, parent, *args, **kwargs):     
        # make sure the window is double buffered (Thanks David!)
        kwargs.update({'attribList' : [wx.glcanvas.WX_GL_RGBA, 
            wx.glcanvas.WX_GL_DOUBLEBUFFER]})
        # call GLCanvas' init method
        GLCanvas.__init__(self, parent, *args, **kwargs)        
        
        self.figure = figure
        
        # find root window
        root = self.GetParent()
        while root.GetParent():
            root = root.GetParent()
        
        # make bindings for events
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        self.Bind(wx.EVT_RIGHT_DCLICK, self.OnDoubleClick)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        #        
        self.Bind(wx.EVT_MOTION, self.OnMotion)        
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)    
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        root.Bind(wx.EVT_CLOSE, self.OnClose) # Note root
        #
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        root.Bind(wx.EVT_ACTIVATE, self.OnActivate) # Note root
        
        # Needs to focus to catch key events
        self.SetFocus()
        
        # if lost, tough luck (thus the comment)
        #self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.OnMouseUp)
        
        # onpaint is called when shown is called by figure() function.
        

    def OnLeftDown(self, event):
        x,y = event.GetPosition()
        self.CaptureMouse() # make sure to capture release outside
        self.figure._GenerateMouseEvent('down', x, y, 1, modifiers(event))

    def OnLeftUp(self, event):
        x,y = event.GetPosition()
        try:
            self.ReleaseMouse()
        except Exception:
            pass
        self.figure._GenerateMouseEvent('up', x, y, 1, modifiers(event))

    def OnRightDown(self, event):
        x,y = event.GetPosition()
        self.CaptureMouse() # make sure to capture release outside
        self.figure._GenerateMouseEvent('down', x, y, 2, modifiers(event))

    def OnRightUp(self, event):
        x,y = event.GetPosition()  
        try:
            self.ReleaseMouse()
        except Exception:
            pass        
        self.figure._GenerateMouseEvent('up', x, y, 2, modifiers(event))
    
    def OnDoubleClick(self, event):
        but = 0
        x,y = event.GetPosition()
        if event.LeftDClick():
            but = 1            
        elif event.RightDClick():
            but = 2
        self.figure._GenerateMouseEvent('double', x, y, but, modifiers(event))
    
    def OnMotion(self, event):
        if self.figure:
            # poduce event
            x,y = event.GetPosition()
            self.figure._GenerateMouseEvent('motion', x, y, 0, modifiers(event))
    
    def OnMouseWheel(self, event):
        numDegrees = event.GetWheelRotation() / 8.0
        numSteps = numDegrees / 15.0
        # There is event.GetWheelAxis() but only in newer versions of wx
        # Mine has not so I am not able to even test it...
        horizontal, vertical = 0, numSteps
        if self.figure:
            x,y = event.GetPosition()
            self.figure._GenerateMouseEvent('scroll', x, y, horizontal, vertical, modifiers(event))
    
    def OnKeyDown(self, event):
        key, text = self._ProcessKey(event)
        self.figure._GenerateKeyEvent('keydown', key, text, modifiers(event))
    
    def OnKeyUp(self, event):        
        key, text = self._ProcessKey(event)
        self.figure._GenerateKeyEvent('keyup', key, text, modifiers(event))
    
    
    def _ProcessKey(self,event):
        """ evaluates the keycode of wx, and transform to visvis key.
        Also produce text version.
        return key, text. """
        key = event.GetKeyCode()
        # special cases for shift control and alt -> map to 17 18 19
        if key in KEYMAP:
            return KEYMAP[key], ''
        else:
            # other key, try producing text            
            if (65 <= key <= 90) and not event.ShiftDown():
                key += 32
            try:
                return key, chr(key)
            except ValueError:
                return key, ''
    
    def OnEnter(self, event):    
        if self.figure:
            ev = self.figure.eventEnter
            ev.Set(0,0,0)
            ev.Fire()
    
    def OnLeave(self, event):    
        if self.figure:
            ev = self.figure.eventLeave
            ev.Set(0,0,0)
            ev.Fire()
        
    def OnResize(self, event):
        if self.figure:
            self.figure._OnResize()
            event.Skip()
    
    def OnClose(self, event):        
        if self.figure:
            self.figure.Destroy()             
            parent = self.GetParent()
            self.Destroy() # Hide and delete window
            # Prevent frame from sticking when there is no wx event loop
            if isinstance(parent, FigureFrame):
                parent.Hide()
        event.Skip()
    
    def OnFocus(self, event):
        if self.figure:
            BaseFigure._currentNr = self.figure.nr
            event.Skip()

    def OnPaint(self, event):
        # I read that you should always create a PaintDC when implementing
        # an OnPaint event handler.        
        a = wx.PaintDC(self) 
        if self.GetContext(): 
            self.figure.OnDraw()
        event.Skip()
    
    def OnActivate(self, event):
        # When the title bar is dragged in ubuntu
        if event.GetActive():
            self.Refresh()
        event.Skip()
    
    def OnEraseBackground(self, event):
        pass # This prevents flicker on Windows


class Figure(BaseFigure):
    """ This is the wxPython implementation of the figure class.
    
    A Figure represents the OpenGl context and is the root
    of the visualization tree; a Figure Wibject does not have a parent.
    
    A Figure can be created with the function vv.figure() or vv.gcf().
    """
    
    def __init__(self, parent, *args, **kwargs):
        
        self._widget = None
        self._widget_args = (parent, args, kwargs)
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
            parent, args, kwargs = self._widget_args
            if 'create_widget' in kwargs:
                updatePosition = True
                del(kwargs['create_widget'])
            self._widget = GLWidget(self, parent, *args, **kwargs)
            if updatePosition:
                self.position._Changed()
        return self._widget
    
    
    def _SetCurrent(self):
        """ make this scene the current context """
        if not self._destroyed and self._widget is not None:            
            try:
                self._widget.SetCurrent()
            except Exception:
                # can happen when trying to call this method after            
                # the window was destroyed.
                pass 
    
    
    def _SwapBuffers(self):
        """ Swap the memory and screen buffer such that
        what we rendered appears on the screen """
        if self._widget and not self._destroyed:
            self._widget.SwapBuffers()

    def _SetTitle(self, title):
        """ Set the title of the figure... """
        if self._widget and not self._destroyed:
            window = self._widget.GetParent()
            if hasattr(window,'SetTitle'):
                window.SetTitle(title)
    
    def _SetPosition(self, x, y, w, h):
        """ Set the position of the widget. """
        # select widget to resize. If it 
        if self._widget and not self._destroyed:            
            widget = self._widget
            if isinstance(widget.GetParent(), FigureFrame):
                widget = widget.GetParent()
            # apply
            #widget.SetDimensions(x, y, w, h)
            widget.MoveXY(x,y)
            widget.SetClientSizeWH(w,h)
    
    def _GetPosition(self):
        """ Get the position of the widget. """
        # select widget to resize. If it 
        if self._widget and not self._destroyed:
            widget = self._widget
            if isinstance(widget.GetParent(), FigureFrame):
                widget = widget.GetParent()
            # get and return
            #tmp = widget.GetRect()        
            #return tmp.left, tmp.top, tmp.width, tmp.height
            size = widget.GetClientSizeTuple()
            pos = widget.GetPositionTuple()
            return pos[0], pos[1], size[0], size[1]
        return 0, 0, 0, 0
    
    
    def _RedrawGui(self):
        if self._widget:
            self._widget.Refresh()
    
    
    def _ProcessGuiEvents(self):
        app.ProcessEvents()
    
    
    def _Close(self, widget):
        if widget is None:
            widget = self._widget
        if widget and widget.GetParent():
            try:
                widget.GetParent().Hide()
                widget.GetParent().Close()
            except wx.PyAssertionError:
                # Prevent "wxEVT_MOUSE_CAPTURE_LOST not being processed" error.
                pass 


class FigureFrame(wx.Frame):
    """ Define a Frame. This is only to be able to tell whether
    the Figure object is used as a widget or as a Figure on its
    own. """
    pass


def newFigure():
    """ Create a window with a figure widget.
    """
    
    # Make sure there is a native app. Need here too, because we need to
    # create the figure frame first
    app.Create()
    
    # Create frame
    refSize = tuple( visvis.settings.figureSize )
    frame = FigureFrame(None, -1, "Figure", size=refSize)
    
    # Correct size. The given size includes the window manager's frame
    size = frame.GetClientSizeTuple()
    w = refSize[0] + (refSize[0] - size[0])
    h = refSize[1] + (refSize[1] - size[1])
    frame.SetSize((w,h))
    
    # Inser figure
    figure = Figure(frame)
    
    # Set icon
    try:
        iconFile = os.path.join(getResourceDir(), 'visvis_icon_wx.png')
        frame.SetIcon(wx.Icon(iconFile, wx.BITMAP_TYPE_PNG))
    except Exception:        
        pass
    
    # Show AFTER canvas is added
    frame.Show() 
    
    # Apply a draw, so that OpenGl can initialize before we will really
    # do some drawing. Otherwis textures end up showing in black.
    figure.DrawNow()
    app.ProcessEvents() # Fixes issue 43
    return figure


class VisvisEventsTimer(wx.Timer):
    def Notify(self):
        events.processVisvisEvents()


class App(events.App):
    """ App()
    
    Application class to wrap the GUI applications in a class
    with a simple interface that is the same for all backends.
    
    This is the wxPython implementation.
    
    """
    
    def __init__(self):
        # Timer to enable timers in visvis. Should be created AFTER the app
        self._timer = None
    
    def _GetNativeApp(self):
        # Get native app in save way. Taken from guisupport.py, 
        # but use wx.App() class because PySimpleApp is deprecated
        app = wx.GetApp()
        if app is None:
            app = wx.App(False)
        # Store so it won't be deleted, but not on a visvis object,
        # or an application may produce error when closed
        wx.app_instance = app
        # Start timer
        if self._timer is None:
            self._timer = VisvisEventsTimer()
            self._timer.Start(10, False)
        # Return
        return app
    
    def _ProcessEvents(self):
        
        # Get app
        app = self._GetNativeApp()
        
        # Keep reference of old eventloop instance
        old = wx.EventLoop.GetActive()
        # Create new eventloop and process
        eventLoop = wx.EventLoop()
        wx.EventLoop.SetActive(eventLoop)                        
        while eventLoop.Pending():
            eventLoop.Dispatch()
        # Process idle
        app.ProcessIdle() # otherwise frames do not close
        # Set back the original
        wx.EventLoop.SetActive(old)  
    
    def _Run(self):
        app = self._GetNativeApp()
        if hasattr(app, '_in_event_loop') and app._in_event_loop:
            pass # Already in event loop
        else:
            app.MainLoop()

# Create application instance now
app = App()
