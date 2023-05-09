import sys
import time
import numpy as np
from vispy import app, scene
from vispy.geometry import curves
from vispy.scene import visuals

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
scatter                          = visuals.Markers()
point_color                      = np.full((NUMBER_POINT, 4), FILTERED_COLOR)
scatter.set_data(pos, edge_width =0, face_color = point_color, size = SCATTER_SIZE)

view.add(scatter)

def points_in_polygon(polygon, pts):
    """
    It's simply a copy/paste of below code provided by @Ta946 to demonstrate feasibility of lasso selection with VisPy
    https://stackoverflow.com/questions/36399381/whats-the-fastest-way-of-checking-if-a-point-is-inside-a-polygon-in-python
    """
    pts = np.asarray(pts,dtype='float32')
    polygon = np.asarray(polygon,dtype='float32')
    contour2 = np.vstack((polygon[1:], polygon[:1]))
    test_diff = contour2-polygon

    m1    = (polygon[:,1] > pts[:,None,1]) != (contour2[:,1] > pts[:,None,1])
    slope = ((pts[:,None,0]-polygon[:,0])*test_diff[:,1])-(test_diff[:,0]*(pts[:,None,1]-polygon[:,1]))
    m2    = slope == 0
    mask2 = (m1 & m2).any(-1)
    m3    = (slope < 0) != (contour2[:,1] < polygon[:,1])
    m4    = m1 & m3
    count = np.count_nonzero(m4,axis=-1)
    mask3 = ~(count%2==0)
    mask  = mask2 | mask3

    return mask

def select(polygon_vertices, points):
    # Optimization: it would be faster to transform coordinates of polygons instead of scatter
    # since number of vertices would be generally much lower.
    polygon_vertices = scatter.get_transform('canvas', 'visual').map(polygon_vertices)

    # Check if points are inside the bounding box otherwise filter them out for
    # subsequent checks. This would reduce required computation most of time.
    
    # Coordinates of selection's bounding box    
    x1, x2, y1, y2 = np.min(polygon_vertices[:, 0]), np.max(polygon_vertices[:, 0]), np.min(polygon_vertices[:, 1]), np.max(polygon_vertices[:, 1])

    bbox_mask = (x1 < points[:, 0]) & (points[:, 0] < x2) & (y1 < points[:, 1]) & (points[:, 1] < y2)
    selected_mask = bbox_mask

    selected_mask = points_in_polygon(polygon_vertices, points)
    # n = len(polygon_vertices)
    # inside = []

    # for x, y in points[bbox_mask]:
    #     p1x, p1y = polygon_vertices[0, 0:2]
    #     inside.append(False)
    #     for i in range(n+1):
    #         p2x, p2y = polygon_vertices[i % n, 0:2]

    #         if min(p1y, p2y) < y <= max(p1y, p2y) and x <= max(p1x, p2x):
    #             if p1y != p2y:
    #                 xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
    #             if p1x == p2x or x <= xints:
    #                 inside[-1] = not inside[-1]

    return selected_mask

@canvas.connect
def on_mouse_press(event):
    global point_color
    
    if event.button == 1:
        # Reset state
        # TODO: Instead of recreating a full array which can be time consuming, only selected points shall be set
        # to filtered color.
        
        lasso.set_data(pos = np.empty((1, 2)))

        # TODO: Check if there's a more convenient way, resetting all vertices is quite slow
        point_color = np.full((len(pos), 4), SELECTED_COLOR)
        scatter.set_data(pos, edge_width =0, face_color = point_color, size = SCATTER_SIZE)
        
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
            # selected_mask    = select(polygon_vertices, pos)
            
            lasso.set_data(pos = np.insert(polygon_vertices, len(polygon_vertices), polygon_vertices[0], axis = 0))

            # Set selected points with selection color
            # point_color[selected_mask] = SELECTED_COLOR
            # point_color[~selected_mask] = FILTERED_COLOR

            scatter.set_data(pos, edge_width = 0, face_color = point_color, size = SCATTER_SIZE)
            px, py = pp

@canvas.connect
def on_mouse_release(event):
    global point_color

    if event.button == 1:
        selected_mask = select(event.trail(), pos)

        # Set selected points with selection color
        point_color[selected_mask] = SELECTED_COLOR
        point_color[~selected_mask] = FILTERED_COLOR
        scatter.set_data(pos, edge_width = 0, face_color = point_color, size = SCATTER_SIZE)

if __name__ == '__main__':
    canvas.show()
    if sys.flags.interactive == 0:
        app.run()