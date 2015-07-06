# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import os
from os import path as op
import warnings


from ctypes import (cast, byref, sizeof, create_unicode_buffer,
                    c_void_p, c_wchar_p)
from ...ext.gdi32plus import (gdiplus, gdi32, user32, winreg, LOGFONT,
                              OUTLINETEXTMETRIC, GM_ADVANCED, FW_NORMAL,
                              FW_BOLD, LF_FACESIZE, DEFAULT_CHARSET,
                              TRUETYPE_FONTTYPE, FONTENUMPROC, BOOL)


# Inspired by:
# http://forums.codeguru.com/showthread.php?90792-How-to-get-a-system-
# font-file-name-given-a-LOGFONT-face-name

# XXX This isn't perfect, but it should work for now...

def find_font(face, bold, italic, orig_face=None):
    style_dict = {'Regular': 0, 'Bold': 1, 'Italic': 2, 'Bold Italic': 3}

    # Figure out which font to actually use by trying to instantiate by name
    dc = user32.GetDC(0)  # noqa, analysis:ignore
    gdi32.SetGraphicsMode(dc, GM_ADVANCED)  # only TT and OT fonts
    logfont = LOGFONT()
    logfont.lfHeight = -12  # conv point to pixels
    logfont.lfWeight = FW_BOLD if bold else FW_NORMAL
    logfont.lfItalic = italic
    logfont.lfFaceName = face  # logfont needs Unicode
    hfont = gdi32.CreateFontIndirectW(byref(logfont))
    original = gdi32.SelectObject(dc, hfont)
    n_byte = gdi32.GetOutlineTextMetricsW(dc, 0, None)
    assert n_byte > 0
    metrics = OUTLINETEXTMETRIC()
    assert sizeof(metrics) >= n_byte
    assert gdi32.GetOutlineTextMetricsW(dc, n_byte, byref(metrics))
    gdi32.SelectObject(dc, original)
    user32.ReleaseDC(None, dc)
    use_face = cast(byref(metrics, metrics.otmpFamilyName), c_wchar_p).value
    if use_face != face:
        warnings.warn('Could not find face match "%s", falling back to "%s"'
                      % (orig_face or face, use_face))
    use_style = cast(byref(metrics, metrics.otmpStyleName), c_wchar_p).value
    use_style = style_dict.get(use_style, 'Regular')
    # AK: I get "Standaard" for use_style, which is Dutch for standard/regular

    # Now we match by creating private font collections until we find
    # the one that was used
    font_dir = op.join(os.environ['WINDIR'], 'Fonts')
    reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    key = 'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts'
    reg_vals = winreg.OpenKey(reg, key)
    n_values = winreg.QueryInfoKey(reg_vals)[1]
    fname = None
    for vi in range(n_values):
        name, ff = winreg.EnumValue(reg_vals, vi)[:2]
        if name.endswith('(TrueType)'):
            ff = op.join(font_dir, ff) if op.basename(ff) == ff else ff
            assert op.isfile(ff)
            pc = c_void_p()
            assert gdiplus.GdipNewPrivateFontCollection(byref(pc)) == 0
            gdiplus.GdipPrivateAddFontFile(pc, ff)
            family = c_void_p()
            if gdiplus.GdipCreateFontFamilyFromName(use_face, pc,
                                                    byref(family)) == 0:
                val = BOOL()
                assert gdiplus.GdipIsStyleAvailable(family, use_style,
                                                    byref(val)) == 0
                if val.value:
                    buf = create_unicode_buffer(LF_FACESIZE)
                    assert gdiplus.GdipGetFamilyName(family, buf, 0) == 0
                    assert buf.value == use_face
                    fname = ff
                    break
    fname = fname or find_font('', bold, italic, face)  # fall back to default
    return fname


def _list_fonts():
    dc = user32.GetDC(0)
    gdi32.SetGraphicsMode(dc, GM_ADVANCED)  # only TT and OT fonts
    logfont = LOGFONT()
    logfont.lfCharSet = DEFAULT_CHARSET
    logfont.lfFaceName = ''
    logfont.lfPitchandFamily = 0
    fonts = list()

    def enum_fun(lp_logfont, lp_text_metric, font_type, l_param):
        # Only support TTF for now (silly Windows shortcomings)
        if font_type == TRUETYPE_FONTTYPE:
            font = lp_logfont.contents.lfFaceName
            if not font.startswith('@') and font not in fonts:
                fonts.append(font)
        return 1

    gdi32.EnumFontFamiliesExW(dc, byref(logfont), FONTENUMPROC(enum_fun), 0, 0)
    user32.ReleaseDC(None, dc)
    return fonts
