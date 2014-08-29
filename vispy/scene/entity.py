# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from . import transforms
from ..util.event import EmitterGroup, Event
from .events import SceneDrawEvent, SceneMouseEvent
from .transforms import NullTransform, create_transform


class Entity(object):
    """ Base class to represent a citizen of a scene.

    Typically an Entity is used to visualize something, although this is not
    strictly necessary. It may for instance also be used as a container to
    apply a certain transformation to a group of objects, or an object that
    performs a specific task without being visible.

    Each entity can have zero or more children. Each entity will
    typically have one parent, although multiple parents are allowed.
    It is recommended to use multi-parenting with care.

    Parameters
    ----------
    parent : Entity
        The parent of the Entity.
    name : str
        The name used to identify the entity.
    """

    def __init__(self, parent=None, name=None):
        self.events = EmitterGroup(source=self,
                                   auto_connect=True,
                                   parents_change=Event,
                                   active_parent_change=Event,
                                   children_change=Event,
                                   mouse_press=SceneMouseEvent,
                                   mouse_move=SceneMouseEvent,
                                   mouse_release=SceneMouseEvent,
                                   mouse_wheel=SceneMouseEvent,
                                   draw=SceneDrawEvent,
                                   children_drawn=SceneDrawEvent,
                                   update=Event,
                                   transform_change=Event,
                                   )
        self.name = name

        # Entities are organized in a parent-children hierarchy
        # todo: I think we want this to be a list. The order *may* be important
        # for some drawing systems. Using a set may lead to inconsistency
        self._children = set()
        # TODO: use weakrefs for parents.
        self._parents = set()
        if parent is not None:
            self.parents = parent
            
        self._document = None

        # Components that all entities in vispy have
        # todo: default transform should be trans-scale-rot transform
        self._transform = transforms.NullTransform()
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    @property
    def children(self):
        """ The list of children of this entity. The children are in
        arbitrary order.
        """
        return list(self._children)

    @property
    def parent(self):
        """ Get/set the parent. If the entity has multiple parents while
        using this property as a getter, an error is raised.
        """
        if not self._parents:
            return None
        elif len(self._parents) == 1:
            return tuple(self._parents)[0]
        else:
            raise RuntimeError('Ambiguous parent: there are multiple parents.')

    @parent.setter
    def parent(self, parent):
        # This is basically an alias
        self.parents = parent

    @property
    def parents(self):
        """ Get/set a tuple of parents.
        """
        return tuple(self._parents)

    @parents.setter
    def parents(self, parents):
        # Test input
        if isinstance(parents, Entity):
            parents = (parents,)
        if not hasattr(parents, '__iter__'):
            raise ValueError("Entity.parents must be iterable (got %s)"
                             % type(parents))

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
        self.update()

    def remove_parent(self, parent):
        if parent not in self._parents:
            raise ValueError("Parent not in set of parents for this entity.")
        self._parents.remove(parent)
        parent._remove_child(self)
        self.events.parents_change(removed=parent)

    def _add_child(self, ent):
        self._children.add(ent)
        self.events.children_change(added=ent)
        ent.events.update.connect(self.events.update)

    def _remove_child(self, ent):
        self._children.remove(ent)
        self.events.children_change(removed=ent)
        ent.events.update.disconnect(self.events.update)

    @property
    def document(self):
        """ The document is an optional property that is an entity representing
        the coordinate system from which this entity should make physical 
        measurements such as px, mm, pt, in, etc. This coordinate system 
        should be used when determining line widths, font sizes, and any
        other lengths specified in physical units.
        
        The default is None; in this case, a default document is used during
        drawing (usually this is supplied by the SceneCanvas).
        """
        return self._document
    
    @document.setter
    def document(self, doc):
        if doc is not None and not isinstance(doc, Entity):
            raise TypeError("Document property must be Entity or None.")
        self._document = doc
        self.update()

    @property
    def transform(self):
        """ The transform that maps the local coordinate frame to the
        coordinate frame of the parent.
        """
        return self._transform

    @transform.setter
    def transform(self, tr):
        if self._transform is not None:
            self._transform.changed.disconnect(self._transform_changed)
        assert isinstance(tr, transforms.BaseTransform)
        self._transform = tr
        self._transform.changed.connect(self._transform_changed)
        self._transform_changed(None)

    def set_transform(self, type, *args, **kwds):
        """ Create a new transform of *type* and assign it to this entity.
        All extra arguments are used in the construction of the transform.
        """
        self.transform = create_transform(type, *args, **kwds)

    def _transform_changed(self, event):
        self.events.transform_change()
        self.update()

    def _parent_chain(self):
        """
        Return the chain of parents starting from this entity. The chain ends
        at the first entity with either no parents or multiple parents.
        """
        chain = [self]
        while True:
            try:
                parent = chain[-1].parent
            except Exception:
                break
            if parent is None:
                break
            chain.append(parent)
        return chain

    def describe_tree(self, with_transform=False):
        """Create tree diagram of children

        Parameters
        ----------
        with_transform : bool
            If true, add information about entity transform types.

        Returns
        ----------
        tree : str
            The tree diagram.
        """
        # inspired by https://github.com/mbr/asciitree/blob/master/asciitree.py
        return self._describe_tree('', with_transform)

    def _describe_tree(self, prefix, with_transform):
        """Helper function to actuall construct the tree"""
        extra = ': "%s"' % self.name if self.name is not None else ''
        if with_transform:
            extra += (' [%s]' % self.transform.__class__.__name__)
        output = ''
        if len(prefix) > 0:
            output += prefix[:-3]
            output += '  +--'
        output += '%s%s\n' % (self.__class__.__name__, extra)

        n_children = len(self.children)
        for ii, child in enumerate(self.children):
            sub_prefix = prefix + ('   ' if ii+1 == n_children else '  |')
            output += child._describe_tree(sub_prefix, with_transform)
        return output

    def common_parent(self, entity):
        """
        Return the common parent of two entities. If the entities have no
        common parent, return None. Does not search past multi-parent branches.
        """
        p1 = self._parent_chain()
        p2 = entity._parent_chain()
        for p in p1:
            if p in p2:
                return p
        return None
        
    def entity_transform(self, entity):
        """
        Return the transform that maps from the coordinate system of
        *entity* to the local coordinate system of *self*.
        
        Note that there must be a _single_ path in the scenegraph that connects
        the two entities; otherwise an exception will be raised.        
        """
        cp = self.common_parent(entity)
        # First map from entity to common parent
        tr = NullTransform()
        
        while entity is not cp:
            if entity.transform is not None:
                tr = entity.transform * tr
            
            entity = entity.parent
        
        if entity is self:
            return tr
        
        # Now map from common parent to self
        tr2 = cp.entity_transform(self)
        return tr2.inverse * tr
        
    def _process_mouse_event(self, event):
        """
        Propagate a mouse event through the scene tree starting at this Entity.
        """
        # 1. find all entities whose mouse-area includes the click point.
        # 2. send the event to each entity one at a time
        #    (we should use a specialized emitter for this, rather than
        #     rebuild the emitter machinery!)

        # TODO: for now we send the event to all entities; need to use
        # picking to decide which entities should receive the event.
        for enter, path in self.walk():
            event._set_path(path)
            entity = path[-1]
            getattr(entity.events, event.type)(event)

    def bounds(self, mode, axis):
        """ Return the (min, max) bounding values describing the location of
        this entity in its local coordinate system.
        
        Parameters
        ----------
        mode : str
            Describes the type of boundary requested. Can be "visual", "data",
            or "mouse".
        axis : 0, 1, 2
            The axis along which to measure the bounding values.
        
        Returns
        -------
        None or (min, max) tuple. 
        """
        return None

    def update(self):
        """
        Emit an event to inform Canvases that this Entity needs to be redrawn.
        """
        self.events.update()

    def __repr__(self):
        name = "" if self.name is None else " name="+self.name
        return "<%s%s at 0x%x>" % (self.__class__.__name__, name, id(self))
