# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

# Adapted from Pyglet

import atexit
from functools import partial
import struct

from ctypes import (windll, Structure, POINTER, byref, WINFUNCTYPE,
                    c_uint, c_float, c_int, c_ulong, c_uint64,
                    c_void_p, c_uint32, c_wchar, c_wchar_p)
from ctypes.wintypes import (LONG, BYTE, HFONT, HGDIOBJ, BOOL, UINT, INT,
                             DWORD, LPARAM)

try:
    import _winreg as winreg
except ImportError:
    import winreg  # noqa, analysis:ignore

_64_bit = (8 * struct.calcsize("P")) == 64

LF_FACESIZE = 32
FW_BOLD = 700
FW_NORMAL = 400
ANTIALIASED_QUALITY = 4
FontStyleBold = 1
FontStyleItalic = 2
UnitPixel = 2
UnitPoint = 3
DEFAULT_CHARSET = 1
ANSI_CHARSET = 0
TRUETYPE_FONTTYPE = 4
GM_ADVANCED = 2
CSIDL_FONTS = 0x0014

PixelFormat24bppRGB = 137224
PixelFormat32bppRGB = 139273
PixelFormat32bppARGB = 2498570

DriverStringOptionsCmapLookup = 1
DriverStringOptionsRealizedAdvance = 4
TextRenderingHintAntiAlias = 4
TextRenderingHintAntiAliasGridFit = 3
ImageLockModeRead = 1
StringFormatFlagsMeasureTrailingSpaces = 0x00000800
StringFormatFlagsNoClip = 0x00004000
StringFormatFlagsNoFitBlackBox = 0x00000004

INT_PTR = c_int
REAL = c_float
TCHAR = c_wchar
UINT32 = c_uint32
HDC = c_void_p
PSTR = c_uint64 if _64_bit else c_uint

HORZSIZE = 4
VERTSIZE = 6

HORZRES = 8
VERTRES = 10


# gdi32

class POINT(Structure):
    _fields_ = [('x', LONG), ('y', LONG)]


class RECT(Structure):
    _fields_ = [('left', LONG), ('top', LONG),
                ('right', LONG), ('bottom', LONG)]


class PANOSE(Structure):
    _fields_ = [
        ('bFamilyType', BYTE), ('bSerifStyle', BYTE), ('bWeight', BYTE),
        ('bProportion', BYTE), ('bContrast', BYTE), ('bStrokeVariation', BYTE),
        ('bArmStyle', BYTE), ('bLetterform', BYTE), ('bMidline', BYTE),
        ('bXHeight', BYTE)]


class TEXTMETRIC(Structure):
    _fields_ = [
        ('tmHeight', LONG), ('tmAscent', LONG), ('tmDescent', LONG),
        ('tmInternalLeading', LONG), ('tmExternalLeading', LONG),
        ('tmAveCharWidth', LONG), ('tmMaxCharWidth', LONG),
        ('tmWeight', LONG), ('tmOverhang', LONG),
        ('tmDigitizedAspectX', LONG), ('tmDigitizedAspectY', LONG),
        ('tmFirstChar', TCHAR), ('tmLastChar', TCHAR),
        ('tmDefaultChar', TCHAR), ('tmBreakChar', TCHAR),
        ('tmItalic', BYTE), ('tmUnderlined', BYTE),
        ('tmStruckOut', BYTE), ('tmPitchAndFamily', BYTE),
        ('tmCharSet', BYTE)]


class OUTLINETEXTMETRIC(Structure):
    _fields_ = [
        ('otmSize', UINT), ('otmTextMetrics', TEXTMETRIC),
        ('otmMysteryBytes', BYTE), ('otmPanoseNumber', PANOSE),
        ('otmMysteryByte', BYTE),
        ('otmfsSelection', UINT), ('otmfsType', UINT),
        ('otmsCharSlopeRise', INT), ('otmsCharSlopeRun', INT),
        ('otmItalicAngle', INT), ('otmEMSquare', UINT), ('otmAscent', INT),
        ('otmDescent', INT), ('otmLineGap', UINT), ('otmsCapEmHeight', UINT),
        ('otmsXHeight', UINT), ('otmrcFontBox', RECT), ('otmMacAscent', INT),
        ('otmMacDescent', INT), ('otmMacLineGap', UINT),
        ('otmusMinimumPPEM', UINT), ('otmptSubscriptSize', POINT),
        ('otmptSubscriptOffset', POINT), ('otmptSuperscriptSize', POINT),
        ('otmptSuperscriptOffset', POINT), ('otmsStrikeoutSize', UINT),
        ('otmsStrikeoutPosition', INT), ('otmsUnderscoreSize', INT),
        ('otmsUnderscorePosition', INT), ('otmpFamilyName', PSTR),
        ('otmpFaceName', PSTR), ('otmpStyleName', PSTR),
        ('otmpFullName', PSTR), ('junk', (BYTE) * 1024)]  # room for strs


class LOGFONT(Structure):
    _fields_ = [
        ('lfHeight', LONG), ('lfWidth', LONG), ('lfEscapement', LONG),
        ('lfOrientation', LONG), ('lfWeight', LONG), ('lfItalic', BYTE),
        ('lfUnderline', BYTE), ('lfStrikeOut', BYTE), ('lfCharSet', BYTE),
        ('lfOutPrecision', BYTE), ('lfClipPrecision', BYTE),
        ('lfQuality', BYTE), ('lfPitchAndFamily', BYTE),
        ('lfFaceName', (TCHAR * LF_FACESIZE))]


gdi32 = windll.gdi32

gdi32.CreateFontIndirectW.restype = HFONT
gdi32.CreateFontIndirectW.argtypes = [POINTER(LOGFONT)]

gdi32.SelectObject.restype = HGDIOBJ
gdi32.SelectObject.argtypes = [HDC, HGDIOBJ]

gdi32.SetGraphicsMode.restype = INT
gdi32.SetGraphicsMode.argtypes = [HDC, INT]

gdi32.GetTextMetricsW.restype = BOOL
gdi32.GetTextMetricsW.argtypes = [HDC, POINTER(TEXTMETRIC)]

FONTENUMPROC = WINFUNCTYPE(INT, POINTER(LOGFONT), POINTER(TEXTMETRIC),
                           DWORD, c_void_p)
gdi32.EnumFontFamiliesExW.restype = INT
gdi32.EnumFontFamiliesExW.argtypes = [HDC, POINTER(LOGFONT),
                                      FONTENUMPROC, LPARAM, DWORD]

gdi32.GetOutlineTextMetricsW.restype = UINT
gdi32.GetOutlineTextMetricsW.argtypes = [HDC, UINT,
                                         POINTER(OUTLINETEXTMETRIC)]


gdi32.GetDeviceCaps.argtypes = [HDC, INT]
gdi32.GetDeviceCaps.restype = INT

user32 = windll.user32

user32.GetDC.restype = HDC  # HDC
user32.GetDC.argtypes = [UINT32]  # HWND

user32.ReleaseDC.argtypes = [c_void_p, HDC]

try:
    user32.SetProcessDPIAware.argtypes = []
except AttributeError:
    pass  # not present on XP


# gdiplus

class GdiplusStartupInput(Structure):
    _fields_ = [
        ('GdiplusVersion', UINT32), ('DebugEventCallback', c_void_p),
        ('SuppressBackgroundThread', BOOL), ('SuppressExternalCodecs', BOOL)]


class GdiplusStartupOutput(Structure):
    _fields = [('NotificationHookProc', c_void_p),
               ('NotificationUnhookProc', c_void_p)]

gdiplus = windll.gdiplus

gdiplus.GdipCreateFontFamilyFromName.restype = c_int
gdiplus.GdipCreateFontFamilyFromName.argtypes = [c_wchar_p, c_void_p, c_void_p]

gdiplus.GdipNewPrivateFontCollection.restype = c_int
gdiplus.GdipNewPrivateFontCollection.argtypes = [c_void_p]

gdiplus.GdipPrivateAddFontFile.restype = c_int
gdiplus.GdipPrivateAddFontFile.argtypes = [c_void_p, c_wchar_p]

gdiplus.GdipGetFamilyName.restype = c_int
gdiplus.GdipGetFamilyName.argtypes = [c_void_p, c_wchar_p, c_int]


def gdiplus_init():
    token = c_ulong()
    startup_in = GdiplusStartupInput()
    startup_in.GdiplusVersion = 1
    startup_out = GdiplusStartupOutput()
    gdiplus.GdiplusStartup(byref(token), byref(startup_in), byref(startup_out))
    atexit.register(partial(gdiplus.GdiplusShutdown, token))

gdiplus_init()
