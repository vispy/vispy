import sys
import numpy as np

if sys.version_info >= (3,):
    xrange = range


class MeshData(object):
    """
    Class for storing and operating on 3D mesh data.

    Parameters
    ----------
    vertexes : ndarray, shape (Nv, 3)
        Vertex coordinates. If faces is not specified, then this will
        instead be interpreted as (Nf, 3, 3) array of coordinates.
    faces : ndarray, shape (Nf, 3)
        Indexes into the vertex array.
    edges : None
        [not available yet]
    vertex_colors : ndarray, shape (Nv, 4)
        Vertex colors. If faces is not specified, this will be
        interpreted as (Nf, 3, 4) array of colors.
    face_colors : ndarray, shape (Nf, 4)
        Face colors.

    Notes
    -----
    All arguments are optional.

    The object may contain:

    - list of vertex locations
    - list of edges
    - list of triangles
    - colors per vertex, edge, or tri
    - normals per vertex or tri

    This class handles conversion between the standard
    [list of vertexes, list of faces] format (suitable for use with
    glDrawElements) and 'indexed' [list of vertexes] format (suitable
    for use with glDrawArrays). It will automatically compute face normal
    vectors as well as averaged vertex normal vectors.

    The class attempts to be as efficient as possible in caching conversion
    results and avoiding unnecessary conversions.
    """

    def __init__(self, vertexes=None, faces=None, edges=None,
                 vertex_colors=None, face_colors=None):
        self._vertexes = None  # (Nv,3) array of vertex coordinates
        self._vertexes_indexed_by_faces = None  # (Nf, 3, 3) vertex coordinates
        self._vertexes_indexed_by_edges = None  # (Ne, 2, 3) vertex coordinates

        ## mappings between vertexes, faces, and edges
        self._faces = None  # Nx3 indexes into self._vertexes, 3 verts/face
        self._edges = None  # Nx2 indexes into self._vertexes, 2 verts/edge
        # inverse mappings
        self._vertex_faces = None  # maps vertex ID to a list of face IDs
        self._vertex_edges = None  # maps vertex ID to a list of edge IDs

        ## Per-vertex data
        self._vertex_normals = None                # (Nv, 3) normals
        self._vertex_normals_indexed_by_faces = None  # (Nf, 3, 3) normals
        self._vertex_colors = None                 # (Nv, 3) colors
        self._vertex_colors_indexed_by_faces = None   # (Nf, 3, 4) colors
        self._vertex_colors_indexed_by_edges = None   # (Nf, 2, 4) colors

        ## Per-face data
        self._face_normals = None                # (Nf, 3) face normals
        self._face_normals_indexed_by_faces = None  # (Nf, 3, 3) face normals
        self._face_colors = None                 # (Nf, 4) face colors
        self._face_colors_indexed_by_faces = None   # (Nf, 3, 4) face colors
        self._face_colors_indexed_by_edges = None   # (Ne, 2, 4) face colors

        ## Per-edge data
        self._edge_colors = None                # (Ne, 4) edge colors
        self._edge_colors_indexed_by_edges = None  # (Ne, 2, 4) edge colors
        # default color to use if no face/edge/vertex colors are given
        #self._meshColor = (1, 1, 1, 0.1)

        if vertexes is not None:
            if faces is None:
                self.setVertexes(vertexes, indexed='faces')
                if vertex_colors is not None:
                    self.setVertexColors(vertex_colors, indexed='faces')
                if face_colors is not None:
                    self.setFaceColors(face_colors, indexed='faces')
            else:
                self.setVertexes(vertexes)
                self.setFaces(faces)
                if vertex_colors is not None:
                    self.setVertexColors(vertex_colors)
                if face_colors is not None:
                    self.setFaceColors(face_colors)

    def faces(self):
        """Array (Nf, 3) of vertex indices, three per triangular face.

        If faces have not been computed for this mesh, returns None.
        """
        return self._faces

    def edges(self):
        """Array (Nf, 3) of vertex indexes, two per edge in the mesh."""
        if self._edges is None:
            self._computeEdges()
        return self._edges

    def setFaces(self, faces):
        """Set the (Nf, 3) array of faces. Each rown in the array contains
        three indexes into the vertex array, specifying the three corners
        of a triangular face."""
        self._faces = faces
        self._edges = None
        self._vertex_faces = None
        self._vertexes_indexed_by_faces = None
        self.resetNormals()
        self._vertex_colors_indexed_by_faces = None
        self._face_colors_indexed_by_faces = None

    def vertexes(self, indexed=None):
        """Return an array (N,3) of the positions of vertexes in the mesh.
        By default, each unique vertex appears only once in the array.
        If indexed is 'faces', then the array will instead contain three
        vertexes per face in the mesh (and a single vertex may appear more
        than once in the array)."""
        if indexed is None:
            if (self._vertexes is None and
                    self._vertexes_indexed_by_faces is not None):
                self._computeUnindexedVertexes()
            return self._vertexes
        elif indexed == 'faces':
            if (self._vertexes_indexed_by_faces is None and
                    self._vertexes is not None):
                self._vertexes_indexed_by_faces = self._vertexes[self.faces()]
            return self._vertexes_indexed_by_faces
        else:
            raise Exception("Invalid indexing mode. Accepts: None, 'faces'")

    def setVertexes(self, verts=None, indexed=None, resetNormals=True):
        """
        Set the array (Nv, 3) of vertex coordinates.
        If indexed=='faces', then the data must have shape (Nf, 3, 3) and is
        assumed to be already indexed as a list of faces.
        This will cause any pre-existing normal vectors to be cleared
        unless resetNormals=False.
        """
        if indexed is None:
            if verts is not None:
                self._vertexes = verts
            self._vertexes_indexed_by_faces = None
        elif indexed == 'faces':
            self._vertexes = None
            if verts is not None:
                self._vertexes_indexed_by_faces = verts
        else:
            raise Exception("Invalid indexing mode. Accepts: None, 'faces'")

        if resetNormals:
            self.resetNormals()

    def resetNormals(self):
        self._vertex_normals = None
        self._vertex_normals_indexed_by_faces = None
        self._face_normals = None
        self._face_normals_indexed_by_faces = None

    def hasFaceIndexedData(self):
        """Return True if this object already has vertex positions indexed
        by face"""
        return self._vertexes_indexed_by_faces is not None

    def hasEdgeIndexedData(self):
        return self._vertexes_indexed_by_edges is not None

    def hasVertexColor(self):
        """Return True if this data set has vertex color information"""
        for v in (self._vertex_colors, self._vertex_colors_indexed_by_faces,
                  self._vertex_colors_indexed_by_edges):
            if v is not None:
                return True
        return False

    def hasFaceColor(self):
        """Return True if this data set has face color information"""
        for v in (self._face_colors, self._face_colors_indexed_by_faces,
                  self._face_colors_indexed_by_edges):
            if v is not None:
                return True
        return False

    def faceNormals(self, indexed=None):
        """
        Return an array (Nf, 3) of normal vectors for each face.
        If indexed='faces', then instead return an indexed array
        (Nf, 3, 3)  (this is just the same array with each vector
        copied three times).
        """
        if self._face_normals is None:
            v = self.vertexes(indexed='faces')
            self._face_normals = np.cross(v[:, 1] - v[:, 0],
                                          v[:, 2] - v[:, 0])

        if indexed is None:
            return self._face_normals
        elif indexed == 'faces':
            if self._face_normals_indexed_by_faces is None:
                norms = np.empty((self._face_normals.shape[0], 3, 3),
                                 dtype=np.float32)
                norms[:] = self._face_normals[:, np.newaxis, :]
                self._face_normals_indexed_by_faces = norms
            return self._face_normals_indexed_by_faces
        else:
            raise Exception("Invalid indexing mode. Accepts: None, 'faces'")

    def vertexNormals(self, indexed=None):
        """
        Return an array of normal vectors.
        By default, the array will be (N, 3) with one entry per unique
        vertex in the mesh. If indexed is 'faces', then the array will
        contain three normal vectors per face (and some vertexes may be
        repeated).
        """
        if self._vertex_normals is None:
            faceNorms = self.faceNormals()
            vertFaces = self.vertexFaces()
            self._vertex_normals = np.empty(self._vertexes.shape,
                                            dtype=np.float32)
            for vindex in xrange(self._vertexes.shape[0]):
                faces = vertFaces[vindex]
                if len(faces) == 0:
                    self._vertex_normals[vindex] = (0, 0, 0)
                    continue
                norms = faceNorms[faces]  # get all face normals
                norm = norms.sum(axis=0)  # sum normals
                norm /= (norm**2).sum()**0.5  # and re-normalize
                self._vertex_normals[vindex] = norm

        if indexed is None:
            return self._vertex_normals
        elif indexed == 'faces':
            return self._vertex_normals[self.faces()]
        else:
            raise Exception("Invalid indexing mode. Accepts: None, 'faces'")

    def vertex_colors(self, indexed=None):
        """
        Return an array (Nv, 4) of vertex colors.
        If indexed=='faces', then instead return an indexed array
        (Nf, 3, 4).
        """
        if indexed is None:
            return self._vertex_colors
        elif indexed == 'faces':
            if self._vertex_colors_indexed_by_faces is None:
                self._vertex_colors_indexed_by_faces = \
                    self._vertex_colors[self.faces()]
            return self._vertex_colors_indexed_by_faces
        else:
            raise Exception("Invalid indexing mode. Accepts: None, 'faces'")

    def setVertexColors(self, colors, indexed=None):
        """
        Set the vertex color array (Nv, 4).
        If indexed=='faces', then the array will be interpreted
        as indexed and should have shape (Nf, 3, 4)
        """
        if indexed is None:
            self._vertex_colors = colors
            self._vertex_colors_indexed_by_faces = None
        elif indexed == 'faces':
            self._vertex_colors = None
            self._vertex_colors_indexed_by_faces = colors
        else:
            raise Exception("Invalid indexing mode. Accepts: None, 'faces'")

    def face_colors(self, indexed=None):
        """
        Return an array (Nf, 4) of face colors.
        If indexed=='faces', then instead return an indexed array
        (Nf, 3, 4)  (note this is just the same array with each color
        repeated three times).
        """
        if indexed is None:
            return self._face_colors
        elif indexed == 'faces':
            if (self._face_colors_indexed_by_faces is None and
                    self._face_colors is not None):
                Nf = self._face_colors.shape[0]
                self._face_colors_indexed_by_faces = \
                    np.empty((Nf, 3, 4), dtype=self._face_colors.dtype)
                self._face_colors_indexed_by_faces[:] = \
                    self._face_colors.reshape(Nf, 1, 4)
            return self._face_colors_indexed_by_faces
        else:
            raise Exception("Invalid indexing mode. Accepts: None, 'faces'")

    def setFaceColors(self, colors, indexed=None):
        """
        Set the face color array (Nf, 4).
        If indexed=='faces', then the array will be interpreted
        as indexed and should have shape (Nf, 3, 4)
        """
        if indexed is None:
            self._face_colors = colors
            self._face_colors_indexed_by_faces = None
        elif indexed == 'faces':
            self._face_colors = None
            self._face_colors_indexed_by_faces = colors
        else:
            raise Exception("Invalid indexing mode. Accepts: None, 'faces'")

    def faceCount(self):
        """
        Return the number of faces in the mesh.
        """
        if self._faces is not None:
            return self._faces.shape[0]
        elif self._vertexes_indexed_by_faces is not None:
            return self._vertexes_indexed_by_faces.shape[0]

    def edgeColors(self):
        return self._edge_colors

    #def _setIndexedFaces(self, faces, vertex_colors=None, face_colors=None):
        #self._vertexes_indexed_by_faces = faces
        #self._vertex_colors_indexed_by_faces = vertex_colors
        #self._face_colors_indexed_by_faces = face_colors

    def _computeUnindexedVertexes(self):
        ## Given (Nv, 3, 3) array of vertexes-indexed-by-face, convert
        ## backward to unindexed vertexes
        ## This is done by collapsing into a list of 'unique' vertexes
        ## (difference < 1e-14)

        ## I think generally this should be discouraged..
        faces = self._vertexes_indexed_by_faces
        verts = {}  # used to remember the index of each vertex position
        self._faces = np.empty(faces.shape[:2], dtype=np.uint)
        self._vertexes = []
        self._vertex_faces = []
        self._face_normals = None
        self._vertex_normals = None
        for i in xrange(faces.shape[0]):
            face = faces[i]
            for j in range(face.shape[0]):
                pt = face[j]
                # quantize to ensure nearly-identical points will be merged
                pt2 = tuple([round(x*1e14) for x in pt])
                index = verts.get(pt2, None)
                if index is None:
                    #self._vertexes.append(QtGui.QVector3D(*pt))
                    self._vertexes.append(pt)
                    self._vertex_faces.append([])
                    index = len(self._vertexes)-1
                    verts[pt2] = index
                # track which vertexes belong to which faces
                self._vertex_faces[index].append(i)
                self._faces[i, j] = index
        self._vertexes = np.array(self._vertexes, dtype=np.float32)

    #def _setUnindexedFaces(self, faces, vertexes, vertex_colors=None,
        #                   face_colors=None):
        #self._vertexes = vertexes #[QtGui.QVector3D(*v) for v in vertexes]
        #self._faces = faces.astype(np.uint)
        #self._edges = None
        #self._vertex_faces = None
        #self._face_normals = None
        #self._vertex_normals = None
        #self._vertex_colors = vertex_colors
        #self._face_colors = face_colors

    def vertexFaces(self):
        """
        List mapping each vertex index to a list of face indices that use it.
        """
        if self._vertex_faces is None:
            self._vertex_faces = [[] for i in xrange(len(self.vertexes()))]
            for i in xrange(self._faces.shape[0]):
                face = self._faces[i]
                for ind in face:
                    self._vertex_faces[ind].append(i)
        return self._vertex_faces

    #def reverseNormals(self):
        #"""
        #Reverses the direction of all normal vectors.
        #"""
        #pass

    #def generateEdgesFromFaces(self):
        #"""
        #Generate a set of edges by listing all the edges of faces and
        #removing any duplicates.
        #Useful for displaying wireframe meshes.
        #"""
        #pass

    def _computeEdges(self):
        if not self.hasFaceIndexedData:
            ## generate self._edges from self._faces
            nf = len(self._faces)
            edges = np.empty(nf*3, dtype=[('i', np.uint, 2)])
            edges['i'][0:nf] = self._faces[:, :2]
            edges['i'][nf:2*nf] = self._faces[:, 1:3]
            edges['i'][-nf:, 0] = self._faces[:, 2]
            edges['i'][-nf:, 1] = self._faces[:, 0]

            # sort per-edge
            mask = edges['i'][:, 0] > edges['i'][:, 1]
            edges['i'][mask] = edges['i'][mask][:, ::-1]

            # remove duplicate entries
            self._edges = np.unique(edges)['i']
            #print self._edges
        elif self._vertexes_indexed_by_faces is not None:
            verts = self._vertexes_indexed_by_faces
            edges = np.empty((verts.shape[0], 3, 2), dtype=np.uint)
            nf = verts.shape[0]
            edges[:, 0, 0] = np.arange(nf) * 3
            edges[:, 0, 1] = edges[:, 0, 0] + 1
            edges[:, 1, 0] = edges[:, 0, 1]
            edges[:, 1, 1] = edges[:, 1, 0] + 1
            edges[:, 2, 0] = edges[:, 1, 1]
            edges[:, 2, 1] = edges[:, 0, 0]
            self._edges = edges
        else:
            raise Exception("MeshData cannot generate edges--no faces in "
                            "this data.")

    def save(self):
        """Serialize this mesh to a string appropriate for disk storage"""
        import pickle
        if self._faces is not None:
            names = ['_vertexes', '_faces']
        else:
            names = ['_vertexes_indexed_by_faces']

        if self._vertex_colors is not None:
            names.append('_vertex_colors')
        elif self._vertex_colors_indexed_by_faces is not None:
            names.append('_vertex_colors_indexed_by_faces')

        if self._face_colors is not None:
            names.append('_face_colors')
        elif self._face_colors_indexed_by_faces is not None:
            names.append('_face_colors_indexed_by_faces')

        state = dict([(n, getattr(self, n)) for n in names])
        return pickle.dumps(state)

    def restore(self, state):
        """Restore the state of a mesh previously saved using save()"""
        import pickle
        state = pickle.loads(state)
        for k in state:
            if isinstance(state[k], list):
                #if isinstance(state[k][0], QtGui.QVector3D):
                #    state[k] = [[v.x(), v.y(), v.z()] for v in state[k]]
                state[k] = np.array(state[k])
            setattr(self, k, state[k])


def sphere(rows, cols, radius=1.0, offset=True):
    """
    Return a MeshData instance with vertexes and faces computed
    for a spherical surface.
    """
    verts = np.empty((rows+1, cols, 3), dtype=np.float32)

    ## compute vertexes
    phi = (np.arange(rows+1) * np.pi / rows).reshape(rows+1, 1)
    s = radius * np.sin(phi)
    verts[..., 2] = radius * np.cos(phi)
    th = ((np.arange(cols) * 2 * np.pi / cols).reshape(1, cols))
    if offset:
        # rotate each row by 1/2 column
        th = th + ((np.pi / cols) * np.arange(rows+1).reshape(rows+1, 1))
    verts[..., 0] = s * np.cos(th)
    verts[..., 1] = s * np.sin(th)
    ## remove redundant vertexes from top and bottom
    verts = verts.reshape((rows+1)*cols, 3)[cols-1:-(cols-1)]

    ## compute faces
    faces = np.empty((rows*cols*2, 3), dtype=np.uint32)
    rowtemplate1 = (((np.arange(cols).reshape(cols, 1) +
                      np.array([[1, 0, 0]])) % cols)
                    + np.array([[0, 0, cols]]))
    rowtemplate2 = (((np.arange(cols).reshape(cols, 1) +
                      np.array([[1, 0, 1]])) % cols)
                    + np.array([[0, cols, cols]]))
    for row in range(rows):
        start = row * cols * 2
        faces[start:start+cols] = rowtemplate1 + row * cols
        faces[start+cols:start+(cols*2)] = rowtemplate2 + row * cols
    ## cut off zero-area triangles at top and bottom
    faces = faces[cols:-cols]

    ## adjust for redundant vertexes that were removed from top and bottom
    vmin = cols-1
    faces[faces < vmin] = vmin
    faces -= vmin
    vmax = verts.shape[0]-1
    faces[faces > vmax] = vmax
    return MeshData(vertexes=verts, faces=faces)


def cylinder(rows, cols, radius=[1.0, 1.0], length=1.0, offset=False):
    """
    Return a MeshData instance with vertexes and faces computed
    for a cylindrical surface.
    The cylinder may be tapered with different radii at each end
    (truncated cone)
    """
    verts = np.empty((rows+1, cols, 3), dtype=np.float32)
    if isinstance(radius, int):
        radius = [radius, radius]  # convert to list
    ## compute vertexes
    th = np.linspace(2 * np.pi, 0, cols).reshape(1, cols)
    # radius as a function of z
    r = np.linspace(radius[0], radius[1], num=rows+1,
                    endpoint=True).reshape(rows+1, 1)
    verts[..., 2] = np.linspace(0, length, num=rows+1,
                                endpoint=True).reshape(rows+1, 1)  # z
    if offset:
        ## rotate each row by 1/2 column
        th = th + ((np.pi / cols) * np.arange(rows+1).reshape(rows+1, 1))
    verts[..., 0] = r * np.cos(th)  # x = r cos(th)
    verts[..., 1] = r * np.sin(th)  # y = r sin(th)
    # just reshape: no redundant vertices...
    verts = verts.reshape((rows+1)*cols, 3)
    ## compute faces
    faces = np.empty((rows*cols*2, 3), dtype=np.uint)
    rowtemplate1 = (((np.arange(cols).reshape(cols, 1) +
                      np.array([[0, 1, 0]])) % cols)
                    + np.array([[0, 0, cols]]))
    rowtemplate2 = (((np.arange(cols).reshape(cols, 1) +
                      np.array([[0, 1, 1]])) % cols)
                    + np.array([[cols, 0, cols]]))
    for row in range(rows):
        start = row * cols * 2
        faces[start:start+cols] = rowtemplate1 + row * cols
        faces[start+cols:start+(cols*2)] = rowtemplate2 + row * cols

    return MeshData(vertexes=verts, faces=faces)
