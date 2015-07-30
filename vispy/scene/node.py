# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import weakref

from ..util.event import Event, EmitterGroup
from ..visuals.transforms import (NullTransform, BaseTransform, 
                                  ChainTransform, create_transform,
                                  TransformSystem)


class Node(object):
    """ Base class representing an object in a scene.

    A group of nodes connected through parent-child relationships define a 
    scenegraph. Nodes may have any number of children.

    Each Node defines a ``transform`` property, which describes the position,
    orientation, scale, etc. of the Node relative to its parent. The Node's
    children inherit this property, and then further apply their own
    transformations on top of that. 
    
    With the ``transform`` property, each Node implicitly defines a "local" 
    coordinate system, and the Nodes and edges in the scenegraph can be thought
    of as coordinate systems connected by transformation functions.
    
    Parameters
    ----------
    parent : Node
        The parent of the Node.
    name : str
        The name used to identify the node.
    transforms : instance of TransformSystem | None
        The associated transforms.
    """
    
    # Needed to allow subclasses to repr() themselves before Node.__init__()
    _name = None

    def __init__(self, parent=None, name=None, transforms=None):
        self.name = name
        self._visible = True
        self._canvas = None
        self._document_node = None
        self._scene_node = None
        self._opacity = 1.0
        self._order = 0
        self._picking = False
        
        # clippers inherited from parents
        self._clippers = weakref.WeakKeyDictionary()  # {node: clipper}

        # whether this widget should clip its children
        self._clip_children = False
        self._clipper = None
        
        self.transforms = (TransformSystem() if transforms is None else 
                           transforms)

        # Add some events to the emitter groups:
        events = ['canvas_change', 'parent_change', 'children_change', 
                  'transform_change', 'mouse_press', 'mouse_move',
                  'mouse_release', 'mouse_wheel', 'key_press', 'key_release']
        # Create event emitter if needed (in subclasses that inherit from
        # Visual, we already have an emitter to share)
        if not hasattr(self, 'events'):
            self.events = EmitterGroup(source=self, auto_connect=True,
                                       update=Event)
        self.events.add(**dict([(ev, Event) for ev in events]))
        
        self._children = []
        self._transform = NullTransform()
        self._parent = None
        if parent is not None:
            self.parent = parent
            
        self._document = None
    
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
    def opacity(self):
        return self._opacity
    
    @opacity.setter
    def opacity(self, o):
        self._opacity = o
        self._update_opacity()
        
    def _update_opacity(self):
        pass
        
    def _set_clipper(self, node, clipper):
        """Assign a clipper that is inherited from a parent node.
        
        If *clipper* is None, then remove any clippers for *node*.
        """
        pass

    @property
    def clip_children(self):
        """Boolean indicating whether children of this node will inherit its
        clipper.
        """
        return self._clip_children
    
    @clip_children.setter
    def clip_children(self, clip):
        if self._clip_children == clip:
            return
        self._clip_children = clip
        
        for ch in self.children:
            ch._set_clipper(self, self.clipper) 

    @property
    def clipper(self):
        """A visual filter that can be used to clip visuals to the boundaries
        of this node.
        """
        return self._clipper
        
    @property
    def order(self):
        """A value used to determine the order in which nodes are drawn.
        
        Greater values are drawn later. Children are always drawn after their
        parent.
        """
        return self._order
    
    @order.setter
    def order(self, o):
        self._order = o
        self.update()
        
    @property
    def children(self):
        """ A copy of the list of children of this node. Do not add
        items to this list, but use ``x.parent = y`` instead.
        """
        return list(self._children)

    @property
    def parent(self):
        """The parent of this node in the scenegraph.
        
        Nodes inherit coordinate transformations and some filters (opacity and
        clipping by default) from their parents. Setting this property assigns
        a new parent, changing the topology of the scenegraph.
        
        May be set to None to remove this node (and its children) from a
        scenegraph.
        """
        if self._parent is None:
            return None
        else:
            return self._parent()

    @parent.setter
    def parent(self, parent):
        if not isinstance(parent, (Node, type(None))):
            raise ValueError('Parent must be Node instance or None (got %s).'
                             % parent.__class__.__name__)
        prev = self.parent
        if parent is prev:
            return
        if prev is not None:
            prev._remove_child(self)
            # remove all clippers inherited from parents
            for k in list(self._clippers):
                self._set_clipper(k, None)
        if parent is None:
            self._set_canvas(None)
            self._parent = None
        else:
            self._set_canvas(parent.canvas)
            self._parent = weakref.ref(parent)
            parent._add_child(self)
            # inherit clippers from parents
            p = parent
            while p is not None:
                if p.clip_children:
                    self._set_clipper(p, p.clipper)
                p = p.parent
        
        self.events.parent_change(new=parent, old=prev)
        self._update_trsys(None)
        self.update()

    def _add_child(self, node):
        self._children.append(node)
        self.events.children_change(added=node)
        node.events.children_change.connect(self.events.children_change)
        self.events.parent_change.connect(node.events.parent_change)

    def _remove_child(self, node):
        self._children.remove(node)
        self.events.children_change(removed=node)
        node.events.children_change.disconnect(self.events.children_change)
        self.events.parent_change.disconnect(node.events.parent_change)

    def on_parent_change(self, event):
        """Parent change event handler

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        self._scene_node = None

    def is_child(self, node):
        """Check if a node is a child of the current node

        Parameters
        ----------
        node : instance of Node
            The potential child.

        Returns
        -------
        child : bool
            Whether or not the node is a child.
        """
        if node in self.children:
            return True
        for c in self.children:
            if c.is_child(node):
                return True
        return False

    @property
    def canvas(self):
        """The canvas in which this node's scenegraph is being drawn.
        """
        if self._canvas is None:
            return None
        else:
            return self._canvas()

    @property
    def document_node(self):
        """The node to be used as the document coordinate system.
        
        By default, the document node is `self.root_node`.
        """
        if self._document_node is None:
            return self.root_node
        return self._document_node

    @document_node.setter
    def document_node(self, doc):
        self._document_node = doc
        self._update_transform()

    @property
    def scene_node(self):
        """The first ancestor of this node that is a SubScene instance, or self
        if no such node exists.
        """
        if self._scene_node is None:
            from .subscene import SubScene
            p = self.parent
            while True:
                if isinstance(p, SubScene) or p is None:
                    self._scene_node = p
                    break
                p = p.parent
            if self._scene_node is None:
                self._scene_node = self
        return self._scene_node

    @property
    def root_node(self):
        node = self
        while True:
            p = node.parent
            if p is None:
                return node
            node = p

    def _set_canvas(self, c):
        old = self.canvas
        if old is c:
            return
        
        # Use canvas/framebuffer transforms from canvas
        self.transforms.canvas = c
        if c is None:
            self._canvas = None
        else:
            self._canvas = weakref.ref(c)
            tr = c.transforms
            self.transforms.canvas_transform = tr.canvas_transform
            self.transforms.framebuffer_transform = tr.framebuffer_transform
        
        # update all children
        for ch in self.children:
            ch._set_canvas(c)

        self.events.canvas_change(old=old, new=c)

    def update(self):
        """
        Emit an event to inform listeners that properties of this Node have
        changed. Also request a canvas update.
        """
        self.events.update()
        c = getattr(self, 'canvas', None)
        if c is not None:
            c.update(node=self)

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
        # Other nodes might be interested in this information, but turning it
        # on by default is too expensive.
        assert isinstance(tr, BaseTransform)
        if tr is not self._transform:
            self._transform = tr
            self._update_trsys(None)

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

    def _update_trsys(self, event):
        """Called when  has changed.
        
        This allows the node and its children to react (notably, VisualNode
        uses this to update its TransformSystem).
        
        Note that this method is only called when one transform is replaced by
        another; it is not called if an existing transform internally changes
        its state.
        """
        for ch in self.children:
            ch._update_trsys(event)
        self.events.transform_change()
        self.update()

    def parent_chain(self):
        """
        Return the list of parents starting from this node. The chain ends
        at the first node with no parents.
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

        Parameters
        ----------
        node : instance of Node
            The other node.

        Returns
        -------
        parent : instance of Node | None
            The parent.
        """
        p1 = self.parent_chain()
        p2 = node.parent_chain()
        for p in p1:
            if p in p2:
                return p
        return None

    def node_path_to_child(self, node):
        """Return a list describing the path from this node to a child node

        If *node* is not a (grand)child of this node, then raise RuntimeError.

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
        while child.parent is not None:
            child = child.parent
            path1.append(child)
            # Early exit
            if child is self:
                return list(reversed(path1))
        
        # Verify that we're not cut off
        if path1[-1].parent is None:
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
        
        """
        p1 = self.parent_chain()
        p2 = node.parent_chain()
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
        transforms : list
            A list of Transform instances.
        """
        a, b = self.node_path(node)
        return ([n.transform for n in a[:-1]] + 
                [n.transform.inverse for n in b])[::-1]

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

    @property
    def picking(self):
        """Boolean that determines whether this node (and its children) are
        drawn in picking mode.
        """
        return self._picking
    
    @picking.setter
    def picking(self, p):
        for c in self.children:
            c.picking = p
        self._picking = p
