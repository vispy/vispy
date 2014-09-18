# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..util.event import EmitterGroup, Event
from ..visuals.transforms import NullTransform, BaseTransform, create_transform


class Node(object):
    """ Mixin class to represent a citizen of a scene.

    Typically an Node is used to visualize something, although this is not
    strictly necessary. It may for instance also be used as a container to
    apply a certain transformation to a group of objects, or an object that
    performs a specific task without being visible.

    Each node can have zero or more children. Each node will
    typically have one parent, although multiple parents are allowed.
    It is recommended to use multi-parenting with care.

    Parameters
    ----------
    parent : Node
        The parent of the Node.
    name : str
        The name used to identify the node.
    """

    def __init__(self, parent=None, name=None):
        self.events = EmitterGroup(source=self,
                                   auto_connect=True,
                                   parents_change=Event,
                                   active_parent_change=Event,
                                   children_change=Event,
                                   mouse_press=Event,
                                   mouse_move=Event,
                                   mouse_release=Event,
                                   mouse_wheel=Event,
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
        self._transform = NullTransform()
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    @property
    def children(self):
        """ The list of children of this node. The children are in
        arbitrary order.
        """
        return list(self._children)

    @property
    def parent(self):
        """ Get/set the parent. If the node has multiple parents while
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
        if isinstance(parents, Node):
            parents = (parents,)
        if not hasattr(parents, '__iter__'):
            raise ValueError("Node.parents must be iterable (got %s)"
                             % type(parents))

        # Test that all parents are entities
        for p in parents:
            if not isinstance(p, Node):
                raise ValueError('A parent of an node must be an node too,'
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
            raise ValueError("Parent not in set of parents for this node.")
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
        """ The document is an optional property that is an node representing
        the coordinate system from which this node should make physical 
        measurements such as px, mm, pt, in, etc. This coordinate system 
        should be used when determining line widths, font sizes, and any
        other lengths specified in physical units.
        
        The default is None; in this case, a default document is used during
        drawing (usually this is supplied by the SceneCanvas).
        """
        return self._document
    
    @document.setter
    def document(self, doc):
        if doc is not None and not isinstance(doc, Node):
            raise TypeError("Document property must be Node or None.")
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
        assert isinstance(tr, BaseTransform)
        self._transform = tr
        self._transform.changed.connect(self._transform_changed)
        self._transform_changed(None)

    def set_transform(self, type, *args, **kwds):
        """ Create a new transform of *type* and assign it to this node.
        All extra arguments are used in the construction of the transform.
        """
        self.transform = create_transform(type, *args, **kwds)

    def _transform_changed(self, event):
        self.events.transform_change()
        self.update()

    def _parent_chain(self):
        """
        Return the chain of parents starting from this node. The chain ends
        at the first node with either no parents or multiple parents.
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
            If true, add information about node transform types.

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

    def common_parent(self, node):
        """
        Return the common parent of two entities. If the entities have no
        common parent, return None. Does not search past multi-parent branches.
        """
        p1 = self._parent_chain()
        p2 = node._parent_chain()
        for p in p1:
            if p in p2:
                return p
        return None
        
    def node_transform(self, node):
        """
        Return the transform that maps from the coordinate system of
        *node* to the local coordinate system of *self*.
        
        Note that there must be a _single_ path in the scenegraph that connects
        the two entities; otherwise an exception will be raised.        
        """
        cp = self.common_parent(node)
        # First map from node to common parent
        tr = NullTransform()
        
        while node is not cp:
            if node.transform is not None:
                tr = node.transform * tr
            
            node = node.parent
        
        if node is self:
            return tr
        
        # Now map from common parent to self
        tr2 = cp.node_transform(self)
        return tr2.inverse * tr
        
    def _process_mouse_event(self, event):
        """
        Propagate a mouse event through the scene tree starting at this Node.
        """
        # 1. find all entities whose mouse-area includes the click point.
        # 2. send the event to each node one at a time
        #    (we should use a specialized emitter for this, rather than
        #     rebuild the emitter machinery!)

        # TODO: for now we send the event to all entities; need to use
        # picking to decide which entities should receive the event.
        for enter, path in self.walk():
            event._set_path(path)
            node = path[-1]
            getattr(node.events, event.type)(event)

    def bounds(self, mode, axis):
        """ Return the (min, max) bounding values describing the location of
        this node in its local coordinate system.
        
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
        Emit an event to inform Canvases that this Node needs to be redrawn.
        """
        self.events.update()

    def __repr__(self):
        name = "" if self.name is None else " name="+self.name
        return "<%s%s at 0x%x>" % (self.__class__.__name__, name, id(self))
