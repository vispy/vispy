# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Vispy Lasso
=============

Demonstrate the use of lasso selection.

The lasso selection is done on a 2D scatter but could be extended further by user.
"""
import sys
import time
import numpy as np
from vispy import app, scene
from vispy.geometry import curves
from vispy.scene import visuals
from matplotlib import path

LASSO_COLOR               = (1, .1, .1)
FILTERED_COLOR            = (1, 1, 1, 0.3)
SELECTED_COLOR            = (0.3, 0, 1, 1.0)
PEN_RADIUS                = 2
MIN_MOVE_UPDATE_THRESHOLD = 5
NUMBER_POINT              = 200000
SCATTER_SIZE              = 5

canvas = scene.SceneCanvas(keys='interactive', show=True)
view = canvas.central_widget.add_view()

pointer = scene.visuals.Ellipse(center=(0., 0.), radius=(PEN_RADIUS, PEN_RADIUS,), color=None, border_width=0.2, border_color="white",
                                num_segments=10, parent=view.scene)

lasso = scene.visuals.Line(pos=np.array([[0, 0], [0, 0]]), color = LASSO_COLOR, parent=view.scene, width = PEN_RADIUS , antialias=True)
px, py = 0, 0

# generate data
pos = 360 * np.random.normal(size=(NUMBER_POINT, 2), scale=1)

# one could stop here for the data generation, the rest is just to make the
# data look more interesting. Copied over from magnify.py
centers = np.random.normal(size=(NUMBER_POINT, 2), scale = 1) * 960
indexes = np.random.normal(size=NUMBER_POINT, loc=centers.shape[0] / 2,
                           scale=centers.shape[0] / 3)
indexes = np.clip(indexes, 0, centers.shape[0] - 1).astype(int)
pos += centers[indexes]

# create scatter object and fill in the data
scatter = visuals.Markers()
point_color = np.full((NUMBER_POINT, 4), FILTERED_COLOR)
scatter.set_data(pos, edge_width=0, face_color=point_color, size=SCATTER_SIZE)

view.add(scatter)

def points_in_polygon(polygon, pts):
    """
    Get boolean mask of points in a polygon reusing matplotlib implementation.
    
    This is a proof of concept and depending on your use case, willingness
    to add other dependencies, and your performance needs one of the other answers
    on the above question would serve you better (ex. shapely, etc).
    """
    polygon = path.Path(polygon[:, :2], closed = True)
    mask = polygon.contains_points(pts[:, :2])
    return mask

def select(polygon_vertices, points):
    # Set default mask to filter everything since user selection
    # is not yet calculated.
    selected_mask = np.full((NUMBER_POINT, 4), FILTERED_COLOR)

    if polygon_vertices is not None:
        # Optimization: It's faster to convert lasso selection straight to visual coordinates since there's generally less vertices
        # this would speed up the processing depending on the scene.
        polygon_vertices = scatter.get_transform('canvas', 'visual').map(polygon_vertices)
        selected_mask = points_in_polygon(polygon_vertices, points)

    return selected_mask

@canvas.connect
def on_mouse_press(event):
    global point_color
    
    if event.button == 1:
        # Reset state.
        lasso.set_data(pos=np.empty((1, 2)))

        # Reset every vertices to the filtered color
        point_color[:] = FILTERED_COLOR

        scatter.set_data(pos, edge_width=0, face_color=point_color, size=SCATTER_SIZE)
        
@canvas.connect
def on_mouse_move(event):
    global pointer, px, py

    pp = event.pos

    # Optimization: to avoid too much recalculation/update we can update scene only if the mouse
    # moved a certain amount of pixel.
    if (abs(px - pp[0]) > MIN_MOVE_UPDATE_THRESHOLD or abs(py - pp[1]) > MIN_MOVE_UPDATE_THRESHOLD):
        pointer.center = pp
        if event.button == 1:            
            polygon_vertices = event.trail()
            lasso.set_data(pos = np.insert(polygon_vertices, len(polygon_vertices), polygon_vertices[0], axis=0))
            scatter.set_data(pos, edge_width=0, face_color=point_color, size=SCATTER_SIZE)
            px, py = pp

@canvas.connect
def on_mouse_release(event):
    global point_color

    if event.button == 1:
        selected_mask = select(event.trail(), pos)

        # Set selected points with selection color
        point_color[selected_mask] = SELECTED_COLOR
        point_color[~selected_mask] = FILTERED_COLOR
        scatter.set_data(pos, edge_width=0, face_color=point_color, size=SCATTER_SIZE)

if __name__ == '__main__':
    canvas.show()
    if sys.flags.interactive == 0:
        app.run()