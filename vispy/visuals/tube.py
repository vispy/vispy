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
    def __init__(self, points, radius=1.0, circle_points=6,
                 closed=False,
                 vertex_colors=None, face_colors=None,
                 color=(1, 1, 0, 1)):

        vtype = [('position', np.float32, 3),
                 ('texcoord', np.float32, 2),
                 ('normal', np.float32, 3),
                 ('color', np.float32, 4)]

        positions = np.zeros((len(points), 3))
        vertices = np.zeros(len(points), vtype)

        # broken
        if vertex_colors is None:
            vertex_colors = np.array([color for _ in range(len(points))])

        vertices, filled_indices, outline_indices = create_cube()

        tangents, normals, binormals = frenet_frames(points, closed)
        print('tangents are', tangents)
        print('normals are', normals)
        print('binormals are', binormals)

        segments = len(points) - 1

        # get the positions of each vertex
        grid = np.zeros((len(points), circle_points, 3))
        for i in range(len(points)):
            pos = points[i]
            tangent = tangents[i]
            normal = normals[i]
            binormal = binormals[i]

            for j in range(circle_points):
                v = float(j) / circle_points * 2 * np.pi
                cx = -1. * radius * np.cos(v)
                cy = radius * np.sin(v)

                pos2 = pos.copy()
                pos2[0] += cx * normal[0] + cy*binormal[0]
                pos2[1] += cx * normal[1] + cy*binormal[1]
                pos2[2] += cx * normal[2] + cy*binormal[2]
                grid[i, j] = pos2

        # construct the mesh
        faces = []
        tex_coords = []
        for i in range(segments):
            for j in range(circle_points):
                ip = (i+1) % segments if closed else i+1
                jp = (j+1) % circle_points

                a = grid[i, j]
                b = grid[ip, j]
                c = grid[ip, jp]
                d = grid[i, jp]

                uva = np.array([i / segments, j / circle_points])
                uvb = np.array([(i+1) / segments, j / circle_points])
                uvc = np.array([(i+1) / segments, (j+1) / circle_points])
                uvb = np.array([i / segments, (j+1) / circle_points])

                faces.append([a, b, d])
                tex_coords.append([uva, uvb, uvd])

                faces.append([b, c, d])
                tex_coords.append([uvb, uvc, uvd])

        faces = n.array(faces)
        tex_coords = n.array(tex_coords)
        print('faces are', faces)
                

    def draw(self, transforms):
        MeshVisual.draw(self, transforms)


def frenet_frames(points, closed):
    '''Calculates and returns the tangents, normals and binormals for
    the tube.'''
    tangents = np.zeros((len(points), 3))
    normals = np.zeros((len(points), 3))
    binormals = np.zeros((len(points), 3))

    num_points = len(points)
    epsilon = 0.0001

    # Compute tangent vectors for each segment
    tangents = np.roll(points, -1, axis=0) - np.roll(points, 1, axis=0)
    mags = np.sqrt(np.sum(tangents * tangents, axis=1))
    for i, m in enumerate(mags):
        tangents[i] /= m

    # Get initial normal and binormal
    t = np.abs(tangents[0])

    smallest = np.argmin(t)
    normal = np.zeros(3)
    normal[smallest] = 1.

    vec = np.cross(tangents[0], normal)
    print('mag vec is', np.sqrt(np.sum(vec)))

    normals[0] = np.cross(tangents[0], vec)
    binormals[0] = np.cross(tangents[0], normals[0])

    # Compute normal and binormal vectors along the path
    for i in range(1, len(points)):
        normals[i] = normals[i-1]
        binormals[i] = binormals[i-1]

        vec = np.cross(tangents[i-1], tangents[i])
        if mag(vec) > epsilon:
            vec /= mag(vec)

            theta = np.arccos(np.clip(tangents[i-1].dot(tangents[i]), -1, 1))
            normals[i] = rotation_about_axis(vec, theta).dot(normals[i])

        binormals[i] = np.cross(tangents[i], normals[i])

    if closed:
        theta = np.arccos(np.clip(normals[0].dot(normals[-1]), -1, 1))
        theta /= len(points) - 1

        if tangents[0].dot(np.cross(normals[0], normals[-1])) > 0:
            theta *= -1.
            
        for i in range(1, len(points)):
            normals[i] = rotation_about_axis(
                tangents[i], theta*i).dot(normals[i])
            binormals[i] = np.cross(tangents[i], normals[i])

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
            
