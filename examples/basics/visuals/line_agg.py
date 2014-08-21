from __future__ import division
from collections import namedtuple
import numpy as np
from math import exp

from vispy import app
from vispy import gloo
#from vispy.scene.shaders import Function, ModularProgram
from vispy.scene.visuals import LineAgg
from vispy.scene.visuals import Visual
from vispy.scene.transforms import STTransform, LogTransform, PolarTransform
from vispy import scene

class PanZoomTransform(STTransform):
    pan = (0., 0.)
    
    def move(self, (dx, dy)):
        """I call this when I want to translate."""
        self.translate = self.translate + (dx, -dy, 0, 0)
        
    def zoom(self, (dx, dy), center=(0., 0.)):
        """I call this when I want to zoom."""
        scale = (exp(0.01*dx), exp(0.01*dy), 1, 1)
        center = center + (0., 1.)
        self.translate = center + ((self.translate - center) * scale)
        self.scale = self.scale * scale




class PlotCanvas(scene.SceneCanvas):
    #def _normalize(self, (x, y)):
        #w, h = float(self.size[0]), float(self.size[1])
        #return x/(w/2.)-1., y/(h/2.)-1.
    
    def __init__(self, **kwargs):
        scene.SceneCanvas.__init__(self, keys='interactive', **kwargs)
        self._visuals = []
        self.panzoom = PanZoomTransform()
        self.panzoom.scale = (200, -200)
        self.panzoom.translate = (300, 300)
        self.doc_px_transform = STTransform(scale=(1, 1), translate=(0, 0))
        self.px_ndc_transform = STTransform(scale=(1, 1), translate=(0, 0))
        self._update_transforms()
        
    def _update_transforms(self):
        # Update doc and pixel transforms to account for new canvas shape.
        
        # Eventually this should be provided by the base Canvas class
        # and should account for logical vs physical pixels, framebuffers, 
        # and glViewport. 
        
        s = self.size
        self.px_ndc_transform.scale = (2.0 / s[0], -2.0 / s[1])
        self.px_ndc_transform.translate = (-1, 1)

    def add_visual(self, name, value):
        self._visuals.append(value)
        value._parent = self
        value.transform = self.panzoom * PolarTransform()
        
    def __setattr__(self, name, value):
        super(PlotCanvas, self).__setattr__(name, value)
        if isinstance(value, Visual):
            self.add_visual(name, value)
        
    def on_mouse_move(self, event):
        if event.is_dragging:
            #x0, y0 = self._normalize(event.press_event.pos)
            #x1, y1 = self._normalize(event.last_event.pos)
            #x, y = self._normalize(event.pos)
            x0, y0 = event.press_event.pos
            x1, y1 = event.last_event.pos
            x, y = event.pos
            dxy = ((x - x1), -(y - y1))
            center = (x0, y0)
            button = event.press_event.button
            
            if button == 1:
                self.panzoom.move(dxy)
            elif button == 2:
                self.panzoom.zoom(dxy, center=center)
                
            self.update()
        
    def on_mouse_wheel(self, event):
        c = 1.01 ** event.delta[1]
        #x, y = self._normalize(event.pos)
        self.panzoom.zoom((c, c), center=event.pos)
        self.update()
        
    def on_resize(self, event):
        self.width, self.height = event.size
        gloo.set_viewport(0, 0, self.width, self.height)
        self._update_transforms()

    def on_draw(self, event):
        gloo.clear()
        for v in self._visuals:
            self.draw_visual(v)

    def show(self):
        super(PlotCanvas, self).show()
        app.run()
        
    
    
    
    


if __name__ == '__main__':
    ax = PlotCanvas(size=(600,600))
    
    x = np.linspace(-1., 1., 1000)
    y = .25*np.sin(15*x) + 1.
    vertices1 = np.c_[x,y]
    vertices2 = np.c_[np.cos(3*x)*.5, np.sin(3*x)*.5]
    
    ax.line = LineAgg(paths=[vertices1, vertices2], style=[
        dict(color=(1., 0., 0., 1.)),
        dict(color=(0., 1., 0., 1.)),
    ])
    ax.show()

