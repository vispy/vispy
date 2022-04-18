# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
The event module implements the classes that make up the event system.
The Event class and its subclasses are used to represent "stuff that happens".
The EventEmitter class provides an interface to connect to events and
to emit events. The EmitterGroup groups EventEmitter objects.

For more information see http://github.com/vispy/vispy/wiki/API_Events

"""

from __future__ import division

from collections import OrderedDict
import inspect
import traceback
import weakref

from .logs import logger, _handle_exception


class Event(object):
    """Class describing events that occur and can be reacted to with callbacks.
    Each event instance contains information about a single event that has
    occurred such as a key press, mouse motion, timer activation, etc.

    Subclasses: :class:`KeyEvent`, :class:`MouseEvent`, :class:`TouchEvent`,
    :class:`StylusEvent`

    The creation of events and passing of events to the appropriate callback
    functions is the responsibility of :class:`EventEmitter` instances.

    Note that each event object has an attribute for each of the input
    arguments listed below.

    Parameters
    ----------
    type : str
       String indicating the event type (e.g. mouse_press, key_release)
    native : object (optional)
       The native GUI event object
    **kwargs : keyword arguments
        All extra keyword arguments become attributes of the event object.
    """

    def __init__(self, type, native=None, **kwargs):
        # stack of all sources this event has been emitted through
        self._sources = []
        self._handled = False
        self._blocked = False
        # Store args
        self._type = type
        self._native = native
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def source(self):
        """The object that the event applies to (i.e. the source of the event)."""
        return self._sources[-1] if self._sources else None

    @property
    def sources(self):
        """List of objects that the event applies to (i.e. are or have
        been a source of the event). Can contain multiple objects in case
        the event traverses a hierarchy of objects.
        """
        return self._sources

    def _push_source(self, source):
        self._sources.append(source)

    def _pop_source(self):
        return self._sources.pop()

    @property
    def type(self):
        # No docstring; documeted in class docstring
        return self._type

    @property
    def native(self):
        # No docstring; documeted in class docstring
        return self._native

    @property
    def handled(self):
        """This boolean property indicates whether the event has already been
        acted on by an event handler. Since many handlers may have access to
        the same events, it is recommended that each check whether the event
        has already been handled as well as set handled=True if it decides to
        act on the event.
        """
        return self._handled

    @handled.setter
    def handled(self, val):
        self._handled = bool(val)

    @property
    def blocked(self):
        """This boolean property indicates whether the event will be delivered
        to event callbacks. If it is set to True, then no further callbacks
        will receive the event. When possible, it is recommended to use
        Event.handled rather than Event.blocked.
        """
        return self._blocked

    @blocked.setter
    def blocked(self, val):
        self._blocked = bool(val)

    def __repr__(self):
        # Try to generate a nice string representation of the event that
        # includes the interesting properties.
        # need to keep track of depth because it is
        # very difficult to avoid excessive recursion.
        global _event_repr_depth
        _event_repr_depth += 1
        try:
            if _event_repr_depth > 2:
                return "<...>"
            attrs = []
            for name in dir(self):
                if name.startswith('_'):
                    continue
                # select only properties
                if not hasattr(type(self), name) or \
                        not isinstance(getattr(type(self), name), property):
                    continue
                attr = getattr(self, name)

                attrs.append("%s=%s" % (name, attr))
            return "<%s %s>" % (self.__class__.__name__, " ".join(attrs))
        finally:
            _event_repr_depth -= 1

    def __str__(self):
        """Shorter string representation"""
        return self.__class__.__name__

_event_repr_depth = 0


class EventEmitter(object):

    """Encapsulates a list of event callbacks.

    Each instance of EventEmitter represents the source of a stream of similar
    events, such as mouse click events or timer activation events. For
    example, the following diagram shows the propagation of a mouse click
    event to the list of callbacks that are registered to listen for that
    event::

       User clicks    |Canvas creates
       mouse on       |MouseEvent:                |'mouse_press' EventEmitter:         |callbacks in sequence: # noqa
       Canvas         |                           |                                    |  # noqa
                   -->|event = MouseEvent(...) -->|Canvas.events.mouse_press(event) -->|callback1(event)  # noqa
                      |                           |                                 -->|callback2(event)  # noqa
                      |                           |                                 -->|callback3(event)  # noqa

    Callback functions may be added or removed from an EventEmitter using
    :func:`connect() <vispy.event.EventEmitter.connect>` or
    :func:`disconnect() <vispy.event.EventEmitter.disconnect>`.

    Calling an instance of EventEmitter will cause each of its callbacks
    to be invoked in sequence. All callbacks are invoked with a single
    argument which will be an instance of :class:`Event <vispy.event.Event>`.

    EventEmitters are generally created by an EmitterGroup instance.

    Parameters
    ----------
    source : object
        The object that the generated events apply to. All emitted Events will
        have their .source property set to this value.
    type : str or None
        String indicating the event type (e.g. mouse_press, key_release)
    event_class : subclass of Event
        The class of events that this emitter will generate.
    """

    def __init__(self, source=None, type=None, event_class=Event):
        self._callbacks = []
        self._callback_refs = []

        # count number of times this emitter is blocked for each callback.
        self._blocked = {None: 0}

        # used to detect emitter loops
        self._emitting = 0
        self.source = source
        self.default_args = {}
        if type is not None:
            self.default_args['type'] = type

        assert inspect.isclass(event_class)
        self.event_class = event_class

        self._ignore_callback_errors = True
        self.print_callback_errors = 'reminders'

    @property
    def ignore_callback_errors(self):
        """Whether exceptions during callbacks will be caught by the emitter

        This allows it to continue invoking other callbacks if an error
        occurs.
        """
        return self._ignore_callback_errors

    @ignore_callback_errors.setter
    def ignore_callback_errors(self, val):
        self._ignore_callback_errors = val

    @property
    def print_callback_errors(self):
        """Print a message and stack trace if a callback raises an exception

        Valid values are "first" (only show first instance), "reminders" (show
        complete first instance, then counts), "always" (always show full
        traceback), or "never".

        This assumes ignore_callback_errors=True. These will be raised as
        warnings, so ensure that the vispy logging level is set to at
        least "warning".
        """
        return self._print_callback_errors

    @print_callback_errors.setter
    def print_callback_errors(self, val):
        if val not in ('first', 'reminders', 'always', 'never'):
            raise ValueError('print_callback_errors must be "first", '
                             '"reminders", "always", or "never"')
        self._print_callback_errors = val

    @property
    def callback_refs(self):
        """The set of callback references"""
        return tuple(self._callback_refs)

    @property
    def callbacks(self):
        """The set of callbacks"""
        return tuple(self._callbacks)

    @property
    def source(self):
        """The object that events generated by this emitter apply to"""
        return None if self._source is None else self._source(
        )  # get object behind weakref

    @source.setter
    def source(self, s):
        if s is None:
            self._source = None
        else:
            self._source = weakref.ref(s)

    def connect(self, callback, ref=False, position='first',
                before=None, after=None):
        """Connect this emitter to a new callback.

        Parameters
        ----------
        callback : function | tuple
            *callback* may be either a callable object or a tuple
            (object, attr_name) where object.attr_name will point to a
            callable object. Note that only a weak reference to ``object``
            will be kept.
        ref : bool | str
            Reference used to identify the callback in ``before``/``after``.
            If True, the callback ref will automatically determined (see
            Notes). If False, the callback cannot be referred to by a string.
            If str, the given string will be used. Note that if ``ref``
            is not unique in ``callback_refs``, an error will be thrown.
        position : str
            If ``'first'``, the first eligible position is used (that
            meets the before and after criteria), ``'last'`` will use
            the last position.
        before : str | callback | list of str or callback | None
            List of callbacks that the current callback should precede.
            Can be None if no before-criteria should be used.
        after : str | callback | list of str or callback | None
            List of callbacks that the current callback should follow.
            Can be None if no after-criteria should be used.

        Notes
        -----
        If ``ref=True``, the callback reference will be determined from:

            1. If ``callback`` is ``tuple``, the secend element in the tuple.
            2. The ``__name__`` attribute.
            3. The ``__class__.__name__`` attribute.

        The current list of callback refs can be obtained using
        ``event.callback_refs``. Callbacks can be referred to by either
        their string reference (if given), or by the actual callback that
        was attached (e.g., ``(canvas, 'swap_buffers')``).

        If the specified callback is already connected, then the request is
        ignored.

        If before is None and after is None (default), the new callback will
        be added to the beginning of the callback list. Thus the
        callback that is connected _last_ will be the _first_ to receive
        events from the emitter.
        """
        callbacks = self.callbacks
        callback_refs = self.callback_refs

        callback = self._normalize_cb(callback)

        if callback in callbacks:
            return

        # deal with the ref
        if isinstance(ref, bool):
            if ref:
                if isinstance(callback, tuple):
                    ref = callback[1]
                elif hasattr(callback, '__name__'):  # function
                    ref = callback.__name__
                else:  # Method, or other
                    ref = callback.__class__.__name__
            else:
                ref = None
        elif not isinstance(ref, str):
            raise TypeError('ref must be a bool or string')
        if ref is not None and ref in self._callback_refs:
            raise ValueError('ref "%s" is not unique' % ref)

        # positions
        if position not in ('first', 'last'):
            raise ValueError('position must be "first" or "last", not %s'
                             % position)

        # bounds
        bounds = list()  # upper & lower bnds (inclusive) of possible cb locs
        for ri, criteria in enumerate((before, after)):
            if criteria is None or criteria == []:
                bounds.append(len(callback_refs) if ri == 0 else 0)
            else:
                if not isinstance(criteria, list):
                    criteria = [criteria]
                for c in criteria:
                    count = sum([(c == cn or c == cc) for cn, cc
                                 in zip(callback_refs, callbacks)])
                    if count != 1:
                        raise ValueError('criteria "%s" is in the current '
                                         'callback list %s times:\n%s\n%s'
                                         % (criteria, count,
                                            callback_refs, callbacks))
                matches = [ci for ci, (cn, cc) in enumerate(zip(callback_refs,
                                                                callbacks))
                           if (cc in criteria or cn in criteria)]
                bounds.append(matches[0] if ri == 0 else (matches[-1] + 1))
        if bounds[0] < bounds[1]:  # i.e., "place before" < "place after"
            raise RuntimeError('cannot place callback before "%s" '
                               'and after "%s" for callbacks: %s'
                               % (before, after, callback_refs))
        idx = bounds[1] if position == 'first' else bounds[0]  # 'last'

        # actually add the callback
        self._callbacks.insert(idx, callback)
        self._callback_refs.insert(idx, ref)
        return callback  # allows connect to be used as a decorator

    def disconnect(self, callback=None):
        """Disconnect a callback from this emitter.

        If no callback is specified, then *all* callbacks are removed.
        If the callback was not already connected, then the call does nothing.
        """
        if callback is None:
            self._callbacks = []
            self._callback_refs = []
        else:
            callback = self._normalize_cb(callback)
            if callback in self._callbacks:
                idx = self._callbacks.index(callback)
                self._callbacks.pop(idx)
                self._callback_refs.pop(idx)

    def _normalize_cb(self, callback):
        # dereference methods into a (self, method_name) pair so that we can
        # make the connection without making a strong reference to the
        # instance.
        if inspect.ismethod(callback):
            callback = (callback.__self__, callback.__name__)

        # always use a weak ref
        if (isinstance(callback, tuple) and not
                isinstance(callback[0], weakref.ref)):
            callback = (weakref.ref(callback[0]),) + callback[1:]

        return callback

    def __call__(self, *args, **kwargs):
        """__call__(**kwargs)
        Invoke all callbacks for this emitter.

        Emit a new event object, created with the given keyword
        arguments, which must match with the input arguments of the
        corresponding event class. Note that the 'type' argument is
        filled in by the emitter.

        Alternatively, the emitter can also be called with an Event
        instance as the only argument. In this case, the specified
        Event will be used rather than generating a new one. This allows
        customized Event instances to be emitted and also allows EventEmitters
        to be chained by connecting one directly to another.

        Note that the same Event instance is sent to all callbacks.
        This allows some level of communication between the callbacks
        (notably, via Event.handled) but also requires that callbacks
        be careful not to inadvertently modify the Event.
        """
        # This is a VERY highly used method; must be fast!
        blocked = self._blocked

        # create / massage event as needed
        event = self._prepare_event(*args, **kwargs)

        # Add our source to the event; remove it after all callbacks have been
        # invoked.
        event._push_source(self.source)
        self._emitting += 1
        try:
            if blocked.get(None, 0) > 0:  # this is the same as self.blocked()
                return event

            rem = []
            for cb in self._callbacks[:]:
                if isinstance(cb, tuple):
                    obj = cb[0]()
                    if obj is None:
                        rem.append(cb)
                        continue
                    cb = getattr(obj, cb[1], None)
                    if cb is None:
                        continue

                if blocked.get(cb, 0) > 0:
                    continue

                if self._emitting > 1:
                    raise RuntimeError('EventEmitter loop detected!')

                self._invoke_callback(cb, event)
                if event.blocked:
                    break

            # remove callbacks to dead objects
            for cb in rem:
                self.disconnect(cb)
        finally:
            self._emitting -= 1
            if event._pop_source() != self.source:
                raise RuntimeError("Event source-stack mismatch.")

        return event

    def _invoke_callback(self, cb, event):
        try:
            cb(event)
        except Exception:
            _handle_exception(self.ignore_callback_errors,
                              self.print_callback_errors,
                              self, cb_event=(cb, event))

    def _prepare_event(self, *args, **kwargs):
        # When emitting, this method is called to create or otherwise alter
        # an event before it is sent to callbacks. Subclasses may extend
        # this method to make custom modifications to the event.
        if len(args) == 1 and not kwargs and isinstance(args[0], Event):
            event = args[0]
            # Ensure that the given event matches what we want to emit
            assert isinstance(event, self.event_class)
        elif not args:
            args = self.default_args.copy()
            args.update(kwargs)
            event = self.event_class(**args)
        else:
            raise ValueError("Event emitters can be called with an Event "
                             "instance or with keyword arguments only.")
        return event

    def blocked(self, callback=None):
        """Return boolean indicating whether the emitter is blocked for
        the given callback.
        """
        return self._blocked.get(callback, 0) > 0

    def block(self, callback=None):
        """Block this emitter. Any attempts to emit an event while blocked
        will be silently ignored. If *callback* is given, then the emitter
        is only blocked for that specific callback.

        Calls to block are cumulative; the emitter must be unblocked the same
        number of times as it is blocked.
        """
        self._blocked[callback] = self._blocked.get(callback, 0) + 1

    def unblock(self, callback=None):
        """Unblock this emitter. See :func:`event.EventEmitter.block`.

        Note: Use of ``unblock(None)`` only reverses the effect of
        ``block(None)``; it does not unblock callbacks that were explicitly
        blocked using ``block(callback)``.
        """
        if callback not in self._blocked or self._blocked[callback] == 0:
            raise RuntimeError("Cannot unblock %s for callback %s; emitter "
                               "was not previously blocked." %
                               (self, callback))
        b = self._blocked[callback] - 1
        if b == 0 and callback is not None:
            del self._blocked[callback]
        else:
            self._blocked[callback] = b

    def blocker(self, callback=None):
        """Return an EventBlocker to be used in 'with' statements.

        Examples
        --------
        For example, one could do::

            with emitter.blocker():
                pass  # ..do stuff; no events will be emitted..

        """
        return EventBlocker(self, callback)


class WarningEmitter(EventEmitter):
    """
    EventEmitter subclass used to allow deprecated events to be used with a
    warning message.
    """

    def __init__(self, message, *args, **kwargs):
        self._message = message
        self._warned = False
        EventEmitter.__init__(self, *args, **kwargs)

    def connect(self, cb, *args, **kwargs):
        self._warn(cb)
        return EventEmitter.connect(self, cb, *args, **kwargs)

    def _invoke_callback(self, cb, event):
        self._warn(cb)
        return EventEmitter._invoke_callback(self, cb, event)

    def _warn(self, cb):
        if self._warned:
            return

        # don't warn about unimplemented connections
        if isinstance(cb, tuple) and getattr(cb[0], cb[1], None) is None:
            return

        traceback.print_stack()
        logger.warning(self._message)
        self._warned = True


class EmitterGroup(EventEmitter):
    """EmitterGroup instances manage a set of related
    :class:`EventEmitters <vispy.event.EventEmitter>`.
    Its primary purpose is to provide organization for objects
    that make use of multiple emitters and to reduce the boilerplate code
    needed to initialize those emitters with default connections.

    EmitterGroup instances are usually stored as an 'events' attribute on
    objects that use multiple emitters. For example::

         EmitterGroup  EventEmitter
                 |       |
        Canvas.events.mouse_press
        Canvas.events.resized
        Canvas.events.key_press

    EmitterGroup is also a subclass of
    :class:`EventEmitters <vispy.event.EventEmitter>`,
    allowing it to emit its own
    events. Any callback that connects directly to the EmitterGroup will
    receive *all* of the events generated by the group's emitters.

    Parameters
    ----------
    source : object
        The object that the generated events apply to.
    auto_connect : bool
        If *auto_connect* is True (default), then one connection will
        be made for each emitter that looks like
        :func:`emitter.connect((source, 'on_' + event_name))
        <vispy.event.EventEmitter.connect>`.
        This provides a simple mechanism for automatically connecting a large
        group of emitters to default callbacks.
    emitters : keyword arguments
        See the :func:`add <vispy.event.EmitterGroup.add>` method.
    """

    def __init__(self, source=None, auto_connect=True, **emitters):
        EventEmitter.__init__(self, source)

        self.auto_connect = auto_connect
        self.auto_connect_format = "on_%s"
        self._emitters = OrderedDict()
        # whether the sub-emitters have been connected to the group:
        self._emitters_connected = False
        self.add(**emitters)

    def __getitem__(self, name):
        """
        Return the emitter assigned to the specified name.
        Note that emitters may also be retrieved as an attribute of the
        EmitterGroup.
        """
        return self._emitters[name]

    def __setitem__(self, name, emitter):
        """Alias for EmitterGroup.add(name=emitter)"""
        self.add(**{name: emitter})

    def add(self, auto_connect=None, **kwargs):
        """Add one or more EventEmitter instances to this emitter group.
        Each keyword argument may be specified as either an EventEmitter
        instance or an Event subclass, in which case an EventEmitter will be
        generated automatically::

            # This statement:
            group.add(mouse_press=MouseEvent,
                      mouse_release=MouseEvent)

            # ..is equivalent to this statement:
            group.add(mouse_press=EventEmitter(group.source, 'mouse_press',
                                               MouseEvent),
                      mouse_release=EventEmitter(group.source, 'mouse_press',
                                                 MouseEvent))
        """
        if auto_connect is None:
            auto_connect = self.auto_connect

        # check all names before adding anything
        for name in kwargs:
            if name in self._emitters:
                raise ValueError(
                    "EmitterGroup already has an emitter named '%s'" %
                    name)
            elif hasattr(self, name):
                raise ValueError("The name '%s' cannot be used as an emitter; "
                                 "it is already an attribute of EmitterGroup"
                                 % name)

        # add each emitter specified in the keyword arguments
        for name, emitter in kwargs.items():
            if emitter is None:
                emitter = Event

            if inspect.isclass(emitter) and issubclass(emitter, Event):
                emitter = EventEmitter(
                    source=self.source,
                    type=name,
                    event_class=emitter)
            elif not isinstance(emitter, EventEmitter):
                raise Exception('Emitter must be specified as either an '
                                'EventEmitter instance or Event subclass. '
                                '(got %s=%s)' % (name, emitter))

            # give this emitter the same source as the group.
            emitter.source = self.source

            setattr(self, name, emitter)
            self._emitters[name] = emitter

            if auto_connect and self.source is not None:
                emitter.connect((self.source, self.auto_connect_format % name))

            # If emitters are connected to the group already, then this one
            # should be connected as well.
            if self._emitters_connected:
                emitter.connect(self)

    @property
    def emitters(self):
        """List of current emitters in this group."""
        return self._emitters

    def __iter__(self):
        """Iterates over the names of emitters in this group."""
        for k in self._emitters:
            yield k

    def block_all(self):
        """Block all emitters in this group."""
        self.block()
        for em in self._emitters.values():
            em.block()

    def unblock_all(self):
        """Unblock all emitters in this group."""
        self.unblock()
        for em in self._emitters.values():
            em.unblock()

    def connect(self, callback, ref=False, position='first',
                before=None, after=None):
        """Connect the callback to the event group. The callback will receive
        events from *all* of the emitters in the group.

        See :func:`EventEmitter.connect() <vispy.event.EventEmitter.connect>`
        for arguments.
        """
        self._connect_emitters(True)
        return EventEmitter.connect(self, callback, ref, position,
                                    before, after)

    def disconnect(self, callback=None):
        """Disconnect the callback from this group. See
        :func:`connect() <vispy.event.EmitterGroup.connect>` and
        :func:`EventEmitter.connect() <vispy.event.EventEmitter.connect>` for
        more information.
        """
        ret = EventEmitter.disconnect(self, callback)
        if len(self._callbacks) == 0:
            self._connect_emitters(False)
        return ret

    def _connect_emitters(self, connect):
        # Connect/disconnect all sub-emitters from the group. This allows the
        # group to emit an event whenever _any_ of the sub-emitters emit,
        # while simultaneously eliminating the overhead if nobody is listening.
        if connect:
            for emitter in self:
                self[emitter].connect(self)
        else:
            for emitter in self:
                self[emitter].disconnect(self)

        self._emitters_connected = connect

    @property
    def ignore_callback_errors(self):
        return super(EventEmitter, self).ignore_callback_errors

    @ignore_callback_errors.setter
    def ignore_callback_errors(self, ignore):
        EventEmitter.ignore_callback_errors.fset(self, ignore)
        for emitter in self._emitters.values():
            if isinstance(emitter, EventEmitter):
                emitter.ignore_callback_errors = ignore
            elif isinstance(emitter, EmitterGroup):
                emitter.ignore_callback_errors_all(ignore)


class EventBlocker(object):
    """Represents a block for an EventEmitter to be used in a context
    manager (i.e. 'with' statement).
    """

    def __init__(self, target, callback=None):
        self.target = target
        self.callback = callback

    def __enter__(self):
        self.target.block(self.callback)

    def __exit__(self, *args):
        self.target.unblock(self.callback)
