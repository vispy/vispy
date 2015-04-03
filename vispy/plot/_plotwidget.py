# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np

from ..scene import (Image, LinePlot, Volume, Mesh,
                     ViewBox, PanZoomCamera, TurntableCamera)
from ..util.fourier import stft
from ..ext.six import string_types
from ..io import read_mesh
from ..geometry import MeshData

__all__ = ['PlotWidget']

# Wish list:
# * bar plot

_quick_method_list = []


def quick(fun):
    """Decorator to auto-populate our plotting method list"""
    _quick_method_list.append(fun.__name__)
    return fun


class PlotWidget(ViewBox):
    """Class to facilitate plotting"""

    def __init__(self, *args, **kwargs):
        super(PlotWidget, self).__init__(*args, **kwargs)
        self._camera_set = False

    def _set_camera(self, cls, *args, **kwargs):
        if not self._camera_set:
            self._camera_set = True
            self.camera = cls(*args, **kwargs)

    @quick
    def histogram(self, data, bins=10, color='w', orientation='horizontal'):
        """Calculate and show a histogram of data

        Parameters
        ----------
        data : array-like
            Data to histogram. Currently only 1D data is supported.
        bins : int | array-like
            Number of bins, or bin edges.
        color : instance of Color
            Color of the histogram.
        orientation : {'h', 'v'}
            Orientation of the histogram.

        Returns
        -------
        hist : instance of Polygon
            The histogram polygon.
        """
        #   4-5
        #   | |
        # 1-2/7-8
        # |/| | |
        # 0-3-6-9
        data = np.asarray(data)
        if data.ndim != 1:
            raise ValueError('Only 1D data currently supported')
        if not isinstance(orientation, string_types) or \
                orientation not in ('h', 'v'):
            raise ValueError('orientation must be "h" or "v", not %s'
                             % (orientation,))
        X, Y = (0, 1) if orientation == 'h' else (1, 0)

        # do the histogramming
        data, bin_edges = np.histogram(data, bins)
        # construct our vertices
        rr = np.zeros((3 * len(bin_edges) - 2, 3), np.float32)
        rr[:, X] = np.repeat(bin_edges, 3)[1:-1]
        rr[1::3, Y] = data
        rr[2::3, Y] = data
        bin_edges.astype(np.float32)
        # and now our tris
        tris = np.zeros((2 * len(bin_edges) - 2, 3), np.uint32)
        offsets = 3 * np.arange(len(bin_edges) - 1,
                                dtype=np.uint32)[:, np.newaxis]
        tri_1 = np.array([0, 2, 1])
        tri_2 = np.array([2, 0, 3])
        tris[::2] = tri_1 + offsets
        tris[1::2] = tri_2 + offsets
        hist = Mesh(rr, tris, color=color)
        self.add(hist)
        self._set_camera(PanZoomCamera)
        return hist

    @quick
    def image(self, data, cmap='cubehelix', clim='auto'):
        """Show an image

        Parameters
        ----------
        data : ndarray
            Should have shape (N, M), (N, M, 3) or (N, M, 4).
        cmap : str
            Colormap name.
        clim : str | tuple
            Colormap limits. Should be ``'auto'`` or a two-element tuple of
            min and max values.

        Returns
        -------
        image : instance of Image
            The image.

        Notes
        -----
        The colormap is only used if the image pixels are scalars.
        """
        image = Image(data, cmap=cmap, clim=clim)
        self.add(image)
        self._set_camera(PanZoomCamera, aspect=1)
        return image

    @quick
    def mesh(self, vertices=None, faces=None, vertex_colors=None,
             face_colors=None, color=(0.5, 0.5, 1.), fname=None,
             meshdata=None, shading='smooth', center=(0., 0., 0.)):
        """Show a 3D mesh

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

        Returns
        -------
        mesh : instance of Mesh
            The mesh.
        """
        if fname is not None:
            if not all(x is None for x in (vertices, faces, meshdata)):
                raise ValueError('vertices, faces, and meshdata must be None '
                                 'if fname is not None')
            vertices, faces = read_mesh(fname)[:2]
        if meshdata is not None:
            if not all(x is None for x in (vertices, faces, fname)):
                raise ValueError('vertices, faces, and fname must be None if '
                                 'fname is not None')
        else:
            meshdata = MeshData(vertices, faces)
        mesh = Mesh(meshdata=meshdata, vertex_colors=vertex_colors,
                    face_colors=face_colors, color=color, shading='smooth')
        self.add(mesh)
        self._set_camera(TurntableCamera, azimuth=0, elevation=0)                
        return mesh

    @quick
    def plot(self, data, **kwargs):
        """Plot a series of data using lines and markers

        Parameters
        ----------
        data : array | two arrays
            Arguments can be passed as ``(Y,)``, ``(X, Y)`` or
            ``np.array((X, Y))``.
        color : instance of Color
            Color of the line.
        symbol : str
            Marker symbol to use.
        line_kind : str
            Kind of line to draw. For now, only solid lines (``'-'``)
            are supported.
        width : float
            Line width.
        marker_size : float
            Marker size. If `size == 0` markers will not be shown.
        edge_color : instance of Color
            Color of the marker edge.
        face_color : instance of Color
            Color of the marker face.
        edge_width : float
            Edge width of the marker.

        Returns
        -------
        line : instance of LinePlot
            The line plot.

        See also
        --------
        marker_types, LinePlot
        """
        line = LinePlot(data, connect='strip', **kwargs)
        self.add(line)
        self._set_camera(PanZoomCamera)
        return line

    @quick
    def spectrogram(self, x, n_fft=256, step=None, fs=1., cmap='cubehelix',
                    clim='auto'):
        """Calculate and show a spectrogram

        Parameters
        ----------
        x : array-like
            1D signal to operate on. ``If len(x) < n_fft``, x will be
            zero-padded to length ``n_fft``.
        n_fft : int
            Number of FFT points. Much faster for powers of two.
        step : int | None
            Step size between calculations. If None, ``n_fft // 2``
            will be used.
        fs : float
            The sample rate of the data.
        cmap : str
            Colormap name.
        clim : str | tuple
            Colormap limits. Should be ``'auto'`` or a two-element tuple of
            min and max values.

        Returns
        -------
        spec : instance of Image
            The spectrogram.

        See also
        --------
        Image
        """
        # XXX once we have axes, we should use the "fft_freqs", too
        data = stft(x, n_fft, step, fs)
        data = 20 * np.log10(np.abs(data))
        image = Image(data, clim=clim, cmap=cmap)
        self.add(image)
        self._set_camera(PanZoomCamera)
        return image

    @quick
    def volume(self, vol, clim=None, style='mip', threshold=None,
               cmap='grays'):
        """Show a 3D volume

        Parameters
        ----------
        vol : ndarray
            Volume to render.
        clim : tuple of two floats | None
            The contrast limits. The values in the volume are mapped to
            black and white corresponding to these values. Default maps
            between min and max.
        style : {'mip', 'iso'}
            The render style to use. See corresponding docs for details.
            Default 'mip'.
        threshold : float
            The threshold to use for the isosurafce render style. By default
            the mean of the given volume is used.

        Returns
        -------
        volume : instance of Volume
            The volume visualization.

        See also
        --------
        Volume
        """
        volume = Volume(vol, clim, style, threshold, cmap=cmap)
        self.add(volume)
        self._set_camera(TurntableCamera, fov=30.)
        return volume
