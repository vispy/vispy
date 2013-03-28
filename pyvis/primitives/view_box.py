"""
Subclass of box which displays children using a user-specified coordinate system.
 - scale / pan / rotate by mouse or keyboard
   (this should be completely configurable with nice defaults; nobody ever agrees on the best way to do this)
 - manages one or more camera objects defining the internal coordinate system
 - clipping to boundaries
 - ideally, changes internal to a view box should cause _only_ that box to be redrawn. This is very important
   if you have, for example, a grid of 20x20 plots
"""
