import numpy as np

from vispy.visuals.transforms import BaseTransform, AffineTransform
from vispy.util.quaternion import Quaternion
from vispy.util import transforms

# todo: rename to simply Transform

class DefaultTransform(BaseTransform):
    """ A transform that supports translation, rotation and scaling

    Instances of this class keep track of the complexity of the
    transformation, and internally describe it in a manner that allows
    for the most effective composition and inversion.
    
    Parameters
    ----------
    scale : None | scalar | tuple of 3 scalars
        The initial scaling for this transform. See ``scale()`` for
        details,
    rotate : None | quaternion
        The initial rotation for this transform. See ``rotate()`` for
        details.
    translate : None | tuple of 3 scalars
        The initial translation for this transform. See ``translate()``
        for details.
    matrix : None | 4x4 numpy array
        The initial transform represented with a matrix. See
        ``set_matrix()`` for details.
    
    Efficiency
    ----------
    If possible, the transformation is internally described using a
    translation vector, a scale vector and a quaternion. When the
    transform becomes such that it can no longer be described with these
    parameters, a 4x4 matrix is used for the internal description. In
    the former case, operations like taking the inverse and composing
    transforms can be done more efficiently.
    
    Whether or not the matrix must be used depends on whether the
    transformation contains any shearing (caused by a rotation followed
    by a scaling).
    """
    
    glsl_map = """
        vec4 default_transform_map(vec4 pos) {
            return $matrix * pos;
        }
    """

    glsl_imap = """
        vec4 default_transform_imap(vec4 pos) {
            return $inv_matrix * pos;
        }
    """
    
    Linear = True
    
    @property
    def IsIdentity(self):
        return self._is_identity
    
    @property
    def IsShearless(self):
        """ When the transformation does not contain shearing, the
        internal representation is not stored in a matrix, allowing for
        more efficient composition and inversion.
        """
        return self._matrix is None
    
    def __init__(self, scale=None, rotate=None, translate=None, matrix=None):
        BaseTransform.__init__(self)
        
        self._reset()
        
        if scale is not None:
            self.scale(scale)
        if rotate is not None:
            self.rotate(rotate)
        if translate is not None:
            self.translate(translate)
        if matrix is not None:
            assert (scale is None and rotate is None and translate is None)
            self.set_matrix(matrix)
    
    def _reset(self):
        # Efficient internal representation
        self._translation = 0.0, 0.0, 0.0
        self._scaling = 1.0, 1.0, 1.0
        self._rotation = Quaternion()
        
        # Fallback internal representation
        self._matrix = None
        
        # Caches for matrices
        self._cache_matrix = None
        self._cache_inv_matrix = None
        
        # Flags
        self._has_translation = False  # updated in translate()
        self._has_scaling = False  # updated in scale()
        self._has_rotation = False  # updated in rotate()
        self._is_identity = True  # updated in update()
    
    def __repr__(self):
        if self.IsIdentity:
            t = '<%s identity>'
            return t % (self.__class__.__name__, )
        if self.IsShearless:
            trans = ', '.join(['%1.4g' % x for x in self._translation])
            scale = ', '.join(['%1.4g' % x for x in self._scaling])
            rotate = ', '.join(['%1.4g' % x for x in self._rotation])
            trans = trans if self._has_translation else 'none'
            scale = scale if self._has_scaling else 'none'
            rotate = rotate if self._has_rotation else 'none'
            
            t = '<%s t(%s) s(%s) r(%s)>'
            return t % (self.__class__.__name__, trans, scale, rotate)
        else:
            s = "<%s([" % self.__class__.__name__
            indent = " " * len(s)
            s += str(list(self._matrix[0])) + ",\n"
            s += indent + str(list(self._matrix[1])) + ",\n"
            s += indent + str(list(self._matrix[2])) + ",\n"
            s += indent + str(list(self._matrix[3])) + "]>"
            return s
    
    def update(self):
        BaseTransform.update(self)
        # invalide
        self._cache_matrix = None
        self._cache_inv_matrix = None
        # Check identity
        if self._matrix is None:
            self._is_identity = not (self._has_translation or 
                                     self._has_scaling or 
                                     self._has_rotation)
        else:
            self._is_identity = False
    
    ## Methods that change the transformation
    
    def reset(self):
        """ Set the transform back to the identity transform.
        """
        self._reset()
        self.update()
    
    def set_matrix(self, matrix):
        """ Set the transform to the given 4x4 matrix
        
        Techcnically, the given matrix can describe any transformation,
        but it is recommended to restrict to transformations composed
        only of scaling, rotations and translations.
        
        It is recommended to not use this method unless the transform
        can only be described with a matrix, because setting the matrix
        will put the transform in a mode where inversion and composition
        are less efficient.
        """
        matrix = np.array(matrix, copy=False)  # if list or matrix was given
        assert matrix.shape == (4, 4)
        self._matrix = matrix
        self.update()
    
    # todo: set_mapping 2D and 3D
    
    # todo: set_ortho? set_perspective?
    
    def translate(self, offset):
        """ Translate the transform.
        
        The translation is applied *after* the transformations already
        present in the matrix.
        """
        dx, dy, dz = offset
        
        if self._matrix is None:
            tx, ty, tz = self._translation
            self._translation = float(tx+dx), float(ty+dy), float(tz+dz)
            self._has_translation = any(self._translation)
        else:
            transmat = transforms.translate((dx, dy, dz))
            self._matrix = np.dot(self._matrix, transmat)
        
        self.update()
    
    def rotate(self, angle, axis=None, deg=True):
        """ Rotate the transform with angle degrees/radians around the axis.
        
        Also accepts a Quaternion object as a single argument.
        
        The rotation is applied *after* the transformations already
        present in the matrix.
        """
        if isinstance(angle, Quaternion):
            q = angle
        else:
            angle = float(angle)
            ax, ay, az = axis
            q = Quaternion.create_from_axis_angle(angle, ax, ay, az, deg)
            
        if self._matrix is None:
            tx, ty, tz = self._translation
            self._translation = q.rotate_point((tx, ty, tz))
            self._rotation = (q * self._rotation)#.normalize()
            qq = self._rotation
            self._has_rotation = qq.w != 1.0 or any(tuple(qq)[1:])
        else:
            rotmat = q.get_matrix()
            self._matrix = np.dot(self._matrix, rotmat)
        
        self.update()
    
    def scale(self, scale):
        """ Scale the transform with a scalar value or a 3-element tuple.
        
        The scaling is applied *after* the transformations already
        present in the matrix.
        
        In case the scaling is non-isometric (not equal for each
        dimension) and the transform already applies a rotation, the
        transform will internally be represented with a matrix from
        here on.
        """
        if isinstance(scale, (float, int)):
            dx = dy = dz = float(scale)
        else:
            dx, dy, dz = scale
        
        if self._matrix is None:
            # Here we check whether we are going to end up with shearing
            # in our transform. This occurs when we append a
            # non-isometric scaling to a transform that contains a
            # rotation. When this happens, we can no longer represent
            # the transform with the trans/scale/quaternion, and need
            # to go into matrix-mode.
            if self._has_rotation and not (dx == dy and dx == dz):
                self._matrix = self.get_matrix()
                return self.scale((dx, dy, dz))
            
            tx, ty, tz = self._translation
            sx, sy, sz = self._scaling
            self._translation = float(tx*dx), float(ty*dy), float(tz*dz)
            self._scaling = float(sx*dx), float(sy*dy), float(sz*dz)
            self._has_scaling = any([x!=1.0 for x in self._scaling])
        else:
            scalemat = transforms.scale((dx, dy, dz))
            self._matrix = np.dot(self._matrix, scalemat)
        self.update()
    
    ## Getting transforms and applying mappings
    
    def get_matrix(self):
        """ Get the matrix that represents the transformation.
        
        The result is cached, so that subsequent calls are fast.
        """
        if self._cache_matrix is None:
            if self._matrix is None:
                m = np.eye(4)
                if self._has_scaling:
                    m = np.dot(m, transforms.scale(self._scaling))
                if self._has_rotation:
                    m = np.dot(m, self._rotation.get_matrix())
                if self._has_translation:
                    m = np.dot(m, transforms.translate(self._translation))
                self._cache_matrix = m
            else:
                self._cache_matrix = self._matrix
        return self._cache_matrix
    
    def get_inv_matrix(self):
        """ Get the matrix that represents the inverse transformation.
        
        The result is cached, so that subsequent calls are fast.
        """
        if self._cache_inv_matrix is None:
            if self._matrix is None:
                m = np.eye(4)
                if self._has_translation:
                    m = np.dot(m, -transforms.translate(self._translation))
                if self._has_rotation:
                    m = np.dot(m, self._rotation.inverse().get_matrix())
                if self._has_scaling:
                    m = np.dot(m, 1.0 / transforms.scale(self._scaling))
                self._cache_inv_matrix = m
            else:
                self._cache_inv_matrix = np.linalg.inv(self._matrix)
        return self._cache_inv_matrix
    
    def map(self, coords):
        coords = np.array(coords, 'float64')
        assert coords.shape == (3, )
        
        if self._is_identity:
            return coords
        elif self._matrix is None:
            # Order: scale, rotate, translate
            if self._has_scaling:
                coords *= self._scaling
            if self._has_rotation:
                coords = np.array(self._rotation.rotate_point(coords))
            if self._has_translation:
                coords += self._translation
            return np.concatenate((coords, [1]))  # todo: what should w return?
        else:
            # Apply matrix
            return np.dot(np.concatenate((coords, [1])), self._matrix)
    
    def imap(self, coords):
        coords = np.array(coords, 'float64')
        assert coords.shape == (3, )
        
        if self._is_identity:
            return coords
        elif self._matrix is None:
            # Order: translate, rotate, scale
            if self._has_translation:
                coords -= self._translation
            if self._has_rotation:
                irot = self._rotation.inverse()
                coords = np.array(irot.rotate_point(coords))
            if self._has_scaling:
                coords /= self._scaling
            return np.concatenate((coords, [1])).shape
        else:
            return np.dot(coords, self.get_inv_matrix())
    
    def shader_map(self):
        fn = BaseTransform.shader_map(self)
        fn['matrix'] = self.get_matrix()  # uniform mat4
        return fn

    def shader_imap(self):
        fn = BaseTransform.shader_imap(self)
        fn['inv_matrix'] = self.get_inv_matrix()  # uniform mat4
        return fn
    
    ## Methods that yield new transforms
    
    def copy(self):
        """ Create a copy of this transform.
        """
        if self._is_identity:
            return DefaultTransform()
        elif self._matrix is None:
            return DefaultTransform(self._scaling, self._rotation,
                                    self._translation)
        else:
            return DefaultTransform(matrix=self._matrix)
    
    def inverse(self):
        """ Get the inverse of this transform.
        """
        if self._is_identity:
            return DefaultTransform()
        elif self._matrix is None:
            # todo: the inverse of a non-shearing transform can be shearing?
            t = DefaultTransform()
            if self._has_translation:
                t.translate([-x for x in self._translation])
            if self._has_scaling:
                t.scale([1/x for x in self._scaling])
            if self._has_rotation:
                t.rotate(self._rotation.inverse())
            return t
        else:
            return DefaultTransform(matrix=self.get_inv_matrix())
    
    def __mul__(self, tr):
        """ Compose this transform with another.
        """
        if isinstance(tr, DefaultTransform):
            
            if tr._is_identity:
                return self.copy()
            elif self._is_identity:
                return tr.copy()
            elif tr.IsShearless and self.IsShearless:
                ret = DefaultTransform()
                ret.scale(self._scaling)
                ret.rotate(self._rotation)
                ret.translate(self._translation)
                ret.scale(tr._scaling)
                ret.rotate(tr._rotation)
                ret.translate(tr._translation)
                return ret
            else:
                matrix = np.dot(self.get_matrix(), tr.get_matrix())
                return DefaultTransform(matrix=matrix)
        
        else:
            raise RuntimeError('What should we do?')
