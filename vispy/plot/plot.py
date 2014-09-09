# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from ..geometry import MeshData
from ..io import read_mesh
from ..scene import SceneCanvas, visuals

plots = []


def plot(*args, **kwds):
    """ Create a new canvas and plot the given data. 
    
    For arguments, see scene.visuals.LinePlot.
    """
    canvas = SceneCanvas(keys='interactive')
    canvas.view = canvas.central_widget.add_view()
    canvas.line = visuals.LinePlot(*args, **kwds)
    canvas.view.add(canvas.line)
    canvas.view.camera.auto_zoom(canvas.line)
    canvas.show()
    plots.append(canvas)
    return canvas


def image(*args, **kwds):
    """ Create a new canvas and display the given image data.
    
    For arguments, see scene.visuals.Image.
    """
    canvas = SceneCanvas(keys='interactive')
    canvas.view = canvas.central_widget.add_view()
    canvas.image = visuals.Image(*args, **kwds)
    canvas.view.add(canvas.image)
    canvas.show()
    canvas.view.camera.invert_y = False
    canvas.view.camera.auto_zoom(canvas.image)
    plots.append(canvas)
    return canvas


def mesh(vertices=None, faces=None, vertex_colors=None, face_colors=None,
         color=(0.5, 0.5, 1.), fname=None, meshdata=None, shading='smooth',
         center=(0., 0., 0.), distance=1., azimuth=0., elevation=0.):
    """Create a new canvas and plot the given mesh

    A TurntableCamera (canvas.view) will be used to show the object.

    Parameters
    ----------
    vertices : array
        Vertices.
    faces : array | None
        Face definitions.
    normals : array | None
        Vertex normals.
    vertex_colors : array | None
        Vertex colors.
    face_colors : array | None
        Face colors.
    color : instance of Color
        Color to use.
    fname : str | None
        Filename to load. If not None, then vertices, faces, and meshdata
        must be None.
    meshdata : MeshData | None
        Meshdata to use. If not None, then vertices, faces, and fname
        must be None.
    center : tuple
        (X, Y, Z) location the camera points at.
    distance : float
        Camera distance.
    azimuth : float
        Azimuth in degrees.

    Returns
    -------
    canvas : SceneCanvas
        The canvas.
    """
    if fname is not None:
        if not all(x is None for x in (vertices, faces, meshdata)):
            raise ValueError('vertices, faces, and meshdata must be None if '
                             'fname is not None')
        vertices, faces = read_mesh(fname)[:2]
    if meshdata is not None:
        if not all(x is None for x in (vertices, faces, fname)):
            raise ValueError('vertices, faces, and fname must be None if '
                             'fname is not None')
    else:
        meshdata = MeshData(vertices, faces)
    canvas = SceneCanvas(keys='interactive')
    canvas.view = canvas.central_widget.add_view()
    canvas.view.set_camera('turntable', mode='perspective',
                           center=center, distance=distance, azimuth=azimuth,
                           elevation=elevation)
    canvas.mesh = visuals.Mesh(meshdata=meshdata,
                               vertex_colors=vertex_colors,
                               face_colors=face_colors,
                               color=color, shading='smooth')
    canvas.view.add(canvas.mesh)
    # canvas.view.camera.auto_zoom(image)  # XXX Don't have this for Turntable
    plots.append(canvas)
    return canvas
