# -*- coding: utf-8 -*-

import warnings
from ctypes import (util, cdll, c_void_p, c_char_p, c_double, c_int, c_bool,
                    Union, Structure, byref, POINTER)
from ..util.wrappers import run_subprocess

# Some code adapted from Pyglet

fc = util.find_library('fontconfig')
if fc is None:
    raise ImportError('fontconfig not found')
fontconfig = cdll.LoadLibrary(fc)

FC_FAMILY = 'family'.encode('ASCII')
FC_SIZE = 'size'.encode('ASCII')
FC_SLANT = 'slant'.encode('ASCII')
FC_WEIGHT = 'weight'.encode('ASCII')
FC_FT_FACE = 'ftface'.encode('ASCII')
FC_FILE = 'file'.encode('ASCII')
FC_STYLE = 'style'.encode('ASCII')
FC_LANG = 'lang'.encode('ASCII')
FC_WEIGHT_REGULAR = 80
FC_WEIGHT_BOLD = 200
FC_SLANT_ROMAN = 0
FC_SLANT_ITALIC = 100

FcMatchPattern = 1
FcTypeVoid = 0
FcTypeInteger = 1
FcTypeDouble = 2
FcTypeString = 3
FcTypeBool = 4
FcTypeMatrix = 5
FcTypeCharSet = 6
FcTypeFTFace = 7
FcTypeLangSet = 8
FcType = c_int


class _FcValueUnion(Union):
    _fields_ = [('s', c_char_p), ('i', c_int), ('b', c_int), ('d', c_double),
                ('m', c_void_p), ('c', c_void_p), ('f', c_void_p),
                ('p', c_void_p), ('l', c_void_p)]


class FcValue(Structure):
    _fields_ = [('type', FcType), ('u', _FcValueUnion)]


class FcFontSet(Structure):
    _fields_ = [('nfont', c_int), ('sfont', c_int),
                ('fonts', POINTER(c_void_p))]


class FcObjectSet(Structure):
    _fields_ = [('nobject', c_int), ('sobject', c_int), ('objects', c_void_p)]

fontconfig.FcConfigSubstitute.argtypes = [c_void_p, c_void_p, c_int]
fontconfig.FcDefaultSubstitute.argtypes = [c_void_p]
fontconfig.FcFontMatch.restype = c_void_p
fontconfig.FcFontMatch.argtypes = [c_void_p, c_void_p, c_void_p]
fontconfig.FcPatternBuild.restype = c_void_p
fontconfig.FcPatternCreate.restype = c_void_p
fontconfig.FcPatternAddDouble.argtypes = [c_void_p, c_char_p, c_double]
fontconfig.FcPatternAddInteger.argtypes = [c_void_p, c_char_p, c_int]
fontconfig.FcPatternAddString.argtypes = [c_void_p, c_char_p, c_char_p]
fontconfig.FcPatternDestroy.argtypes = [c_void_p]
fontconfig.FcPatternGetFTFace.argtypes = [c_void_p, c_char_p, c_int, c_void_p]
fontconfig.FcPatternGet.argtypes = [c_void_p, c_char_p, c_int, c_void_p]

fontconfig.FcObjectSetBuild.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p]
fontconfig.FcObjectSetBuild.restype = FcObjectSet
fontconfig.FcFontList.restype = FcFontSet
fontconfig.FcFontList.argtypes = [c_void_p, c_void_p, FcObjectSet]
fontconfig.FcNameUnparse.restype = c_char_p
fontconfig.FcNameUnparse.argtypes = [c_void_p]
fontconfig.FcFontSetDestroy.argtypes = [FcFontSet]
fontconfig.FcFontSort.restype = FcFontSet
fontconfig.FcFontSort.argtypes = [c_void_p, c_void_p, c_bool,
                                  c_void_p, c_void_p]
fontconfig.FcConfigGetCurrent.restype = c_void_p


def find_font(face, bold, italic):
    """Find font"""
    bold = FC_WEIGHT_BOLD if bold else FC_WEIGHT_REGULAR
    italic = FC_SLANT_ITALIC if italic else FC_SLANT_ROMAN
    face = face.encode('utf8')
    fontconfig.FcInit()
    pattern = fontconfig.FcPatternCreate()
    fontconfig.FcPatternAddInteger(pattern, FC_WEIGHT, bold)
    fontconfig.FcPatternAddInteger(pattern, FC_SLANT, italic)
    fontconfig.FcPatternAddString(pattern, FC_FAMILY, face)
    fontconfig.FcConfigSubstitute(0, pattern, FcMatchPattern)
    fontconfig.FcDefaultSubstitute(pattern)
    result = FcType()
    match = fontconfig.FcFontMatch(0, pattern, byref(result))
    fontconfig.FcPatternDestroy(pattern)
    if not match:
        raise RuntimeError('Could not match font "%s"' % face)
    value = FcValue()
    fontconfig.FcPatternGet(match, FC_FAMILY, 0, byref(value))
    if(value.u.s != face):
        warnings.warn('Could not find face match "%s", falling back to "%s"'
                      % (face, value.u.s))
    result = fontconfig.FcPatternGet(match, FC_FILE, 0, byref(value))
    if result != 0:
        raise RuntimeError('No filename or FT face for "%s"' % face)
    fname = value.u.s
    return fname.decode('utf-8')


def _list_fonts():
    """List system fonts"""
    stdout_, stderr = run_subprocess(['fc-list', ':scalable=true', 'family'])
    vals = [v.split(',')[0] for v in stdout_.strip().splitlines(False)]
    return vals
