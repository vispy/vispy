# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# This module was taken from visvis
"""This module produces functionality to read and write wavefront (.OBJ) files.

See `wikipedia <http://en.wikipedia.org/wiki/Wavefront_.obj_file>`_ for more details.

The wavefront format is quite powerful and allows a wide variety of surfaces
to be described.

This implementation does only supports mesh stuff, so no nurbs etc. Further,
material properties are ignored, although this might be implemented later,

The classes are written with compatibility of Python3 in mind.

"""

import numpy as np
import time
from gzip import GzipFile
from os import path as op

from ..geometry import _calculate_normals
from ..util import logger


class WavefrontReader(object):

    def __init__(self, f):
        self._f = f

        # Original vertices, normals and texture coords.
        # These are not necessarily of the same length.
        self._v = []
        self._vn = []
        self._vt = []

        # Final vertices, normals and texture coords.
        # All three lists are of the same length, as opengl wants it.
        self._vertices = []
        self._normals = []
        self._texcords = []

        # The faces, indices to vertex/normal/texcords arrays.
        self._faces = []

        # Dictionary to keep track of processed face data, so we can
        # convert the original v/vn/vn to the final vertices/normals/texcords.
        self._facemap = {}

    @classmethod
    def read(cls, fname):
        """Entry point for reading OBJ files.

        Parameters
        ----------
        fname : str
            The name of the file to read.

        """
        # Open file
        fmt = op.splitext(fname)[1].lower()
        assert fmt in ('.obj', '.gz')
        opener = open if fmt == '.obj' else GzipFile
        with opener(fname, 'rb') as f:
            try:
                reader = WavefrontReader(f)
                while True:
                    reader.readLine()
            except EOFError:
                pass

        # Done
        t0 = time.time()
        mesh = reader.finish()
        logger.debug('reading mesh took ' +
                     str(time.time() - t0) +
                     ' seconds')
        return mesh

    def readLine(self):
        """The method that reads a line and processes it."""
        # Read line
        line = self._f.readline().decode('ascii', 'ignore')
        if not line:
            raise EOFError()
        line = line.strip()

        if line.startswith('v '):
            # self._vertices.append( *self.readTuple(line) )
            self._v.append(self.readTuple(line))
        elif line.startswith('vt '):
            self._vt.append(self.readTuple(line, 3))
        elif line.startswith('vn '):
            self._vn.append(self.readTuple(line))
        elif line.startswith('f '):
            self._faces.append(self.readFace(line))
        elif line.startswith('#'):
            pass  # Comment
        elif line.startswith('mtllib '):
            logger.warning('Notice reading .OBJ: material properties are '
                           'ignored.')
        elif any(line.startswith(x) for x in ('g ', 's ', 'o ', 'usemtl ')):
            pass  # Ignore groups and smoothing groups, obj names, material
        elif not line.strip():
            pass
        else:
            logger.warning('Notice reading .OBJ: ignoring %s command.'
                           % line.strip())

    def readTuple(self, line, n=3):
        """Reads a tuple of numbers. e.g. vertices, normals or teture coords."""
        numbers = [num for num in line.split(' ') if num]
        return [float(num) for num in numbers[1:n + 1]]

    def readFace(self, line):
        """Each face consists of three or more sets of indices. Each set
        consists of 1, 2 or 3 indices to vertices/normals/texcords.
        """
        # Get parts (skip first)
        indexSets = [num for num in line.split(' ') if num][1:]

        final_face = []
        for indexSet in indexSets:

            # Did we see this exact index earlier? If so, it's easy
            final_index = self._facemap.get(indexSet)
            if final_index is not None:
                final_face.append(final_index)
                continue

            # If not, we need to sync the vertices/normals/texcords ...

            # Get and store final index
            final_index = len(self._vertices)
            final_face.append(final_index)
            self._facemap[indexSet] = final_index

            # What indices were given?
            indices = [i for i in indexSet.split('/')]

            # Store new set of vertex/normal/texcords.
            # If there is a single face that does not specify the texcord
            # index, the texcords are ignored. Likewise for the normals.
            if True:
                vertex_index = self._absint(indices[0], len(self._v))
                self._vertices.append(self._v[vertex_index])
            if self._texcords is not None:
                if len(indices) > 1 and indices[1]:
                    texcord_index = self._absint(indices[1], len(self._vt))
                    self._texcords.append(self._vt[texcord_index])
                else:
                    if self._texcords:
                        logger.warning('Ignoring texture coordinates because '
                                       'it is not specified for all faces.')
                    self._texcords = None
            if self._normals is not None:
                if len(indices) > 2 and indices[2]:
                    normal_index = self._absint(indices[2], len(self._vn))
                    self._normals.append(self._vn[normal_index])
                else:
                    if self._normals:
                        logger.warning('Ignoring normals because it is not '
                                       'specified for all faces.')
                    self._normals = None

        # Check face
        if self._faces and len(self._faces[0]) != len(final_face):
            raise RuntimeError(
                'Vispy requires that all faces are either triangles or quads.')

        # Done
        return final_face

    def _absint(self, i, ref):
        i = int(i)
        if i > 0:
            return i - 1
        else:
            return ref + i

    def _calculate_normals(self):
        vertices, faces = self._vertices, self._faces
        if faces is None:
            # ensure it's always 2D so we can use our methods
            faces = np.arange(0, vertices.size, dtype=np.uint32)[:, np.newaxis]
        normals = _calculate_normals(vertices, faces)
        return normals

    def finish(self):
        """Converts gathere lists to numpy arrays and creates
        BaseMesh instance.
        """
        self._vertices = np.array(self._vertices, 'float32')
        if self._faces:
            self._faces = np.array(self._faces, 'uint32')
        else:
            # Use vertices only
            self._vertices = np.array(self._v, 'float32')
            self._faces = None
        if self._normals:
            self._normals = np.array(self._normals, 'float32')
        else:
            self._normals = self._calculate_normals()
        if self._texcords:
            self._texcords = np.array(self._texcords, 'float32')
        else:
            self._texcords = None

        return self._vertices, self._faces, self._normals, self._texcords


class WavefrontWriter(object):

    def __init__(self, f):
        self._f = f

    @classmethod
    def write(cls, fname, vertices, faces, normals,
              texcoords, name='', reshape_faces=True):
        """This classmethod is the entry point for writing mesh data to OBJ.

        Parameters
        ----------
        fname : string
            The filename to write to. Must end with ".obj" or ".gz".
        vertices : numpy array
            The vertex data
        faces : numpy array
            The face data
        texcoords : numpy array
            The texture coordinate per vertex
        name : str
            The name of the object (e.g. 'teapot')
        reshape_faces : bool
            Reshape the `faces` array to (Nf, 3). Set to `False`
            if you need to write a mesh with non triangular faces.
        """
        # Open file
        fmt = op.splitext(fname)[1].lower()
        if fmt not in ('.obj', '.gz'):
            raise ValueError('Filename must end with .obj or .gz, not "%s"'
                             % (fmt,))
        opener = open if fmt == '.obj' else GzipFile
        f = opener(fname, 'wb')
        try:
            writer = WavefrontWriter(f)
            writer.writeMesh(vertices, faces, normals,
                             texcoords, name, reshape_faces=reshape_faces)
        except EOFError:
            pass
        finally:
            f.close()

    def writeLine(self, text):
        """Simple writeLine function to write a line of code to the file.
        The encoding is done here, and a newline character is added.
        """
        text += '\n'
        self._f.write(text.encode('ascii'))

    def writeTuple(self, val, what):
        """Writes a tuple of numbers (on one line)."""
        # Limit to three values. so RGBA data drops the alpha channel
        # Format can handle up to 3 texcords
        val = val[:3]
        # Make string
        val = ' '.join([str(v) for v in val])
        # Write line
        self.writeLine('%s %s' % (what, val))

    def writeFace(self, val, what='f'):
        """Write the face info to the net line."""
        # OBJ counts from 1
        val = [v + 1 for v in val]
        # Make string
        if self._hasValues and self._hasNormals:
            val = ' '.join(['%i/%i/%i' % (v, v, v) for v in val])
        elif self._hasNormals:
            val = ' '.join(['%i//%i' % (v, v) for v in val])
        elif self._hasValues:
            val = ' '.join(['%i/%i' % (v, v) for v in val])
        else:
            val = ' '.join(['%i' % v for v in val])
        # Write line
        self.writeLine('%s %s' % (what, val))

    def writeMesh(self, vertices, faces, normals, values,
                  name='', reshape_faces=True):
        """Write the given mesh instance."""
        # Store properties
        self._hasNormals = normals is not None
        self._hasValues = values is not None
        self._hasFaces = faces is not None

        # Get faces and number of vertices
        if faces is None:
            faces = np.arange(len(vertices))
            reshape_faces = True

        if reshape_faces:
            Nfaces = faces.size // 3
            faces = faces.reshape((Nfaces, 3))
        else:
            is_triangular = np.array([len(f) == 3
                                      for f in faces])
            if not(np.all(is_triangular)):
                logger.warning('''Faces doesn't appear to be triangular,
                be advised the file cannot be read back in vispy''')
        # Number of vertices
        N = vertices.shape[0]

        # Get string with stats
        stats = []
        stats.append('%i vertices' % N)
        if self._hasValues:
            stats.append('%i texcords' % N)
        else:
            stats.append('no texcords')
        if self._hasNormals:
            stats.append('%i normals' % N)
        else:
            stats.append('no normals')
        stats.append('%i faces' % faces.shape[0])

        # Write header
        self.writeLine('# Wavefront OBJ file')
        self.writeLine('# Created by vispy.')
        self.writeLine('#')
        if name:
            self.writeLine('# object %s' % name)
        else:
            self.writeLine('# unnamed object')
        self.writeLine('# %s' % ', '.join(stats))
        self.writeLine('')

        # Write data
        if True:
            for i in range(N):
                self.writeTuple(vertices[i], 'v')
        if self._hasNormals:
            for i in range(N):
                self.writeTuple(normals[i], 'vn')
        if self._hasValues:
            for i in range(N):
                self.writeTuple(values[i], 'vt')
        if True:
            for i in range(faces.shape[0]):
                self.writeFace(faces[i])
