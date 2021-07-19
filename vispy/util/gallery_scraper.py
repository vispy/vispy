# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Scraper for sphinx-gallery.

This is used to collect screenshots from the examples when executed via
sphinx-gallery. This can be included in any project wanting to take
advantage of this by adding the following to your sphinx ``conf.py``:

.. code-block:: python

    sphinx_gallery_conf = {
        ...
        'image_scrapers': ('vispy',)
    }

The scraper is provided to sphinx-gallery via the
``vispy._get_sg_image_scraper()`` function.

"""

from __future__ import annotations

import os
import time
from sphinx_gallery.scrapers import optipng, figure_rst
from vispy.io import imsave


def _get_sg_image_scraper():
    return VisPyGalleryScraper()


class VisPyGalleryScraper:
    """Custom sphinx-gallery scraper to save the current Canvas to an image."""

    def __repr__(self):
        return self.__class__.__name__

    def __call__(self, block, block_vars, gallery_conf):
        """Scrape VisPy Canvases and applications.

        Parameters
        ----------
        block : tuple
            A tuple containing the (label, content, line_number) of the block.
        block_vars : dict
            Dict of block variables.
        gallery_conf : dict
            Contains the configuration of Sphinx-Gallery

        Returns
        -------
        rst : str
            The ReSTructuredText that will be rendered to HTML containing
            the images. This is often produced by
            :func:`sphinx_gallery.scrapers.figure_rst`.

        """
        example_fn = block_vars["src_file"]
        frame_num_list = self._get_frame_list_from_source(example_fn)
        image_path_iterator = block_vars['image_path_iterator']
        canvas_or_widget = self._get_canvaslike_from_globals(block_vars["example_globals"])

        image_path = next(image_path_iterator)
        frame_grabber = FrameGrabber(canvas_or_widget, frame_num_list)
        frame_grabber.collect_frames()
        if len(frame_num_list) > 1:
            # let's make an animation
            # FUTURE: mp4 with imageio?
            image_path = os.path.splitext(image_path)[0] + ".gif"
            frame_grabber.save_animation(image_path)
        else:
            frame_grabber.save_frame(image_path)
        if 'images' in gallery_conf['compress_images']:
            optipng(image_path, gallery_conf['compress_images_args'])
        fig_titles = ""  # alt text
        # FUTURE: Handle non-images (ex. MP4s) with raw HTML
        return figure_rst([image_path], gallery_conf['src_dir'], fig_titles)

    @staticmethod
    def _get_frame_list_from_source(filename):
        lines = open(filename, 'rb').read().decode('utf-8').splitlines()
        for line in lines[:10]:
            if line.startswith('# vispy:') and 'gallery' in line:
                # Get what frames to grab
                _frames = line.split('gallery')[1].split(',')[0].strip()
                _frames = _frames or '0'
                frames = [int(i) for i in _frames.split(':')]
                if not frames:
                    frames = [5]
                if len(frames) > 1:
                    frames = list(range(*frames))
                break
        else:
            # no frame number hint
            frames = [5]
        return frames

    def _get_canvaslike_from_globals(self, globals_dict):
        qt_widget = self._get_qt_top_parent(globals_dict)
        if qt_widget is not None:
            return qt_widget

        # Get canvas
        if "canvas" in globals_dict:
            return globals_dict["canvas"]
        if "Canvas" in globals_dict:
            return globals_dict["Canvas"]()
        if "fig" in globals_dict:
            return globals_dict["fig"]
        return None

    @staticmethod
    def _get_qt_top_parent(globals_dict):
        if "QWidget" not in globals_dict and "QMainWindow" not in globals_dict:
            return None

        qmainwindow = globals_dict.get("QMainWindow")
        qwidget = globals_dict.get("QWidget", qmainwindow)
        all_qt_widgets = [widget for widget in globals_dict.values()
                          if isinstance(widget, qwidget) and widget is not None]
        all_qt_mains = [widget for widget in all_qt_widgets if isinstance(widget, qmainwindow)]
        if all_qt_mains:
            return all_qt_mains[0]
        if all_qt_widgets:
            return all_qt_widgets[0]
        return None


class FrameGrabber:
    """Helper to grab a series of screenshots from the current Canvas-like object."""

    def __init__(self, canvas_obj, frame_grab_list: list[int]):
        self._canvas = canvas_obj
        self._done = False
        self._current_frame = -1
        self._collected_images = []
        self._frames_to_grab = frame_grab_list[:]  # copy so original list is preserved

    def on_draw(self, _):
        if self._done:
            return  # Grab only once
        self._current_frame += 1
        if self._current_frame in self._frames_to_grab:
            self._frames_to_grab.remove(self._current_frame)
            im = self._canvas.render(alpha=True)
            self._collected_images.append(im)
        if not self._frames_to_grab:
            self._done = True

    def collect_frames(self):
        """Show current Canvas and render and collect all frames requested."""
        if self._is_qt_widget():
            self._grab_qt_screenshot()
        else:
            self._grab_vispy_screenshots()

    def _is_qt_widget(self):
        try:
            from PyQt5.QtWidgets import QWidget
        except ImportError:
            return False
        return isinstance(self._canvas, QWidget)

    def _grab_qt_screenshot(self):
        from PyQt5.QtWidgets import QApplication
        self._canvas.show()
        # Qt is going to grab from the screen so we need the window on top
        self._canvas.raise_()
        # We need to give the GUI event loop and OS time to draw everything
        QApplication.processEvents()
        time.sleep(1.5)
        QApplication.processEvents()
        screen = QApplication.screenAt(self._canvas.pos())
        screenshot = screen.grabWindow(int(self._canvas.windowHandle().winId()))
        arr = self._qpixmap_to_ndarray(screenshot)
        self._collected_images.append(arr)

    @staticmethod
    def _qpixmap_to_ndarray(pixmap):
        import numpy as np
        im = pixmap.toImage()
        size = pixmap.size()
        width = size.width()
        height = size.height()
        im_bits = im.bits()
        im_bits.setsize(height * width * 4)  # RGBA
        return np.frombuffer(im_bits, np.uint8).reshape((height, width, 4))

    def _grab_vispy_screenshots(self):
        os.environ['VISPY_IGNORE_OLD_VERSION'] = 'true'
        self._canvas.events.draw.connect(self.on_draw)
        with self._canvas as c:
            self._collect_frames(c)

    def _collect_frames(self, canvas, limit=10000):
        n = 0
        while not self._done and n < limit:
            canvas.update()
            canvas.app.process_events()
            n += 1
        if n >= limit or len(self._frames_to_grab) > 0:
            raise RuntimeError("Could not collect any images")

    def save_frame(self, filename, frame_index=0):
        imsave(filename, self._collected_images[frame_index])

    def save_animation(self, filename):
        import imageio  # multiple gif not properly supported yet
        imageio.mimsave(filename, self._collected_images)


