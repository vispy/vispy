from __future__ import division

# from ..geometry import create_tube  # to move to
from ..geometry import create_cube
from ..gloo import set_state
from .mesh import MeshVisual
import numpy as np


class TubeVisual(MeshVisual):
    """Visual that displays a tube by extruding a circle
    along a piecewise-linear path.

    Parameters
    ----------
    
    """
    def __init__(self, points, radius=1.0, tube_points=8,
                 colors=None,
                 closed=False,
                 shading='flat',
                 vertex_colors=None, face_colors=None,
                 color=(0, 1, 0, 1),
                 mode='triangles'):

        tangents, normals, binormals = frenet_frames(points, closed)

        segments = len(points) - 1

       # get the positions of each vertex
        grid = np.zeros((len(points), tube_points, 3))
        for i in range(len(points)):
            pos = points[i]
            tangent = tangents[i]
            normal = normals[i]
            binormal = binormals[i]

            for j in range(tube_points):
                v = j / tube_points * 2 * np.pi
                cx = -1. * radius * np.cos(v)
                cy = radius * np.sin(v)

                grid[i, j] =pos + cx*normal + cy*binormal

        # construct the mesh
        faces = []
        tex_coords = []
        indices = []
        for i in range(segments):
            for j in range(tube_points):
                ip = (i+1) % segments if closed else i+1
                jp = (j+1) % tube_points

                a = grid[i, j]
                b = grid[ip, j]
                c = grid[ip, jp]
                d = grid[i, jp]

                index_a = i*tube_points + j
                index_b = ip*tube_points + j
                index_c = ip*tube_points + jp
                index_d = i*tube_points + jp

                uva = np.array([i / segments, j / tube_points])
                uvb = np.array([(i+1) / segments, j / tube_points])
                uvc = np.array([(i+1) / segments, (j+1) / tube_points])
                uvd = np.array([i / segments, (j+1) / tube_points])

                faces.append([a, b, d])
                tex_coords.append([uva, uvb, uvd])
                indices.append([index_a, index_b, index_d])

                faces.append([b, c, d])
                tex_coords.append([uvb, uvc, uvd])
                indices.append([index_b, index_c, index_d])

        faces = np.array(faces)
        tex_coords = np.array(tex_coords)
        print('faces are', faces)

        vertices = grid.reshape(grid.shape[0]*grid.shape[1], 3)
        print('vertices are', vertices)

        if vertex_colors is None:
            vertex_colors = np.zeros(vertices.shape, dtype=np.float32)
            if colors is None:
                vertex_colors[:, 0] = color[0]
                vertex_colors[:, 1] = color[1]
                vertex_colors[:, 2] = color[2]
            else:
                vertex_colors[:, 0] = np.repeat(colors[:, 0], tube_points)
                vertex_colors[:, 1] = np.repeat(colors[:, 1], tube_points)
                vertex_colors[:, 2] = np.repeat(colors[:, 2], tube_points)

        indices = np.array(indices, dtype=np.uint32)

        print('color is', color)
        MeshVisual.__init__(self, vertices, indices,
                            vertex_colors=vertex_colors,
                            shading=shading,
                            color='r',
                            mode=mode)
                

    def draw(self, transforms):
        MeshVisual.draw(self, transforms)


def frenet_frames(points, closed):
    '''Calculates and returns the tangents, normals and binormals for
    the tube.'''
    tangents = np.zeros((len(points), 3))
    normals = np.zeros((len(points), 3))

    epsilon = 0.0001

    # Compute tangent vectors for each segment
    tangents = np.roll(points, -1, axis=0) - np.roll(points, 1, axis=0)
    mags = np.sqrt(np.sum(tangents * tangents, axis=1))
    tangents /= mags[:, np.newaxis]

    # Get initial normal and binormal
    t = np.abs(tangents[0])

    smallest = np.argmin(t)
    normal = np.zeros(3)
    normal[smallest] = 1.

    vec = np.cross(tangents[0], normal)

    normals[0] = np.cross(tangents[0], vec)

    # Compute normal and binormal vectors along the path
    for i in range(1, len(points)):
        normals[i] = normals[i-1]

        vec = np.cross(tangents[i-1], tangents[i])
        if mag(vec) > epsilon:
            vec /= mag(vec)

            theta = np.arccos(np.clip(tangents[i-1].dot(tangents[i]), -1, 1))
            normals[i] = rotation_about_axis(vec, theta).dot(normals[i])

    if closed:
        theta = np.arccos(np.clip(normals[0].dot(normals[-1]), -1, 1))
        theta /= len(points) - 1

        if tangents[0].dot(np.cross(normals[0], normals[-1])) > 0:
            theta *= -1.
            
        for i in range(1, len(points)):
            normals[i] = rotation_about_axis(
                tangents[i], theta*i).dot(normals[i])

    binormals = np.cross(tangents, normals)

    return tangents, normals, binormals
                


def mag(v):
    return np.sqrt(v.dot(v))


def rotation_about_axis(axis, angle):
    c = np.cos(angle)
    s = np.sin(angle)
    t = 1. - c
    x, y, z = axis
    tx = t*x
    ty = t*y
    tz = t*z

    return np.array([[tx*x + c, tx*y - s*z, tx*z + s*y],
                     [tx*y + s*z, ty*y + c, ty*z - s*x],
                     [tx*z - s*y, ty*z + s*x, tz*z + c]])
            
