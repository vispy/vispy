"""
The vispy.scene namespace provides functionality for higher level
visuals as well as scenegraph and related classes.


Terminology
-----------

* entity - an object that lives in the scenegraph. It can have zero or
  more children and zero or more parents (although one is recommended).
  It also has a transform that maps the local coordinate frame to the
  coordinate frame of the parent.
  
* scene - a complete connected graph of entities.
  
* subscene - the entities that are children of a viewbox. Any viewboxes
  inside this subscene are part of the subscene, but not their children.
  The SubScene class is the toplevel entity for any subscene. Each
  subscene has its own camera, lights, aspect ratio, etc.
  
* visual - an entity that has a visual representation. It can be made
  visible/invisible and also has certain bounds.
  
* widget - an entity of a certain size that provides interaction. It
  is made to live in a 2D scene with a pixel camera.
  
* viewbox - an entity that provides a rectangular window to which a
  subscene is rendered. Clipping is performed in one of several ways.
  
* camera - an entity that specifies how the subscene of a viewbox is
  rendered to the pixel grid. It determines position and orientation
  (through its transform) an projection (through a special
  transformation property). Some cameras also provide interaction (e.g.
  zooming). Although there can be multiple cameras in a subscene, each
  subscene has one active camera.

* viewport - as in glViewPort, a sub pixel grid in a framebuffer.
  
* drawing system - a part of the viewbox that takes care of rendering
  a subscene to the pixel grid of that viewbox.

"""

from .entity import Entity
from .canvas import SceneCanvas
from .viewbox import ViewBox
from . import visuals
from . import widgets
from . import cameras
