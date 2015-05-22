# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..util.event import Event, EmitterGroup
from ..visuals.transforms import (NullTransform, BaseTransform, 
                                  ChainTransform, create_transform)


class Node(object):
    """ Base class representing an object in a scene.

    A group of nodes connected through parent-child relationships define a 
    scenegraph. Nodes may have any number of children or parents, although 
    it is uncommon to have more than one parent.

    Each Node defines a ``transform`` property, which describes the position,
    orientation, scale, etc. of the Node relative to its parent. The Node's
    children inherit this property, and then further apply their own
    transformations on top of that. 
    
    With the ``transform`` property, each Node implicitly defines a "local" 
    coordinate system, and the Nodes and edges in the scenegraph can be though
    of as coordinate systems connected by transformation functions.
    
    Parameters
    ----------
    parent : Node
        The parent of the Node.
    name : str
        The name used to identify the node.
    """
    
    # Needed to allow subclasses to repr() themselves before Node.__init__()
    _name = None

    def __init__(self, parent=None, name=None):
        self.name = name
        self._visible = True

        # Add some events to the emitter groups:
        events = ['parents_change', 'children_change', 'transform_change',
                  'mouse_press', 'mouse_move', 'mouse_release', 'mouse_wheel', 
                  'key_press', 'key_release']
        # Create event emitter if needed (in subclasses that inherit from
        # Visual, we already have an emitter to share)
        if not hasattr(self, 'events'):
            self.events = EmitterGroup(source=self, auto_connect=True,
                                       update=Event)
        self.events.add(**dict([(ev, Event) for ev in events]))
        
        # Entities are organized in a parent-children hierarchy
        self._children = []
        # TODO: use weakrefs for parents.
        self._parents = []
        if parent is not None:
            self.parents = parent
            
        self._document = None

        # Components that all entities in vispy have
        # todo: default transform should be trans-scale-rot transform
        self._transform = NullTransform()
    
    # todo: move visible to BaseVisualNode class when we make Node not a Visual
    @property
    def visible(self):
        """ Whether this node should be drawn or not. Only applicable to
        nodes that can be drawn.
        """
        return self._visible
    
    @visible.setter
    def visible(self, val):
        self._visible = bool(val)
        self.update()
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    @property
    def children(self):
        """ A copy of the list of children of this node. Do not add
        items to this list, but use ``x.parent = y`` instead.
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
            return self._parents[0]
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

        # Apply
        prev = list(self._parents)  # No list.copy() on Py2.x
        with self.events.parents_change.blocker():
            # Remove parents
            for parent in prev:
                if parent not in parents:
                    self.remove_parent(parent)
            # Add new parents
            for parent in parents:
                if parent not in prev:
                    self.add_parent(parent)

        self.events.parents_change(new=parents, old=prev)

    def add_parent(self, parent):
        """Add a parent

        Parameters
        ----------
        parent : instance of Node
            The parent.
        """
        if parent in self._parents:
            return
        self._parents.append(parent)
        parent._add_child(self)
        self.events.parents_change(added=parent)
        self.update()

    def remove_parent(self, parent):
        """Remove a parent

        Parameters
        ----------
        parent : instance of Node
            The parent.
        """
        if parent not in self._parents:
            raise ValueError("Parent not in set of parents for this node.")
        self._parents.remove(parent)
        parent._remove_child(self)
        self.events.parents_change(removed=parent)

    def _add_child(self, node):
        self._children.append(node)
        self.events.children_change(added=node)
        node.events.update.connect(self.events.update)

    def _remove_child(self, node):
        self._children.remove(node)
        self.events.children_change(removed=node)
        node.events.update.disconnect(self.events.update)

    def update(self):
        """
        Emit an event to inform listeners that properties of this Node or its
        children have changed.
        """
        self.events.update()

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

    def set_transform(self, type_, *args, **kwargs):
        """ Create a new transform of *type* and assign it to this node.

        All extra arguments are used in the construction of the transform.

        Parameters
        ----------
        type_ : str
            The transform type.
        *args : tuple
            Arguments.
        **kwargs : dict
            Keywoard arguments.
        """
        self.transform = create_transform(type_, *args, **kwargs)

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
        Return the common parent of two entities

        If the entities have no common parent, return None.
        Does not search past multi-parent branches.

        Parameters
        ----------
        node : instance of Node
            The other node.

        Returns
        -------
        parent : instance of Node | None
            The parent.
        """
        p1 = self._parent_chain()
        p2 = node._parent_chain()
        for p in p1:
            if p in p2:
                return p
        return None

    def node_path_to_child(self, node):
        """Return a list describing the path from this node to a child node

        This method assumes that the given node is a child node. Multiple
        parenting is allowed.

        Parameters
        ----------
        node : instance of Node
            The child node.

        Returns
        -------
        path : list | None
            The path.
        """
        if node is self:
            return []

        # Go up from the child node as far as we can
        path1 = [node]
        child = node
        while len(child.parents) == 1:
            child = child.parent
            path1.append(child)
            # Early exit
            if child is self:
                return list(reversed(path1))
        
        # Verify that we're not cut off
        if len(path1[-1].parents) == 0:
            raise RuntimeError('%r is not a child of %r' % (node, self))
        
        def _is_child(path, parent, child):
            path.append(parent)
            if child in parent.children:
                return path
            else:
                for c in parent.children:
                    possible_path = _is_child(path[:], c, child)
                    if possible_path:
                        return possible_path
            return None

        # Search from the parent towards the child
        path2 = _is_child([], self, path1[-1])
        if not path2:
            raise RuntimeError('%r is not a child of %r' % (node, self))

        # Return
        return path2 + list(reversed(path1))

    def node_path(self, node):
        """Return two lists describing the path from this node to another

        Parameters
        ----------
        node : instance of Node
            The other node.

        Returns
        -------
        p1 : list
            First path (see below).
        p2 : list
            Second path (see below).

        Notes
        -----
        The first list starts with this node and ends with the common parent
        between the endpoint nodes. The second list contains the remainder of
        the path from the common parent to the specified ending node.
        
        For example, consider the following scenegraph::
        
            A --- B --- C --- D
                   \
                    --- E --- F
        
        Calling `D.node_path(F)` will return::
        
            ([D, C, B], [E, F])
        
        Note that there must be a _single_ path in the scenegraph that connects
        the two entities; otherwise an exception will be raised.        
        """
        p1 = self._parent_chain()
        p2 = node._parent_chain()
        cp = None
        for p in p1:
            if p in p2:
                cp = p
                break
        if cp is None:
            raise RuntimeError("No single-path common parent between nodes %s "
                               "and %s." % (self, node))
        
        p1 = p1[:p1.index(cp)+1]
        p2 = p2[:p2.index(cp)][::-1]
        return p1, p2
        
    def node_path_transforms(self, node):
        """Return the list of transforms along the path to another node.
        
        The transforms are listed in reverse order, such that the last 
        transform should be applied first when mapping from this node to 
        the other.

        Parameters
        ----------
        node : instance of Node
            The other node.

        Returns
        -------
        transform : instance of Transform
            The transform.
        """
        a, b = self.node_path(node)
        return ([n.transform.inverse for n in b] +
                [n.transform for n in a[:-1]])[::-1]

    def node_transform(self, node):
        """
        Return the transform that maps from the coordinate system of
        *self* to the local coordinate system of *node*.

        Note that there must be a _single_ path in the scenegraph that connects
        the two entities; otherwise an exception will be raised.

        Parameters
        ----------
        node : instance of Node
            The other node.

        Returns
        -------
        transform : instance of ChainTransform
            The transform.
        """
        return ChainTransform(self.node_path_transforms(node))

    def __repr__(self):
        name = "" if self.name is None else " name="+self.name
        return "<%s%s at 0x%x>" % (self.__class__.__name__, name, id(self))
