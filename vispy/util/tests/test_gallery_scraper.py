# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Test the sphinx-gallery custom scraper."""

import os

from vispy.testing import TestingCanvas, requires_application

import pytest

try:
    from sphinx_gallery.gen_gallery import DEFAULT_GALLERY_CONF
except ImportError:
    pytest.skip("Skipping sphinx-gallery tests", allow_module_level=True)

from ..gallery_scraper import VisPyGalleryScraper


def _create_fake_block_vars(canvas):
    block_vars = {
        "example_globals": {
            "canvas": canvas,
        },
        "src_file": "example.py",
        "image_path_iterator": (f"{x}.png" for x in range(10)),
    }
    return block_vars


def _create_fake_gallery_conf(src_dir):
    gallery_conf = {}
    gallery_conf.update(DEFAULT_GALLERY_CONF)
    gallery_conf.update({
        "compress_images": "images",
        "compress_images_args": [],
        "src_dir": src_dir,
        "gallery_dirs": src_dir,
    })
    return gallery_conf


@requires_application()
@pytest.mark.parametrize("include_gallery_comment", [False, True])
def test_single_frame(include_gallery_comment, tmpdir):
    canvas = TestingCanvas()
    block_vars = _create_fake_block_vars(canvas)
    gallery_conf = _create_fake_gallery_conf(str(tmpdir))
    script = "\n# vispy: gallery 30\n" if include_gallery_comment else ""
    with tmpdir.as_cwd():
        with open("example.py", "w") as example_file:
            example_file.write(script)
        scraper = VisPyGalleryScraper()
        rst = scraper(None, block_vars, gallery_conf)
        if include_gallery_comment:
            assert "0.png" in rst
            assert os.path.isfile("0.png")
        else:
            assert "0.png" not in rst
            assert not os.path.isfile("0.png")
        assert not os.path.isfile("1.png")  # only one file created


@requires_application()
def test_single_animation(tmpdir):
    canvas = TestingCanvas()
    block_vars = _create_fake_block_vars(canvas)
    gallery_conf = _create_fake_gallery_conf(str(tmpdir))
    with tmpdir.as_cwd():
        with open("example.py", "w") as example_file:
            example_file.write("""# vispy: gallery 10:50:5
            """)
        scraper = VisPyGalleryScraper()
        rst = scraper(None, block_vars, gallery_conf)
        assert "0.gif" in rst
        assert os.path.isfile("0.gif")
        assert not os.path.isfile("0.png")  # only gif file created
        assert not os.path.isfile("1.png")  # only one file created


@requires_application()
@pytest.mark.parametrize(
    "exported_files",
    [
        ("example.png",),
        ("example.gif",),
        ("example1.png", "example2.png"),
    ])
def test_single_export(exported_files, tmpdir):
    canvas = TestingCanvas()
    block_vars = _create_fake_block_vars(canvas)
    gallery_conf = _create_fake_gallery_conf(str(tmpdir))
    with tmpdir.as_cwd():
        # create the files that the example should have created
        for fn in exported_files:
            open(fn, "w").close()

        with open("example.py", "w") as example_file:
            example_file.write("""# vispy: gallery-exports {}
            """.format(" ".join(exported_files)))

        scraper = VisPyGalleryScraper()
        rst = scraper(None, block_vars, gallery_conf)
        for idx, fn in enumerate(exported_files):
            # the original file should have been moved
            assert not os.path.isfile(fn)
            # the new name should from the sphinx-gallery iterator
            new_name = str(idx) + os.path.splitext(fn)[1]
            assert os.path.isfile(new_name)
            assert new_name in rst
