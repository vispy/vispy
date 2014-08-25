# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


from .line import Line
from .markers import Markers
from .visual import Visual

class PlotLine(Visual):
    """
    Visual displaying a plot line with optional markers.
    
    Examples:
    
    PlotLine(y_vals)
    PlotLine(x_vals, y_vals)
    PlotLine(xy_vals)
    
    
    
    """
    def __init__(self, *args, **kwds):
        my_kwds = {}
        for k in ['color', 'width', 'connect']:
            my_kwds[k] = kwds.pop(k, None)
        
        Visual.__init__(self, **kwds)
        self._line = Line()
        self._markers = Markers()
        
        self.set_data(*args, **my_kwds)
        
    def set_data(self, *args, **kwds):
        args = [np.array(x) for x in args]
        
        if len(args) == 1:
            arg = args[0]
            if arg.ndim == 2:
                # xy array already provided
                pos = arg
            elif arg.ndim == 1:
                # only y supplied, generate arange x
                pos = np.empty((len(arg), 2), dtype=np.float32)
                pos[:, 1] = arg
                pos[:, 0] = np.arange(len(arg))
            else:
                raise TypeError("Invalid argument: array must have ndim "
                                "<= 2.")
        elif len(args) == 2:
            pos = np.concatenate([args[0][:,np.newaxis], 
                                  args[1][:,np.newaxis]], axis=1)
        else:
            raise TypeError("Too many positional arguments given (max is 2).")
        
        # todo: have both sub-visuals share the same buffers.
        line_kwds = {}
        for k in ['width', 'connect', 'color']:
            line_kwds[k] = kwds.pop(k, None)
        self._line.set_data(pos=pos, **line_kwds)
        
        self._markers.set_data(pos=pos)
        
        if len(kwds) > 0:
            raise TypeError("Invalid keyword arguments: %s" % kwds.keys())
        
    def draw(self, event):
        for v in self._line, self._markers:
            event.push_visual(v)
            try:
                v.draw(event)
            finally:
                event.pop_visual(v)
    