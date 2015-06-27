# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from ..scene import (Image, LinePlot, Volume, Mesh, Histogram,
                     Spectrogram, ViewBox, PanZoomCamera, TurntableCamera)
from ..io import read_mesh
from ..geometry import MeshData

__all__ = ['PlotWidget']


class PlotWidget(ViewBox):
    """Widget to facilitate plotting

    Parameters
    ----------
    *args : arguments
        Arguments passed to the `ViewBox` super class.
    **kwargs : keywoard arguments
        Keyword arguments passed to the `ViewBox` super class.

    Notes
    -----
    This class is typically instantiated implicitly by a `Figure`
    instance, e.g., by doing ``fig[0, 0]``.

    See Also
    --------
    """
    def __init__(self, *args, **kwargs):
        super(PlotWidget, self).__init__(*args, **kwargs)
        self._camera_set = False

    def _set_camera(self, cls, *args, **kwargs):
        if not self._camera_set:
            self._camera_set = True
            self.camera = cls(*args, **kwargs)
            self.camera.set_range(margin=0)

    def histogram(self, data, bins=10, color='w', orientation='h'):
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
        hist = Histogram(data, bins, color, orientation)
        self.add(hist)
        self._set_camera(PanZoomCamera)
        return hist

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

    def mesh(self, vertices=None, faces=None, vertex_colors=None,
             face_colors=None, color=(0.5, 0.5, 1.), fname=None,
             meshdata=None):
        """Show a 3D mesh

        Parameters
        ----------
        vertices : array
            Vertices.
        faces : array | None
            Face definitions.
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

    def plot(self, data, color='k', symbol=None, line_kind='-', width=1.,
             marker_size=10., edge_color='k', face_color='b', edge_width=1.):
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
        line = LinePlot(data, connect='strip', color=color, symbol=symbol,
                        line_kind=line_kind, width=width,
                        marker_size=marker_size, edge_color=edge_color,
                        face_color=face_color, edge_width=edge_width)
        self.add(line)
        self._set_camera(PanZoomCamera)
        return line

    def spectrogram(self, x, n_fft=256, step=None, fs=1., window='hann',
                    color_scale='log', cmap='cubehelix', clim='auto'):
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
        window : str | None
            Window function to use. Can be ``'hann'`` for Hann window, or None
            for no windowing.
        color_scale : {'linear', 'log'}
            Scale to apply to the result of the STFT.
            ``'log'`` will use ``10 * log10(power)``.
        cmap : str
            Colormap name.
        clim : str | tuple
            Colormap limits. Should be ``'auto'`` or a two-element tuple of
            min and max values.

        Returns
        -------
        spec : instance of Spectrogram
            The spectrogram.

        See also
        --------
        Image
        """
        # XXX once we have axes, we should use "fft_freqs", too
        spec = Spectrogram(x, n_fft, step, fs, window,
                           color_scale, cmap, clim)
        self.add(spec)
        self._set_camera(PanZoomCamera)
        return spec

    def volume(self, vol, clim=None, method='mip', threshold=None,
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
        method : {'mip', 'iso', 'translucent', 'additive'}
            The render style to use. See corresponding docs for details.
            Default 'mip'.
        threshold : float
            The threshold to use for the isosurafce render style. By default
            the mean of the given volume is used.
        cmap : str
            The colormap to use.

        Returns
        -------
        volume : instance of Volume
            The volume visualization.

        See also
        --------
        Volume
        """
        volume = Volume(vol, clim, method, threshold, cmap=cmap)
        self.add(volume)
        self._set_camera(TurntableCamera, fov=30.)
        return volume
