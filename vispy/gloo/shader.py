# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import re
import os.path

from . import gl
from ..util import logger
from .globject import GLObject


# ------------------------------------------------------------ Shader class ---
class Shader(GLObject):

    """Abstract shader class."""

    _gtypes = {
        'float':       gl.GL_FLOAT,
        'vec2':        gl.GL_FLOAT_VEC2,
        'vec3':        gl.GL_FLOAT_VEC3,
        'vec4':        gl.GL_FLOAT_VEC4,
        'int':         gl.GL_INT,
        'ivec2':       gl.GL_INT_VEC2,
        'ivec3':       gl.GL_INT_VEC3,
        'ivec4':       gl.GL_INT_VEC4,
        'bool':        gl.GL_BOOL,
        'bvec2':       gl.GL_BOOL_VEC2,
        'bvec3':       gl.GL_BOOL_VEC3,
        'bvec4':       gl.GL_BOOL_VEC4,
        'mat2':        gl.GL_FLOAT_MAT2,
        'mat3':        gl.GL_FLOAT_MAT3,
        'mat4':        gl.GL_FLOAT_MAT4,
        #        'sampler1D':   gl.GL_SAMPLER_1D,
        'sampler2D':   gl.GL_SAMPLER_2D,
        #        'sampler13':   gl.GL_SAMPLER_3D,
    }

    def __init__(self, target, code=None):
        """
        Initialize the shader and get code if possible.

        Parameters
        ----------

        code: str
            code can be a filename or the actual code
        """

        GLObject.__init__(self)
        if target not in [gl.GL_VERTEX_SHADER, gl.GL_FRAGMENT_SHADER]:
            raise ValueError("Shader target must be vertex or fragment")

        self._target = target
        self._code = None
        self._source = None
        if code is not None:
            self.code = code

    @property
    def code(self):
        """ Shader source code """
        return self._code

    @code.setter
    def code(self, code):
        """ Shader source code """
        if os.path.exists(code):
            with open(code) as file:
                self._code = file.read()
                self._source = os.path.basename(code)
        else:
            self._code = code
            self._source = '<string>'
        self._need_update = True

    @property
    def source(self):
        """ Shader source (string or filename) """
        return self._source

    def _create(self):
        """ Compile the source and checks eveyrthing's ok """

        # Check if we have something to compile
        if not self._code:
            raise RuntimeError("No code has been given")

        # Check that shader object has been created
        if self._handle <= 0:
            self._handle = gl.glCreateShader(self._target)
            if self._handle <= 0:
                raise RuntimeError("Cannot create shader object")

        # Set shader source
        gl.glShaderSource(self._handle, self._code)

        logger.debug("GPU: Creating shader")

        # Actual compilation
        gl.glCompileShader(self._handle)
        status = gl.glGetShaderiv(self._handle, gl.GL_COMPILE_STATUS)
        if not status:
            error = gl.glGetShaderInfoLog(self._handle)
            lineno, mesg = self._parse_error(error)
            self._print_error(mesg, lineno - 1)
            raise RuntimeError("Shader compilation error")

    def _delete(self):
        """ Delete shader from GPU memory (if it was present). """

        gl.glDeleteShader(self._handle)

    def _parse_error(self, error):
        """
        Parses a single GLSL error and extracts the line number and error
        description.

        Parameters
        ----------
        error : str
            An error string as returned byt the compilation process
        """

        # Nvidia
        # 0(7): error C1008: undefined variable "MV"
        m = re.match(r'(\d+)\((\d+)\):\s(.*)', error)
        if m:
            return int(m.group(2)), m.group(3)

        # ATI / Intel
        # ERROR: 0:131: '{' : syntax error parse error
        m = re.match(r'ERROR:\s(\d+):(\d+):\s(.*)', error)
        if m:
            return int(m.group(2)), m.group(3)

        # Nouveau
        # 0:28(16): error: syntax error, unexpected ')', expecting '('
        m = re.match(r'(\d+):(\d+)\((\d+)\):\s(.*)', error)
        if m:
            return int(m.group(2)), m.group(4)

        raise ValueError('Unknown GLSL error format')

    def _print_error(self, error, lineno):
        """
        Print error and show the faulty line + some context

        Parameters
        ----------
        error : str
            An error string as returned byt the compilation process

        lineno: int
            Line where error occurs
        """
        lines = self._code.split('\n')
        start = max(0, lineno - 2)
        end = min(len(lines), lineno + 1)

        print('Error in %s' % (repr(self)))
        print(' -> %s' % error)
        print()
        if start > 0:
            print(' ...')
        for i, line in enumerate(lines[start:end]):
            if (i + start) == lineno:
                print(' %03d %s' % (i + start, line))
            else:
                if len(line):
                    print(' %03d %s' % (i + start, line))
        if end < len(lines):
            print(' ...')
        print()

    @property
    def uniforms(self):
        """ Shader uniforms obtained from source code """

        uniforms = []
        regex = re.compile("""\s*uniform\s+(?P<type>\w+)\s+"""
                           """(?P<name>\w+)\s*(\[(?P<size>\d+)\])?\s*;""")
        for m in re.finditer(regex, self._code):
            size = -1
            gtype = Shader._gtypes[m.group('type')]
            if m.group('size'):
                size = int(m.group('size'))
            if size >= 1:
                for i in range(size):
                    name = '%s[%d]' % (m.group('name'), i)
                    uniforms.append((name, gtype))
            else:
                uniforms.append((m.group('name'), gtype))
        return uniforms

    @property
    def attributes(self):
        """ Shader attributes obtained from source code """

        attributes = []
        regex = re.compile("""\s*attribute\s+(?P<type>\w+)\s+"""
                           """(?P<name>\w+)\s*(\[(?P<size>\d+)\])?\s*;""")
        for m in re.finditer(regex, self._code):
            size = -1
            gtype = Shader._gtypes[m.group('type')]
            if m.group('size'):
                size = int(m.group('size'))
            if size >= 1:
                for i in range(size):
                    name = '%s[%d]' % (m.group('name'), i)
                    attributes.append((name, gtype))
            else:
                attributes.append((m.group('name'), gtype))
        return attributes


# ------------------------------------------------------ VertexShader class ---
class VertexShader(Shader):

    """ Vertex shader class """

    def __init__(self, code=None):
        Shader.__init__(self, gl.GL_VERTEX_SHADER, code)

    def __repr__(self):
        return "Vertex Shader %d (%s)" % (self._id, self._source)


# ---------------------------------------------------- FragmentShader class ---
class FragmentShader(Shader):

    """ Fragment shader class """

    def __init__(self, code=None):
        Shader.__init__(self, gl.GL_FRAGMENT_SHADER, code)

    def __repr__(self):
        return "Fragment Shader %d (%s)" % (self._id, self._source)
