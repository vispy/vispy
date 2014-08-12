"""
Matplotlib Exporter
===================
This submodule contains tools for crawling a matplotlib figure and exporting
relevant pieces to a renderer.

Copyright (c) 2014, mpld3
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,  # noqa
are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this  # noqa
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.

* Neither the name of the {organization} nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR  # noqa
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
import warnings
import io
from . import mplutils as utils

import matplotlib
from matplotlib import transforms


class Exporter(object):
    """Matplotlib Exporter

    Parameters
    ----------
    renderer : Renderer object
        The renderer object called by the exporter to create a figure
        visualization.  See mplexporter.Renderer for information on the
        methods which should be defined within the renderer.
    close_mpl : bool
        If True (default), close the matplotlib figure as it is rendered. This
        is useful for when the exporter is used within the notebook, or with
        an interactive matplotlib backend.
    """

    def __init__(self, renderer, close_mpl=True):
        self.close_mpl = close_mpl
        self.renderer = renderer

    def run(self, fig):
        """
        Run the exporter on the given figure

        Parmeters
        ---------
        fig : matplotlib.Figure instance
            The figure to export
        """
        # Calling savefig executes the draw() command, putting elements
        # in the correct place.
        fig.savefig(io.BytesIO(), format='png', dpi=fig.dpi)
        if self.close_mpl:
            import matplotlib.pyplot as plt
            plt.close(fig)
        self.crawl_fig(fig)

    @staticmethod
    def process_transform(transform, ax=None, data=None, return_trans=False,
                          force_trans=None):
        """Process the transform and convert data to figure or data coordinates

        Parameters
        ----------
        transform : matplotlib Transform object
            The transform applied to the data
        ax : matplotlib Axes object (optional)
            The axes the data is associated with
        data : ndarray (optional)
            The array of data to be transformed.
        return_trans : bool (optional)
            If true, return the final transform of the data
        force_trans : matplotlib.transform instance (optional)
            If supplied, first force the data to this transform

        Returns
        -------
        code : string
            Code is either "data", "axes", "figure", or "display", indicating
            the type of coordinates output.
        transform : matplotlib transform
            the transform used to map input data to output data.
            Returned only if return_trans is True
        new_data : ndarray
            Data transformed to match the given coordinate code.
            Returned only if data is specified
        """
        if isinstance(transform, transforms.BlendedGenericTransform):
            warnings.warn("Blended transforms not yet supported. "
                          "Zoom behavior may not work as expected.")

        if force_trans is not None:
            if data is not None:
                data = (transform - force_trans).transform(data)
            transform = force_trans

        code = "display"
        if ax is not None:
            for (c, trans) in [("data", ax.transData),
                               ("axes", ax.transAxes),
                               ("figure", ax.figure.transFigure),
                               ("display", transforms.IdentityTransform())]:
                if transform.contains_branch(trans):
                    code, transform = (c, transform - trans)
                    break

        if data is not None:
            if return_trans:
                return code, transform.transform(data), transform
            else:
                return code, transform.transform(data)
        else:
            if return_trans:
                return code, transform
            else:
                return code

    def crawl_fig(self, fig):
        """Crawl the figure and process all axes"""
        with self.renderer.draw_figure(fig=fig,
                                       props=utils.get_figure_properties(fig)):
            for ax in fig.axes:
                self.crawl_ax(ax)

    def crawl_ax(self, ax):
        """Crawl the axes and process all elements within"""
        with self.renderer.draw_axes(ax=ax,
                                     props=utils.get_axes_properties(ax)):
            for line in ax.lines:
                self.draw_line(ax, line)
            for text in ax.texts:
                self.draw_text(ax, text)
            for (text, ttp) in zip([ax.xaxis.label, ax.yaxis.label, ax.title],
                                   ["xlabel", "ylabel", "title"]):
                if(hasattr(text, 'get_text') and text.get_text()):
                    self.draw_text(ax, text, force_trans=ax.transAxes,
                                   text_type=ttp)
            for artist in ax.artists:
                # TODO: process other artists
                if isinstance(artist, matplotlib.text.Text):
                    self.draw_text(ax, artist)
            for patch in ax.patches:
                self.draw_patch(ax, patch)
            for collection in ax.collections:
                self.draw_collection(ax, collection)
            for image in ax.images:
                self.draw_image(ax, image)

            legend = ax.get_legend()
            if legend is not None:
                props = utils.get_legend_properties(ax, legend)
                with self.renderer.draw_legend(legend=legend, props=props):
                    if props['visible']:
                        self.crawl_legend(ax, legend)

    def crawl_legend(self, ax, legend):
        """
        Recursively look through objects in legend children
        """
        legendElements = list(utils.iter_all_children(legend._legend_box,
                                                      skipContainers=True))
        legendElements.append(legend.legendPatch)
        for child in legendElements:
            # force a large zorder so it appears on top
            child.set_zorder(1E6 + child.get_zorder())

            try:
                # What kind of object...
                if isinstance(child, matplotlib.patches.Patch):
                    self.draw_patch(ax, child, force_trans=ax.transAxes)
                elif isinstance(child, matplotlib.text.Text):
                    if not (child is legend.get_children()[-1]
                            and child.get_text() == 'None'):
                        self.draw_text(ax, child, force_trans=ax.transAxes)
                elif isinstance(child, matplotlib.lines.Line2D):
                    self.draw_line(ax, child, force_trans=ax.transAxes)
                elif isinstance(child, matplotlib.collections.Collection):
                    self.draw_collection(ax, child,
                                         force_pathtrans=ax.transAxes)
                else:
                    warnings.warn("Legend element %s not impemented" % child)
            except NotImplementedError:
                warnings.warn("Legend element %s not impemented" % child)

    def draw_line(self, ax, line, force_trans=None):
        """Process a matplotlib line and call renderer.draw_line"""
        coordinates, data = self.process_transform(line.get_transform(),
                                                   ax, line.get_xydata(),
                                                   force_trans=force_trans)
        linestyle = utils.get_line_style(line)
        if linestyle['dasharray'] is None:
            linestyle = None
        markerstyle = utils.get_marker_style(line)
        if (markerstyle['marker'] in ['None', 'none', None]
                or markerstyle['markerpath'][0].size == 0):
            markerstyle = None
        label = line.get_label()
        if markerstyle or linestyle:
            self.renderer.draw_marked_line(data=data, coordinates=coordinates,
                                           linestyle=linestyle,
                                           markerstyle=markerstyle,
                                           label=label,
                                           mplobj=line)

    def draw_text(self, ax, text, force_trans=None, text_type=None):
        """Process a matplotlib text object and call renderer.draw_text"""
        content = text.get_text()
        if content:
            transform = text.get_transform()
            position = text.get_position()
            coords, position = self.process_transform(transform, ax,
                                                      position,
                                                      force_trans=force_trans)
            style = utils.get_text_style(text)
            self.renderer.draw_text(text=content, position=position,
                                    coordinates=coords,
                                    text_type=text_type,
                                    style=style, mplobj=text)

    def draw_patch(self, ax, patch, force_trans=None):
        """Process a matplotlib patch object and call renderer.draw_path"""
        vertices, pathcodes = utils.SVG_path(patch.get_path())
        transform = patch.get_transform()
        coordinates, vertices = self.process_transform(transform,
                                                       ax, vertices,
                                                       force_trans=force_trans)
        linestyle = utils.get_path_style(patch, fill=patch.get_fill())
        self.renderer.draw_path(data=vertices,
                                coordinates=coordinates,
                                pathcodes=pathcodes,
                                style=linestyle,
                                mplobj=patch)

    def draw_collection(self, ax, collection,
                        force_pathtrans=None,
                        force_offsettrans=None):
        """Process a matplotlib collection and call renderer.draw_collection"""
        (transform, transOffset,
         offsets, paths) = collection._prepare_points()

        offset_coords, offsets = self.process_transform(
            transOffset, ax, offsets, force_trans=force_offsettrans)
        path_coords = self.process_transform(
            transform, ax, force_trans=force_pathtrans)

        processed_paths = [utils.SVG_path(path) for path in paths]
        processed_paths = [(self.process_transform(
            transform, ax, path[0], force_trans=force_pathtrans)[1], path[1])
            for path in processed_paths]

        path_transforms = collection.get_transforms()
        try:
            # matplotlib 1.3: path_transforms are transform objects.
            # Convert them to numpy arrays.
            path_transforms = [t.get_matrix() for t in path_transforms]
        except AttributeError:
            # matplotlib 1.4: path transforms are already numpy arrays.
            pass

        styles = {'linewidth': collection.get_linewidths(),
                  'facecolor': collection.get_facecolors(),
                  'edgecolor': collection.get_edgecolors(),
                  'alpha': collection._alpha,
                  'zorder': collection.get_zorder()}

        offset_dict = {"data": "before",
                       "screen": "after"}
        offset_order = offset_dict[collection.get_offset_position()]

        self.renderer.draw_path_collection(paths=processed_paths,
                                           path_coordinates=path_coords,
                                           path_transforms=path_transforms,
                                           offsets=offsets,
                                           offset_coordinates=offset_coords,
                                           offset_order=offset_order,
                                           styles=styles,
                                           mplobj=collection)

    def draw_image(self, ax, image):
        """Process a matplotlib image object and call renderer.draw_image"""
        self.renderer.draw_image(imdata=utils.image_to_base64(image),
                                 extent=image.get_extent(),
                                 coordinates="data",
                                 style={"alpha": image.get_alpha(),
                                        "zorder": image.get_zorder()},
                                 mplobj=image)


##############################################################################
# Renderers/base.py

import itertools
from contextlib import contextmanager

import numpy as np

from . import _mpl_py3k_compat as py3k


class Renderer(object):
    @staticmethod
    def ax_zoomable(ax):
        return bool(ax and ax.get_navigate())

    @staticmethod
    def ax_has_xgrid(ax):
        return bool(ax and ax.xaxis._gridOnMajor and ax.yaxis.get_gridlines())

    @staticmethod
    def ax_has_ygrid(ax):
        return bool(ax and ax.yaxis._gridOnMajor and ax.yaxis.get_gridlines())

    @property
    def current_ax_zoomable(self):
        return self.ax_zoomable(self._current_ax)

    @property
    def current_ax_has_xgrid(self):
        return self.ax_has_xgrid(self._current_ax)

    @property
    def current_ax_has_ygrid(self):
        return self.ax_has_ygrid(self._current_ax)

    @contextmanager
    def draw_figure(self, fig, props):
        if hasattr(self, "_current_fig") and self._current_fig is not None:
            warnings.warn("figure embedded in figure: something is wrong")
        self._current_fig = fig
        self._fig_props = props
        self.open_figure(fig=fig, props=props)
        yield
        self.close_figure(fig=fig)
        self._current_fig = None
        self._fig_props = {}

    @contextmanager
    def draw_axes(self, ax, props):
        if hasattr(self, "_current_ax") and self._current_ax is not None:
            warnings.warn("axes embedded in axes: something is wrong")
        self._current_ax = ax
        self._ax_props = props
        self.open_axes(ax=ax, props=props)
        yield
        self.close_axes(ax=ax)
        self._current_ax = None
        self._ax_props = {}

    @contextmanager
    def draw_legend(self, legend, props):
        self._current_legend = legend
        self._legend_props = props
        self.open_legend(legend=legend, props=props)
        yield
        self.close_legend(legend=legend)
        self._current_legend = None
        self._legend_props = {}

    # Following are the functions which should be overloaded in subclasses

    def open_figure(self, fig, props):
        """
        Begin commands for a particular figure.

        Parameters
        ----------
        fig : matplotlib.Figure
            The Figure which will contain the ensuing axes and elements
        props : dictionary
            The dictionary of figure properties
        """
        pass

    def close_figure(self, fig):
        """
        Finish commands for a particular figure.

        Parameters
        ----------
        fig : matplotlib.Figure
            The figure which is finished being drawn.
        """
        pass

    def open_axes(self, ax, props):
        """
        Begin commands for a particular axes.

        Parameters
        ----------
        ax : matplotlib.Axes
            The Axes which will contain the ensuing axes and elements
        props : dictionary
            The dictionary of axes properties
        """
        pass

    def close_axes(self, ax):
        """
        Finish commands for a particular axes.

        Parameters
        ----------
        ax : matplotlib.Axes
            The Axes which is finished being drawn.
        """
        pass

    def open_legend(self, legend, props):
        """
        Beging commands for a particular legend.

        Parameters
        ----------
        legend : matplotlib.legend.Legend
                The Legend that will contain the ensuing elements
        props : dictionary
                The dictionary of legend properties
        """
        pass

    def close_legend(self, legend):
        """
        Finish commands for a particular legend.

        Parameters
        ----------
        legend : matplotlib.legend.Legend
                The Legend which is finished being drawn
        """
        pass

    def draw_marked_line(self, data, coordinates, linestyle, markerstyle,
                         label, mplobj=None):
        """Draw a line that also has markers.

        If this isn't reimplemented by a renderer object, by default, it will
        make a call to BOTH draw_line and draw_markers when both markerstyle
        and linestyle are not None in the same Line2D object.

        """
        if linestyle is not None:
            self.draw_line(data, coordinates, linestyle, label, mplobj)
        if markerstyle is not None:
            self.draw_markers(data, coordinates, markerstyle, label, mplobj)

    def draw_line(self, data, coordinates, style, label, mplobj=None):
        """
        Draw a line. By default, draw the line via the draw_path() command.
        Some renderers might wish to override this and provide more
        fine-grained behavior.

        In matplotlib, lines are generally created via the plt.plot() command,
        though this command also can create marker collections.

        Parameters
        ----------
        data : array_like
            A shape (N, 2) array of datapoints.
        coordinates : string
            A string code, which should be either 'data' for data coordinates,
            or 'figure' for figure (pixel) coordinates.
        style : dictionary
            a dictionary specifying the appearance of the line.
        mplobj : matplotlib object
            the matplotlib plot element which generated this line
        """
        pathcodes = ['M'] + (data.shape[0] - 1) * ['L']
        pathstyle = dict(facecolor='none', **style)
        pathstyle['edgecolor'] = pathstyle.pop('color')
        pathstyle['edgewidth'] = pathstyle.pop('linewidth')
        self.draw_path(data=data, coordinates=coordinates,
                       pathcodes=pathcodes, style=pathstyle, mplobj=mplobj)

    @staticmethod
    def _iter_path_collection(paths, path_transforms, offsets, styles):
        """Build an iterator over the elements of the path collection"""
        N = max(len(paths), len(offsets))

        if not path_transforms:
            path_transforms = [np.eye(3)]

        edgecolor = styles['edgecolor']
        if np.size(edgecolor) == 0:
            edgecolor = ['none']
        facecolor = styles['facecolor']
        if np.size(facecolor) == 0:
            facecolor = ['none']

        elements = [paths, path_transforms, offsets,
                    edgecolor, styles['linewidth'], facecolor]

        it = itertools
        return it.islice(py3k.zip(*py3k.map(it.cycle, elements)), N)

    def draw_path_collection(self, paths, path_coordinates, path_transforms,
                             offsets, offset_coordinates, offset_order,
                             styles, mplobj=None):
        """
        Draw a collection of paths. The paths, offsets, and styles are all
        iterables, and the number of paths is max(len(paths), len(offsets)).

        By default, this is implemented via multiple calls to the draw_path()
        function. For efficiency, Renderers may choose to customize this
        implementation.

        Examples of path collections created by matplotlib are scatter plots,
        histograms, contour plots, and many others.

        Parameters
        ----------
        paths : list
            list of tuples, where each tuple has two elements:
            (data, pathcodes).  See draw_path() for a description of these.
        path_coordinates: string
            the coordinates code for the paths, which should be either
            'data' for data coordinates, or 'figure' for figure (pixel)
            coordinates.
        path_transforms: array_like
            an array of shape (*, 3, 3), giving a series of 2D Affine
            transforms for the paths. These encode translations, rotations,
            and scalings in the standard way.
        offsets: array_like
            An array of offsets of shape (N, 2)
        offset_coordinates : string
            the coordinates code for the offsets, which should be either
            'data' for data coordinates, or 'figure' for figure (pixel)
            coordinates.
        offset_order : string
            either "before" or "after". This specifies whether the offset
            is applied before the path transform, or after.  The matplotlib
            backend equivalent is "before"->"data", "after"->"screen".
        styles: dictionary
            A dictionary in which each value is a list of length N, containing
            the style(s) for the paths.
        mplobj : matplotlib object
            the matplotlib plot element which generated this collection
        """
        if offset_order == "before":
            raise NotImplementedError("offset before transform")

        for tup in self._iter_path_collection(paths, path_transforms,
                                              offsets, styles):
            (path, path_transform, offset, ec, lw, fc) = tup
            vertices, pathcodes = path
            path_transform = transforms.Affine2D(path_transform)
            vertices = path_transform.transform(vertices)
            # This is a hack:
            if path_coordinates == "figure":
                path_coordinates = "points"
            style = {"edgecolor": utils.color_to_hex(ec),
                     "facecolor": utils.color_to_hex(fc),
                     "edgewidth": lw,
                     "dasharray": "10,0",
                     "alpha": styles['alpha'],
                     "zorder": styles['zorder']}
            self.draw_path(data=vertices, coordinates=path_coordinates,
                           pathcodes=pathcodes, style=style, offset=offset,
                           offset_coordinates=offset_coordinates,
                           mplobj=mplobj)

    def draw_markers(self, data, coordinates, style, label, mplobj=None):
        """
        Draw a set of markers. By default, this is done by repeatedly
        calling draw_path(), but renderers should generally overload
        this method to provide a more efficient implementation.

        In matplotlib, markers are created using the plt.plot() command.

        Parameters
        ----------
        data : array_like
            A shape (N, 2) array of datapoints.
        coordinates : string
            A string code, which should be either 'data' for data coordinates,
            or 'figure' for figure (pixel) coordinates.
        style : dictionary
            a dictionary specifying the appearance of the markers.
        mplobj : matplotlib object
            the matplotlib plot element which generated this marker collection
        """
        vertices, pathcodes = style['markerpath']
        pathstyle = dict((key, style[key]) for key in ['alpha', 'edgecolor',
                                                       'facecolor', 'zorder',
                                                       'edgewidth'])
        pathstyle['dasharray'] = "10,0"
        for vertex in data:
            self.draw_path(data=vertices, coordinates="points",
                           pathcodes=pathcodes, style=pathstyle,
                           offset=vertex, offset_coordinates=coordinates,
                           mplobj=mplobj)

    def draw_text(self, text, position, coordinates, style,
                  text_type=None, mplobj=None):
        """
        Draw text on the image.

        Parameters
        ----------
        text : string
            The text to draw
        position : tuple
            The (x, y) position of the text
        coordinates : string
            A string code, which should be either 'data' for data coordinates,
            or 'figure' for figure (pixel) coordinates.
        style : dictionary
            a dictionary specifying the appearance of the text.
        text_type : string or None
            if specified, a type of text such as "xlabel", "ylabel", "title"
        mplobj : matplotlib object
            the matplotlib plot element which generated this text
        """
        raise NotImplementedError()

    def draw_path(self, data, coordinates, pathcodes, style,
                  offset=None, offset_coordinates="data", mplobj=None):
        """
        Draw a path.

        In matplotlib, paths are created by filled regions, histograms,
        contour plots, patches, etc.

        Parameters
        ----------
        data : array_like
            A shape (N, 2) array of datapoints.
        coordinates : string
            A string code, which should be either 'data' for data coordinates,
            'figure' for figure (pixel) coordinates, or "points" for raw
            point coordinates (useful in conjunction with offsets, below).
        pathcodes : list
            A list of single-character SVG pathcodes associated with the data.
            Path codes are one of ['M', 'm', 'L', 'l', 'Q', 'q', 'T', 't',
                                   'S', 's', 'C', 'c', 'Z', 'z']
            See the SVG specification for details.  Note that some path codes
            consume more than one datapoint (while 'Z' consumes none), so
            in general, the length of the pathcodes list will not be the same
            as that of the data array.
        style : dictionary
            a dictionary specifying the appearance of the line.
        offset : list (optional)
            the (x, y) offset of the path. If not given, no offset will
            be used.
        offset_coordinates : string (optional)
            A string code, which should be either 'data' for data coordinates,
            or 'figure' for figure (pixel) coordinates.
        mplobj : matplotlib object
            the matplotlib plot element which generated this path
        """
        raise NotImplementedError()

    def draw_image(self, imdata, extent, coordinates, style, mplobj=None):
        """
        Draw an image.

        Parameters
        ----------
        imdata : string
            base64 encoded png representation of the image
        extent : list
            the axes extent of the image: [xmin, xmax, ymin, ymax]
        coordinates: string
            A string code, which should be either 'data' for data coordinates,
            or 'figure' for figure (pixel) coordinates.
        style : dictionary
            a dictionary specifying the appearance of the image
        mplobj : matplotlib object
            the matplotlib plot object which generated this image
        """
        raise NotImplementedError()
