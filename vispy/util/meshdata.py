import sys
import numpy as np

if sys.version_info >= (3,):
    xrange = range


class MeshData(object):
    """
    Class for storing and operating on 3D mesh data.

    Parameters
    ----------
    vertices : ndarray, shape (Nv, 3)
        Vertex coordinates. If faces is not specified, then this will
        instead be interpreted as (Nf, 3, 3) array of coordinates.
    faces : ndarray, shape (Nf, 3)
        Indices into the vertex array.
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
    [list of vertices, list of faces] format (suitable for use with
    glDrawElements) and 'indexed' [list of vertices] format (suitable
    for use with glDrawArrays). It will automatically compute face normal
    vectors as well as averaged vertex normal vectors.

    The class attempts to be as efficient as possible in caching conversion
    results and avoiding unnecessary conversions.
    """

    def __init__(self, vertices=None, faces=None, edges=None,
                 vertex_colors=None, face_colors=None):
        self._vertices = None  # (Nv,3) array of vertex coordinates
        self._vertices_indexed_by_faces = None  # (Nf, 3, 3) vertex coordinates
        self._vertices_indexed_by_edges = None  # (Ne, 2, 3) vertex coordinates

        ## mappings between vertices, faces, and edges
        self._faces = None  # Nx3 indices into self._vertices, 3 verts/face
        self._faces_indexed_by_faces = None  # (Nf, 3, 2) indices
        # into self._vertices
        self._edges = None  # Nx2 indices into self._vertices, 2 verts/edge
        self._edges_indexed_by_faces = None  # (Ne, 3, 2) indoces into 
        # self._vertices, 3 edge / face and 2 verts/edge
        
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

        if vertices is not None:
            if faces is None:
                self.set_vertices(vertices, indexed='faces')
                if vertex_colors is not None:
                    self.set_vertex_colors(vertex_colors, indexed='faces')
                if face_colors is not None:
                    self.set_face_colors(face_colors, indexed='faces')
            else:
                self.set_vertices(vertices)
                self.set_faces(faces)
                if vertex_colors is not None:
                    self.set_vertex_colors(vertex_colors)
                if face_colors is not None:
                    self.set_face_colors(face_colors)

    def faces(self, indexed=None):
        """Array (Nf, 3) of vertex indices, three per triangular face.
           "If indexed is 'faces', then return (Nf, 3, 2)
           array of vertex indices with 3 edges per face,
           and two vertices per edge.

        If faces have not been computed for this mesh, returns None.
        """
        if indexed is None:
            return self._faces
        elif indexed == 'faces':
            return self._faces_indexed_by_faces
        else:
            raise Exception("Invalid indexing mode. Accepts: None, 'faces'")

    def edges(self, indexed=None):
        """Array (Nf, 3) of vertex indices, two per edge in the mesh.
           If indexed is 'faces', then return (Nf, 3, 2) array of vertex
           indices with 3 edges per face, and two vertices per edge."""
        if indexed is None:
            if self._edges is None:
                self._compute_edges(indexed=None)
            return self._edges
        elif indexed == 'faces':
            if self._edges is None:
                self._compute_edges(indexed='faces')
            return self._edges_indexed_by_faces
        else:
            raise Exception("Invalid indexing mode. Accepts: None, 'faces'")

    def set_faces(self, faces):
        """Set the (Nf, 3) array of faces. Each rown in the array contains
        three indices into the vertex array, specifying the three corners
        of a triangular face."""
        self._faces = faces
        self._edges = None
        self._edges_indexed_by_faces = None
        self._faces_indexed_by_faces = None
        self._vertex_faces = None
        self._vertices_indexed_by_faces = None
        self.reset_normals()
        self._vertex_colors_indexed_by_faces = None
        self._face_colors_indexed_by_faces = None

    def vertices(self, indexed=None):
        """Return an array (N,3) of the positions of vertices in the mesh.
        By default, each unique vertex appears only once in the array.
        If indexed is 'faces', then the array will instead contain three
        vertices per face in the mesh (and a single vertex may appear more
        than once in the array)."""
        if indexed is None:
            if (self._vertices is None and
                    self._vertices_indexed_by_faces is not None):
                self._compute_unindexed_vertices()
            return self._vertices
        elif indexed == 'faces':
            if (self._vertices_indexed_by_faces is None and
                    self._vertices is not None):
                self._vertices_indexed_by_faces = self._vertices[self.faces()]
            return self._vertices_indexed_by_faces
        else:
            raise Exception("Invalid indexing mode. Accepts: None, 'faces'")

    def set_vertices(self, verts=None, indexed=None, reset_normals=True):
        """
        Set the array (Nv, 3) of vertex coordinates.
        If indexed=='faces', then the data must have shape (Nf, 3, 3) and is
        assumed to be already indexed as a list of faces.
        This will cause any pre-existing normal vectors to be cleared
        unless reset_normals=False.
        """
        if indexed is None:
            if verts is not None:
                self._vertices = verts
            self._vertices_indexed_by_faces = None
        elif indexed == 'faces':
            self._vertices = None
            if verts is not None:
                self._vertices_indexed_by_faces = verts
        else:
            raise Exception("Invalid indexing mode. Accepts: None, 'faces'")

        if reset_normals:
            self.reset_normals()

    def reset_normals(self):
        self._vertex_normals = None
        self._vertex_normals_indexed_by_faces = None
        self._face_normals = None
        self._face_normals_indexed_by_faces = None

    def has_face_indexed_data(self):
        """Return True if this object already has vertex positions indexed
        by face"""
        return self._vertices_indexed_by_faces is not None

    def has_edge_indexed_data(self):
        return self._vertices_indexed_by_edges is not None

    def has_vertex_color(self):
        """Return True if this data set has vertex color information"""
        for v in (self._vertex_colors, self._vertex_colors_indexed_by_faces,
                  self._vertex_colors_indexed_by_edges):
            if v is not None:
                return True
        return False

    def has_face_color(self):
        """Return True if this data set has face color information"""
        for v in (self._face_colors, self._face_colors_indexed_by_faces,
                  self._face_colors_indexed_by_edges):
            if v is not None:
                return True
        return False

    def face_normals(self, indexed=None):
        """
        Return an array (Nf, 3) of normal vectors for each face.
        If indexed='faces', then instead return an indexed array
        (Nf, 3, 3)  (this is just the same array with each vector
        copied three times).
        """
        if self._face_normals is None:
            v = self.vertices(indexed='faces')
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

    def vertex_normals(self, indexed=None):
        """
        Return an array of normal vectors.
        By default, the array will be (N, 3) with one entry per unique
        vertex in the mesh. If indexed is 'faces', then the array will
        contain three normal vectors per face (and some vertices may be
        repeated).
        """
        if self._vertex_normals is None:
            faceNorms = self.face_normals()
            vertFaces = self.vertex_faces()
            self._vertex_normals = np.empty(self._vertices.shape,
                                            dtype=np.float32)
            for vindex in xrange(self._vertices.shape[0]):
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

    def set_vertex_colors(self, colors, indexed=None):
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

    def set_face_colors(self, colors, indexed=None):
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

    def face_count(self):
        """
        Return the number of faces in the mesh.
        """
        if self._faces is not None:
            return self._faces.shape[0]
        elif self._vertices_indexed_by_faces is not None:
            return self._vertices_indexed_by_faces.shape[0]

    def edge_colors(self):
        return self._edge_colors

    #def _set_indexed_faces(self, faces, vertex_colors=None, face_colors=None):
        #self._vertices_indexed_by_faces = faces
        #self._vertex_colors_indexed_by_faces = vertex_colors
        #self._face_colors_indexed_by_faces = face_colors

    def _compute_unindexed_vertices(self):
        ## Given (Nv, 3, 3) array of vertices-indexed-by-face, convert
        ## backward to unindexed vertices
        ## This is done by collapsing into a list of 'unique' vertices
        ## (difference < 1e-14)

        ## I think generally this should be discouraged..
        faces = self._vertices_indexed_by_faces
        verts = {}  # used to remember the index of each vertex position
        self._faces = np.empty(faces.shape[:2], dtype=np.uint)
        self._vertices = []
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
                    #self._vertices.append(QtGui.QVector3D(*pt))
                    self._vertices.append(pt)
                    self._vertex_faces.append([])
                    index = len(self._vertices)-1
                    verts[pt2] = index
                # track which vertices belong to which faces
                self._vertex_faces[index].append(i)
                self._faces[i, j] = index
        self._vertices = np.array(self._vertices, dtype=np.float32)

    #def _setUnindexedFaces(self, faces, vertices, vertex_colors=None,
        #                   face_colors=None):
        #self._vertices = vertices #[QtGui.QVector3D(*v) for v in vertices]
        #self._faces = faces.astype(np.uint)
        #self._edges = None
        #self._vertex_faces = None
        #self._face_normals = None
        #self._vertex_normals = None
        #self._vertex_colors = vertex_colors
        #self._face_colors = face_colors

    def vertex_faces(self):
        """
        List mapping each vertex index to a list of face indices that use it.
        """
        if self._vertex_faces is None:
            self._vertex_faces = [[] for i in xrange(len(self.vertices()))]
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

    def _compute_edges(self, indexed=None):
        if indexed is None:
            if self._faces is not None:
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
            else:
                raise Exception("MeshData cannot generate edges--no faces in "
                                "this data.")
        elif indexed == 'faces':
            if self._vertices_indexed_by_faces is not None:
                verts = self._vertices_indexed_by_faces
                edges = np.empty((verts.shape[0], 3, 2), dtype=np.uint)
                nf = verts.shape[0]
                edges[:, 0, 0] = np.arange(nf) * 3
                edges[:, 0, 1] = edges[:, 0, 0] + 1
                edges[:, 1, 0] = edges[:, 0, 1]
                edges[:, 1, 1] = edges[:, 1, 0] + 1
                edges[:, 2, 0] = edges[:, 1, 1]
                edges[:, 2, 1] = edges[:, 0, 0]
                self._edges_indexed_by_faces = edges
            else:
                raise Exception("MeshData cannot generate edges--no faces in "
                                "this data.")
        else:
            raise Exception("Invalid indexing mode. Accepts: None, 'faces'")

    def save(self):
        """Serialize this mesh to a string appropriate for disk storage"""
        import pickle
        if self._faces is not None:
            names = ['_vertices', '_faces']
        else:
            names = ['_vertices_indexed_by_faces']

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
    Return a MeshData instance with vertices and faces computed
    for a spherical surface.
    """
    verts = np.empty((rows+1, cols, 3), dtype=np.float32)

    ## compute vertices
    phi = (np.arange(rows+1) * np.pi / rows).reshape(rows+1, 1)
    s = radius * np.sin(phi)
    verts[..., 2] = radius * np.cos(phi)
    th = ((np.arange(cols) * 2 * np.pi / cols).reshape(1, cols))
    if offset:
        # rotate each row by 1/2 column
        th = th + ((np.pi / cols) * np.arange(rows+1).reshape(rows+1, 1))
    verts[..., 0] = s * np.cos(th)
    verts[..., 1] = s * np.sin(th)
    ## remove redundant vertices from top and bottom
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

    ## adjust for redundant vertices that were removed from top and bottom
    vmin = cols-1
    faces[faces < vmin] = vmin
    faces -= vmin
    vmax = verts.shape[0]-1
    faces[faces > vmax] = vmax
    return MeshData(vertices=verts, faces=faces)


def cylinder(rows, cols, radius=[1.0, 1.0], length=1.0, offset=False):
    """
    Return a MeshData instance with vertices and faces computed
    for a cylindrical surface.
    The cylinder may be tapered with different radii at each end
    (truncated cone)
    """
    verts = np.empty((rows+1, cols, 3), dtype=np.float32)
    if isinstance(radius, int):
        radius = [radius, radius]  # convert to list
    ## compute vertices
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

    return MeshData(vertices=verts, faces=faces)


def cone(cols, radius=3.0, length=10.0):
    """
    Return a MeshData instance with vertexes and faces computed
    for a cone surface.
    """
    verts = np.empty((cols+1, 3), dtype=float)
    ## compute vertexes
    th = np.linspace(2 * np.pi, 0, cols+1).reshape(1, cols+1)
    verts[:-1, 2] = 0.0
    verts[:-1, 0] = radius * np.cos(th[0, :-1])  # x = r cos(th)
    verts[:-1, 1] = radius * np.sin(th[0, :-1])  # y = r sin(th)
    # Add the extremity
    verts[-1, 0] = 0.0
    verts[-1, 1] = 0.0
    verts[-1, 2] = length
    verts = verts.reshape((cols+1), 3)  # just reshape: no redundant vertices
    ## compute faces
    faces = np.empty((cols, 3), dtype=np.uint)
    template = np.array([[0, 1]])
    for pos in range(cols):
        faces[pos, :-1] = template + pos
    faces[:, 2] = cols
    faces[-1, 1] = 0

    return MeshData(vertices=verts, faces=faces)


def arrow(rows, cols, radius=0.1, length=1.0, fRC=2.0, fLC=0.3):
    """
    Return a MeshData instance with vertexes and faces computed
    for an arrow surface.
    it's a cylinder + a cone

    IN :
        - length : Arrow length
        - radius = Cylinder Radius
        - fCR = factor Cone Radius : Cone radius = fCR*radius
        - fLC = factor Cone length of arrow length : Cone length = fLC*length
                                                     Cylinder length =
                                    length - fLC*length if fLC < 1.0 else = 0.0
            0 < flc < 1.0
        - rows : number of vertexes on radius

    OUT: a MeshData object.


    TODO: add the colors for the head and cylinder
    """
    # create the cylinder
    mdCyl = None
    conL = length * fLC
    if abs(fLC) < 1.0:
        cylL = length * (1.0 - fLC)
        mdCyl = cylinder(rows, cols, radius=[radius, radius], length=cylL)
    # create the cone
    mdCon = cone(cols, radius=radius*fRC, length=conL)
    verts = mdCon.vertices()
    nbrVertsCon = verts.size/3
    faces = mdCon.faces()
    if mdCyl is not None:
        trans = np.array([[0.0, 0.0, cylL]])
        verts = np.vstack((verts+trans, mdCyl.vertices()))
        faces = np.vstack((faces, mdCyl.faces()+nbrVertsCon))

    return MeshData(vertices=verts, faces=faces)
