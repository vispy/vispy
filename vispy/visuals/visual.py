# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division
import weakref

from ..util.event import EmitterGroup, Event
from .shaders import StatementList, MultiProgram
from .transforms import TransformSystem
from .. import gloo


class VisualShare(object):
    """Contains data that is shared between all views of a visual.
    
    This includes:
    
    * GL state variables (blending, depth test, etc.)
    * A weak dictionary of all views
    * A list of filters that should be applied to all views
    * A cache for bounds.
    """
    def __init__(self):
        # Note: in some cases we will need to compute bounds independently for each
        # view. That will have to be worked out later..
        self.bounds = {}
        self.gl_state = {}
        self.views = weakref.WeakValueDictionary()
        self.filters = []


class BaseVisual(object):
    """Superclass for all visuals.
    
    This class provides:
    
    * A TransformSystem.
    * Two events: `update` and `bounds_change`.
    * Minimal framework for creating views of the visual.
    * A data structure that is shared between all views of the visual.
    * Abstract `draw`, `bounds`, `attach`, and `detach` methods.
    
    """
    def __init__(self, vshare=None, key=None):
        self._view_class = getattr(self, '_view_class', VisualView)
        
        if vshare is None:
            vshare = VisualShare()
            assert key is None
            key = 'default'
        
        self._vshare = vshare
        self._view_key = key
        self._vshare.views[key] = self
        
        self.events = EmitterGroup(source=self,
                                   auto_connect=True,
                                   update=Event,
                                   bounds_change=Event,
                                   )
        
        self.transforms = TransformSystem()

    @property
    def transform(self):
        return self.transforms.visual_to_document
    
    @transform.setter
    def transform(self, tr):
        self.transforms.visual_transform = tr

    def view(self, key=None):
        """Return a new view of this visual.
        """
        if key is None:
            i = 0
            while True:
                key = 'view_%d' % i
                if key not in self._vshare.views:
                    break
                i += 1
                
        return self._view_class(self, key)

    def draw(self):
        raise NotImplementedError()

    def bounds(self, axis):
        raise NotImplementedError()
        
    def attach(self, filter):
        raise NotImplementedError()
        
    def detach(self, filter):
        raise NotImplementedError()


class BaseVisualView(object):
    """Base class for a view on a visual.
    
    This class must be mixed with another Visual class to work properly. It 
    works mainly by forwarding the calls to _prepare_draw, _prepare_transforms,
    and _compute_bounds to the viewed visual.
    """
    def __init__(self, visual, key):
        self._visual = visual
        
    @property
    def visual(self):
        return self._visual
        
    def _prepare_draw(self, view=None):
        self._visual._prepare_draw(view=view)
        
    def _prepare_transforms(self, view):
        self._visual._prepare_transforms(view)
    
    def _compute_bounds(self, axis):
        self._visual._compute_bounds(axis)
        
    def __repr__(self):
        return '<%s on %r>' % (self.__class__.__name__, self._visual)


class Visual(BaseVisual):
    """Base class for all visuals that can be drawn using a single shader 
    program.
    
    This class creates a MultiProgram, which is an object that 
    behaves like a normal shader program (you can assign shader code, upload
    values, set template variables, etc.) but internally manages multiple 
    ModularProgram instances, one per view.
    
    Subclasses generally only need to reimplement _compute_bounds,
    _prepare_draw, and _prepare_transforms.
    """
    def __init__(self, vshare=None, key=None, vcode=None, fcode=None):
        self._view_class = VisualView
        BaseVisual.__init__(self, vshare, key)
        if vshare is None:
            self._vshare.draw_mode = 'triangles'
            self._vshare.index_buffer = None
            self._vshare.program = MultiProgram(vcode, fcode)
        
        self._program = self._vshare.program.add_program(key)
        self._prepare_transforms(self)
        self._filters = []
        self._hooks = {}

    def set_gl_state(self, preset=None, **kwargs):
        """Completely define the set of GL state parameters to use when drawing
        this visual.
        """
        self._vshare.gl_state = kwargs
        self._vshare.gl_state['preset'] = preset
    
    def update_gl_state(self, *args, **kwargs):
        """Modify the set of GL state parameters to use when drawing
        this visual.
        """
        if len(args) == 1:
            self._gl_state['preset'] = args[0]
        elif len(args) != 0:
            raise TypeError("Only one positional argument allowed.")
        self._gl_state.update(kwargs)

    def bounds(self, axis):
        cache = self.vshare.bounds
        if axis not in cache:
            cache[axis] = self._compute_bounds(axis)
        return cache[axis]

    def _compute_bounds(self, *args):
        """Return the (min, max) bounding values of this visual along *axis*
        in the local coordinate system.
        """
        raise NotImplementedError()

    def _prepare_draw(self, view=None):
        """This visual is about to be drawn.
        
        Visuals must implement this method to ensure that all program 
        and GL state variables are updated immediately before drawing.
        """
        raise NotImplementedError()

    @staticmethod
    def _prepare_transforms(view):
        """Assign a view's transforms to the proper shader template variables
        on the view's shader program. 
        """
        
        # Todo: this method can be removed if we somehow enable the shader
        # to specify exactly which transform functions it needs by name. For
        # example:
        #
        #     // mapping function is automatically defined from the 
        #     // corresponding transform in the view's TransformSystem
        #     gl_Position = visual_to_render(a_position);
        #     
        raise NotImplementedError()

    @property
    def shared_program(self):
        return self._vshare.program

    @property
    def view_program(self):
        return self._program

    @property
    def _draw_mode(self):
        return self._vshare.draw_mode
    
    @_draw_mode.setter
    def _draw_mode(self, m):
        self._vshare.draw_mode = m
        
    @property
    def _index_buffer(self):
        return self._vshare.index_buffer
        
    @_index_buffer.setter
    def _index_buffer(self, buf):
        self._vshare.index_buffer = buf
        
    def draw(self):
        gloo.set_state(**self._vshare.gl_state)
        
        self._prepare_transforms(view=self)
        self._prepare_draw(view=self)
        
        self._program.draw(self._vshare.draw_mode, self._vshare.index_buffer)
        
    def bounds(self):
        # check self._vshare for cached bounds before computing
        return None
        
    def _get_hook(self, shader, name):
        """Return a FunctionChain that Filters may use to modify the program.
        
        *shader* should be "frag" or "vert"
        *name* should be "pre" or "post"
        """
        assert name in ('pre', 'post')
        key = (shader, name)
        if key in self._hooks:
            return self._hooks[key]
        
        hook = StatementList()
        if shader == 'vert':
            self.view_program.vert[name] = hook
        elif shader == 'frag':
            self.view_program.frag[name] = hook
        self._hooks[key] = hook
        return hook
        
    def attach(self, filter, view=None):
        """Attach a Filter to this visual. 
        
        Each filter modifies the appearance or behavior of the visual.
        """
        if view is None:
            self._vshare.filters.append(filter)
            for view in self._vshare.views.values():
                filter._attach(view)
        else:
            view._filters.append(filter)
            filter._attach(view)
        
    def detach(self, filter, view=None):
        """Detach a filter.
        """
        if view is None:
            self._vshare.filters.remove(filter)
            for view in self._vshare.views.values():
                filter._detach(view)
        else:
            view._filters.remove(filter)
            filter._detach(view)
        

class VisualView(BaseVisualView, Visual):
    """A view on another Visual instance.
    
    View instances are created by calling ``visual.view()``.
    """
    def __init__(self, visual, key):
        BaseVisualView.__init__(self, visual, key)
        Visual.__init__(self, visual._vshare, key)
        
        # Attach any shared filters 
        for filter in self._vshare.filters:
            filter._attach(self)

        
class CompoundVisual(BaseVisual):
    """Visual consisting entirely of sub-visuals.

    To the user, a compound visual behaves exactly like a normal visual--it
    has a transform system, draw() and bounds() methods, etc. Internally, the
    compound visual automatically manages proxying these transforms and methods
    to its sub-visuals.
    """
    def __init__(self, subvisuals):
        self._view_class = CompoundVisualView
        BaseVisual.__init__(self)
        self._subvisuals = subvisuals
        for v in subvisuals:
            v.transforms = self.transforms
            v._prepare_transforms(v)
        
    def draw(self):
        for v in self._subvisuals:
            v.draw()
            
    def bounds(self, axis):
        # TODO: return union of bounds
        return self._subvisuals[0].bounds(axis)
        
    def set_gl_state(self, preset=None, **kwargs):
        for v in self._subvisuals:
            v.set_gl_state(preset=preset, **kwargs)
    
    def update_gl_state(self, *args, **kwargs):
        for v in self._subvisuals:
            v.update_gl_state(*args, **kwargs)

    def attach(self, filter, view=None):
        for v in self._subvisuals:
            v.attach(filter, v)
    
    def detach(self, filter, view=None):
        for v in self._subvisuals:
            v.detach(filter, v)
    

class CompoundVisualView(BaseVisualView, CompoundVisual):
    def __init__(self, visual, key):
        BaseVisualView.__init__(self, visual, key)
        # Create a view on each sub-visual 
        subv = [v.view() for v in visual._subvisuals]
        CompoundVisual.__init__(self, subv)

        # Attach any shared filters 
        for filter in self._vshare.filters:
            for v in self._subvisuals:
                filter._attach(v)        
