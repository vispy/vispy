# -*- coding: utf-8 -*-
# vispy: testskip
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
This is a very minimal example that opens a window and makes the background
color to change from black to white to black ...

The wx backend is used to embed the canvas in a simple wx Frame with
a menubar.
"""

import wx
import math
from vispy import app, gloo


class Canvas(app.Canvas):
    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        self._timer = app.Timer('auto', connect=self.on_timer, start=True)
        self.tick = 0

    def on_draw(self, event):
        gloo.clear(color=True)

    def on_timer(self, event):
        self.tick += 1 / 60.0
        c = abs(math.sin(self.tick))
        gloo.set_clear_color((c, c, c, 1))
        self.update()

    def stop_timer(self):
        self._timer.stop()


class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Vispy Test",
                          wx.DefaultPosition, size=(500, 500))

        MenuBar = wx.MenuBar()
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_EXIT, "&Quit")
        self.Bind(wx.EVT_MENU, self.on_quit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_SHOW, self.on_show)
        MenuBar.Append(file_menu, "&File")
        self.SetMenuBar(MenuBar)

        self.canvas = Canvas(app="wx", parent=self)

    def on_quit(self, event):
        self.canvas.stop_timer()
        self.Close(True)

    def on_show(self, event):
        self.canvas.show()
        event.Skip()


if __name__ == '__main__':
    myapp = wx.App(0)
    frame = TestFrame()
    frame.Show(True)
    myapp.MainLoop()
