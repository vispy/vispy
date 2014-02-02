# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..visuals import transforms

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

    Visual = None

    def __init__(self, parent=None, **kwargs):

        # Entities are organized in a parent-children hierarchy
        self._children = []
        self._parents = ()
        self._parent = None
        self.parent = parent

        # Components that all entities in vispy have
        self._transform = transforms.AffineTransform()
        self._visuals = {}
        self._visual_kwargs = kwargs

    @property
    def children(self):
        """ The list of children of this entity.
        """
        return [c for c in self._children]

    @property
    def parent(self):
        """ The parent entity. In case there are multiple parents,
        the first parent is given. During a draw, however, the parent
        from which the draw originated is given.
        """
        return self._parent

    @parent.setter
    def parent(self, value):
        if value is None:
            self.parents = ()
        else:
            self.parents = (value,)

    @property
    def parents(self):
        """ Get/set the tuple of parents. Typically the tuple will have
        one element.
        """
        return self._parents

    @parents.setter
    def parents(self, parents):

        # Test input
        if not isinstance(parents, (tuple, list)):
            raise ValueError("Entity.parents must be a tuple or list.")

        # Test that all parents are entities
        for p in parents:
            if not isinstance(p, Entity):
                raise ValueError('A parent of an entity must be an entity too,'
                                 ' not %s.' % p.__class__.__name__)

        # Test that each parent occurs exactly once
        parentids = set([id(p) for p in parents])
        if len(parentids) != len(parents):
            raise ValueError('An entity cannot have the same parent twice '
                             '(%r)' % self)

        # Remove from old parents (and from new parents just to be sure)
        oldparents = self.parents
        for oldparent in oldparents:
            while self in oldparent._children:
                oldparent._children.remove(self)
        for parent in parents:
            while self in parent._children:
                parent._children.remove(self)

        # Set new parents and add ourself to their list of children
        self._parents = tuple(parents)
        for parent in parents:
            parent._children.append(self)

        # Set singleton parent
        self._parent = self._parents[0] if self._parents else None

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



#     @property
#     def visual(self):
#         """ The visual object that can draw this entity. Can be None.
#         """
#         return self._visual

    def get_visual(self, root):
        """ Get the visual for this entity, based on the given root.
        May be overloaded to enable the use of multiple visuals.
        """
        if self.Visual is None:
            return None
        try:
            visual = self._visuals[id(root)]
        except KeyError:
            visual = self._visuals[id(root)] = self.Visual(
                                                    **self._visual_kwargs)
        return visual

    def get_path_transform(self, path):
        """
        Return the complete Transform that maps from *path[0]* to self.
        """
        return transforms.TransformChain([e.transform for e in path])

    def paint(self, canvas, path):
        """
        Paint this entity, given that we are drawing on *canvas* through 
        the given entity *path*.
        """
        pass
    
    def paint_tree(self, canvas):
        """
        Paint the entire tree of Entities beginnging here.            
        """
        
        # Determine the order in which entity paths should be painted.
        # (here, we may draw a single entity multiple times if there are
        # multiple paths from self to the entity)
        order = [[self]]  # (this is incomplete)
        
        # Paint all in order.
        for path in order:
            entity = path[-1]
            if hasattr(entity, 'paint'):
                entity.paint(canvas, path)

    def process_mouse_event(self, canvas, ev):
        """
        Propagate a mouse event through the scene tree starting at this Entity.
        """
        pass
        
        # 1. find all entities whose mouse-area includes the point of the click.
        # 2. send the event to each entity one at a time
        #    (we should use a specialized emitter for this, rather than 
        #     rebuild the emitter machinery!)



