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
from .texture import GL_SAMPLER_3D


# ------------------------------------------------------------ Shader class ---
class Shader(GLObject):
    """ Abstract shader class
    
    Parameters
    ----------

    code: str
        code can be a filename or the actual code
    """

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
        'sampler3D':   GL_SAMPLER_3D,
    }

    def __init__(self, target, code=None):
        GLObject.__init__(self)
        if target not in [gl.GL_VERTEX_SHADER, gl.GL_FRAGMENT_SHADER]:
            raise ValueError("Shader target must be vertex or fragment")

        self._target = target
        self._code = None
        self._source = None
        self._need_compile = False
        self.__clean_code = None
        self._attributes = None
        self._uniforms = None
        if code is not None:
            self.code = code

    @property
    def code(self):
        """ Shader source code """
        return self._code

    @code.setter
    def code(self, code):
        """ Shader source code """
        if os.path.isfile(code):
            with open(code, 'rt') as file:
                self._code = file.read()
                self._source = os.path.basename(code)
        else:
            self._code = code
            self._source = '<string>'
        self._need_compile = True
        self.__clean_code = None
        self._attributes = None
        self._uniforms = None

    @property
    def source(self):
        """ Shader source (string or filename) """
        return self._source
    
    def _activate(self):
        # shaders do not need any kind of (de)activation
        # in the sense of glActiveSomething()
        
        # Recompile if necessary
        if self._need_compile:
            self._compile_shader()
            self._need_compile = False
    
    def _deactivate(self):
        pass  # shaders do not need any kind of (de)activation
    
    def _create(self):
        """ Create the shader object on the GPU """

        # Check if we have something to compile
        if not self._code:
            raise RuntimeError("No code has been given")

        # Create and check that shader object has been created
        self._handle = gl.glCreateShader(self._target)
        if self._handle <= 0:
            raise RuntimeError("Cannot create shader object")

    def _compile_shader(self):
        """ Compile the source and checks everything's ok """
        # Set shader source
        gl.glShaderSource(self._handle, self._code)

        logger.debug("GPU: Creating shader")

        # Actual compilation
        gl.glCompileShader(self._handle)
        status = gl.glGetShaderParameter(self._handle, gl.GL_COMPILE_STATUS)
        if not status:
            errors = gl.glGetShaderInfoLog(self._handle)
            errormsg = self._get_error(errors, 4)
            raise RuntimeError("Shader compilation error in %r:\n%s" % 
                               (self, errormsg))

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
        error = str(error)
        
        # Nvidia
        # 0(7): error C1008: undefined variable "MV"
        m = re.match(r'(\d+)\((\d+)\)\s*:\s(.*)', error)
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

    @property
    def uniforms(self):
        """ Shader uniforms obtained from source code """
        if self._uniforms is None:
            uniforms = []
            regex = re.compile("""\s*uniform\s+(?P<type>\w+)\s+"""
                               """(?P<name>\w+)\s*(\[(?P<size>\d+)\])?\s*;""",
                               flags=re.MULTILINE)
            for m in re.finditer(regex, self._clean_code):
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
            self._uniforms = uniforms
        return self._uniforms

    @property
    def attributes(self):
        """ Shader attributes obtained from source code """
        if self._attributes is None:
            attributes = []
            regex = re.compile("""\s*attribute\s+(?P<type>\w+)\s+"""
                               """(?P<name>\w+)\s*(\[(?P<size>\d+)\])?\s*;""",
                               flags=re.MULTILINE)
            for m in re.finditer(regex, self._clean_code):
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
            self._attributes = attributes
        return self._attributes

    @property
    def _clean_code(self):
        # Return code with comments stripped
        if self.__clean_code is None:
            self.__clean_code = re.sub(r'(.*)(//.*)', r'\1', self._code, re.M)
        return self.__clean_code


# ------------------------------------------------------ VertexShader class ---
class VertexShader(Shader):
    """ Vertex shader object
    
    Parameters
    ----------

    code: str
        code can be a filename or the actual code
    """

    def __init__(self, code=None):
        Shader.__init__(self, gl.GL_VERTEX_SHADER, code)

    def __repr__(self):
        return "Vertex Shader %d (%s)" % (self._id, self._source)


# ---------------------------------------------------- FragmentShader class ---
class FragmentShader(Shader):
    """ Fragment shader object
    
    Parameters
    ----------

    code: str
        code can be a filename or the actual code
    """

    def __init__(self, code=None):
        Shader.__init__(self, gl.GL_FRAGMENT_SHADER, code)

    def __repr__(self):
        return "Fragment Shader %d (%s)" % (self._id, self._source)
