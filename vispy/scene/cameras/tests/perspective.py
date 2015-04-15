# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import sys

from vispy import app, scene, io

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 800, 600
canvas.show()

grid = canvas.central_widget.add_grid()
grid.padding = 20

imdata = io.load_crate().astype('float32') / 255

views = []
images = []
for i in range(2):
    for j in range(2):
        v = grid.add_view(row=i, col=j, border_color='white')
        v.camera = 'turntable'
        v.camera.fov = 50
        v.camera.distance = 30
        #v.camera = 'panzoom'
        #v.camera.aspect = 1
        
        views.append(v)
        image = scene.visuals.Image(imdata, method='impostor', grid=(4, 4))
        image.transform = scene.STTransform(translate=(-12.8, -12.8),
                                            scale=(0.1, 0.1))
        v.add(image)
        images.append(image)
        

@canvas.connect
def on_key_press(ev):
    if ev.key.name == '1':
        print("Image method: impostor")
        for im in images:
            im.method = 'impostor'
    elif ev.key.name == '2':
        print("Image method: subdivide")
        for im in images:
            im.method = 'subdivide'
    elif ev.key.name == '3':
        print("Viewbox method: fragment")
        for vb in views:
            vb.clip_method = 'fragment'
    elif ev.key.name == '4':
        print("Viewbox method: viewport")
        for vb in views:
            vb.clip_method = 'viewport'
    elif ev.key.name == '5':
        print("Viewbox method: fbo")
        for vb in views:
            vb.clip_method = 'fbo'
    

if __name__ == '__main__':
    if sys.flags.interactive != 1:
        app.run()
