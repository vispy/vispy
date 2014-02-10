# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..visuals import transforms
from ..util.event import EmitterGroup, Event
from .events import SceneMouseEvent

class Entity(object):

    """ Base class to represent a citizen of a scene. Typically an
    Entity is used to visualize something, although this is not strictly
    necessary. It may for instance also be used as a container to apply
    a certain transformation to a group of objects, or an object that
    performs a specific task without being visible.

    Each entity can have zero or more children. Each entity will
    typically have one parent, although multiple parents are allowed.
    It is recommended to use multi-parenting with care.
    """

    def __init__(self, parent=None, **kwargs):
        self.events = EmitterGroup(source=self,
                                   auto_connect=True,
                                   parents_change=Event,
                                   active_parent_change=Event,
                                   children_change=Event,
                                   mouse_press=SceneMouseEvent,
                                   mouse_move=SceneMouseEvent,
                                   mouse_release=SceneMouseEvent,
                                   )

        # Entities are organized in a parent-children hierarchy
        self._children = set()
        # TODO: use weakrefs for parents. 
        self._parents = set()
        self._active_parent = None
        self.parent = parent

        # Components that all entities in vispy have
        self._transform = transforms.AffineTransform()
        

    @property
    def children(self):
        """ The list of children of this entity.
        """
        return list(self._children)

    @property
    def parent(self):
        """ The parent entity. In case there are multiple parents,
        the active parent is given, if any.
        """
        return self._active_parent

    @parent.setter
    def parent(self, value):
        if value is None:
            self.parents = set()
        else:
            self.parents = set([value])

    @property
    def parents(self):
        """ Get/set the list of parents. Typically the tuple will have
        one element.
        """
        return list(self._parents)

    @parents.setter
    def parents(self, parents):
        # Test input
        if not hasattr(parents, '__iter__'):
            raise ValueError("Entity.parents must be iterable (got %s)" % type(parents))

        # Test that all parents are entities
        for p in parents:
            if not isinstance(p, Entity):
                raise ValueError('A parent of an entity must be an entity too,'
                                 ' not %s.' % p.__class__.__name__)
        
        # convert to set
        prev = self._parents.copy()
        parents = set(parents)
        
        with self.events.parents_change.blocker():
            # Remove from parents
            for parent in prev - parents:
                self.remove_parent(parent)
                
            # Add new
            for parent in parents - prev:
                self.add_parent(parent)

        self.events.parents_change(new=parents, old=prev)

    def add_parent(self, parent):
        if parent in self._parents:
            return
        self._parents.add(parent)
        parent._add_child(self)
        self.events.parents_change(added=parent)
        
    def remove_parent(self, parent):
        if parent not in self._parents:
            raise ValueError("Parent not in set of parents for this entity.")
        self._parents.remove(parent)
        parent._remove_child(self)
        self.events.parents_change(removed=parent)

    def _add_child(self, ent):
        self._children.add(ent)
        self.events.children_change(added=ent)

    def _remove_child(self, ent):
        self._children.remove(ent)
        self.events.children_change(removed=ent)
        
    def _set_active_parent(self, parent):
        """
        Set the currently active parent for this entity.
        If None, then this entity is assumed to be the root of
        the scenegraph until a new parent is selected.
        """
        assert parent is None or parent in self._parents
        prev = self._active_parent
        self._active_parent = parent
        self.events.active_parent_change(prev=prev)
    
        # todo: Should we destroy GL objects (because we are removed)
# from an OpenGL context)?
# LC: No--only destroy when the visual is garbage collected or when explicitly 
# asked to destroy.
#         canvas1 = self.get_canvas()
#         canvas2 = value.get_canvas()
#         if canvas1 and (canvas1 is not canvas2):
#             self.clear_gl()

    def __iter__(self):
        return self._children.__iter__()

    @property
    def transform(self):
        """ The transform for this entity; how the local coordinate system
        is transformed with respect to the parent coordinate system.
        
        By default, this is an AffineTransform instance.
        """
        return self._transform

    @transform.setter
    def transform(self, tr):
        assert isinstance(tr, transforms.Transform)
        self._transform = tr

    def root_transform(self):
        """
        Return the complete Transform that maps from self to the root of the 
        scenegraph.
        """
        tr = []
        ent = self
        while ent is not None:
            tr.append(ent.transform)
            ent = ent.parent
        return transforms.TransformChain(tr)

    def document_transform(self):
        """
        Return the complete Transform that maps from self to the first
        Document in its ancestry.
        """

        from .entities import Document
        tr = []
        ent = self
        while not isinstance(ent, Document):
            tr.append(ent.transform)
            ent = ent.parent
        return transforms.TransformChain(tr)

    def paint(self, canvas, path):
        """
        Paint this entity, given that we are drawing on *canvas* through 
        the given entity *path*.
        """
        pass
    
    def paint_tree(self, canvas, parent=None):
        """
        Paint the entire tree of Entities beginnging here.            
        """
        self._set_active_parent(parent)
        
        for child in self:
            child.paint_tree(canvas, parent=self)
        
        self.paint(canvas)

    def process_mouse_event(self, canvas, event):
        """
        Propagate a mouse event through the scene tree starting at this Entity.
        """
        
        # 1. find all entities whose mouse-area includes the point of the click.
        # 2. send the event to each entity one at a time
        #    (we should use a specialized emitter for this, rather than 
        #     rebuild the emitter machinery!)
        
        # TODO: for now we send the event to all entities; need to use
        # picking to decide which entities should receive the event.
        scene_event = SceneMouseEvent(event)
        for entity in self.walk():
            getattr(entity.events, event.type)(scene_event)

    def walk(self):
        """
        Return an iterator that walks the entire scene graph starting at this
        Entity.        
        """
        # TODO: need some control over the order..
        yield self
        for ch in self:
            for e in ch.walk():
                yield e

    def update(self):
        """
        Emit an event to inform Canvases that this Entity needs to be redrawn.
        """
        # TODO
        pass
