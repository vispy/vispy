# -*- coding: utf-8 -*-
"""
This example demonstrates the use of the SurfacePlot visual.
"""

import vispy.app, vispy.scene
import vispy.util.filter
import numpy as np


canvas = vispy.scene.SceneCanvas(keys='interactive')
canvas.show()
view = canvas.central_widget.add_view()
view.set_camera('turntable', mode='perspective', up='z', distance=2)


## Simple surface plot example
## x, y values are not specified, so assumed to be 0:50
z = vispy.util.filter.gaussian_filter(np.random.normal(size=(50,50)), (1, 1))
p1 = vispy.scene.visuals.SurfacePlot(z=z, color=(0.5, 0.5, 1, 1), 
                                     shading='smooth')
p1.transform = vispy.scene.transforms.AffineTransform()
p1.transform.scale([1/49., 1/49., 0.02])
p1.transform.translate([-0.5, -0.5, 0])

normal_comp = vispy.scene.components.VertexNormalComponent(p1._meshdata)
p1.color_components = [
    vispy.scene.components.UniformColorComponent((0.5, 0.5, 1, 1)),
    vispy.scene.components.ShadingComponent(normal_comp,
                                        lights=[((-1, -1, -1),
                                                 (1.0, 1.0, 1.0))],
                                        ambient=0.2)]

view.add(p1)


# Add a 3D axis to keep us oriented
axis = vispy.scene.visuals.XYZAxis(parent=view.scene)



### Saddle example with x and y specified
#x = np.linspace(-8, 8, 50)
#y = np.linspace(-8, 8, 50)
#z = 0.1 * ((x.reshape(50,1) ** 2) - (y.reshape(1,50) ** 2))
#p2 = gl.GLSurfacePlotItem(x=x, y=y, z=z, shader='normalColor')
#p2.translate(-10,-10,0)
#w.addItem(p2)


### Manually specified colors
#z = pg.gaussianFilter(np.random.normal(size=(50,50)), (1,1))
#x = np.linspace(-12, 12, 50)
#y = np.linspace(-12, 12, 50)
#colors = np.ones((50,50,4), dtype=float)
#colors[...,0] = np.clip(np.cos(((x.reshape(50,1) ** 2) + (y.reshape(1,50) ** 2)) ** 0.5), 0, 1)
#colors[...,1] = colors[...,0]

#p3 = gl.GLSurfacePlotItem(z=z, colors=colors.reshape(50*50,4), shader='shaded', smooth=False)
#p3.scale(16./49., 16./49., 1.0)
#p3.translate(2, -18, 0)
#w.addItem(p3)




### Animated example
### compute surface vertex data
#cols = 90
#rows = 100
#x = np.linspace(-8, 8, cols+1).reshape(cols+1,1)
#y = np.linspace(-8, 8, rows+1).reshape(1,rows+1)
#d = (x**2 + y**2) * 0.1
#d2 = d ** 0.5 + 0.1

### precompute height values for all frames
#phi = np.arange(0, np.pi*2, np.pi/20.)
#z = np.sin(d[np.newaxis,...] + phi.reshape(phi.shape[0], 1, 1)) / d2[np.newaxis,...]


### create a surface plot, tell it to use the 'heightColor' shader
### since this does not require normal vectors to render (thus we 
### can set computeNormals=False to save time when the mesh updates)
#p4 = gl.GLSurfacePlotItem(x=x[:,0], y = y[0,:], shader='heightColor', computeNormals=False, smooth=False)
#p4.shader()['colorMap'] = np.array([0.2, 2, 0.5, 0.2, 1, 1, 0.2, 0, 2])
#p4.translate(10, 10, 0)
#w.addItem(p4)

#index = 0
#def update():
    #global p4, z, index
    #index -= 1
    ##p4.setData(z=z[index%z.shape[0]])
    #w.update()
    
#timer = QtCore.QTimer()
#timer.timeout.connect(update)
#timer.start(0)

### Start Qt event loop unless running in interactive mode.
#if __name__ == '__main__':
    #import sys
    #if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        #QtGui.QApplication.instance().exec_()

#canvas.app.run()
