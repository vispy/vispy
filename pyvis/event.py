## Event system:
##    - Canvas subclasses abstract basic windowing and input events
##    - High-level canvas will automatically forward events to scenegraph
##      and implement basic paint callback
##    - All events may trigger a list of callbacks which can be customized

##    - Must be possible to 
##        - respond to events by setting method attribute, overriding method,
##          or using event-connection decorator
##        - must be able to connect/disconnect functions 

"""

Example uses:


class Visual(EventHandler):
    
    clicked = EventEmitter('click')
    
    def click_event(self, ev):
        print "Visual was clicked at:", ev.pos
        

vis = Visual()

def cb1(event):
    print "cb1"
vis.clicked.connect(cb1)

@vis.clicked.connect
def cb2(event):
    print cb2

def cb3(event):
    print "cb3"
vis.connect('click', cb3)

vis.clicked.emit()  ## calls all four event handler functions



Another possibility:

class Visual(EventHandler):
    def __init__(self):
        EventHandler.__init__(self)
        self.clicked = EventEmitter(connect=self.click_event)
    
    def click_event(self, ev):
        print "Visual was clicked at:", ev.pos
        

Is it possible to do without the EventHandler class altogether? 







"""


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


class EventHandler(object):
    """Class that manages a group of related events.
    
    Intended to be used as the 'events' attribute for objects that need to
    manage a large number of event emitters.
    """
    def __init__(self, source, **kwds):
        self._emitters = {}
        for name,cb in kwds.items():
            em = EventEmitter(cb)
            em.defaults = {'event_name': name, 'source': source}
            setattr(self, name, em)
            self._emitters[name] = em
            
    def __getitem__(self, item):
        return self._emitters[item]
            
    @property
    def emitters(self):
        return self._emitters
            
    def block(self):
        for em in self._emitters.values():
            em.block()
            
    def unblock(self):
        for em in self._emitters.values():
            em.unblock()
            
    def blocker(self):
        return EventBlocker(self)

            
class EventBlocker(object):
    def __init__(self, target):
        self.target = target
        
    def __enter__(self):
        self.target.block()
        
    def __exit__(self, *args):
        self.target.unblock()

