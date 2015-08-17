# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from ..import scene
from ..io import read_mesh
from ..geometry import MeshData

__all__ = ['PlotWidget']


class PlotWidget(scene.Widget):
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
        self._fg = kwargs.pop('fg_color', 'k')
        self.grid = None
        self.camera = None
        self.title = None
        self.yaxis = None
        self.xaxis = None
        self.xlabel = None
        self.ylabel = None
        self._configured = False

        self.cbar_top = None
        self.cbar_bottom = None
        self.cbar_left = None
        self.cbar_right = None

        self.visuals = []

        super(PlotWidget, self).__init__(*args, **kwargs)
        self.grid = self.add_grid(spacing=0, margin=10)

        self.title = scene.Label("", font_size=16)
        self.title.stretch = (1, 0.1)
        self.grid.add_widget(self.title, row=0, col=3)
        self.view = self.grid.add_view(row=2, col=3, border_color='grey')

    def _configure_2d(self, fg_color=None):
        if self._configured:
            return
        if fg_color is None:
            fg = self._fg
        else:
            fg = fg_color
        self.yaxis = scene.AxisWidget(orientation='left', text_color=fg,
                                      axis_color=fg, tick_color=fg)
        self.yaxis.stretch = (0.1, 1)
        self.grid.add_widget(self.yaxis, row=2, col=2)

        self.ylabel = scene.Label("", rotation=-90)
        self.ylabel.stretch = (0.05, 1)
        self.grid.add_widget(self.ylabel, row=2, col=1)

        self.xaxis = scene.AxisWidget(orientation='bottom', text_color=fg,
                                      axis_color=fg, tick_color=fg)
        self.xaxis.stretch = (1, 0.1)
        self.grid.add_widget(self.xaxis, row=3, col=3)

        self.xlabel = scene.Label("")
        self.xlabel.stretch = (1, 0.05)
        self.grid.add_widget(self.xlabel, row=4, col=3)

        self.view.camera = 'panzoom'
        self.camera = self.view.camera

        self.xaxis.link_view(self.view)
        self.yaxis.link_view(self.view)

        self._configured = True

    def _configure_3d(self):
        if self._configured:
            return
        self.view.camera = 'turntable'
        self.camera = self.view.camera

        self._configured = True

    def histogram(self, data, bins=10, color='blue', orientation='h'):
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
        self._configure_2d()
        hist = scene.Histogram(data, bins, color, orientation)
        self.view.add(hist)
        self.view.camera.set_range()
        return hist

    def image(self, data, cmap='cubehelix', clim='auto', fg_color=None):
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
        fg_color : Color or None
            Sets the plot foreground color if specified.

        Returns
        -------
        image : instance of Image
            The image.

        Notes
        -----
        The colormap is only used if the image pixels are scalars.
        """
        self._configure_2d(fg_color)
        image = scene.Image(data, cmap=cmap, clim=clim)
        self.view.add(image)
        self.view.camera.aspect = 1
        self.view.camera.set_range()

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
        self._configure_3d()
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
        mesh = scene.Mesh(meshdata=meshdata, vertex_colors=vertex_colors,
                          face_colors=face_colors, color=color,
                          shading='smooth')
        self.view.add(mesh)
        self.view.camera.set_range()
        return mesh

    def plot(self, data, color='k', symbol=None, line_kind='-', width=1.,
             marker_size=10., edge_color='k', face_color='b', edge_width=1.,
             title=None, xlabel=None, ylabel=None):
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
        title : str | None
            The title string to be displayed above the plot
        xlabel : str | None
            The label to display along the bottom axis
        ylabel : str | None
            The label to display along the left axis.

        Returns
        -------
        line : instance of LinePlot
            The line plot.

        See also
        --------
        marker_types, LinePlot
        """
        self._configure_2d()
        line = scene.LinePlot(data, connect='strip', color=color,
                              symbol=symbol, line_kind=line_kind,
                              width=width, marker_size=marker_size,
                              edge_color=edge_color,
                              face_color=face_color,
                              edge_width=edge_width)
        self.view.add(line)
        self.view.camera.set_range()
        self.visuals.append(line)

        if title is not None:
            self.title.text = title
        if xlabel is not None:
            self.xlabel.text = xlabel
        if ylabel is not None:
            self.ylabel.text = ylabel

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
        self._configure_2d()
        # XXX once we have axes, we should use "fft_freqs", too
        spec = scene.Spectrogram(x, n_fft, step, fs, window,
                                 color_scale, cmap, clim)
        self.view.add(spec)
        self.view.camera.set_range()
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
        self._configure_3d()
        volume = scene.Volume(vol, clim, method, threshold, cmap=cmap)
        self.view.add(volume)
        self.view.camera.set_range()
        return volume

    def surface(self, zdata, **kwargs):
        """Show a 3D surface plot.

        Extra keyword arguments are passed to `SurfacePlot()`.

        Parameters
        ----------
        zdata : array-like
            A 2D array of the surface Z values.

        """
        self._configure_3d()
        surf = scene.SurfacePlot(z=zdata, **kwargs)
        self.view.add(surf)
        self.view.camera.set_range()
        return surf

    def colorbar(self, cmap, position="right",
                 label="", clim=("", ""),
                 border_width=0.0, border_color="black",
                 **kwargs):
        """Show a ColorBar

        Parameters
        ----------
        cmap : str | vispy.color.ColorMap
            Either the name of the ColorMap to be used from the standard
            set of names (refer to `vispy.color.get_colormap`),
            or a custom ColorMap object.
            The ColorMap is used to apply a gradient on the colorbar.
        position : {'left', 'right', 'top', 'bottom'}
            The position of the colorbar with respect to the plot.
            'top' and 'bottom' are placed horizontally, while
            'left' and 'right' are placed vertically
        label : str
            The label that is to be drawn with the colorbar
            that provides information about the colorbar.
        clim : tuple (min, max)
            the minimum and maximum values of the data that
            is given to the colorbar. This is used to draw the scale
            on the side of the colorbar.
        border_width : float (in px)
            The width of the border the colormap should have. This measurement
            is given in pixels
        border_color : str | vispy.color.Color
            The color of the border of the colormap. This can either be a
            str as the color's name or an actual instace of a vipy.color.Color

        Returns
        -------
        colorbar : instance of ColorBarWidget

        See also
        --------
        ColorBarWidget
        """

        self._configure_2d()

        cbar = scene.ColorBarWidget(orientation=position,
                                    label_str=label,
                                    cmap=cmap,
                                    clim=clim,
                                    border_width=border_width,
                                    border_color=border_color,
                                    **kwargs)

        if cbar.orientation == "bottom":
            self.grid.add_widget(cbar, row=5, col=3)
            cbar.stretch = (1, 0.3)
            self.cbar_bottom = cbar
        elif cbar.orientation == "top":
            self.grid.add_widget(cbar, row=1, col=3)
            cbar.stretch = (1, 0.3)
            self.cbar_top = cbar
        elif cbar.orientation == "left":
            cbar.stretch = (0.3, 1)
            self.grid.add_widget(cbar, row=2, col=0)
            self.cbar_left = cbar
        else:  # cbar.orientation == "right"
            cbar.stretch = (0.3, 1)
            self.grid.add_widget(cbar, row=2, col=4)
            self.cbar_right = cbar

        return cbar
