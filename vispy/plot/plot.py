# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np

from ..geometry import MeshData
from ..io import read_mesh
from ..scene import SceneCanvas, visuals, cameras
from ..color import Colormap

plots = []


def plot(*args, **kwargs):
    """ Create a new canvas and plot the given data.

    For arguments, see scene.visuals.LinePlot.
    """
    canvas = SceneCanvas(keys='interactive')
    canvas.view = canvas.central_widget.add_view()
    canvas.line = visuals.LinePlot(*args, **kwargs)
    canvas.view.add(canvas.line)
    if False:  # todo: of data-is-3D
        canvas.view.camera = 'turntable'
    else:    
        canvas.view.camera = 'panzoom'
    canvas.show()
    plots.append(canvas)
    return canvas


def image(*args, **kwargs):
    """ Create a new canvas and display the given image data.

    For arguments, see scene.visuals.Image.
    """
    canvas = SceneCanvas(keys='interactive')
    canvas.view = canvas.central_widget.add_view()
    canvas.image = visuals.Image(*args, **kwargs)
    canvas.view.add(canvas.image)  # This sets the parent of the image

    canvas.show()
    canvas.view.camera = cameras.PanZoomCamera(aspect=1)
    plots.append(canvas)
    # todo: (AK) I think this should return an image
    # Also, wtf: this creates an image in a viewbox in a widget in a canvas.
    return canvas


# todo: deal with new camera model once we've got it figured out
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
    canvas.mesh = visuals.Mesh(meshdata=meshdata,
                               vertex_colors=vertex_colors,
                               face_colors=face_colors,
                               color=color, shading='smooth')
    canvas.view.add(canvas.mesh)
    canvas.view.camera = cameras.TurntableCamera(fov=60, 
                                                 azimuth=azimuth,
                                                 elevation=elevation)
    plots.append(canvas)
    return canvas


def scatter(*args, **kwargs):
    ''' Create a new canvas and make a scatter plot.

    Parameters
    ----------
    args : array | two arrays
        Arguments can be passed as (Y,), (X, Y) or (np.array((X, Y))).
    style : str
        The style of symbol to draw (see Notes).
    size : float or array
        The symbol size in px.
    edge_width : float | None
        The width of the symbol outline in pixels.
    edge_width_rel : float | None
        The width as a fraction of marker size. Exactly one of
        `edge_width` and `edge_width_rel` must be supplied.
    edge_color : Color | ColorArray | Colormap
        The color used to draw each symbol outline.
    face_color : Color | ColorArray | Colormap
        The color used to draw each symbol interior.
    scaling : bool
        If set to True, marker scales when rezooming.

    Notes
    -----
    Allowed style strings are: disc, arrow, ring, clobber, square, diamond,
    vbar, hbar, cross, tailed_arrow, x, triangle_up, triangle_down,
    and star.
    '''
    canvas = SceneCanvas(keys='interactive', bgcolor='white')
    canvas.view = canvas.central_widget.add_view()
    _pos = np.zeros((len(args[0]), 2))
    if len(args) == 1:
        pos = np.asarray(args[0])
        if pos.ndim == 1:
            _pos[:, 0] = np.arange(len(args[0]))
            _pos[:, 1] = pos
        else:
            _pos = pos
    elif len(args) == 2:
        _pos[:, 0] = np.asarray(args[0])
        _pos[:, 1] = np.asarray(args[1])
    else:
        raise ValueError('Invalid shape for position data')
    if 'edge_color' in kwargs and isinstance(kwargs['edge_color'], Colormap):
        kwargs['edge_color'] = kwargs['edge_color'].colors
    if 'face_color' in kwargs and isinstance(kwargs['face_color'], Colormap):
        kwargs['face_color'] = kwargs['face_color'].colors
    if not 'face_color' in kwargs:
        kwargs['face_color'] = 'black'
    canvas.scatter = visuals.Markers()
    kwargs['pos'] = _pos
    canvas.scatter.set_data(**kwargs)
    canvas.view.add(canvas.scatter)
    canvas.view.camera = 'panzoom'
    canvas.show()
    plots.append(canvas)
    return canvas
