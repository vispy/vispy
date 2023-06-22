import numpy as np

_data_cache = None


def isosurface(data, level):
    """
    Generate isosurface from volumetric data using marching cubes algorithm.
    See Paul Bourke, "Polygonising a Scalar Field"
    (http://paulbourke.net/geometry/polygonise/)

    *data*   3D numpy array of scalar values
    *level*  The level at which to generate an isosurface

    Returns an array of vertex coordinates (Nv, 3) and an array of
    per-face vertex indexes (Nf, 3)
    """
    # For improvement, see:
    #
    # Efficient implementation of Marching Cubes' cases with topological
    # guarantees.
    # Thomas Lewiner, Helio Lopes, Antonio Wilson Vieira and Geovan Tavares.
    # Journal of Graphics Tools 8(2): pp. 1-15 (december 2003)

    (face_shift_tables, edge_shifts, edge_table, n_table_faces) = _get_data_cache()

    # mark everything below the isosurface level
    mask = data < level

    # Because we make use of the strides data attribute below, we have to make
    # sure that the data is contiguous (which it won't be if the user did
    # data.transpose() for example). Note that this doesn't copy the data if it
    # is already contiguous.
    data = np.ascontiguousarray(data)

    # make eight sub-fields and compute indexes for grid cells
    index = np.zeros([x - 1 for x in data.shape], dtype=np.ubyte)
    fields = np.empty((2, 2, 2), dtype=object)
    slices = [slice(0, -1), slice(1, None)]
    for i in [0, 1]:
        for j in [0, 1]:
            for k in [0, 1]:
                fields[i, j, k] = mask[slices[i], slices[j], slices[k]]
                # this is just to match Bourk's vertex numbering scheme:
                vertIndex = i - 2 * j * i + 3 * j + 4 * k
                index += (fields[i, j, k] * 2**vertIndex).astype(np.ubyte)

    # Generate table of edges that have been cut
    cut_edges = np.zeros([x + 1 for x in index.shape] + [3], dtype=np.uint32)
    edges = edge_table[index]
    for i, shift in enumerate(edge_shifts[:12]):
        slices = [slice(shift[j], cut_edges.shape[j] + (shift[j] - 1)) for j in range(3)]
        cut_edges[slices[0], slices[1], slices[2], shift[3]] += edges & 2**i

    # for each cut edge, interpolate to see where exactly the edge is cut and
    # generate vertex positions
    m = cut_edges > 0
    vertex_inds = np.argwhere(m)  # argwhere is slow!
    vertexes = vertex_inds[:, :3].astype(np.float32).copy()
    dataFlat = data.reshape(data.shape[0] * data.shape[1] * data.shape[2])

    # re-use the cut_edges array as a lookup table for vertex IDs
    cut_edges[
        vertex_inds[:, 0], vertex_inds[:, 1], vertex_inds[:, 2], vertex_inds[:, 3]
    ] = np.arange(vertex_inds.shape[0])

    for i in [0, 1, 2]:
        vim = vertex_inds[:, 3] == i
        vi = vertex_inds[vim, :3]
        vi_flat = (vi * (np.array(data.strides[:3]) // data.itemsize)[np.newaxis, :]).sum(axis=1)
        v1 = dataFlat[vi_flat]
        v2 = dataFlat[vi_flat + data.strides[i] // data.itemsize]
        vertexes[vim, i] += (level - v1) / (v2 - v1)

    # compute the set of vertex indexes for each face.

    # This works, but runs a bit slower.
    # all cells with at least one face:
    # cells = np.argwhere((index != 0) & (index != 255))
    # cellInds = index[cells[:, 0], cells[:, 1], cells[:, 2]]
    # verts = faceTable[cellInds]
    # mask = verts[..., 0, 0] != 9
    # we now have indexes into cut_edges:
    # verts[...,:3] += cells[:, np.newaxis, np.newaxis,:]
    # verts = verts[mask]
    # and these are the vertex indexes we want:
    # faces = cut_edges[verts[..., 0], verts[..., 1], verts[..., 2],
    #                  verts[..., 3]]

    # To allow this to be vectorized efficiently, we count the number of faces
    # in each grid cell and handle each group of cells with the same number
    # together.

    # determine how many faces to assign to each grid cell
    n_faces = n_table_faces[index]
    tot_faces = n_faces.sum()
    faces = np.empty((tot_faces, 3), dtype=np.uint32)
    ptr = 0

    # this helps speed up an indexing operation later on
    cs = np.array(cut_edges.strides) // cut_edges.itemsize
    cut_edges = cut_edges.flatten()

    # this, strangely, does not seem to help.
    # ins = np.array(index.strides)/index.itemsize
    # index = index.flatten()

    for i in range(1, 6):
        # expensive:
        # all cells which require i faces  (argwhere is expensive)
        cells = np.argwhere(n_faces == i)
        if cells.shape[0] == 0:
            continue
        # index values of cells to process for this round:
        cellInds = index[cells[:, 0], cells[:, 1], cells[:, 2]]

        # expensive:
        verts = face_shift_tables[i][cellInds]
        # we now have indexes into cut_edges:
        verts[..., :3] += (cells[:, np.newaxis, np.newaxis, :]).astype(np.uint16)
        verts = verts.reshape((verts.shape[0] * i,) + verts.shape[2:])

        # expensive:
        verts = (verts * cs[np.newaxis, np.newaxis, :]).sum(axis=2)
        vert_inds = cut_edges[verts]
        nv = vert_inds.shape[0]
        faces[ptr : ptr + nv] = vert_inds  # .reshape((nv, 3))
        ptr += nv

    return vertexes, faces


def _get_data_cache():
    # Precompute lookup tables on the first run

    global _data_cache

    if _data_cache is None:
        # map from grid cell index to edge index.
        # grid cell index tells us which corners are below the isosurface,
        # edge index tells us which edges are cut by the isosurface.
        # (Data stolen from Bourk; see above.)
        edge_table = np.array(
            [
                0x0,
                0x109,
                0x203,
                0x30A,
                0x406,
                0x50F,
                0x605,
                0x70C,
                0x80C,
                0x905,
                0xA0F,
                0xB06,
                0xC0A,
                0xD03,
                0xE09,
                0xF00,
                0x190,
                0x99,
                0x393,
                0x29A,
                0x596,
                0x49F,
                0x795,
                0x69C,
                0x99C,
                0x895,
                0xB9F,
                0xA96,
                0xD9A,
                0xC93,
                0xF99,
                0xE90,
                0x230,
                0x339,
                0x33,
                0x13A,
                0x636,
                0x73F,
                0x435,
                0x53C,
                0xA3C,
                0xB35,
                0x83F,
                0x936,
                0xE3A,
                0xF33,
                0xC39,
                0xD30,
                0x3A0,
                0x2A9,
                0x1A3,
                0xAA,
                0x7A6,
                0x6AF,
                0x5A5,
                0x4AC,
                0xBAC,
                0xAA5,
                0x9AF,
                0x8A6,
                0xFAA,
                0xEA3,
                0xDA9,
                0xCA0,
                0x460,
                0x569,
                0x663,
                0x76A,
                0x66,
                0x16F,
                0x265,
                0x36C,
                0xC6C,
                0xD65,
                0xE6F,
                0xF66,
                0x86A,
                0x963,
                0xA69,
                0xB60,
                0x5F0,
                0x4F9,
                0x7F3,
                0x6FA,
                0x1F6,
                0xFF,
                0x3F5,
                0x2FC,
                0xDFC,
                0xCF5,
                0xFFF,
                0xEF6,
                0x9FA,
                0x8F3,
                0xBF9,
                0xAF0,
                0x650,
                0x759,
                0x453,
                0x55A,
                0x256,
                0x35F,
                0x55,
                0x15C,
                0xE5C,
                0xF55,
                0xC5F,
                0xD56,
                0xA5A,
                0xB53,
                0x859,
                0x950,
                0x7C0,
                0x6C9,
                0x5C3,
                0x4CA,
                0x3C6,
                0x2CF,
                0x1C5,
                0xCC,
                0xFCC,
                0xEC5,
                0xDCF,
                0xCC6,
                0xBCA,
                0xAC3,
                0x9C9,
                0x8C0,
                0x8C0,
                0x9C9,
                0xAC3,
                0xBCA,
                0xCC6,
                0xDCF,
                0xEC5,
                0xFCC,
                0xCC,
                0x1C5,
                0x2CF,
                0x3C6,
                0x4CA,
                0x5C3,
                0x6C9,
                0x7C0,
                0x950,
                0x859,
                0xB53,
                0xA5A,
                0xD56,
                0xC5F,
                0xF55,
                0xE5C,
                0x15C,
                0x55,
                0x35F,
                0x256,
                0x55A,
                0x453,
                0x759,
                0x650,
                0xAF0,
                0xBF9,
                0x8F3,
                0x9FA,
                0xEF6,
                0xFFF,
                0xCF5,
                0xDFC,
                0x2FC,
                0x3F5,
                0xFF,
                0x1F6,
                0x6FA,
                0x7F3,
                0x4F9,
                0x5F0,
                0xB60,
                0xA69,
                0x963,
                0x86A,
                0xF66,
                0xE6F,
                0xD65,
                0xC6C,
                0x36C,
                0x265,
                0x16F,
                0x66,
                0x76A,
                0x663,
                0x569,
                0x460,
                0xCA0,
                0xDA9,
                0xEA3,
                0xFAA,
                0x8A6,
                0x9AF,
                0xAA5,
                0xBAC,
                0x4AC,
                0x5A5,
                0x6AF,
                0x7A6,
                0xAA,
                0x1A3,
                0x2A9,
                0x3A0,
                0xD30,
                0xC39,
                0xF33,
                0xE3A,
                0x936,
                0x83F,
                0xB35,
                0xA3C,
                0x53C,
                0x435,
                0x73F,
                0x636,
                0x13A,
                0x33,
                0x339,
                0x230,
                0xE90,
                0xF99,
                0xC93,
                0xD9A,
                0xA96,
                0xB9F,
                0x895,
                0x99C,
                0x69C,
                0x795,
                0x49F,
                0x596,
                0x29A,
                0x393,
                0x99,
                0x190,
                0xF00,
                0xE09,
                0xD03,
                0xC0A,
                0xB06,
                0xA0F,
                0x905,
                0x80C,
                0x70C,
                0x605,
                0x50F,
                0x406,
                0x30A,
                0x203,
                0x109,
                0x0,
            ],
            dtype=np.uint16,
        )

        # Table of triangles to use for filling each grid cell.
        # Each set of three integers tells us which three edges to
        # draw a triangle between.
        # (Data stolen from Bourk; see above.)
        triTable = [
            [],
            [0, 8, 3],
            [0, 1, 9],
            [1, 8, 3, 9, 8, 1],
            [1, 2, 10],
            [0, 8, 3, 1, 2, 10],
            [9, 2, 10, 0, 2, 9],
            [2, 8, 3, 2, 10, 8, 10, 9, 8],
            [3, 11, 2],
            [0, 11, 2, 8, 11, 0],
            [1, 9, 0, 2, 3, 11],
            [1, 11, 2, 1, 9, 11, 9, 8, 11],
            [3, 10, 1, 11, 10, 3],
            [0, 10, 1, 0, 8, 10, 8, 11, 10],
            [3, 9, 0, 3, 11, 9, 11, 10, 9],
            [9, 8, 10, 10, 8, 11],
            [4, 7, 8],
            [4, 3, 0, 7, 3, 4],
            [0, 1, 9, 8, 4, 7],
            [4, 1, 9, 4, 7, 1, 7, 3, 1],
            [1, 2, 10, 8, 4, 7],
            [3, 4, 7, 3, 0, 4, 1, 2, 10],
            [9, 2, 10, 9, 0, 2, 8, 4, 7],
            [2, 10, 9, 2, 9, 7, 2, 7, 3, 7, 9, 4],
            [8, 4, 7, 3, 11, 2],
            [11, 4, 7, 11, 2, 4, 2, 0, 4],
            [9, 0, 1, 8, 4, 7, 2, 3, 11],
            [4, 7, 11, 9, 4, 11, 9, 11, 2, 9, 2, 1],
            [3, 10, 1, 3, 11, 10, 7, 8, 4],
            [1, 11, 10, 1, 4, 11, 1, 0, 4, 7, 11, 4],
            [4, 7, 8, 9, 0, 11, 9, 11, 10, 11, 0, 3],
            [4, 7, 11, 4, 11, 9, 9, 11, 10],
            [9, 5, 4],
            [9, 5, 4, 0, 8, 3],
            [0, 5, 4, 1, 5, 0],
            [8, 5, 4, 8, 3, 5, 3, 1, 5],
            [1, 2, 10, 9, 5, 4],
            [3, 0, 8, 1, 2, 10, 4, 9, 5],
            [5, 2, 10, 5, 4, 2, 4, 0, 2],
            [2, 10, 5, 3, 2, 5, 3, 5, 4, 3, 4, 8],
            [9, 5, 4, 2, 3, 11],
            [0, 11, 2, 0, 8, 11, 4, 9, 5],
            [0, 5, 4, 0, 1, 5, 2, 3, 11],
            [2, 1, 5, 2, 5, 8, 2, 8, 11, 4, 8, 5],
            [10, 3, 11, 10, 1, 3, 9, 5, 4],
            [4, 9, 5, 0, 8, 1, 8, 10, 1, 8, 11, 10],
            [5, 4, 0, 5, 0, 11, 5, 11, 10, 11, 0, 3],
            [5, 4, 8, 5, 8, 10, 10, 8, 11],
            [9, 7, 8, 5, 7, 9],
            [9, 3, 0, 9, 5, 3, 5, 7, 3],
            [0, 7, 8, 0, 1, 7, 1, 5, 7],
            [1, 5, 3, 3, 5, 7],
            [9, 7, 8, 9, 5, 7, 10, 1, 2],
            [10, 1, 2, 9, 5, 0, 5, 3, 0, 5, 7, 3],
            [8, 0, 2, 8, 2, 5, 8, 5, 7, 10, 5, 2],
            [2, 10, 5, 2, 5, 3, 3, 5, 7],
            [7, 9, 5, 7, 8, 9, 3, 11, 2],
            [9, 5, 7, 9, 7, 2, 9, 2, 0, 2, 7, 11],
            [2, 3, 11, 0, 1, 8, 1, 7, 8, 1, 5, 7],
            [11, 2, 1, 11, 1, 7, 7, 1, 5],
            [9, 5, 8, 8, 5, 7, 10, 1, 3, 10, 3, 11],
            [5, 7, 0, 5, 0, 9, 7, 11, 0, 1, 0, 10, 11, 10, 0],
            [11, 10, 0, 11, 0, 3, 10, 5, 0, 8, 0, 7, 5, 7, 0],
            [11, 10, 5, 7, 11, 5],
            [10, 6, 5],
            [0, 8, 3, 5, 10, 6],
            [9, 0, 1, 5, 10, 6],
            [1, 8, 3, 1, 9, 8, 5, 10, 6],
            [1, 6, 5, 2, 6, 1],
            [1, 6, 5, 1, 2, 6, 3, 0, 8],
            [9, 6, 5, 9, 0, 6, 0, 2, 6],
            [5, 9, 8, 5, 8, 2, 5, 2, 6, 3, 2, 8],
            [2, 3, 11, 10, 6, 5],
            [11, 0, 8, 11, 2, 0, 10, 6, 5],
            [0, 1, 9, 2, 3, 11, 5, 10, 6],
            [5, 10, 6, 1, 9, 2, 9, 11, 2, 9, 8, 11],
            [6, 3, 11, 6, 5, 3, 5, 1, 3],
            [0, 8, 11, 0, 11, 5, 0, 5, 1, 5, 11, 6],
            [3, 11, 6, 0, 3, 6, 0, 6, 5, 0, 5, 9],
            [6, 5, 9, 6, 9, 11, 11, 9, 8],
            [5, 10, 6, 4, 7, 8],
            [4, 3, 0, 4, 7, 3, 6, 5, 10],
            [1, 9, 0, 5, 10, 6, 8, 4, 7],
            [10, 6, 5, 1, 9, 7, 1, 7, 3, 7, 9, 4],
            [6, 1, 2, 6, 5, 1, 4, 7, 8],
            [1, 2, 5, 5, 2, 6, 3, 0, 4, 3, 4, 7],
            [8, 4, 7, 9, 0, 5, 0, 6, 5, 0, 2, 6],
            [7, 3, 9, 7, 9, 4, 3, 2, 9, 5, 9, 6, 2, 6, 9],
            [3, 11, 2, 7, 8, 4, 10, 6, 5],
            [5, 10, 6, 4, 7, 2, 4, 2, 0, 2, 7, 11],
            [0, 1, 9, 4, 7, 8, 2, 3, 11, 5, 10, 6],
            [9, 2, 1, 9, 11, 2, 9, 4, 11, 7, 11, 4, 5, 10, 6],
            [8, 4, 7, 3, 11, 5, 3, 5, 1, 5, 11, 6],
            [5, 1, 11, 5, 11, 6, 1, 0, 11, 7, 11, 4, 0, 4, 11],
            [0, 5, 9, 0, 6, 5, 0, 3, 6, 11, 6, 3, 8, 4, 7],
            [6, 5, 9, 6, 9, 11, 4, 7, 9, 7, 11, 9],
            [10, 4, 9, 6, 4, 10],
            [4, 10, 6, 4, 9, 10, 0, 8, 3],
            [10, 0, 1, 10, 6, 0, 6, 4, 0],
            [8, 3, 1, 8, 1, 6, 8, 6, 4, 6, 1, 10],
            [1, 4, 9, 1, 2, 4, 2, 6, 4],
            [3, 0, 8, 1, 2, 9, 2, 4, 9, 2, 6, 4],
            [0, 2, 4, 4, 2, 6],
            [8, 3, 2, 8, 2, 4, 4, 2, 6],
            [10, 4, 9, 10, 6, 4, 11, 2, 3],
            [0, 8, 2, 2, 8, 11, 4, 9, 10, 4, 10, 6],
            [3, 11, 2, 0, 1, 6, 0, 6, 4, 6, 1, 10],
            [6, 4, 1, 6, 1, 10, 4, 8, 1, 2, 1, 11, 8, 11, 1],
            [9, 6, 4, 9, 3, 6, 9, 1, 3, 11, 6, 3],
            [8, 11, 1, 8, 1, 0, 11, 6, 1, 9, 1, 4, 6, 4, 1],
            [3, 11, 6, 3, 6, 0, 0, 6, 4],
            [6, 4, 8, 11, 6, 8],
            [7, 10, 6, 7, 8, 10, 8, 9, 10],
            [0, 7, 3, 0, 10, 7, 0, 9, 10, 6, 7, 10],
            [10, 6, 7, 1, 10, 7, 1, 7, 8, 1, 8, 0],
            [10, 6, 7, 10, 7, 1, 1, 7, 3],
            [1, 2, 6, 1, 6, 8, 1, 8, 9, 8, 6, 7],
            [2, 6, 9, 2, 9, 1, 6, 7, 9, 0, 9, 3, 7, 3, 9],
            [7, 8, 0, 7, 0, 6, 6, 0, 2],
            [7, 3, 2, 6, 7, 2],
            [2, 3, 11, 10, 6, 8, 10, 8, 9, 8, 6, 7],
            [2, 0, 7, 2, 7, 11, 0, 9, 7, 6, 7, 10, 9, 10, 7],
            [1, 8, 0, 1, 7, 8, 1, 10, 7, 6, 7, 10, 2, 3, 11],
            [11, 2, 1, 11, 1, 7, 10, 6, 1, 6, 7, 1],
            [8, 9, 6, 8, 6, 7, 9, 1, 6, 11, 6, 3, 1, 3, 6],
            [0, 9, 1, 11, 6, 7],
            [7, 8, 0, 7, 0, 6, 3, 11, 0, 11, 6, 0],
            [7, 11, 6],
            [7, 6, 11],
            [3, 0, 8, 11, 7, 6],
            [0, 1, 9, 11, 7, 6],
            [8, 1, 9, 8, 3, 1, 11, 7, 6],
            [10, 1, 2, 6, 11, 7],
            [1, 2, 10, 3, 0, 8, 6, 11, 7],
            [2, 9, 0, 2, 10, 9, 6, 11, 7],
            [6, 11, 7, 2, 10, 3, 10, 8, 3, 10, 9, 8],
            [7, 2, 3, 6, 2, 7],
            [7, 0, 8, 7, 6, 0, 6, 2, 0],
            [2, 7, 6, 2, 3, 7, 0, 1, 9],
            [1, 6, 2, 1, 8, 6, 1, 9, 8, 8, 7, 6],
            [10, 7, 6, 10, 1, 7, 1, 3, 7],
            [10, 7, 6, 1, 7, 10, 1, 8, 7, 1, 0, 8],
            [0, 3, 7, 0, 7, 10, 0, 10, 9, 6, 10, 7],
            [7, 6, 10, 7, 10, 8, 8, 10, 9],
            [6, 8, 4, 11, 8, 6],
            [3, 6, 11, 3, 0, 6, 0, 4, 6],
            [8, 6, 11, 8, 4, 6, 9, 0, 1],
            [9, 4, 6, 9, 6, 3, 9, 3, 1, 11, 3, 6],
            [6, 8, 4, 6, 11, 8, 2, 10, 1],
            [1, 2, 10, 3, 0, 11, 0, 6, 11, 0, 4, 6],
            [4, 11, 8, 4, 6, 11, 0, 2, 9, 2, 10, 9],
            [10, 9, 3, 10, 3, 2, 9, 4, 3, 11, 3, 6, 4, 6, 3],
            [8, 2, 3, 8, 4, 2, 4, 6, 2],
            [0, 4, 2, 4, 6, 2],
            [1, 9, 0, 2, 3, 4, 2, 4, 6, 4, 3, 8],
            [1, 9, 4, 1, 4, 2, 2, 4, 6],
            [8, 1, 3, 8, 6, 1, 8, 4, 6, 6, 10, 1],
            [10, 1, 0, 10, 0, 6, 6, 0, 4],
            [4, 6, 3, 4, 3, 8, 6, 10, 3, 0, 3, 9, 10, 9, 3],
            [10, 9, 4, 6, 10, 4],
            [4, 9, 5, 7, 6, 11],
            [0, 8, 3, 4, 9, 5, 11, 7, 6],
            [5, 0, 1, 5, 4, 0, 7, 6, 11],
            [11, 7, 6, 8, 3, 4, 3, 5, 4, 3, 1, 5],
            [9, 5, 4, 10, 1, 2, 7, 6, 11],
            [6, 11, 7, 1, 2, 10, 0, 8, 3, 4, 9, 5],
            [7, 6, 11, 5, 4, 10, 4, 2, 10, 4, 0, 2],
            [3, 4, 8, 3, 5, 4, 3, 2, 5, 10, 5, 2, 11, 7, 6],
            [7, 2, 3, 7, 6, 2, 5, 4, 9],
            [9, 5, 4, 0, 8, 6, 0, 6, 2, 6, 8, 7],
            [3, 6, 2, 3, 7, 6, 1, 5, 0, 5, 4, 0],
            [6, 2, 8, 6, 8, 7, 2, 1, 8, 4, 8, 5, 1, 5, 8],
            [9, 5, 4, 10, 1, 6, 1, 7, 6, 1, 3, 7],
            [1, 6, 10, 1, 7, 6, 1, 0, 7, 8, 7, 0, 9, 5, 4],
            [4, 0, 10, 4, 10, 5, 0, 3, 10, 6, 10, 7, 3, 7, 10],
            [7, 6, 10, 7, 10, 8, 5, 4, 10, 4, 8, 10],
            [6, 9, 5, 6, 11, 9, 11, 8, 9],
            [3, 6, 11, 0, 6, 3, 0, 5, 6, 0, 9, 5],
            [0, 11, 8, 0, 5, 11, 0, 1, 5, 5, 6, 11],
            [6, 11, 3, 6, 3, 5, 5, 3, 1],
            [1, 2, 10, 9, 5, 11, 9, 11, 8, 11, 5, 6],
            [0, 11, 3, 0, 6, 11, 0, 9, 6, 5, 6, 9, 1, 2, 10],
            [11, 8, 5, 11, 5, 6, 8, 0, 5, 10, 5, 2, 0, 2, 5],
            [6, 11, 3, 6, 3, 5, 2, 10, 3, 10, 5, 3],
            [5, 8, 9, 5, 2, 8, 5, 6, 2, 3, 8, 2],
            [9, 5, 6, 9, 6, 0, 0, 6, 2],
            [1, 5, 8, 1, 8, 0, 5, 6, 8, 3, 8, 2, 6, 2, 8],
            [1, 5, 6, 2, 1, 6],
            [1, 3, 6, 1, 6, 10, 3, 8, 6, 5, 6, 9, 8, 9, 6],
            [10, 1, 0, 10, 0, 6, 9, 5, 0, 5, 6, 0],
            [0, 3, 8, 5, 6, 10],
            [10, 5, 6],
            [11, 5, 10, 7, 5, 11],
            [11, 5, 10, 11, 7, 5, 8, 3, 0],
            [5, 11, 7, 5, 10, 11, 1, 9, 0],
            [10, 7, 5, 10, 11, 7, 9, 8, 1, 8, 3, 1],
            [11, 1, 2, 11, 7, 1, 7, 5, 1],
            [0, 8, 3, 1, 2, 7, 1, 7, 5, 7, 2, 11],
            [9, 7, 5, 9, 2, 7, 9, 0, 2, 2, 11, 7],
            [7, 5, 2, 7, 2, 11, 5, 9, 2, 3, 2, 8, 9, 8, 2],
            [2, 5, 10, 2, 3, 5, 3, 7, 5],
            [8, 2, 0, 8, 5, 2, 8, 7, 5, 10, 2, 5],
            [9, 0, 1, 5, 10, 3, 5, 3, 7, 3, 10, 2],
            [9, 8, 2, 9, 2, 1, 8, 7, 2, 10, 2, 5, 7, 5, 2],
            [1, 3, 5, 3, 7, 5],
            [0, 8, 7, 0, 7, 1, 1, 7, 5],
            [9, 0, 3, 9, 3, 5, 5, 3, 7],
            [9, 8, 7, 5, 9, 7],
            [5, 8, 4, 5, 10, 8, 10, 11, 8],
            [5, 0, 4, 5, 11, 0, 5, 10, 11, 11, 3, 0],
            [0, 1, 9, 8, 4, 10, 8, 10, 11, 10, 4, 5],
            [10, 11, 4, 10, 4, 5, 11, 3, 4, 9, 4, 1, 3, 1, 4],
            [2, 5, 1, 2, 8, 5, 2, 11, 8, 4, 5, 8],
            [0, 4, 11, 0, 11, 3, 4, 5, 11, 2, 11, 1, 5, 1, 11],
            [0, 2, 5, 0, 5, 9, 2, 11, 5, 4, 5, 8, 11, 8, 5],
            [9, 4, 5, 2, 11, 3],
            [2, 5, 10, 3, 5, 2, 3, 4, 5, 3, 8, 4],
            [5, 10, 2, 5, 2, 4, 4, 2, 0],
            [3, 10, 2, 3, 5, 10, 3, 8, 5, 4, 5, 8, 0, 1, 9],
            [5, 10, 2, 5, 2, 4, 1, 9, 2, 9, 4, 2],
            [8, 4, 5, 8, 5, 3, 3, 5, 1],
            [0, 4, 5, 1, 0, 5],
            [8, 4, 5, 8, 5, 3, 9, 0, 5, 0, 3, 5],
            [9, 4, 5],
            [4, 11, 7, 4, 9, 11, 9, 10, 11],
            [0, 8, 3, 4, 9, 7, 9, 11, 7, 9, 10, 11],
            [1, 10, 11, 1, 11, 4, 1, 4, 0, 7, 4, 11],
            [3, 1, 4, 3, 4, 8, 1, 10, 4, 7, 4, 11, 10, 11, 4],
            [4, 11, 7, 9, 11, 4, 9, 2, 11, 9, 1, 2],
            [9, 7, 4, 9, 11, 7, 9, 1, 11, 2, 11, 1, 0, 8, 3],
            [11, 7, 4, 11, 4, 2, 2, 4, 0],
            [11, 7, 4, 11, 4, 2, 8, 3, 4, 3, 2, 4],
            [2, 9, 10, 2, 7, 9, 2, 3, 7, 7, 4, 9],
            [9, 10, 7, 9, 7, 4, 10, 2, 7, 8, 7, 0, 2, 0, 7],
            [3, 7, 10, 3, 10, 2, 7, 4, 10, 1, 10, 0, 4, 0, 10],
            [1, 10, 2, 8, 7, 4],
            [4, 9, 1, 4, 1, 7, 7, 1, 3],
            [4, 9, 1, 4, 1, 7, 0, 8, 1, 8, 7, 1],
            [4, 0, 3, 7, 4, 3],
            [4, 8, 7],
            [9, 10, 8, 10, 11, 8],
            [3, 0, 9, 3, 9, 11, 11, 9, 10],
            [0, 1, 10, 0, 10, 8, 8, 10, 11],
            [3, 1, 10, 11, 3, 10],
            [1, 2, 11, 1, 11, 9, 9, 11, 8],
            [3, 0, 9, 3, 9, 11, 1, 2, 9, 2, 11, 9],
            [0, 2, 11, 8, 0, 11],
            [3, 2, 11],
            [2, 3, 8, 2, 8, 10, 10, 8, 9],
            [9, 10, 2, 0, 9, 2],
            [2, 3, 8, 2, 8, 10, 0, 1, 8, 1, 10, 8],
            [1, 10, 2],
            [1, 3, 8, 9, 1, 8],
            [0, 9, 1],
            [0, 3, 8],
            [],
        ]

        # maps edge ID (0-11) to (x, y, z) cell offset and edge ID (0-2)
        edge_shifts = np.array(
            [
                [0, 0, 0, 0],
                [1, 0, 0, 1],
                [0, 1, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0],
                [1, 0, 1, 1],
                [0, 1, 1, 0],
                [0, 0, 1, 1],
                [0, 0, 0, 2],
                [1, 0, 0, 2],
                [1, 1, 0, 2],
                [0, 1, 0, 2],
                # [9, 9, 9, 9] fake
                # don't use ubyte here! This value gets added to cell index later;
                # will need the extra precision.
            ],
            dtype=np.uint16,
        )
        n_table_faces = np.array([len(f) / 3 for f in triTable], dtype=np.ubyte)
        face_shift_tables = [None]
        for i in range(1, 6):
            # compute lookup table of index: vertexes mapping
            faceTableI = np.zeros((len(triTable), i * 3), dtype=np.ubyte)
            faceTableInds = np.argwhere(n_table_faces == i)[:, 0]
            faceTableI[faceTableInds] = np.array([triTable[j] for j in faceTableInds])
            faceTableI = faceTableI.reshape((len(triTable), i, 3))
            face_shift_tables.append(edge_shifts[faceTableI])

        _data_cache = (face_shift_tables, edge_shifts, edge_table, n_table_faces)

    return _data_cache
