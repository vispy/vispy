## Event system:
##    - Canvas subclasses abstract basic windowing and input events
##    - High-level canvas will automatically forward events to scenegraph
##      and implement basic paint callback
##    - All events may trigger a list of callbacks which can be customized

##    - Must be possible to 
##        - respond to events by setting method attribute, overriding method,
##          or using event-connection decorator
##        - must be able to connect/disconnect functions 

import collections

# todo: we want Events to be light and fast, so that performance  is not degraded too much with move events.
# todo: use __slots__ (at least on the event classes where it matters)

class Event(object):
    """Class describing events that occur and can be reacted to with callbacks.
    For example, window and input events.
    
    Specific event types may implement extra attributes to fully describe
    the event.
    """
    def __init__(self, **kwds):
        self.accepted = False
        self.__dict__.update(kwds)
        
    def accept(self):
        """Inform the event dispatcher that this event has been handled and 
        should not be delivered to any more callbacks."""
        self.accepted = True
    
    def ignore(self):
        """Inform the event dispatcher that this event has not been handled and 
        should be delivered to another callback."""
        self.accepted = False
        
    def __repr__(self):
        attrs = " ".join(["%s=%s" % pair for pair in self.__dict__.items()])
        return "<%s %s>" % (self.__class__.__name__, attrs)


class EventEmitter(object):
    """Manages a list of event callbacks. 
    
    Each instance of EventEmitter is intended to represent a particular event. 
    Callbacks may be registered with the EventEmitter to receive notifications
    whenever the event occurs. 
    
    To inform the EventEmitter that the event has occurred (and thus it should
    invoke all of its callbacks), it is called directly with either an Event 
    instance as an argument or a set of arguments used to construct an Event.
    
    Callbacks may be specified either as a callable object or symbolically,
    as (object, attribute_name). In the latter case, the attribute is retrieved
    from object and called every time the event is emitted. 
    """
    def __init__(self, callback=None):
        """May be initialized with or without a callback.
        """
        self.callbacks = []
        self.blocked = 0
        self.defaults = {}
        if callback is not None:
            self.connect(callback)
        
    def connect(self, callback):
        """Connect this emitter to a new callback. 
        
        *callback* may be either a callable object or a tuple 
        (object, attr_name) where object.attr_name will point to a callable
        object.
        
        If the callback is already connected, then the request is ignored.
        """
        if callback in self.callbacks:
            return
        self.callbacks.insert(0, callback)
        return callback  ## allows connect to be used as a decorator
            
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
        """Invoke all callbacks for this emitter.
        
        This may be called either with an Event instance as the first argument
        or with any other set of arguments used to construct an Event.
        
        All events emitted will have extra attributes set corresponding to
        self.defaults, unless the Event already has those attributes.
        """
        if len(args) > 0 and isinstance(args[0], Event):
            event = args[0]
        else:
            event = Event(*args, **kwds)
            
        ## Copy default attributes onto this event (unless they are already 
        ## specified)
        for k,v in self.defaults.items():
            if not hasattr(event, k):
                setattr(event, k, v)
        
        if self.blocked > 0:
            return event
        
        for cb in self.callbacks:
            if isinstance(cb, tuple):
                cb = getattr(cb[0], cb[1], None)
                if cb is None:
                    continue
                
            cb(event)
            if event.accepted:
                break
        
        return event
            
    def block(self):
        self.blocked += 1
        
    def unblock(self):
        self.blocked = max(0, self.blocked-1)

    def blocker(self):
        return EventBlocker(self)


class EmitterGroup(EventEmitter):
    """EmitterGroup is a convenience class that manages a set of related 
    EventEmitters. Its primary purpose is to provide organization for objects
    that make use of multiple emitters and to reduce the boilerplate code needed
    to initialize those emitters with default connections.
    
    EmitterGroup instances are commonly stored as an 'events' attribute on 
    objects that use multiple emitters.
    
    EmitterGroup is also a subclass of EventEmitter, allowing it to emit its own
    events. Any callback that connects directly to the EmitterGroup will 
    receive _all_ of the events generated by the group's emitters.
    """
    def __init__(self, source, auto_connect=True, event_names=None, **kwds):
        """
        Initialize the EmitterGroup, optionally attaching new EventEmitters.
        
        *source* must be specified and indicates the object to which emitters
        will be automatically connected if *auto_connect* is True. All emitted
        events will also be given a 'source' attribute with this value.
        
        If *event_names* is given, it specifies a list of names of emitters
        to create and add to the handler. Each name generates one call to 
        `self.add(name)`.
        
        Keyword arguments are also used to initialize emitters, but additionally
        provide a mechanism for specifying pre-built EventEmitter instances.
        Each Keyword argument generates one call to `self.add(name, emitter)`.
        
        If *auto_connect* is True, then one connection will be made for each
        emitter that looks like `emitter.connect((source, 'on_'+event_name))`.
        This provides a simple mechanism for automatically connecting a large
        group of emitters to default callbacks.
        
        Example::
        
            source = SomeObject()
            source.events = EmitterGroup(source,
                                event_names=['mouse', 'key'],
                                wheel=None,
                                stylus=MyStylusEmitter()
                                )
                                
        The example above does the following:
        
            #. Create an EmitterGroup instance
            #. Attach four EventEmitters to the handler with the names 'mouse',
               'key', 'wheel', and 'stylus'.
            #. The first three emitters are all instances of EventEmitter,
               whereas the last is an instance of MyStylusEmitter.
            #. The four emitters are automatically connected to default 
               callbacks: source.on_mouse, source.on_key, source.on_wheel, and
               source.on_stylus. These connections are symbolic, so source
               is not required to have the callbacks implemented.
        """
        EventEmitter.__init__(self)
        
        self.source = source
        self.auto_connect = auto_connect
        self.auto_connect_format = "on_%s"
        self._emitters = collections.OrderedDict()
        self._emitters_connected = False  ## whether the sub-emitters have 
                                          ## been connected to the group
        if event_names is not None:
            kwds.update(dict([(name, None) for name in event_names]))
        for name,em in kwds.items():
            if em is None:
                em = EventEmitter()
            self.add(name, em)
    
    def __getitem__(self, name):
        """
        Return the emitter assigned to the specified name. 
        Note that emitters may also be retrieved as an attribute of the 
        EmitterGroup.
        """
        return self._emitters[name]
        
    def __setitem__(self, name, emitter):
        """
        Alias for EmitterGroup.add(name, emitter)
        """
        self.add(name, emitter)
        
    def add(self, name, emitter=None, auto_connect=None):
        if name in self._emitters:
            raise ValueError("EmitterGroup already has an emitter named '%s'" % name)
        if auto_connect is None:
            auto_connect = self.auto_connect
        if emitter is None:
            emitter = EventEmitter()
        emitter.defaults['event_name'] = name
        emitter.defaults['source'] = self.source
        
        self.__dict__[name] = emitter
        self._emitters[name] = emitter
        
        if auto_connect:
            emitter.connect((self.source, self.auto_connect_format % name))
            
        # If emitters are connected to the group already, then this one should
        # be connected as well.
        if self._emitters_connected:
            emitter.connect(self)
            
        return emitter

    @property
    def emitters(self):
        return self._emitters
    
    def __iter__(self):
        """
        Iterates over the names of emitters in this group.
        """
        for k in self._emitters:
            yield k
    
    def block_all(self):
        for em in self._emitters.values():
            em.block()
    
    def unblock_all(self):
        for em in self._emitters.values():
            em.unblock()
    
    #def blocker(self):
        #return EventBlocker(self)

    def connect(self, *args, **kwds):
        self._connect_emitters(True)
        return EventEmitter.connect(self, *args, **kwds)

    def disconnect(self, *args, **kwds):
        ret = EventEmitter.disconnect(self, *args, **kwds)
        if len(self.connections) == 0:
            self._connect_emitters(False)
        return ret
    
    def _connect_emitters(self, connect):
        ## Connect/disconnect all sub-emitters from the group. This allows the
        ## group to emit an event whenever _any_ of the sub-emitters emit, 
        ## while simultaneously eliminating the overhead if nobody is listening.
        if connect:
            for emitter in self:
                self[emitter].connect(self)
        else:
            for emitter in self:
                self[emitter].disconnect(self)
            
        self._emitters_connected = connect
        
            
class EventBlocker(object):
    def __init__(self, target):
        self.target = target
        
    def __enter__(self):
        self.target.block()
        
    def __exit__(self, *args):
        self.target.unblock()

