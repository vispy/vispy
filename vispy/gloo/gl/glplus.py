# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" This module provides a namespace for additional desktop OpenGL functions.

The functions in this module are copied from PyOpenGL, but any deprecated
functions are omitted, as well as any functions that are in our ES 2.0 API.

"""

from OpenGL import GL as _GL
from . import _pyopengl2
from . import _constants


def _inject():
    """ Inject functions and constants from PyOpenGL but leave out the
    names that are deprecated or that we provide in our API.
    """
    
    # Get namespaces
    NS = globals()
    GLNS = _GL.__dict__
    
    # Get names that we use in our API
    used_names = []
    used_names.extend([names[0] for names in _pyopengl2._functions_to_import])
    used_names.extend([name for name in _pyopengl2._used_functions])
    NS['_used_names'] = used_names
    #
    used_constants = set(_constants.__dict__)
    # Count
    injected_constants = 0
    injected_functions = 0
    
    for name in dir(_GL):
        
        if name.startswith('GL_'):
            # todo: find list of deprecated constants
            if name not in used_constants:
                NS[name] = GLNS[name]
                injected_constants += 1
        
        elif name.startswith('gl'):
            # Functions
            if (name + ',') in _deprecated_functions:
                pass  # Function is deprecated
            elif name in used_names:
                pass  # Function is in our GL ES 2.0 API
            else:
                NS[name] = GLNS[name]
                injected_functions += 1
    
    #print('injected %i constants and %i functions in glplus' % 
    #      (injected_constants, injected_functions))


# List of deprecated functions, obtained by parsing gl.spec
_deprecated_functions = """
    glAccum, glAlphaFunc, glAreTexturesResident, glArrayElement, glBegin, 
    glBitmap, glCallList, glCallLists, glClearAccum, glClearIndex, 
    glClientActiveTexture, glClipPlane, glColor3b, glColor3bv, glColor3d, 
    glColor3dv, glColor3f, glColor3fv, glColor3i, glColor3iv, glColor3s, 
    glColor3sv, glColor3ub, glColor3ubv, glColor3ui, glColor3uiv, glColor3us, 
    glColor3usv, glColor4b, glColor4bv, glColor4d, glColor4dv, glColor4f, 
    glColor4fv, glColor4i, glColor4iv, glColor4s, glColor4sv, glColor4ub, 
    glColor4ubv, glColor4ui, glColor4uiv, glColor4us, glColor4usv, 
    glColorMaterial, glColorPointer, glColorSubTable, glColorTable, 
    glColorTableParameterfv, glColorTableParameteriv, glConvolutionFilter1D, 
    glConvolutionFilter2D, glConvolutionParameterf, glConvolutionParameterfv, 
    glConvolutionParameteri, glConvolutionParameteriv, glCopyColorSubTable, 
    glCopyColorTable, glCopyConvolutionFilter1D, glCopyConvolutionFilter2D, 
    glCopyPixels, glDeleteLists, glDisableClientState, glDrawPixels, 
    glEdgeFlag, glEdgeFlagPointer, glEdgeFlagv, glEnableClientState, glEnd, 
    glEndList, glEvalCoord1d, glEvalCoord1dv, glEvalCoord1f, glEvalCoord1fv, 
    glEvalCoord2d, glEvalCoord2dv, glEvalCoord2f, glEvalCoord2fv, 
    glEvalMesh1, glEvalMesh2, glEvalPoint1, glEvalPoint2, glFeedbackBuffer, 
    glFogCoordPointer, glFogCoordd, glFogCoorddv, glFogCoordf, glFogCoordfv, 
    glFogf, glFogfv, glFogi, glFogiv, glFrustum, glGenLists, glGetClipPlane, 
    glGetColorTable, glGetColorTableParameterfv, glGetColorTableParameteriv, 
    glGetConvolutionFilter, glGetConvolutionParameterfv, 
    glGetConvolutionParameteriv, glGetHistogram, glGetHistogramParameterfv, 
    glGetHistogramParameteriv, glGetLightfv, glGetLightiv, glGetMapdv, 
    glGetMapfv, glGetMapiv, glGetMaterialfv, glGetMaterialiv, glGetMinmax, 
    glGetMinmaxParameterfv, glGetMinmaxParameteriv, glGetPixelMapfv, 
    glGetPixelMapuiv, glGetPixelMapusv, glGetPolygonStipple, 
    glGetSeparableFilter, glGetTexEnvfv, glGetTexEnviv, glGetTexGendv, 
    glGetTexGenfv, glGetTexGeniv, glHistogram, glIndexMask, glIndexPointer, 
    glIndexd, glIndexdv, glIndexf, glIndexfv, glIndexi, glIndexiv, glIndexs, 
    glIndexsv, glInitNames, glInterleavedArrays, glIsList, glLightModelf, 
    glLightModelfv, glLightModeli, glLightModeliv, glLightf, glLightfv, 
    glLighti, glLightiv, glLineStipple, glListBase, glLoadIdentity, 
    glLoadMatrixd, glLoadMatrixf, glLoadName, glLoadTransposeMatrixd, 
    glLoadTransposeMatrixf, glMap1d, glMap1f, glMap2d, glMap2f, glMapGrid1d, 
    glMapGrid1f, glMapGrid2d, glMapGrid2f, glMaterialf, glMaterialfv, 
    glMateriali, glMaterialiv, glMatrixMode, glMinmax, glMultMatrixd, 
    glMultMatrixf, glMultTransposeMatrixd, glMultTransposeMatrixf, 
    glMultiTexCoord1d, glMultiTexCoord1dv, glMultiTexCoord1f, 
    glMultiTexCoord1fv, glMultiTexCoord1i, glMultiTexCoord1iv, 
    glMultiTexCoord1s, glMultiTexCoord1sv, glMultiTexCoord2d, 
    glMultiTexCoord2dv, glMultiTexCoord2f, glMultiTexCoord2fv, 
    glMultiTexCoord2i, glMultiTexCoord2iv, glMultiTexCoord2s, 
    glMultiTexCoord2sv, glMultiTexCoord3d, glMultiTexCoord3dv, 
    glMultiTexCoord3f, glMultiTexCoord3fv, glMultiTexCoord3i, 
    glMultiTexCoord3iv, glMultiTexCoord3s, glMultiTexCoord3sv, 
    glMultiTexCoord4d, glMultiTexCoord4dv, glMultiTexCoord4f, 
    glMultiTexCoord4fv, glMultiTexCoord4i, glMultiTexCoord4iv, 
    glMultiTexCoord4s, glMultiTexCoord4sv, glNewList, glNormal3b, 
    glNormal3bv, glNormal3d, glNormal3dv, glNormal3f, glNormal3fv, 
    glNormal3i, glNormal3iv, glNormal3s, glNormal3sv, glNormalPointer, 
    glOrtho, glPassThrough, glPixelMapfv, glPixelMapuiv, glPixelMapusv, 
    glPixelTransferf, glPixelTransferi, glPixelZoom, glPolygonStipple, 
    glPopAttrib, glPopClientAttrib, glPopMatrix, glPopName, 
    glPrioritizeTextures, glPushAttrib, glPushClientAttrib, glPushMatrix, 
    glPushName, glRasterPos2d, glRasterPos2dv, glRasterPos2f, glRasterPos2fv, 
    glRasterPos2i, glRasterPos2iv, glRasterPos2s, glRasterPos2sv, 
    glRasterPos3d, glRasterPos3dv, glRasterPos3f, glRasterPos3fv, 
    glRasterPos3i, glRasterPos3iv, glRasterPos3s, glRasterPos3sv, 
    glRasterPos4d, glRasterPos4dv, glRasterPos4f, glRasterPos4fv, 
    glRasterPos4i, glRasterPos4iv, glRasterPos4s, glRasterPos4sv, glRectd, 
    glRectdv, glRectf, glRectfv, glRecti, glRectiv, glRects, glRectsv, 
    glRenderMode, glResetHistogram, glResetMinmax, glRotated, glRotatef, 
    glScaled, glScalef, glSecondaryColor3b, glSecondaryColor3bv, 
    glSecondaryColor3d, glSecondaryColor3dv, glSecondaryColor3f, 
    glSecondaryColor3fv, glSecondaryColor3i, glSecondaryColor3iv, 
    glSecondaryColor3s, glSecondaryColor3sv, glSecondaryColor3ub, 
    glSecondaryColor3ubv, glSecondaryColor3ui, glSecondaryColor3uiv, 
    glSecondaryColor3us, glSecondaryColor3usv, glSecondaryColorPointer, 
    glSelectBuffer, glSeparableFilter2D, glShadeModel, glTexCoord1d, 
    glTexCoord1dv, glTexCoord1f, glTexCoord1fv, glTexCoord1i, glTexCoord1iv, 
    glTexCoord1s, glTexCoord1sv, glTexCoord2d, glTexCoord2dv, glTexCoord2f, 
    glTexCoord2fv, glTexCoord2i, glTexCoord2iv, glTexCoord2s, glTexCoord2sv, 
    glTexCoord3d, glTexCoord3dv, glTexCoord3f, glTexCoord3fv, glTexCoord3i, 
    glTexCoord3iv, glTexCoord3s, glTexCoord3sv, glTexCoord4d, glTexCoord4dv, 
    glTexCoord4f, glTexCoord4fv, glTexCoord4i, glTexCoord4iv, glTexCoord4s, 
    glTexCoord4sv, glTexCoordPointer, glTexEnvf, glTexEnvfv, glTexEnvi, 
    glTexEnviv, glTexGend, glTexGendv, glTexGenf, glTexGenfv, glTexGeni, 
    glTexGeniv, glTranslated, glTranslatef, glVertex2d, glVertex2dv, 
    glVertex2f, glVertex2fv, glVertex2i, glVertex2iv, glVertex2s, 
    glVertex2sv, glVertex3d, glVertex3dv, glVertex3f, glVertex3fv, 
    glVertex3i, glVertex3iv, glVertex3s, glVertex3sv, glVertex4d, 
    glVertex4dv, glVertex4f, glVertex4fv, glVertex4i, glVertex4iv, 
    glVertex4s, glVertex4sv, glVertexAttrib1d, glVertexAttrib1dv, 
    glVertexAttrib1f, glVertexAttrib1fv, glVertexAttrib1s, glVertexAttrib1sv, 
    glVertexAttrib2d, glVertexAttrib2dv, glVertexAttrib2f, glVertexAttrib2fv, 
    glVertexAttrib2s, glVertexAttrib2sv, glVertexAttrib3d, glVertexAttrib3dv, 
    glVertexAttrib3f, glVertexAttrib3fv, glVertexAttrib3s, glVertexAttrib3sv, 
    glVertexAttrib4Nbv, glVertexAttrib4Niv, glVertexAttrib4Nsv, 
    glVertexAttrib4Nub, glVertexAttrib4Nubv, glVertexAttrib4Nuiv, 
    glVertexAttrib4Nusv, glVertexAttrib4bv, glVertexAttrib4d, 
    glVertexAttrib4dv, glVertexAttrib4f, glVertexAttrib4fv, 
    glVertexAttrib4iv, glVertexAttrib4s, glVertexAttrib4sv, 
    glVertexAttrib4ubv, glVertexAttrib4uiv, glVertexAttrib4usv, 
    glVertexAttribI1i, glVertexAttribI1iv, glVertexAttribI1ui, 
    glVertexAttribI1uiv, glVertexAttribI2i, glVertexAttribI2iv, 
    glVertexAttribI2ui, glVertexAttribI2uiv, glVertexAttribI3i, 
    glVertexAttribI3iv, glVertexAttribI3ui, glVertexAttribI3uiv, 
    glVertexAttribI4bv, glVertexAttribI4i, glVertexAttribI4iv, 
    glVertexAttribI4sv, glVertexAttribI4ubv, glVertexAttribI4ui, 
    glVertexAttribI4uiv, glVertexAttribI4usv, glVertexPointer, glWindowPos2d, 
    glWindowPos2dv, glWindowPos2f, glWindowPos2fv, glWindowPos2i, 
    glWindowPos2iv, glWindowPos2s, glWindowPos2sv, glWindowPos3d, 
    glWindowPos3dv, glWindowPos3f, glWindowPos3fv, glWindowPos3i, 
    glWindowPos3iv, glWindowPos3s, glWindowPos3sv, 
    """


_inject()
