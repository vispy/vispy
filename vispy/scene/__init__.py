"""
The vispy.scene namespace provides functionality for higher level
visuals as well as scenegraph and related classes.


Some docs/ideas about the key scenegraph concepts:

class Entity:
  The base object of an object in a scene graph.
  - parent: the parent(s) that this object is a child of
  - children: the children (sub-entities) for this entity
  - transform: the transform from the parent to local coordinate frame

class Widget:
  - size: the extend (w, h) of the widget

class ViewBox:
  A viewbox provides a rectangular pixel grid to render the subscene
  to. The viewbox defines a certain coordinate frame using a camera
  (which is an entity in the subscene itself). A viewbox also defines
  lights, and has its own drawing system.
  - resolution: the size (w, h) of the "canvas" that this viewbox exposes.

  The transform of the root viewbox is not used at all, since there is
  no parent to define a transformation to.
  
  A Viewbox can work in three ways:
  - via a viewport
  - via a simple transform
  - via an FBO
  
  The first two cases can work in case the viewbox maps to a rectangular
  grid of an underlying viewbox, and if the size of the region that the
  viewbox takes up in the parent subscene matches with the resolution.
  If either requirements are not met, we need an FBO. 
  
  Using a transform rather than a viewport may have some performance
  advantages, but we need to do clipping in the fragment shader, which
  poses additional complexity and performance overhead. It probably
  depends on the situation what works best. We probably want to allow
  both approaches.

"""

from .entity import Entity
from .canvas import SceneCanvas
from .viewbox import ViewBox
from . import visuals
from . import widgets
from . import cameras
