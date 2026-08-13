# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from pathlib import Path

# List the vispy fonts made available online
_vispy_fonts = {'OpenSans'}
_vispy_font_dirs = {Path(__file__).parent / 'data'}


def _get_vispy_font_filename(face, bold, italic):
    """Fetch a remote vispy font"""
    name = face + '-'
    name += 'Regular' if not bold and not italic else ''
    name += 'Bold' if bold else ''
    name += 'Italic' if italic else ''
    for font_dir in _vispy_font_dirs:
        if (fontfile := font_dir / f'{name}.ttf').exists():
            return str(fontfile)
    raise ValueError(f'Font "{name}" is not available. Did you forget to register it?')


def register_vispy_font(path, face, bold, italic):
    _vispy_fonts.add(face)
    _vispy_font_dirs.add(Path(path))
