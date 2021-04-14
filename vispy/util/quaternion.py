# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# Based on the quaternion class in the visvis project.

import numpy as np


class Quaternion(object):
    """Quaternion(w=1, x=0, y=0, z=0, normalize=True)

    A quaternion is a mathematically convenient way to
    describe rotations.

    """

    def __init__(self, w=1, x=0, y=0, z=0, normalize=True):

        self.w = float(w)
        self.x, self.y, self.z = float(x), float(y), float(z)
        if normalize:
            self._normalize()

    def __repr__(self):
        return "<Quaternion object %1.3g + %1.3gi + %1.3gj + %1.3gk>" % (
               self.w, self.x, self.y, self.z)

    def copy(self):
        """Create an exact copy of this quaternion."""
        return Quaternion(self.w, self.x, self.y, self.z, False)

    def norm(self):
        """Returns the norm of the quaternion

        norm = w**2 + x**2 + y**2 + z**2
        """
        tmp = self.w**2 + self.x**2 + self.y**2 + self.z**2
        return tmp**0.5

    def _normalize(self):
        """Make the quaternion unit length."""
        # Get length
        L = self.norm()
        if not L:
            raise ValueError('Quaternion cannot have 0-length.')
        # Correct
        self.w /= L
        self.x /= L
        self.y /= L
        self.z /= L

    def normalize(self):
        """Returns a normalized (unit length) version of the quaternion."""
        new = self.copy()
        new._normalize()
        return new

    def conjugate(self):
        """Obtain the conjugate of the quaternion.

        This is simply the same quaternion but with the sign of the
        imaginary (vector) parts reversed.
        """
        new = self.copy()
        new.x *= -1
        new.y *= -1
        new.z *= -1
        return new

    def inverse(self):
        """Returns q.conjugate()/q.norm()**2

        So if the quaternion is unit length, it is the same
        as the conjugate.
        """
        new = self.conjugate()
        tmp = self.norm()**2
        new.w /= tmp
        new.x /= tmp
        new.y /= tmp
        new.z /= tmp
        return new

    def exp(self):
        """Returns the exponent of the quaternion. 
        (not tested)
        """
        # Init
        vecNorm = self.x**2 + self.y**2 + self.z**2
        wPart = np.exp(self.w)        
        q = Quaternion()

        # Calculate
        q.w = wPart * np.cos(vecNorm)
        q.x = wPart * self.x * np.sin(vecNorm) / vecNorm
        q.y = wPart * self.y * np.sin(vecNorm) / vecNorm
        q.z = wPart * self.z * np.sin(vecNorm) / vecNorm

        return q

    def log(self):
        """Returns the natural logarithm of the quaternion. 
        (not tested)
        """
        # Init
        norm = self.norm()
        vecNorm = self.x**2 + self.y**2 + self.z**2
        tmp = self.w / norm
        q = Quaternion()

        # Calculate
        q.w = np.log(norm)
        q.x = np.log(norm) * self.x * np.arccos(tmp) / vecNorm
        q.y = np.log(norm) * self.y * np.arccos(tmp) / vecNorm
        q.z = np.log(norm) * self.z * np.arccos(tmp) / vecNorm

        return q

    def __add__(self, q):
        """Add quaternions."""
        new = self.copy()
        new.w += q.w
        new.x += q.x
        new.y += q.y
        new.z += q.z
        return new

    def __sub__(self, q):
        """Subtract quaternions."""
        new = self.copy()
        new.w -= q.w
        new.x -= q.x
        new.y -= q.y
        new.z -= q.z
        return new

    def __mul__(self, q2):
        """Multiply two quaternions."""
        new = Quaternion()
        q1 = self       
        new.w = q1.w*q2.w - q1.x*q2.x - q1.y*q2.y - q1.z*q2.z
        new.x = q1.w*q2.x + q1.x*q2.w + q1.y*q2.z - q1.z*q2.y
        new.y = q1.w*q2.y + q1.y*q2.w + q1.z*q2.x - q1.x*q2.z
        new.z = q1.w*q2.z + q1.z*q2.w + q1.x*q2.y - q1.y*q2.x
        return new

    def rotate_point(self, p):
        """Rotate a Point instance using this quaternion."""
        # Prepare 
        p = Quaternion(0, p[0], p[1], p[2], False)  # Do not normalize!
        q1 = self.normalize()
        q2 = self.inverse()
        # Apply rotation
        r = (q1*p)*q2
        # Make point and return        
        return r.x, r.y, r.z

    def get_matrix(self):
        """Create a 4x4 homography matrix that represents the rotation
        of the quaternion.
        """
        # Init matrix (remember, a matrix, not an array)
        a = np.zeros((4, 4), dtype=np.float32)
        w, x, y, z = self.w, self.x, self.y, self.z
        # First row
        a[0, 0] = - 2.0 * (y * y + z * z) + 1.0
        a[1, 0] = + 2.0 * (x * y + z * w)
        a[2, 0] = + 2.0 * (x * z - y * w)
        a[3, 0] = 0.0
        # Second row
        a[0, 1] = + 2.0 * (x * y - z * w)
        a[1, 1] = - 2.0 * (x * x + z * z) + 1.0
        a[2, 1] = + 2.0 * (z * y + x * w)
        a[3, 1] = 0.0
        # Third row
        a[0, 2] = + 2.0 * (x * z + y * w)
        a[1, 2] = + 2.0 * (y * z - x * w)
        a[2, 2] = - 2.0 * (x * x + y * y) + 1.0
        a[3, 2] = 0.0
        # Fourth row
        a[0, 3] = 0.0
        a[1, 3] = 0.0
        a[2, 3] = 0.0
        a[3, 3] = 1.0
        return a

    def get_axis_angle(self):
        """Get the axis-angle representation of the quaternion. 
        (The angle is in radians)
        """
        # Init
        angle = 2 * np.arccos(max(min(self.w, 1.), -1.))
        scale = (self.x**2 + self.y**2 + self.z**2)**0.5    

        # Calc axis
        if scale:
            ax = self.x / scale
            ay = self.y / scale
            az = self.z / scale
        else:
            # No rotation, so arbitrary axis
            ax, ay, az = 1, 0, 0
        # Return
        return angle, ax, ay, az

    @classmethod
    def create_from_axis_angle(cls, angle, ax, ay, az, degrees=False):
        """Classmethod to create a quaternion from an axis-angle representation. 
        (angle should be in radians).
        """
        if degrees:
            angle = np.radians(angle)
        while angle < 0:
            angle += np.pi*2
        angle2 = angle/2.0
        sinang2 = np.sin(angle2)
        return Quaternion(np.cos(angle2), ax*sinang2, ay*sinang2, az*sinang2)

    @classmethod
    def create_from_euler_angles(cls, rx, ry, rz, degrees=False):
        """Classmethod to create a quaternion given the euler angles."""
        if degrees:
            rx, ry, rz = np.radians([rx, ry, rz])
        # Obtain quaternions
        qx = Quaternion(np.cos(rx/2), 0, 0, np.sin(rx/2))
        qy = Quaternion(np.cos(ry/2), 0, np.sin(ry/2), 0)
        qz = Quaternion(np.cos(rz/2), np.sin(rz/2), 0, 0)
        # Almost done
        return qx*qy*qz   
