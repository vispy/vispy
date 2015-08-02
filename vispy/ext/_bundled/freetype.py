#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
# -----------------------------------------------------------------------------
'''
FreeType high-level python API

Adapted from freetype-py.
'''

import sys
import struct
from ctypes import (byref, c_char_p, c_ushort, cast, util, CDLL, Structure,
                    POINTER, c_int, c_short, c_long, c_void_p, c_uint,
                    c_char, c_ubyte, CFUNCTYPE)

from ..six import string_types
from ...util import load_data_file

FT_LOAD_RENDER = 4
FT_KERNING_DEFAULT = 0
FT_KERNING_UNFITTED = 1
FT_LOAD_NO_HINTING = 2
FT_LOAD_FORCE_AUTOHINT = 32
FT_LOAD_NO_AUTOHINT = 32768
FT_LOAD_TARGET_LCD = 196608
FT_LOAD_TARGET_LIGHT = 65536
FT_LOAD_NO_SCALE = 1
FT_FACE_FLAG_SCALABLE = 1

_64_bit = (8 * struct.calcsize("P")) == 64
##############################################################################
# ft_structs

FT_Int = c_int
FT_UInt = c_uint
FT_F2Dot14 = c_short
FT_Pos = FT_Fixed = FT_Long = c_long
FT_Glyph_Format = c_int
FT_String_p = c_char_p
FT_Short = c_short  # A typedef for signed short.
FT_UShort = c_ushort  # A typedef for unsigned short.
FT_Generic_Finalizer = CFUNCTYPE(None, c_void_p)
FT_Encoding = c_int


class FT_LibraryRec(Structure):
    _fields_ = []
FT_Library = POINTER(FT_LibraryRec)


class FT_Vector(Structure):
    _fields_ = [('x', FT_Pos), ('y', FT_Pos)]


class FT_UnitVector(Structure):
    _fields_ = [('x', FT_F2Dot14), ('y', FT_F2Dot14)]


class FT_Matrix(Structure):
    _fields_ = [('xx', FT_Fixed), ('xy', FT_Fixed),
                ('yx', FT_Fixed), ('yy', FT_Fixed)]


class FT_GlyphRec(Structure):
    _fields_ = [('library', FT_Library), ('clazz', c_void_p),
                ('format', FT_Glyph_Format), ('advance', FT_Vector)]
FT_Glyph = POINTER(FT_GlyphRec)


class FT_Bitmap(Structure):
    _fields_ = [('rows', c_int), ('width', c_int),
                ('pitch', c_int), ('buffer', POINTER(c_ubyte)),
                ('num_grays', c_short), ('pixel_mode', c_ubyte),
                ('palette_mode', c_char), ('palette', c_void_p)]


class FT_BitmapGlyphRec(Structure):
    _fields_ = [('root', FT_GlyphRec), ('left', FT_Int),
                ('top', FT_Int), ('bitmap', FT_Bitmap)]
FT_BitmapGlyph = POINTER(FT_BitmapGlyphRec)


class FT_Glyph_Metrics(Structure):
    _fields_ = [('width', FT_Pos), ('height', FT_Pos),
                ('horiBearingX', FT_Pos), ('horiBearingY', FT_Pos),
                ('horiAdvance',  FT_Pos), ('vertBearingX', FT_Pos),
                ('vertBearingY', FT_Pos), ('vertAdvance',  FT_Pos)]


class FT_Outline(Structure):
    _fields_ = [('n_contours', c_short), ('n_points', c_short),
                ('points', POINTER(FT_Vector)), ('tags', POINTER(c_ubyte)),
                ('contours', POINTER(c_short)), ('flags', c_int)]


class FT_Size_Metrics(Structure):
    _fields_ = [('x_ppem', FT_UShort), ('y_ppem', FT_UShort),
                ('x_scale', FT_Fixed), ('y_scale', FT_Fixed),
                ('ascender', FT_Pos),  ('descender', FT_Pos),
                ('height', FT_Pos), ('max_advance', FT_Pos)]


class FT_BBox(Structure):
    _fields_ = [('xMin', FT_Pos), ('yMin', FT_Pos),
                ('xMax', FT_Pos), ('yMax', FT_Pos)]


class FT_Generic(Structure):
    _fields_ = [('data', c_void_p), ('finalizer', FT_Generic_Finalizer)]


class FT_SizeRec(Structure):
    _fields_ = [('face', c_void_p), ('generic', FT_Generic),
                ('metrics', FT_Size_Metrics), ('internal', c_void_p)]
FT_Size = POINTER(FT_SizeRec)


class FT_CharmapRec(Structure):
    _fields_ = [('face', c_void_p), ('encoding', FT_Encoding),
                ('platform_id', FT_UShort), ('encoding_id', FT_UShort)]
FT_Charmap = POINTER(FT_CharmapRec)


class FT_Bitmap_Size(Structure):
    _fields_ = [('height', FT_Short), ('width', FT_Short),
                ('size', FT_Pos), ('x_ppem', FT_Pos), ('y_ppem', FT_Pos)]


class FT_GlyphSlotRec(Structure):
    _fields_ = [('library', FT_Library), ('face', c_void_p),
                ('next', c_void_p), ('reserved', c_uint),
                ('generic', FT_Generic), ('metrics', FT_Glyph_Metrics),
                ('linearHoriAdvance', FT_Fixed),
                ('linearVertAdvance', FT_Fixed),
                ('advance', FT_Vector), ('format',  FT_Glyph_Format),
                ('bitmap', FT_Bitmap), ('bitmap_left', FT_Int),
                ('bitmap_top', FT_Int), ('outline', FT_Outline),
                ('num_subglyphs', FT_UInt), ('subglyphs', c_void_p),
                ('control_data', c_void_p), ('control_len', c_long),
                ('lsb_delta', FT_Pos), ('rsb_delta', FT_Pos),
                ('other', c_void_p), ('internal', c_void_p)]
FT_GlyphSlot = POINTER(FT_GlyphSlotRec)


class FT_FaceRec(Structure):
    _fields_ = [('num_faces', FT_Long), ('face_index', FT_Long),
                ('face_flags', FT_Long), ('style_flags', FT_Long),
                ('num_glyphs', FT_Long), ('family_name', FT_String_p),
                ('style_name', FT_String_p), ('num_fixed_sizes', FT_Int),
                ('available_sizes', POINTER(FT_Bitmap_Size)),
                ('num_charmaps', c_int), ('charmaps', POINTER(FT_Charmap)),
                ('generic', FT_Generic), ('bbox', FT_BBox),
                ('units_per_EM', FT_UShort), ('ascender', FT_Short),
                ('descender', FT_Short), ('height', FT_Short),
                ('max_advance_width', FT_Short),
                ('max_advance_height', FT_Short),
                ('underline_position',  FT_Short),
                ('underline_thickness', FT_Short),
                ('glyph', FT_GlyphSlot), ('size', FT_Size),
                ('charmap', FT_Charmap),
                ('driver', c_void_p), ('memory', c_void_p),
                ('stream', c_void_p), ('sizes_list_head', c_void_p),
                ('sizes_list_tail', c_void_p), ('autohint', FT_Generic),
                ('extensions', c_void_p), ('internal', c_void_p)]
FT_Face = POINTER(FT_FaceRec)


##############################################################################
# __init__.py

__dll__ = None
FT_Library_filename = util.find_library('freetype')
if not FT_Library_filename and sys.platform.startswith('win'):
    fname_end = '_x64.dll' if _64_bit else '.dll'
    FT_Library_filename = load_data_file('freetype/freetype253' + fname_end)
if not FT_Library_filename:
    raise ImportError('Freetype library not found')
if not __dll__:
    __dll__ = CDLL(FT_Library_filename)


FT_Init_FreeType = __dll__.FT_Init_FreeType
FT_Done_FreeType = __dll__.FT_Done_FreeType
FT_Library_Version = __dll__.FT_Library_Version
__handle__ = None


# Comment out to avoid segfaults on Py34
# def __del_library__(self):
#     global __handle__
#     if __handle__:
#         try:
#             FT_Done_FreeType(self)
#             __handle__ = None
#         except:
#             pass
# FT_Library.__del__ = __del_library__


def get_handle():
    '''
    Get unique FT_Library handle
    '''
    global __handle__
    if not __handle__:
        __handle__ = FT_Library()
        error = FT_Init_FreeType(byref(__handle__))
        if error:
            raise RuntimeError(hex(error))
    return __handle__


def version():
    '''
    Return the version of the FreeType library being used as a tuple of
    ( major version number, minor version number, patch version number )
    '''
    amajor = FT_Int()
    aminor = FT_Int()
    apatch = FT_Int()
    library = get_handle()
    FT_Library_Version(library, byref(amajor), byref(aminor), byref(apatch))
    return (amajor.value, aminor.value, apatch.value)


try:
    FT_Library_SetLcdFilter = __dll__.FT_Library_SetLcdFilter
except:
    def FT_Library_SetLcdFilter(*args, **kwargs):
        return 0
if version() >= (2, 4, 0):
    FT_Library_SetLcdFilterWeights = __dll__.FT_Library_SetLcdFilterWeights
FT_New_Face = __dll__.FT_New_Face
FT_New_Memory_Face = __dll__.FT_New_Memory_Face
FT_Open_Face = __dll__.FT_Open_Face
FT_Attach_File = __dll__.FT_Attach_File
FT_Attach_Stream = __dll__.FT_Attach_Stream
if version() >= (2, 4, 2):
    FT_Reference_Face = __dll__.FT_Reference_Face
FT_Done_Face = __dll__.FT_Done_Face
FT_Done_Glyph = __dll__.FT_Done_Glyph
FT_Select_Size = __dll__.FT_Select_Size
FT_Request_Size = __dll__.FT_Request_Size
FT_Set_Char_Size = __dll__.FT_Set_Char_Size
FT_Set_Pixel_Sizes = __dll__.FT_Set_Pixel_Sizes
FT_Load_Glyph = __dll__.FT_Load_Glyph
FT_Load_Char = __dll__.FT_Load_Char
FT_Set_Transform = __dll__.FT_Set_Transform
FT_Render_Glyph = __dll__.FT_Render_Glyph
FT_Get_Kerning = __dll__.FT_Get_Kerning
FT_Get_Track_Kerning = __dll__.FT_Get_Track_Kerning
FT_Get_Glyph_Name = __dll__.FT_Get_Glyph_Name
FT_Get_Glyph = __dll__.FT_Get_Glyph

FT_Glyph_Get_CBox = __dll__.FT_Glyph_Get_CBox

FT_Get_Postscript_Name = __dll__.FT_Get_Postscript_Name
FT_Get_Postscript_Name.restype = c_char_p
FT_Select_Charmap = __dll__.FT_Select_Charmap
FT_Set_Charmap = __dll__.FT_Set_Charmap
FT_Get_Charmap_Index = __dll__.FT_Get_Charmap_Index
FT_Get_CMap_Language_ID = __dll__.FT_Get_CMap_Language_ID
FT_Get_CMap_Format = __dll__.FT_Get_CMap_Format
FT_Get_Char_Index = __dll__.FT_Get_Char_Index
FT_Get_First_Char = __dll__.FT_Get_First_Char
FT_Get_Next_Char = __dll__.FT_Get_Next_Char
FT_Get_Name_Index = __dll__.FT_Get_Name_Index
FT_Get_SubGlyph_Info = __dll__.FT_Get_SubGlyph_Info
if version() >= (2, 3, 8):
    FT_Get_FSType_Flags = __dll__.FT_Get_FSType_Flags
    FT_Get_FSType_Flags.restype = c_ushort

FT_Get_X11_Font_Format = __dll__.FT_Get_X11_Font_Format
FT_Get_X11_Font_Format.restype = c_char_p

FT_Get_Sfnt_Name_Count = __dll__.FT_Get_Sfnt_Name_Count
FT_Get_Sfnt_Name = __dll__.FT_Get_Sfnt_Name
FT_Get_Advance = __dll__.FT_Get_Advance


FT_Outline_GetInsideBorder = __dll__.FT_Outline_GetInsideBorder
FT_Outline_GetOutsideBorder = __dll__.FT_Outline_GetOutsideBorder
FT_Outline_Get_BBox = __dll__.FT_Outline_Get_BBox
FT_Outline_Get_CBox = __dll__.FT_Outline_Get_CBox
FT_Stroker_New = __dll__.FT_Stroker_New
FT_Stroker_Set = __dll__.FT_Stroker_Set
FT_Stroker_Rewind = __dll__.FT_Stroker_Rewind
FT_Stroker_ParseOutline = __dll__.FT_Stroker_ParseOutline
FT_Stroker_BeginSubPath = __dll__.FT_Stroker_BeginSubPath
FT_Stroker_EndSubPath = __dll__.FT_Stroker_EndSubPath
FT_Stroker_LineTo = __dll__.FT_Stroker_LineTo
FT_Stroker_ConicTo = __dll__.FT_Stroker_ConicTo
FT_Stroker_CubicTo = __dll__.FT_Stroker_CubicTo
FT_Stroker_GetBorderCounts = __dll__.FT_Stroker_GetBorderCounts
FT_Stroker_ExportBorder = __dll__.FT_Stroker_ExportBorder
FT_Stroker_GetCounts = __dll__.FT_Stroker_GetCounts
FT_Stroker_Export = __dll__.FT_Stroker_Export
FT_Stroker_Done = __dll__.FT_Stroker_Done
FT_Glyph_Stroke = __dll__.FT_Glyph_Stroke
FT_Glyph_StrokeBorder = __dll__.FT_Glyph_StrokeBorder
FT_Glyph_To_Bitmap = __dll__.FT_Glyph_To_Bitmap


Vector = FT_Vector
Matrix = FT_Matrix


class Bitmap(object):
    def __init__(self, bitmap):
        self._FT_Bitmap = bitmap

    rows = property(lambda self: self._FT_Bitmap.rows)
    width = property(lambda self: self._FT_Bitmap.width)
    pitch = property(lambda self: self._FT_Bitmap.pitch)
    buffer = property(lambda self:
                      [self._FT_Bitmap.buffer[i]
                       for i in range(self.rows * self.pitch)])


class Glyph(object):
    def __init__(self, glyph):
        self._FT_Glyph = glyph

    def __del__(self):
        if self._FT_Glyph is not None and FT_Done_Glyph is not None:
            FT_Done_Glyph(self._FT_Glyph)

    def to_bitmap(self, mode, origin, destroy=False):
        error = FT_Glyph_To_Bitmap(byref(self._FT_Glyph),
                                   mode, origin, destroy)
        if error:
            raise RuntimeError(hex(error))
        return BitmapGlyph(self._FT_Glyph)


class BitmapGlyph(object):
    def __init__(self, glyph):
        self._FT_BitmapGlyph = cast(glyph, FT_BitmapGlyph)

    bitmap = property(lambda self:
                      Bitmap(self._FT_BitmapGlyph.contents.bitmap))
    left = property(lambda self: self._FT_BitmapGlyph.contents.left)
    top = property(lambda self: self._FT_BitmapGlyph.contents.top)


class GlyphSlot(object):
    def __init__(self, slot):
        self._FT_GlyphSlot = slot

    def get_glyph(self):
        aglyph = FT_Glyph()
        error = FT_Get_Glyph(self._FT_GlyphSlot, byref(aglyph))
        if error:
            raise RuntimeError(hex(error))
        return Glyph(aglyph)

    bitmap = property(lambda self: Bitmap(self._FT_GlyphSlot.contents.bitmap))
    metrics = property(lambda self: self._FT_GlyphSlot.contents.metrics)
    next = property(lambda self: GlyphSlot(self._FT_GlyphSlot.contents.next))
    advance = property(lambda self: self._FT_GlyphSlot.contents.advance)
    format = property(lambda self: self._FT_GlyphSlot.contents.format)
    bitmap_top = property(lambda self: self._FT_GlyphSlot.contents.bitmap_top)
    bitmap_left = property(lambda self:
                           self._FT_GlyphSlot.contents.bitmap_left)


class Face(object):
    def __init__(self, filename, index=0):
        library = get_handle()
        face = FT_Face()
        self._FT_Face = None
        # error = FT_New_Face( library, filename, 0, byref(face) )
        u_filename = c_char_p(filename.encode('utf-8'))
        error = FT_New_Face(library, u_filename, index, byref(face))
        if error:
            raise RuntimeError(hex(error))
        self._filename = filename
        self._index = index
        self._FT_Face = face

    def __del__(self):
        if self._FT_Face is not None and FT_Done_Face is not None:
            FT_Done_Face(self._FT_Face)

    def attach_file(self, filename):
        error = FT_Attach_File(self._FT_Face, filename)
        if error:
            raise RuntimeError(hex(error))

    def set_char_size(self, width=0, height=0, hres=72, vres=72):
        error = FT_Set_Char_Size(self._FT_Face, width, height, hres, vres)
        if error:
            raise RuntimeError('Could not set size: %s' % hex(error))

    def set_pixel_sizes(self, width, height):
        error = FT_Set_Pixel_Sizes(self._FT_Face, width, height)
        if error:
            raise RuntimeError(hex(error))

    def select_charmap(self, encoding):
        error = FT_Select_Charmap(self._FT_Face, encoding)
        if error:
            raise RuntimeError(hex(error))

    def set_charmap(self, charmap):
        error = FT_Set_Charmap(self._FT_Face, charmap._FT_Charmap)
        if error:
            raise RuntimeError(hex(error))

    def get_char_index(self, charcode):
        if isinstance(charcode, string_types):
            charcode = ord(charcode)
        return FT_Get_Char_Index(self._FT_Face, charcode)

    def get_first_char(self):
        agindex = FT_UInt()
        charcode = FT_Get_First_Char(self._FT_Face, byref(agindex))
        return charcode, agindex.value

    def get_next_char(self, charcode, agindex):
        agindex = FT_UInt(0)  # agindex )
        charcode = FT_Get_Next_Char(self._FT_Face, charcode, byref(agindex))
        return charcode, agindex.value

    def get_name_index(self, name):
        return FT_Get_Name_Index(self._FT_Face, name)

    def set_transform(self, matrix, delta):
        FT_Set_Transform(self._FT_Face,
                         byref(matrix), byref(delta))

    def select_size(self, strike_index):
        error = FT_Select_Size(self._FT_Face, strike_index)
        if error:
            raise RuntimeError(hex(error))

    def load_glyph(self, index, flags=FT_LOAD_RENDER):
        error = FT_Load_Glyph(self._FT_Face, index, flags)
        if error:
            raise RuntimeError(hex(error))

    def load_char(self, char, flags=FT_LOAD_RENDER):
        if len(char) == 1:
            char = ord(char)
        error = FT_Load_Char(self._FT_Face, char, flags)
        if error:
            raise RuntimeError(hex(error))

    def get_advance(self, gindex, flags):
        padvance = FT_Fixed(0)
        error = FT_Get_Advance(self._FT_Face, gindex, flags, byref(padvance))
        if error:
            raise RuntimeError(hex(error))
        return padvance.value

    def get_kerning(self, left, right, mode=FT_KERNING_DEFAULT):
        left_glyph = self.get_char_index(left)
        right_glyph = self.get_char_index(right)
        kerning = FT_Vector(0, 0)
        error = FT_Get_Kerning(self._FT_Face,
                               left_glyph, right_glyph, mode, byref(kerning))
        if error:
            raise RuntimeError(hex(error))
        return kerning

    def get_format(self):
        return FT_Get_X11_Font_Format(self._FT_Face)

    sfnt_name_count = property(lambda self:
                               FT_Get_Sfnt_Name_Count(self._FT_Face))
    postscript_name = property(lambda self:
                               FT_Get_Postscript_Name(self._FT_Face))
    num_faces = property(lambda self: self._FT_Face.contents.num_faces)
    face_index = property(lambda self: self._FT_Face.contents.face_index)
    face_flags = property(lambda self: self._FT_Face.contents.face_flags)
    style_flags = property(lambda self: self._FT_Face.contents.style_flags)
    num_glyphs = property(lambda self: self._FT_Face.contents.num_glyphs)
    family_name = property(lambda self: self._FT_Face.contents.family_name)
    style_name = property(lambda self: self._FT_Face.contents.style_name)
    num_fixed_sizes = property(lambda self:
                               self._FT_Face.contents.num_fixed_sizes)
    num_charmaps = property(lambda self: self._FT_Face.contents.num_charmaps)
    units_per_EM = property(lambda self: self._FT_Face.contents.units_per_EM)
    ascender = property(lambda self: self._FT_Face.contents.ascender)
    descender = property(lambda self: self._FT_Face.contents.descender)
    height = property(lambda self: self._FT_Face.contents.height)
    max_advance_width = property(lambda self:
                                 self._FT_Face.contents.max_advance_width)
    max_advance_height = property(lambda self:
                                  self._FT_Face.contents.max_advance_height)
    underline_position = property(lambda self:
                                  self._FT_Face.contents.underline_position)
    underline_thickness = property(lambda self:
                                   self._FT_Face.contents.underline_thickness)
    glyph = property(lambda self: GlyphSlot(self._FT_Face.contents.glyph))
