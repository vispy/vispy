"""
The vispy.scene namespace provides functionality for higher level
visuals as well as scenegraph and related classes.


Terminology
-----------

* entity - an object that lives in the scenegraph. It can have zero or
  more children and zero or more parents (although one is recommended).
  It also has a transform that specifies that transformation from the
  parent to the local coordinate frame.
  
* scene - a complete connected graph of entities.
  
* subscene - the entities that are children of a viewbox. Any viewboxes
  inside this subscene are part of the subscene, but not their children.
  
* visual - an entity that has a visual representation. It can be made
  visible/invisible and also has certain bounds.
  
* widget - an entity of a certain size that provides interaction. It
  is made to live in a 2D scene with a pixel camera.
  
* viewbox - an entity that provides a pixel grid for its children (i.e.
  the subscene). It *can* use a viewport for this, but t can also do
  this via a transform or an fbo. Each viewbox has its own camera, its
  own lights, etc.
  
* camera - an entity that specifies how the subscene of a viewbox is
  rendered to the pixel grid. It determines position and orientation
  (through its transform) an projection (through a special
  transformation property). Some cameras also provide interaction (e.g.
  zooming). Although there can be multiple cameras in a subscene, each
  viewbox has one active camera.
  
* pixel grid - a uniform rectangular grid of a certain resolution that
  can be rendered to.
  
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
