# -*- coding: utf-8 -*-
# vispy: testskip (KNOWNFAIL)
# Copyright (c) 2015, Felix Schill.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of mouse drawing and editing of a line plot.
This demo extends the Line visual from scene adding mouse events that allow
modification and creation of line points with the mouse.
Vispy takes care of coordinate transforms from screen to ViewBox - the
demo works on different zoom levels.
"""

import numpy as np

from vispy import app, scene


class EditLineVisual(scene.visuals.Line):
    """
    Mouse editing extension to the Line visual.
    This class adds mouse picking for line points, mouse_move handling for
    dragging existing points, and
    adding new points when clicking into empty space.
    """

    def __init__(self, *args, **kwargs):
        scene.visuals.Line.__init__(self, *args, **kwargs)

        # initialize point markers
        self.markers = scene.visuals.Markers()
        self.marker_colors = np.ones((len(self.pos), 4), dtype=np.float32)
        self.markers.set_data(pos=self.pos, symbol="s", edge_color="red",
                              size=6)
        self.selected_point = None
        self.selected_index = -1
        # snap grid size
        self.gridsize = 10

    def draw(self, transforms):
        # draw line and markers
        scene.visuals.Line.draw(self, transforms)
        self.markers.draw(transforms)

    def print_mouse_event(self, event, what):
        """ print mouse events for debugging purposes """
        print('%s - pos: %r, button: %s,  delta: %r' %
              (what, event.pos, event.button, event.delta))

    def select_point(self, event, radius=5):

        """
        Get line point close to mouse pointer and its index

        Parameters
        ----------
        event : the mouse event being processed
        radius : scalar
            max. distance in pixels between mouse and line point to be accepted
        return: (numpy.array, int)
            picked point and index of the point in the pos array
        """

        # position in scene/document coordinates
        pos_scene = event.pos[:3]

        # project mouse radius from screen coordinates to document coordinates
        mouse_radius = \
            (event.visual_to_canvas.imap(np.array([radius, radius, radius])) -
             event.visual_to_canvas.imap(np.array([0, 0, 0])))[0]
        # print("Mouse radius in document units: ", mouse_radius)

        # find first point within mouse_radius
        index = 0
        for p in self.pos:
            if np.linalg.norm(pos_scene - p) < mouse_radius:
                # print p, index
                # point found, return point and its index
                return p, index
            index += 1
        # no point found, return None
        return None, -1

    def update_markers(self, selected_index=-1, highlight_color=(1, 0, 0, 1)):
        """ update marker colors, and highlight a marker with a given color """
        self.marker_colors.fill(1)
        # default shape (non-highlighted)
        shape = "o"
        size = 6
        if 0 <= selected_index < len(self.marker_colors):
            self.marker_colors[selected_index] = highlight_color
            # if there is a highlighted marker,
            # change all marker shapes to a square
            shape = "s"
            size = 8
        self.markers.set_data(pos=self.pos, symbol=shape, edge_color='red',
                              size=size, face_color=self.marker_colors)

    def on_mouse_press(self, event):
        self.print_mouse_event(event, 'Mouse press')
        pos_scene = event.pos[:3]

        # find closest point to mouse and select it
        self.selected_point, self.selected_index = self.select_point(event)

        # if no point was clicked add a new one
        if self.selected_point is None:
            print("adding point", len(self.pos))
            self._pos = np.append(self.pos, [pos_scene], axis=0)
            self.set_data(pos=self.pos)
            self.marker_colors = np.ones((len(self.pos), 4), dtype=np.float32)
            self.selected_point = self.pos[-1]
            self.selected_index = len(self.pos) - 1

        # update markers and highlights
        self.update_markers(self.selected_index)

    def on_mouse_release(self, event):
        self.print_mouse_event(event, 'Mouse release')
        self.selected_point = None
        self.update_markers()

    def on_mouse_move(self, event):
        # left mouse button
        if event.button == 1:
            # self.print_mouse_event(event, 'Mouse drag')
            if self.selected_point is not None:
                pos_scene = event.pos
                # update selected point to new position given by mouse
                self.selected_point[0] = round(pos_scene[0] / self.gridsize) \
                    * self.gridsize
                self.selected_point[1] = round(pos_scene[1] / self.gridsize) \
                    * self.gridsize
                self.set_data(pos=self.pos)
                self.update_markers(self.selected_index)

        else:
            #  if no button is pressed, just highlight the marker that would be
            # selected on click
            hl_point, hl_index = self.select_point(event)
            self.update_markers(hl_index, highlight_color=(0.5, 0.5, 1.0, 1.0))
            self.update()


class Canvas(scene.SceneCanvas):
    """ A simple test canvas for testing the EditLineVisual """

    def __init__(self):
        scene.SceneCanvas.__init__(self, keys='interactive',
                                   size=(800, 800))

        # Create some initial points
        n = 7
        self.pos = np.zeros((n, 3), dtype=np.float32)
        self.pos[:, 0] = np.linspace(-50, 50, n)
        self.pos[:, 1] = np.random.normal(size=n, scale=10, loc=0)

        # create new editable line
        self.line = EditLineVisual(pos=self.pos, color='w', width=3,
                                   antialias=True, method='gl')

        self.view = self.central_widget.add_view()
        self.view.camera = scene.PanZoomCamera(rect=(-100, -100, 200, 200),
                                               aspect=1.0)
        # the left mouse button pan has to be disabled in the camera, as it
        # interferes with dragging line points
        # Proposed change in camera: make mouse buttons configurable
        self.view.camera._viewbox.events.mouse_move.disconnect(
            self.view.camera.viewbox_mouse_event)

        self.view.add(self.line)
        self.show()
        self.selected_point = None
        scene.visuals.GridLines(parent=self.view.scene)


if __name__ == '__main__':
    win = Canvas()
    app.run()
