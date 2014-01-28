# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
This package defines the scene graph and associated classes.


**The Entity**

Vispy uses an entity-component system to make up the scene graph; each
entity is a node in the scene graph, a "thing" inside the scene. Most
entities are visible, but they do not have to be. Each entity has its
own coordinate system. The transform attribute defines how its
coordinate system is transformed from the coordinate system of the
parent. In that way, the scene graph represents the hierarchy of
transformations.

Each entity has several components. A common component is the visual,
which defines how that entity is drawn. Each scene has several systems
that process the graph of entities to perform a certain task. The
drawing system, for example, is responsible for drawing all the entities
by using the visual components.


**Graph properties**


Mathematically speaking, the scene is represented by a weakly connected
directed graph. Entities are allowed to have multiple parents (although
we recommend using this feature only in specific situations). Circular
references (cyclic graphs) should be avoided.


**The ViewBox**


The ViewBox is a special Entity that represents the root of a scene. A
scene can in turn contain a ViewBox that contains its own sub-scene.

The purpose of the ViewBox is to: 1) provide a rectangular region to
render the scene within the viewbox to; 2) provide a user-definable
transformation for rendering the scene within the viewbox (via a camera
entity that is inside the viewbox itself); 3) provide clipping when
rendering.

The "scene within the viewbox" is simply the list of its children. As
such, the total scenegraph is a complete graph without interruptions
(i.e. contiguous). The way that a viewBox renders its scene may depend
on the situation. The easiest would be to use glViewport and glScissor.
Other options are to use an FBO, or chaining the scenes transformation
with the viewbox' own transformations and then using fragment-clipping
or a stencil buffer.

With the word "scene" we refer to the part of the scenegraph that is
within a ViewBox. Any ViewBox is itself part of a scene (except the
root ViewBox). The children of a ViewBox make up its "sub-scene". The
"total scene" would be analogous to the whole scene graph.

The total scene grap typically has one root node, although there can
be multiple roots in case a certain a (group of) entities have multiple
parents that lead to different root viewboxes.


**The Camera**


The camera is an entity in a scene that defines the viewpoint (by its
position and orientation) and the projection (e.g. field of view,
perspective, log, polar, ...) with which the scene is projected onto
the rectangular region of the viewbox.

"""

from __future__ import division

from .base import Entity, Camera, ViewBox  # noqa
from .canvas import CanvasWithScene  # noqa
from .cameras import *  # noqa
from .entities import *  # noqa
from .systems import *  # noqa
