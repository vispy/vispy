## Event system:
##    - Canvas subclasses abstract basic windowing and input events
##    - High-level canvas will automatically forward events to scenegraph
##      and implement basic paint callback
##    - All events may trigger a list of callbacks which can be customized

##    - Must be possible to 
##        - respond to events by setting method attribute, overriding method,
##          or using event-connection decorator
##        - must be able to connect/disconnect functions 

class Event(object):
    """Class describing events that occur and can be reacted to with callbacks.
    For example, window and input events.
    
    *type* may be any string. Subclasses of EventReceiver will define the
    event types that they may receive.
    
    Specific event types may implement extra attributes to fully describe
    the event.
    """
    def __init__(self, type, **kwds):
        self.type = type
        self.accepted = False
        self.__dict__.update(kwds)
        
    def accept(self):
        """Inform the event dispatcher that this event has been handled and 
        should not be delivered to any more callbacks."""
        self.accepted = True


class EventReceiver(object):
    """Base class for objects that can receive and propagate event 
    notifications."""
    def __init__(self):
        self._event_callbacks = {}  # {event_type: [list of callbacks], ...}
        self._blocked_events = []
    
    def call_event(self, *args, **kwds):
        """Deliver an event to the event handlers registered for event.type on 
        this object. 
        
        If the first argument is an Event instance, then that Event is sent and
        all other arguments are ignored. Otherwise, a new Event will be 
        constructed as Event(*args, **kwds).
        
        If the object has a method named event.type+"_event", it will be called
        after all other registered handlers.
        
        Returns the event.
        """
        if len(args) > 0 and isinstance(args[0], Event):
            event = args[0]
        else:
            event = Event(*args, **kwds)
        
        if 'all' in self._blocked_events or event.type in self._blocked_events:
            return event
        
        ## run externally registered callbackes
        for cb in self._event_callbacks.get(event.type, []):
            cb(event)
            if event.accepted is True:
                break

        ## run local method callback, if it is defined.
        if hasattr(self, event.type+'_event'):
            getattr(self, event.type+'_event')(event)
        
        return event
    
    def connect(self, event_type, callback=None, append=False):
        """Register a new callback to be invoked when events are received with 
        type == event_type. 
        
        By default, callbacks are added to the beginning of
        the callback list (when an event arrives, the last callback registered
        is the first one invoked). If *append* == True, then the callback will 
        be added to the end of the callback list. If the callback was already
        connected, it will be removed and re-added in the new position. 
        
        If callback is None, then this function returns a function allowing it
        to be used as a decorator::
        
            @window.connect('resize')
            def resize_handler(event):
               ...
        """
        if callback is None:
            return self._make_decorator(event_type, append)

        if event_type not in self._event_callbacks:
            self._event_callbacks[event_type] = []
            
        cb_list = self._event_callbacks[event_type]
        if callback in cb_list:
            cb_list.remove(callback)
        
        if append:
            cb_list.append(callback)
        else:
            cb_list.insert(0, callback)
        
    def disconnect(self, event_type=None, callback=None):
        """Disconnect events from their registered callbacks. 
        
        If *event_type* is None, then the *callback* is disconnected from 
        any event types it is connected to. If *callback* is None, then 
        all callbacks are disconnected from *event_type*. If both arguments
        are None, then all event callbacks are disconnected.
        
        Note that this has no effect on callbacks that are implemented as 
        methods of the event receiver.
        """
        if event_type is None:
            event_type = [self._event_callbacks.keys()]
        else:
            event_type = [event_type]
            
        if callback is None:
            for type in event_type:
                self._event_callbacks.pop(type, None)
        else:
            for type in event_type:
                self._event_callbacks.remove(callback)
            
    def is_connected(self, event_type, callback):
        """Return True if *callback* is registered to receive events of
        *event_type* from this object."""
        return callback in self._event_callbacks.get(event_type, [])
        
    def block_events(self, event_type):
        """Temporarily block execution of events until unblock_events is called.
        
        *event_type* specifies the type of events to block. If block_events is 
        called more than once with a specific event type, that type must be 
        unblocked the same number of times before it will be delivered again.
        
        If *event_type* is 'all', then all events will be blocked until 
        unblock_events('all') is called."""
        self._blocked_events.append(event_type)
        
        
    def unblock_events(self, event_type):
        """Restore execution of events blocked with block_events.
        
        *event_type* specifies the type of events to unblock. By default, all
        event types are unblocked."""
        self._blocked_events.remove(event_type)

    def _make_decorator(self, event_type, append):
        ## see connect(callback=None)
        def connect(fn):
            self.connect(event_type, fn, append)
            return fn
        return connect

