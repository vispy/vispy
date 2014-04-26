import numpy as np
from .entity import Entity
from .viewbox import ViewBox
from . import transforms

class Camera(Entity):
    """ The Camera class defines the viewpoint from which a scene is
    visualized. It is itself an Entity (with transformations) but by
    default does not draw anything.
    
    Next to the normal transformation, a camera also defines a
    projection tranformation that defines the camera view. This can for
    instance be orthographic, perspective, log, polar, etc.
    """
    
    def __init__(self, parent=None):
        Entity.__init__(self, parent)
        
        # Can be orthograpic, perspective, log, polar, map, etc.
        # Default unit
        self._projection = transforms.NullTransform()
    
    
    def get_projection(self, viewbox):
        """ Get the projection matrix. Should be overloaded by camera
        classes to define the projection of view.
        """
        return self._projection

    
    def on_mouse_press(self, event):
        pass
    
    def on_mouse_move(self, event):
        pass
    
    def get_camera_transform(self):
        """ Calculate the transformation matrix of the camera to the scene
        (i.e. the transformation is already inverted).
        This is used by the drawing system to establish the view matrix.
        """
        # note: perhaps a camera should have a transform that can only 
        # translate and rotate... on the other hand, a parent entity
        # could have a scaling in it, so we need to remove the scaling anyway...
        
        # Get total transform of the camera
        object = self
        camtransform = object.transform
        
        while True:
            # todo: does it make sense to have a camera in a multi-path scene?
            object = object.parents[0]
            if object is None:
                break  # Root viewbox
            elif isinstance(object, ViewBox):
                break  # Go until the any parent ViewBox
            assert isinstance(object, Entity)
            if object.transform is not None:
                camtransform = camtransform * object.transform
                #camtransform[...] = np.dot(camtransform, object.transform)
        
        # We are only interested in translation and rotation,
        # so we set the scaling to unit
        #camtransform[np.eye(4,dtype=np.bool)] = 1.0
        # NO! This screws up rotations. So either we live with the fact 
        # that scaling also scales the camera view, or we find a real way
        # of normalizing the homography matrix for scale.
        
        # Return inverse!
        return camtransform.inverse()
        # todo: I don't like depending on np on this ...
        # glsl can do this for us too. Or is 4x4 matrix inversion easy?
        #return np.linalg.inv(camtransform)





class NDCCamera(Camera):
    """ Camera that presents a view on the world in normalized device
    coordinates (-1..1).
    """
    pass



class PixelCamera(Camera):
    """ Camera that presents a view on the world in pixel coordinates.
    The coordinates map directly to the viewbox coordinates. The origin
    is in the upper left.
    """
    def get_projection(self, viewbox):
        w, h = viewbox.resolution
        from vispy.util import transforms as trans
        projection = np.eye(4)
        trans.scale(projection, 2.0/w, 2.0/h)
        trans.translate(projection, -1, -1)
        trans.scale(projection, 1, -1)  # Flip y-axis
        return transforms.AffineTransform(projection)



class TwoDCamera(Camera):
    def __init__(self, parent=None):
        Camera.__init__(self, parent)
        self.fov = 1, 1
    
    # xlim and ylim are convenience methods to set the view using limits
    @property
    def xlim(self):
        x = self.transform[-1, 0]
        dx = self.fov[0] / 2.0
        return x-dx, x+dx
    
    @property
    def ylim(self):
        y = self.transform[-1, 1]
        dy = self.fov[1] / 2.0
        return y-dy, y+dy
    
    @xlim.setter
    def xlim(self, value):
        x = 0.5 * (value[0] + value[1])
        rx = max(value) - min(value)
        self.fov = rx, self.fov[1]
        self.transform[-1,0] = x
    
    
    @ylim.setter
    def ylim(self, value):
        y = 0.5 * (value[0] + value[1])
        ry = max(value) - min(value)
        self.fov = self.fov[0], ry
        self.transform[-1,1] = y
    
    
    def get_projection(self, viewbox):
        w, h = self.fov
        from vispy.util import transforms as trans
        projection = np.eye(4)
        trans.scale(projection, 2.0/w, 2.0/h)
        trans.scale(projection, 1, -1)  # Flip y-axis
        return transforms.AffineTransform(projection)
        
    
    def on_mouse_press(self, event):
        pass
    
    def on_mouse_move(self, event):
        if event.is_dragging:
            
            # Get (or set) the reference position)
            if hasattr(event.press_event, 'reflim'):
                pos, fov = event.press_event.reflim
            else:
                pos = self.transform[-1,0], self.transform[-1,1]
                pos, fov = event.press_event.reflim = pos, self.fov
            
            # Get the delta position
            startpos = event.press_event.pos
            curpos = event.pos
            dpos = curpos[0] - startpos[0], curpos[1] - startpos[1] 
            
            if 1 in event.buttons:
                # Pan
                self.transform[-1,0] = pos[0] - dpos[0] / 2
                self.transform[-1,1] = pos[1] - dpos[1] / 2
                #dx, dy = -dpos[0] / 2, -dpos[1] / 2
                #self.xlim = xlim[0]+dx, xlim[1]+dx
                #self.ylim = ylim[0]+dy, ylim[1]+dy
            elif 2 in event.buttons:
                # Zoom
                self.fov = (    fov[0] - dpos[0] / 2,
                                fov[1] + dpos[1] / 2  )
                #dx, dy = -dpos[0] / 2, dpos[1] / 2
                #self.xlim = xlim[0]-dx, xlim[1]+dx
                #self.ylim = ylim[0]-dy, ylim[1]+dy
            
            # Force redraw
            event.source.update()



class ThreeDCamera(Camera):
    def __init__(self, parent=None):
        Camera.__init__(self, parent)
        
        self._pos = 200, 200, 200
        self._fov = 45.0
        
        self._view_az = -10.0 # azimuth
        self._view_el = 30.0 # elevation
        self._view_ro = 0.0 # roll
        self._fov = 0.0 # field of view - if 0, use ortho view
    
    def on_mouse_move(self, event):
        
        if not event.is_dragging:
            return
        
        if 1 in event.buttons:
            # rotate
            
            # Get (or set) the reference position)
            if hasattr(event.press_event, '_refangles'):
                refangles = event.press_event._refangles
            else:
                refangles = self._view_az, self._view_el, self._view_ro
                event.press_event._refangles = refangles
            
            # Get the delta position
            startpos = event.press_event.pos
            curpos = event.pos
            dpos = curpos[0] - startpos[0], curpos[1] - startpos[1] 
            
            # get normalized delta values
            sze = 400, 400 # todo: get from viewbox
            d_az = dpos[0] / sze[0]
            d_el = dpos[1] / sze[1]
            
            # change az and el accordingly
            self._view_az = refangles[0] - d_az * 90.0
            self._view_el = refangles[1] + d_el * 90.0
            
            # keep within bounds            
            while self._view_az < -180:
                self._view_az += 360
            while self._view_az >180:
                self._view_az -= 360
            if self._view_el < -90:
                self._view_el = -90
            if self._view_el > 90:
                self._view_el = 90
            #print(self._view_az, self._view_el)
            
            # Init matrix 
            M = np.eye(4)
            
            
            
            
            # Move camera backwards to account for perspective
            # this should actually be triggered by change in fov.
            transforms.translate(M, 0, 0, self._d)
            
            # Rotate it
            transforms.rotate(M, self._view_ro, 0, 0, 1)
            transforms.rotate(M, 270-self._view_el, 1, 0, 0)
            transforms.rotate(M, -self._view_az, 0, 0, 1)
            
            # Translate it
            transforms.translate(M, *self._pos)
            
            # Translate it with previous transform
            # This should also work, because position and rotation 
            # are stored in different elements of the matrix ...
            
#             transforms.translate(M, self.transform[-1, 0],
#                                     self.transform[-1, 1],
#                                     self.transform[-1, 2])
            
            # Apply
            self._transform = M
    
    
    def get_projection(self, viewbox):
        
        w, h = viewbox.resolution
        
        fov = self._fov
        aspect = 1.0
        fx, fy = 600.0, 600.0 # todo: hard-coded
        
        # Calculate distance to center in order to have correct FoV and fy.
        if fov == 0:
            M = transforms.ortho(-0.5*fx, 0.5*fx, -0.5*fy, 0.5*fy, -10000, 10000)
            self._d = 0
        else:
            d = fy / (2 * math.tan(math.radians(fov)/2))
            val = math.sqrt(10000)  # math.sqrt(getDepthValue())
            znear, zfar = d/val, d*val
            M = transforms.perspective(fov, aspect, znear, zfar)
            self._d = d
            #transforms.translate(M, 0, 0, d)  # move camera backwards - done in on_mouse_move
        
        
        # Translation and rotation is done by our 'transformation' parameter
        
        return M
        

from cybertools.util import Quaternion


class FirstPersonCamera(Camera):
    
    def __init__(self, parent=None):
        Camera.__init__(self, parent)
        
        self._pos = 200, 200, 200
        self._fov = 45.0  # field of view - if 0, use ortho view
        
        # todo: we probably want quaternions here ...
        self._view_az = 0.0 # azimuth
        self._view_el = 0.0 # elevation
        self._view_ro = 0.0 # roll
        
        self._orientation = Quaternion()
        
    
    def update_angles(self):
        """ Temporary method to turn angles into our transform matrix.
        """
        orientation = self._orientation.normalize()
        M = orientation.get_matrix()
        
        # Translate it
        transforms.translate(M, *self._pos)
        
        # Apply
        self._transform = M
        
    
    def get_projection(self, viewbox):
        
        w, h = viewbox.resolution
        
        fov = self._fov
        aspect = 1.0
        fx = fy = 1.0 # todo: hard-coded
        
        # Calculate distance to center in order to have correct FoV and fy.
        if fov == 0:
            M = transforms.ortho(-0.5*fx, 0.5*fx, -0.5*fy, 0.5*fy, -10000, 10000)
            self._d = 0
        else:
            d = fy / (2 * math.tan(math.radians(fov)/2))
            val = math.sqrt(10000)  # math.sqrt(getDepthValue())
            znear, zfar = d/val, d*val
            M = transforms.perspective(fov, aspect, znear, zfar)
        
        # Translation and rotation is done by our 'transformation' parameter
        return M
        
        
    
        