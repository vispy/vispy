# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
The event modules implements the classes that make up the event system.
The Event class and its subclasses are used to represent "stuff that happens".
The EventEmitter class provides an interface to connect to events and
to emit events. The EmitterGroup groups EventEmitter objects.

For more information see http://github.com/vispy/vispy/wiki/API_Events

"""

from __future__ import division

import sys
import inspect
import weakref

from .ordereddict import OrderedDict
from ._logging import logger


class Event(object):

    """Class describing events that occur and can be reacted to with callbacks.
    Each event instance contains information about a single event that has
    occurred such as a key press, mouse motion, timer activation, etc.

    Subclasses: :class:`KeyEvent`, :class:`MouseEvent`, :class:`TouchEvent`,
    :class:`StylusEvent`

    The creation of events and passing of events to the appropriate callback
    functions in the responsibility of :class:`EventEmitter` instances.

    Note that each event object has an attribute for each of the input
    arguments listed below.

    Input arguments
    ---------------
    type : str
       String indicating the event type (e.g. mouse_press, key_release)
    native : object (optional)
       The native GUI event object
    **kwds : keyword arguments
        All extra keyword arguments become attributes of the event object.
    """

    def __init__(self, type, native=None, **kwds):
        # stack of all sources this event has been emitted through
        self._sources = []
        self._handled = False
        self._blocked = False
        # Store args
        self._type = type
        self._native = native
        for k, v in kwds.items():
            setattr(self, k, v)

    @property
    def source(self):
        """The object that the event applies to (i.e. the source of the event).
        """
        return self._sources[-1] if self._sources else None

    @property
    def sources(self):
        """ List of objects that the event applies to (i.e. are or have
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
        global _event_repr_depth  # need to keep track of depth because it is
                                 # very difficult to avoid excessive recursion.
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

    Input arguments
    ---------------
    source : object
        The object that the generated events apply to. All emitted Events will
        have their .source property set to this value.
    type : str or None
        String indicating the event type (e.g. mouse_press, key_release)
    event_class : subclass of Event
        The class of events that this emitter will generate.


    Attributes
    ----------

    ignore_callback_errors : bool
        If True, exceptions raised while invoking callbacks will be caught by
        the emitter, allowing it to continue invoking other callbacks.
    print_callback_errors : bool
        If True, the emitter prints a message and stack trace whenever a
        callback raises an exception. (assumes ignore_callback_errors=True).
        NOTE: These will be raised as warnings, so ensure that the vispy
        logging level is set to at least "warning".
    """

    def __init__(self, source=None, type=None, event_class=Event):
        self.callbacks = []
        self.blocked = 0
        self._emitting = False  # used to detect emitter loops
        self.source = source
        self.default_args = {}
        if type is not None:
            self.default_args['type'] = type

        assert inspect.isclass(event_class)
        self.event_class = event_class

        self.ignore_callback_errors = True
        self.print_callback_errors = True

    @property
    def source(self):
        """ The object that events generated by this emitter apply to.
        """
        return None if self._source is None else self._source(
        )  # get object behind weakref

    @source.setter
    def source(self, s):
        if s is None:
            self._source = None
        else:
            self._source = weakref.ref(s)

    def connect(self, callback):
        """Connect this emitter to a new callback.

        *callback* may be either a callable object or a tuple
        (object, attr_name) where object.attr_name will point to a callable
        object.

        If the callback is already connected, then the request is ignored.

        The new callback will be added to the beginning of the callback list;
        thus the callback that is connected _last_ will be the _first_ to
        receive events from the emitter.
        """
        if callback in self.callbacks:
            return
        self.callbacks.insert(0, callback)
        return callback  # allows connect to be used as a decorator

    def disconnect(self, callback=None):
        """Disconnect a callback from this emitter.

        If no callback is specified, then _all_ callbacks are removed.
        If the callback was not already connected, then the call does nothing.
        """
        if callback is None:
            self.callbacks = []
        else:
            try:
                self.callbacks.remove(callback)
            except ValueError:
                pass

    def __call__(self, *args, **kwds):
        """ __call__(**kwds)
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
        if self._emitting:
            raise RuntimeError('EventEmitter loop detected!')

        # create / massage event as needed
        event = self._prepare_event(*args, **kwds)

        # Add our source to the event; remove it after all callbacks have been
        # invoked.
        event._push_source(self.source)
        self._emitting = True
        try:
            if self.blocked > 0:
                return event

            for cb in self.callbacks:
                if isinstance(cb, tuple):
                    cb = getattr(cb[0], cb[1], None)
                    if cb is None:
                        continue

                try:
                    cb(event)
                except:
                    # get traceback and store (so we can do postmortem
                    # debugging)
                    type, value, tb = sys.exc_info()
                    tb = tb.tb_next  # Skip *this* frame
                    sys.last_type = type
                    sys.last_value = value
                    sys.last_traceback = tb
                    # Handle
                    if self.ignore_callback_errors:
                        if self.print_callback_errors:
                            sys.excepthook(type, value, tb)
                            logger.warning("Error invoking callback for "
                                           "event: %s" % str(event))
                    else:
                        raise

                if event.blocked:
                    break
        finally:
            self._emitting = False
            if event._pop_source() != self.source:
                raise RuntimeError("Event source-stack mismatch.")

        return event

    def _prepare_event(self, *args, **kwds):
        # When emitting, this method is called to create or otherwise alter
        # an event before it is sent to callbacks. Subclasses may extend
        # this method to make custom modifications to the event.
        if len(args) == 1 and not kwds and isinstance(args[0], Event):
            event = args[0]
            # Ensure that the given event matches what we want to emit
            assert isinstance(event, self.event_class)
        elif not args:
            args = self.default_args.copy()
            args.update(kwds)
            event = self.event_class(**args)
        else:
            raise ValueError("Event emitters can be called with an Event "
                             "instance or with keyword arguments only.")
        return event

    def block(self):
        """Block this emitter. Any attempts to emit an event while blocked
        will be silently ignored.

        Calls to block are cumulative; the emitter must be unblocked the same
        number of times as it is blocked.
        """
        self.blocked += 1

    def unblock(self):
        """ Unblock this emitter. See :func:`event.EventEmitter.block`.
        """
        self.blocked = max(0, self.blocked - 1)

    def blocker(self):
        """Return an EventBlocker to be used in 'with' statements::

               with emitter.blocker():
                   ..do stuff; no events will be emitted..

        """
        return EventBlocker(self)


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
    receive _all_ of the events generated by the group's emitters.

    Input arguments
    ---------------
    source : object
        The object that the generated events apply to.
    auto_connect : bool
        If *auto_connect* is True (default), then one connection will
        be made for each emitter that looks like
        :func:`emitter.connect((source, 'on_'+event_name))
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
        self._emitters_connected = False  # whether the sub-emitters have
                                          # been connected to the group

        self.add(**emitters)

    def __getitem__(self, name):
        """
        Return the emitter assigned to the specified name.
        Note that emitters may also be retrieved as an attribute of the
        EmitterGroup.
        """
        return self._emitters[name]

    def __setitem__(self, name, emitter):
        """
        Alias for EmitterGroup.add(name=emitter)
        """
        self.add(**{name: emitter})

    def add(self, auto_connect=None, **kwds):
        """ Add one or more EventEmitter instances to this emitter group.
        Each keyword argument may be specified as either an EventEmitter
        instance or an Event subclass, in which case an EventEmitter will be
        generated automatically. Thus::

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
        for name in kwds:
            if name in self._emitters:
                raise ValueError(
                    "EmitterGroup already has an emitter named '%s'" %
                    name)
            elif hasattr(self, name):
                raise ValueError("The name '%s' cannot be used as an emitter; "
                                 "it is already an attribute of EmitterGroup"
                                 % name)

        # add each emitter specified in the keyword arguments
        for name, emitter in kwds.items():
            if emitter is None:
                emitter = Event

            if inspect.isclass(emitter) and issubclass(emitter, Event):
                emitter = EventEmitter(
                    source=self.source,
                    type=name,
                    event_class=emitter)
            elif not isinstance(emitter, EventEmitter):
                raise Exception('Emitter must be specified as either an '
                                'EventEmitter instance or Event subclass')

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
        """ List of current emitters in this group.
        """
        return self._emitters

    def __iter__(self):
        """
        Iterates over the names of emitters in this group.
        """
        for k in self._emitters:
            yield k

    def block_all(self):
        """ Block all emitters in this group.
        """
        self.block()
        for em in self._emitters.values():
            em.block()

    def unblock_all(self):
        """ Unblock all emitters in this group.
        """
        self.unblock()
        for em in self._emitters.values():
            em.unblock()

    def connect(self, callback):
        """ Connect the callback to the event group. The callback will receive
        events from _all_ of the emitters in the group.

        See :func:`EventEmitter.connect() <vispy.event.EventEmitter.connect>`
        for arguments.
        """
        self._connect_emitters(True)
        return EventEmitter.connect(self, callback)

    def disconnect(self, callback=None):
        """ Disconnect the callback from this group. See
        :func:`connect() <vispy.event.EmitterGroup.connect>` and
        :func:`EventEmitter.connect() <vispy.event.EventEmitter.connect>` for
        more information.
        """
        ret = EventEmitter.disconnect(self, callback)
        if len(self.callbacks) == 0:
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


class EventBlocker(object):

    """ Represents a block for an EventEmitter to be used in a context
    manager (i.e. 'with' statement).
    """

    def __init__(self, target):
        self.target = target

    def __enter__(self):
        self.target.block()

    def __exit__(self, *args):
        self.target.unblock()
