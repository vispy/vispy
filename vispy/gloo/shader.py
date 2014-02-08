# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All rights reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
VertexShader and FragmentShader classes.

These classes are almost never created explicitly but are created implicitly
from within a Program object.

Example
-------

  vert = "some code"
  frag = "some code"

  program = Program(vert,frag)
"""
from __future__ import division

import re
import os
from OpenGL import error

from ..util import is_string
from . import gl
from . import GLObject


# ------------------------------------------------------- class ShaderError ---
class ShaderError(RuntimeError):

    """ Shader error class """
    pass


# ------------------------------------------------------------ class Shader ---
class Shader(GLObject):

    """ Abstract shader class.
    """

    # Conversion of known uniform and attribute types to GL constants
    _gtypes = {
        'float': gl.GL_FLOAT,
        'vec2': gl.GL_FLOAT_VEC2,
        'vec3': gl.GL_FLOAT_VEC3,
        'vec4': gl.GL_FLOAT_VEC4,
        'int': gl.GL_INT,
        'ivec2': gl.GL_INT_VEC2,
        'ivec3': gl.GL_INT_VEC3,
        'ivec4': gl.GL_INT_VEC4,
        'bool': gl.GL_BOOL,
        'bvec2': gl.GL_BOOL_VEC2,
        'bvec3': gl.GL_BOOL_VEC3,
        'bvec4': gl.GL_BOOL_VEC4,
        'mat2': gl.GL_FLOAT_MAT2,
        'mat3': gl.GL_FLOAT_MAT3,
        'mat4': gl.GL_FLOAT_MAT4,
        'sampler2D': gl.GL_SAMPLER_2D,
        'sampler3D': gl.ext.GL_SAMPLER_3D,
        'samplerCube': gl.GL_SAMPLER_CUBE}

    def __init__(self, target, code=None):
        """
        Create the shader and store code.
        """

        GLObject.__init__(self)

        # Check and store target
        if target not in [gl.GL_VERTEX_SHADER, gl.GL_FRAGMENT_SHADER]:
            raise ValueError('Target must be vertex or fragment shader.')
        self._target = target

        # For auto-enabling point sprites
        self._need_enabled = set()

        # Set code
        self._code = None
        self._source = None
        if code is not None:
            self.set_code(code)

    def __repr__(self):
        return "<%s %d (%s)>" % (self.__class__.__name__,
                                 self._id, self._source)

    def set_code(self, code, source=None):
        """ Set the code for this shader.

        Parameters
        ----------
        code : str
            The GLSL source code, or a filename that contains the code.
        source : str
            A specifier where the code came from. If not given,
            "<string>" is used, or the filename where the code is loaded
            from. Optional.
        """

        if not is_string(code):
            raise TypeError('Code must be a string (%s)' % type(code))

        # Set code and source
        if os.path.isfile(code):
            with open(code, 'rb') as file:
                self._code = file.read().decode('utf-8')
                self._source = os.path.basename(code)
        else:
            self._code = code
            self._source = '<string>'

        # Set given source?
        if source is not None:
            if not is_string(source):
                raise TypeError('Source must be a string (%s)' % type(source))
            self._source = source

        # Set flags
        self._need_update = True

    @property
    def code(self):
        """ The GLSL code of this shader.
        """
        return self._code

    @property
    def source(self):
        """ The source of the code for this shader
        (as in where it came from, not the source code).
        """
        return self._source

    def _get_attributes(self):
        """
        Extract attributes (name and type) from code.
        """

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

    def _get_uniforms(self):
        """
        Extract uniforms (name and type) from code.
        """

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

    def _create(self):
        """
        Create the shader.
        """
        self._handle = gl.glCreateShader(self._target)

    def _delete(self):
        """
        Delete the shader.
        """

        gl.glDeleteShader(self._handle)

    def _update(self):
        """
        Compile the shader.
        """

        # Check if we have source code
        if not self._code:
            raise ShaderError('No source code given for shader.')

        # Set source
        # Note, some implementations cannot deal with a sequence of chars
        #gl.glShaderSource(self._handle, self._code)
        #gl.glShaderSource(self._handle, [self._code])

        # More compativle variant (also deals with above chars problem)
        self._need_enabled = gl.glShaderSource_compat(self._handle, self._code)

        # Compile the shader
        try:
            gl.glCompileShader(self._handle)
        except error.GLError as errors:
            errormsg = self._get_error(str(errors), 4)
            raise ShaderError("Error compiling %r:\n" % self + errormsg)

        # Check the compile status
        status = gl.glGetShaderiv(self._handle, gl.GL_COMPILE_STATUS)
        if not status:
            errors = gl.glGetShaderInfoLog(self._handle)
            errormsg = self._get_error(errors, 4)
            raise ShaderError("Error compiling %r:\n" % self + errormsg)

    def _parse_error(self, error):
        """Parse a GLSL error to extract the line number and description

        Parameters
        ----------
        error : str
            An error string as returned by the compilation process
        """

        # Nvidia
        # 0(7): error C1008: undefined variable "MV"
        match = re.match(r'(\d+)\((\d+)\)\s*:\s(.*)', error)
        if match:
            return int(match.group(2)), match.group(3)

        # ATI / Intel
        # ERROR: 0:131: '{' : syntax error parse error
        match = re.match(r'ERROR:\s(\d+):(\d+):\s(.*)', error)
        if match:
            return int(match.group(2)), match.group(3)

        # Nouveau
        # 0:28(16): error: syntax error, unexpected ')', expecting '('
        match = re.match(r'(\d+):(\d+)\((\d+)\):\s(.*)', error)
        if match:
            return int(match.group(2)), match.group(4)

        # Other ...
        return None, error

    def _get_error(self, errors, indentation=0):
        """Get error and show the faulty line + some context

        Parameters
        ----------
        error : str
            An error string as returned by the compilation process
        indentation : int
            Number of spaces to indent the found error.
        """
        # Init
        if not is_string(errors):
            errors = errors.decode('utf-8', 'replace')
        results = []
        lines = None
        if self._code:
            lines = [line.strip() for line in self._code.split('\n')]

        for error in errors.split('\n'):
            # Strip; skip empy lines
            error = error.strip()
            if not error:
                continue
            # Separate line number from description (if we can)
            linenr, error = self._parse_error(error)
            if None in (linenr, lines):
                results.append('%s' % error)
            else:
                results.append('on line %i: %s' % (linenr, error))
                if linenr > 0 and linenr < len(lines):
                    results.append('  %s' % lines[linenr - 1])

        # Add indentation and return
        results = [' ' * indentation + r for r in results]
        return '\n'.join(results)


# ------------------------------------------------------ class VertexShader ---
class VertexShader(Shader):

    """ Vertex shader class. Inherits :class:`shader.Shader`.

    Parameters
    ----------
    code : str
        The GLSL source code, or a filename that contains the code.

    """

    def __init__(self, code=None):
        """
        Create the shader.
        """

        Shader.__init__(self, gl.GL_VERTEX_SHADER, code)


# ---------------------------------------------------- class FragmentShader ---
class FragmentShader(Shader):

    """ Fragment shader class. Inherits :class:`shader.Shader`.

    Parameters
    ----------
    code : str
        The GLSL source code, or a filename that contains the code.

    """

    def __init__(self, code=None):
        """
        Create the shader.
        """

        Shader.__init__(self, gl.GL_FRAGMENT_SHADER, code)
