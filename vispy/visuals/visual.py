# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""

Definitions
===========

Visual : an object that (1) can be drawn on-screen, (2) can be manipulated
by configuring the coordinate transformations that it uses.

View : a special type of visual that (1) draws the contents of another visual,
(2) using a different set of transforms. Views have only the basic visual
interface (draw, bounds, attach, etc.) and lack access to the specific features
of the visual they are linked to (for example, LineVisual has a ``set_data()``
method, but there is no corresponding method on a view of a LineVisual).


Class Structure
===============

* `BaseVisual` - provides transforms and view creation
  This class lays out the basic API for all visuals: ``draw()``, ``bounds()``,
  ``view()``, and ``attach()`` methods, as well as a `TransformSystem` instance
  that determines where the visual will be drawn.
    * `Visual` - defines a shader program to draw.
      Subclasses are responsible for supplying the shader code and configuring
      program variables, including transforms.
        * `VisualView` - clones the shader program from a Visual instance.
          Instances of `VisualView` contain their own shader program,
          transforms and filter attachments, and generally behave like a normal
          instance of `Visual`.
    * `CompoundVisual` - wraps multiple Visual instances.
      These visuals provide no program of their own, but instead rely on one or
      more internally generated `Visual` instances to do their drawing. For
      example, a PolygonVisual consists of an internal LineVisual and
      MeshVisual.
        * `CompoundVisualView` - wraps multiple VisualView instances.
          This allows a `CompoundVisual` to be viewed with a different set of
          transforms and filters.


Making Visual Subclasses
========================

When making subclasses of `Visual`, it is only necessary to reimplement the
``_prepare_draw()``, ``_prepare_transforms()``, and ``_compute_bounds()``
methods. These methods will be called by the visual automatically when it is
needed for itself or for a view of the visual.

It is important to remember
when implementing these methods that most changes made to the visual's shader
program should also be made to the programs for each view. To make this easier,
the visual uses a `MultiProgram`, which allows all shader programs across the
visual and its views to be accessed simultaneously. For example::

    def _prepare_draw(self, view):
        # This line applies to the visual and all of its views
        self.shared_program['a_position'] = self._vbo

        # This line applies only to the view that is about to be drawn
        view.view_program['u_color'] = (1, 1, 1, 1)

Under most circumstances, it is not necessary to reimplement `VisualView`
because a view will directly access the ``_prepare`` and ``_compute`` methods
from the visual it is viewing. However, if the `Visual` to be viewed is a
subclass that reimplements other methods such as ``draw()`` or ``bounds()``,
then it will be necessary to provide a new matching `VisualView` subclass.


Making CompoundVisual Subclasses
================================

Compound visual subclasses are generally very easy to construct::

    class PlotLineVisual(visuals.CompoundVisual):
        def __init__(self, ...):
            self._line = LineVisual(...)
            self._point = PointVisual(...)
            visuals.CompoundVisual.__init__(self, [self._line, self._point])

A compound visual will automatically handle forwarding transform system changes
and filter attachments to its internally-wrapped visuals. To the user, this
will appear to behave as a single visual.
"""

from __future__ import division
import weakref

from .. import gloo
from ..util.event import EmitterGroup, Event
from ..util import logger, Frozen
from .shaders import StatementList, MultiProgram
from .transforms import TransformSystem


class VisualShare(object):
    """Contains data that is shared between all views of a visual.

    This includes:

        * GL state variables (blending, depth test, etc.)
        * A weak dictionary of all views
        * A list of filters that should be applied to all views
        * A cache for bounds.

    """
    def __init__(self):
        # Note: in some cases we will need to compute bounds independently for
        # each view. That will have to be worked out later..
        self.bounds = {}
        self.gl_state = {}
        self.views = weakref.WeakKeyDictionary()
        self.filters = []
        self.visible = True


class BaseVisual(Frozen):
    """Superclass for all visuals.

    This class provides:

        * A TransformSystem.
        * Two events: `update` and `bounds_change`.
        * Minimal framework for creating views of the visual.
        * A data structure that is shared between all views of the visual.
        * Abstract `draw`, `bounds`, `attach`, and `detach` methods.

    Parameters
    ----------
    vshare : instance of VisualShare | None
        The visual share.

    Notes
    -----
    When used in the scenegraph, all Visual classes are mixed with
    `vispy.scene.Node` in order to implement the methods, attributes and
    capabilities required for their usage within it.

    This subclasses Frozen so that subclasses can easily freeze their
    properties.
    """
    def __init__(self, vshare=None):
        self._view_class = getattr(self, '_view_class', VisualView)

        self._vshare = VisualShare() if vshare is None else vshare
        self._vshare.views[self] = None

        self.events = EmitterGroup(source=self,
                                   auto_connect=True,
                                   update=Event,
                                   bounds_change=Event
                                   )

        self._transforms = None
        self.transforms = TransformSystem()

    @property
    def transform(self):
        return self.transforms.visual_transform.transforms[0]

    @transform.setter
    def transform(self, tr):
        self.transforms.visual_transform = tr

    @property
    def transforms(self):
        return self._transforms

    @transforms.setter
    def transforms(self, trs):
        if trs is self._transforms:
            return
        if self._transforms is not None:
            self._transforms.changed.disconnect(self._transform_changed)
        self._transforms = trs
        trs.changed.connect(self._transform_changed)
        self._transform_changed()

    def get_transform(self, map_from='visual', map_to='render'):
        """Return a transform mapping between any two coordinate systems.

        Parameters
        ----------
        map_from : str
            The starting coordinate system to map from. Must be one of: visual,
            scene, document, canvas, framebuffer, or render.
        map_to : str
            The ending coordinate system to map to. Must be one of: visual,
            scene, document, canvas, framebuffer, or render.
        """
        return self.transforms.get_transform(map_from, map_to)

    @property
    def visible(self):
        return self._vshare.visible

    @visible.setter
    def visible(self, v):
        if v != self._vshare.visible:
            self._vshare.visible = v
            self.update()

    def view(self):
        """Return a new view of this visual.
        """
        return self._view_class(self)

    def draw(self):
        raise NotImplementedError(self)

    def attach(self, filt, view=None):
        """Attach a Filter to this visual.

        Each filter modifies the appearance or behavior of the visual.

        Parameters
        ----------
        filt : object
            The filter to attach.
        view : instance of VisualView | None
            The view to use.
        """
        raise NotImplementedError(self)

    def detach(self, filt, view=None):
        """Detach a filter.

        Parameters
        ----------
        filt : object
            The filter to detach.
        view : instance of VisualView | None
            The view to use.
        """
        raise NotImplementedError(self)

    def bounds(self, axis, view=None):
        """Get the bounds of the Visual

        Parameters
        ----------
        axis : int
            The axis.
        view : instance of VisualView
            The view to use.
        """
        if view is None:
            view = self
        if axis not in self._vshare.bounds:
            self._vshare.bounds[axis] = self._compute_bounds(axis, view)
        return self._vshare.bounds[axis]

    def _compute_bounds(self, axis, view):
        raise NotImplementedError(self)

    def _bounds_changed(self):
        self._vshare.bounds.clear()

    def update(self):
        """Update the Visual"""
        self.events.update()

    def _transform_changed(self, event=None):
        self.update()


class BaseVisualView(object):
    """Base class for a view on a visual.

    This class must be mixed with another Visual class to work properly. It
    works mainly by forwarding the calls to _prepare_draw, _prepare_transforms,
    and _compute_bounds to the viewed visual.
    """
    def __init__(self, visual):
        self._visual = visual

    @property
    def visual(self):
        return self._visual

    def _prepare_draw(self, view=None):
        self._visual._prepare_draw(view=view)

    def _prepare_transforms(self, view):
        self._visual._prepare_transforms(view)

    def _compute_bounds(self, axis, view):
        self._visual._compute_bounds(axis, view)

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

    Parameters
    ----------
    vcode : str
        Vertex shader code.
    fcode : str
        Fragment shader code.
    program : instance of Program | None
        The program to use. If None, a program will be constructed using
        ``vcode`` and ``fcode``.
    vshare : instance of VisualShare | None
        The visual share, if necessary.
    """
    def __init__(self, vcode='', fcode='', program=None, vshare=None):
        self._view_class = VisualView
        BaseVisual.__init__(self, vshare)
        if vshare is None:
            self._vshare.draw_mode = None
            self._vshare.index_buffer = None
            if program is None:
                self._vshare.program = MultiProgram(vcode, fcode)
            else:
                self._vshare.program = program
                if len(vcode) > 0 or len(fcode) > 0:
                    raise ValueError("Cannot specify both program and "
                                     "vcode/fcode arguments.")

        self._program = self._vshare.program.add_program()
        self._prepare_transforms(self)
        self._filters = []
        self._hooks = {}

    def set_gl_state(self, preset=None, **kwargs):
        """Define the set of GL state parameters to use when drawing

        Parameters
        ----------
        preset : str
            Preset to use.
        **kwargs : dict
            Keyword arguments to `gloo.set_state`.
        """
        self._vshare.gl_state = kwargs
        self._vshare.gl_state['preset'] = preset

    def update_gl_state(self, *args, **kwargs):
        """Modify the set of GL state parameters to use when drawing

        Parameters
        ----------
        *args : tuple
            Arguments.
        **kwargs : dict
            Keyword argments.
        """
        if len(args) == 1:
            self._vshare.gl_state['preset'] = args[0]
        elif len(args) != 0:
            raise TypeError("Only one positional argument allowed.")
        self._vshare.gl_state.update(kwargs)

    def _compute_bounds(self, axis, view):
        """Return the (min, max) bounding values of this visual along *axis*
        in the local coordinate system.
        """
        return None

    def _prepare_draw(self, view=None):
        """This visual is about to be drawn.

        Visuals should implement this method to ensure that all program
        and GL state variables are updated immediately before drawing.

        Return False to indicate that the visual should not be drawn.
        """
        return True

    def _prepare_transforms(self, view):
        """This method is called whenever the TransformSystem instance is
        changed for a view.

        Assign a view's transforms to the proper shader template variables
        on the view's shader program.

        Note that each view has its own TransformSystem. In this method we
        connect the appropriate mapping functions from the view's
        TransformSystem to the view's program.
        """
        raise NotImplementedError()
        # Todo: this method can be removed if we somehow enable the shader
        # to specify exactly which transform functions it needs by name. For
        # example:
        #
        #     // mapping function is automatically defined from the
        #     // corresponding transform in the view's TransformSystem
        #     gl_Position = visual_to_render(a_position);
        #

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
        if not self.visible:
            return
        self._configure_gl_state()
        if self._prepare_draw(view=self) is False:
            return

        if self._vshare.draw_mode is None:
            raise ValueError("_draw_mode has not been set for visual %r" %
                             self)
        try:
            self._program.draw(self._vshare.draw_mode,
                               self._vshare.index_buffer)
        except Exception:
            logger.warn("Error drawing visual %r" % self)
            raise

    def _configure_gl_state(self):
        gloo.set_state(**self._vshare.gl_state)

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

    def attach(self, filt, view=None):
        """Attach a Filter to this visual

        Each filter modifies the appearance or behavior of the visual.

        Parameters
        ----------
        filt : object
            The filter to attach.
        view : instance of VisualView | None
            The view to use.
        """
        if view is None:
            self._vshare.filters.append(filt)
            for view in self._vshare.views.keys():
                filt._attach(view)
        else:
            view._filters.append(filt)
            filt._attach(view)

    def detach(self, filt, view=None):
        """Detach a filter.

        Parameters
        ----------
        filt : object
            The filter to detach.
        view : instance of VisualView | None
            The view to use.
        """
        if view is None:
            self._vshare.filters.remove(filt)
            for view in self._vshare.views.keys():
                filt._detach(view)
        else:
            view._filters.remove(filt)
            filt._detach(view)


class VisualView(BaseVisualView, Visual):
    """A view on another Visual instance.

    View instances are created by calling ``visual.view()``.

    Because this is a subclass of `Visual`, all instances of `VisualView`
    define their own shader program (which is a clone of the viewed visual's
    program), transforms, and filter attachments.
    """
    def __init__(self, visual):
        BaseVisualView.__init__(self, visual)
        Visual.__init__(self, vshare=visual._vshare)

        # Attach any shared filters
        for filt in self._vshare.filters:
            filt._attach(self)


class CompoundVisual(BaseVisual):
    """Visual consisting entirely of sub-visuals.

    To the user, a compound visual behaves exactly like a normal visual--it
    has a transform system, draw() and bounds() methods, etc. Internally, the
    compound visual automatically manages proxying these transforms and methods
    to its sub-visuals.

    Parameters
    ----------
    subvisuals : list of BaseVisual instances
        The list of visuals to be combined in this compound visual.
    """
    def __init__(self, subvisuals):
        self._view_class = CompoundVisualView
        self._subvisuals = []
        BaseVisual.__init__(self)
        for v in subvisuals:
            self.add_subvisual(v)
        self.freeze()

    def add_subvisual(self, visual):
        """Add a subvisual

        Parameters
        ----------
        visual : instance of Visual
            The visual to add.
        """
        visual.transforms = self.transforms
        visual._prepare_transforms(visual)
        self._subvisuals.append(visual)
        visual.events.update.connect(self._subv_update)
        self.update()

    def remove_subvisual(self, visual):
        """Remove a subvisual

        Parameters
        ----------
        visual : instance of Visual
            The visual to remove.
        """
        visual.events.update.disconnect(self._subv_update)
        self._subvisuals.remove(visual)
        self.update()

    def _subv_update(self, event):
        self.update()

    def _transform_changed(self, event=None):
        for v in self._subvisuals:
            v.transforms = self.transforms
        BaseVisual._transform_changed(self)

    def draw(self):
        """Draw the visual
        """
        if not self.visible:
            return
        if self._prepare_draw(view=self) is False:
            return

        for v in self._subvisuals:
            if v.visible:
                v.draw()

    def _prepare_draw(self, view):
        pass

    def _prepare_transforms(self, view):
        for v in view._subvisuals:
            v._prepare_transforms(v)

    def set_gl_state(self, preset=None, **kwargs):
        """Define the set of GL state parameters to use when drawing

        Parameters
        ----------
        preset : str
            Preset to use.
        **kwargs : dict
            Keyword arguments to `gloo.set_state`.
        """
        for v in self._subvisuals:
            v.set_gl_state(preset=preset, **kwargs)

    def update_gl_state(self, *args, **kwargs):
        """Modify the set of GL state parameters to use when drawing

        Parameters
        ----------
        *args : tuple
            Arguments.
        **kwargs : dict
            Keyword argments.
        """
        for v in self._subvisuals:
            v.update_gl_state(*args, **kwargs)

    def attach(self, filt, view=None):
        """Attach a Filter to this visual

        Each filter modifies the appearance or behavior of the visual.

        Parameters
        ----------
        filt : object
            The filter to attach.
        view : instance of VisualView | None
            The view to use.
        """
        for v in self._subvisuals:
            v.attach(filt, v)

    def detach(self, filt, view=None):
        """Detach a filter.

        Parameters
        ----------
        filt : object
            The filter to detach.
        view : instance of VisualView | None
            The view to use.
        """
        for v in self._subvisuals:
            v.detach(filt, v)

    def _compute_bounds(self, axis, view):
        bounds = None
        for v in view._subvisuals:
            if v.visible:
                vb = v.bounds(axis)
                if bounds is None:
                    bounds = vb
                elif vb is not None:
                    bounds = [min(bounds[0], vb[0]), max(bounds[1], vb[1])]
        return bounds


class CompoundVisualView(BaseVisualView, CompoundVisual):
    def __init__(self, visual):
        BaseVisualView.__init__(self, visual)
        # Create a view on each sub-visual
        subv = [v.view() for v in visual._subvisuals]
        CompoundVisual.__init__(self, subv)

        # Attach any shared filters
        for filt in self._vshare.filters:
            for v in self._subvisuals:
                filt._attach(v)
