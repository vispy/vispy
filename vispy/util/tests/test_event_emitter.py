import unittest
import copy
import functools

from vispy.util.event import Event, EventEmitter


class BasicEvent(Event):
    pass


class TypedEvent(Event):

    def __init__(self, **kwds):
        kwds['type'] = 'typed_event'
        Event.__init__(self, **kwds)


class TestEmitters(unittest.TestCase):

    def test_emitter(self):
        """Emitter constructed with no arguments"""
        em = EventEmitter()

        # type must be specified when emitting since Event requires type
        # argument and the emitter was constructed without it.
        try:
            em()
            assert False, "Emitting event with no type should have failed."
        except TypeError:
            pass

        # See that emitted event has all of the properties we expect
        ev = self.try_emitter(em, type='test_event')
        self.assert_result(
            event=ev,
            event_class=Event,
            source=None,
            type='test_event',
            sources=[None])

    def test_emitter_source(self):
        """Emitter constructed with source argument"""
        em = EventEmitter(source=self)
        ev = self.try_emitter(em, type='test_event')
        self.assert_result(
            event=ev,
            event_class=Event,
            source=self,
            type='test_event',
            sources=[self])

        # overriding source should fail:
        try:
            ev = em(type='test_event', source=None)
            assert False, "Should not be able to specify source when emitting"
        except AttributeError:
            pass

    def test_emitter_type(self):
        """Emitter constructed with type argument"""
        em = EventEmitter(type='asdf')
        ev = self.try_emitter(em)
        self.assert_result(
            event=ev,
            event_class=Event,
            source=None,
            type='asdf',
            sources=[None])

        # overriding type is ok:
        ev = self.try_emitter(em, type='qwer')
        self.assert_result(
            event=ev,
            event_class=Event,
            source=None,
            type='qwer',
            sources=[None])

    def test_emitter_type_event_class(self):
        """Emitter constructed with event_class argument"""
        em = EventEmitter(event_class=BasicEvent)
        ev = self.try_emitter(em, type='test_event')
        self.assert_result(
            event=ev,
            event_class=BasicEvent,
            source=None,
            type='test_event',
            sources=[None])

        # specifying non-event class should fail (eventually):
        class X:

            def __init__(self, *args, **kwds):
                self.blocked = False

            def _push_source(self, s):
                pass

            def _pop_source(self):
                pass

        try:
            em = EventEmitter(event_class=X)
            ev = self.try_emitter(em, type='test_event')
            self.assert_result()  # checks event type
            assert False, \
                "Should not be able to construct emitter with non-Event class"
        except:
            pass

    def test_event_kwargs(self):
        """Extra Event kwargs"""
        em = EventEmitter(type='test_event')
        em.default_args['key1'] = 'test1'
        em.connect(self.record_event)
        self.result = None
        em(key2='test2')
        self.assert_result(key1='test1', key2='test2')

    def test_prebuilt_event(self):
        """Emit pre-built event"""
        em = EventEmitter(type='test_event')
        em.default_args['key1'] = 'test1'
        em.connect(self.record_event)

        self.result = None
        ev = Event(type='my_type')
        em(ev)
        self.assert_result(event=ev, type='my_type')
        assert not hasattr(self.result[0], 'key1')

    def test_emitter_subclass(self):
        """EventEmitter subclassing"""
        class MyEmitter(EventEmitter):

            def _prepare_event(self, *args, **kwds):
                ev = super(MyEmitter, self)._prepare_event(*args, **kwds)
                ev.test_tag = 1
                return ev
        em = MyEmitter(type='test_event')
        em.connect(self.record_event)
        self.result = None
        em()
        self.assert_result(test_tag=1)

    def test_typed_event(self):
        """Emit Event class with pre-specified type"""
        em = EventEmitter(event_class=TypedEvent)
        ev = self.try_emitter(em)  # no need to specify type here
        self.assert_result(
            event=ev,
            event_class=TypedEvent,
            source=None,
            type='typed_event',
            sources=[None])

    def test_disconnect(self):
        """Emitter disconnection"""
        em = EventEmitter(type='test_event')

        def cb1(ev):
            self.result = 1

        def cb2(ev):
            self.result = 2

        em.connect((self, 'record_event'))
        em.connect(cb1)
        em.connect(cb2)
        self.result = None
        em.disconnect(cb2)
        ev = em()
        self.assert_result(event=ev)

        self.result = None
        em.disconnect((self, 'record_event'))
        ev = em()
        assert self.result == 1

        self.result = None
        em.connect(cb1)
        em.connect(cb2)
        em.connect((self, 'record_event'))
        em.disconnect()
        em()
        assert self.result is None

    def test_reconnect(self):
        """Ignore callback reconnect"""
        em = EventEmitter(type='test_event')

        def cb(ev):
            self.result += 1

        em.connect(cb)
        em.connect(cb)  # second connection should do nothing.
        self.result = 0
        em()
        assert self.result == 1

    def test_decorator_connection(self):
        """Connection by decorator"""
        em = EventEmitter(type='test_event')

        @em.connect
        def cb(ev):
            self.result = 1

        self.result = None
        em()
        assert self.result == 1

    def test_chained_emitters(self):
        """Chained emitters"""
        em1 = EventEmitter(source=None, type='test_event1')
        em2 = EventEmitter(source=self, type='test_event2')
        em1.connect(em2)
        em1.connect(self.record_event)
        self.result = None
        ev = em1()
        self.assert_result(
            event=ev,
            event_class=Event,
            source=None,
            type='test_event1',
            sources=[None])

        # sources look different from second emitter, but type is the same.
        em1.disconnect(self.record_event)
        em2.connect(self.record_event)
        self.result = None
        ev = em1()
        self.assert_result(
            event=ev,
            event_class=Event,
            source=self,
            type='test_event1',
            sources=[
                None,
                self])

    def test_emitter_error_handling(self):
        """Emitter error handling"""
        em = EventEmitter(type='test_event')
        em.print_callback_errors = False

        def cb(ev):
            raise Exception('test')

        # first callback fails; second callback still runs.
        em.connect(self.record_event)
        em.connect(cb)
        self.result = None
        ev = em()
        self.assert_result(event=ev)

        # this time we should get an exception
        self.result = None
        em.ignore_callback_errors = False
        try:
            em()
            assert False, "Emission should have raised exception"
        except Exception as err:
            if str(err) != 'test':
                raise

    def test_emission_order(self):
        """Event emission order"""
        em = EventEmitter(type='test_event')

        def cb1(ev):
            self.result = 1

        def cb2(ev):
            self.result = 2

        em.connect(cb1)
        em.connect(cb2)
        self.result = None
        em()
        assert self.result == 1, "Events emitted in wrong order"

        em.disconnect()
        em.connect(cb2)
        em.connect(cb1)
        self.result = None
        em()
        assert self.result == 2, "Events emitted in wrong order"

    def test_multiple_callbacks(self):
        """Multiple emitter callbacks"""
        em = EventEmitter(type='test_event')
        em.connect(functools.partial(self.record_event, key=1))
        em.connect(functools.partial(self.record_event, key=2))
        em.connect(functools.partial(self.record_event, key=3))
        ev = em()
        self.assert_result(key=1, event=ev, sources=[None])
        self.assert_result(key=2, event=ev, sources=[None])
        self.assert_result(key=3, event=ev, sources=[None])

    def test_symbolic_callback(self):
        """Symbolic callbacks"""
        em = EventEmitter(type='test_event')
        em.connect((self, 'record_event'))
        ev = em()
        self.assert_result(event=ev)

        # now check overriding the connected method
        def cb(ev):
            self.result = 1

        self.result = None
        orig_method = self.record_event
        try:
            self.record_event = cb
            em()
            assert self.result == 1
        finally:
            self.record_event = orig_method

    def test_source_stack_integrity(self):
        """Emitter checks source stack"""
        em = EventEmitter(type='test_event')

        def cb(ev):
            ev._sources.append('x')
        em.connect(cb)

        try:
            em()
        except RuntimeError as err:
            if str(err) != 'Event source-stack mismatch.':
                raise

        em.disconnect()

        def cb(ev):
            ev._sources = []
        em.connect(cb)

        try:
            em()
        except IndexError:
            pass

    def test_emitter_loop(self):
        """Catch emitter loops"""
        em1 = EventEmitter(type='test_event1')
        em2 = EventEmitter(type='test_event2')
        em1.ignore_callback_errors = False
        em2.ignore_callback_errors = False

        # cross-connect emitters; when we emit, an exception should be raised
        # indicating an event loop.
        em1.connect(em2)
        em2.connect(em1)
        try:
            em1()
        except RuntimeError as err:
            if str(err) != 'EventEmitter loop detected!':
                raise err

    def test_emitter_block(self):
        """EventEmitter.blocker"""
        em = EventEmitter(type='test_event')
        em.connect(self.record_event)
        self.result = None

        with em.blocker():
            em()
        assert self.result is None

        ev = em()
        self.assert_result(event=ev)

    def test_event_handling(self):
        """Event.handled"""
        em = EventEmitter(type='test_event')

        def cb1(ev):
            ev.handled = True

        def cb2(ev):
            assert ev.handled
            self.result = 1
        em.connect(cb2)
        em.connect(cb1)
        self.result = None
        em()
        assert self.result == 1

    def test_event_block(self):
        """Event.blocked"""
        em = EventEmitter(type='test_event')

        def cb1(ev):
            ev.handled = True
            self.result = 1

        def cb2(ev):
            ev.blocked = True
            self.result = 2

        em.connect(self.record_event)
        em.connect(cb1)
        self.result = None
        em()
        self.assert_result()

        em.connect(cb2)
        self.result = None
        em()
        assert self.result == 2

    def try_emitter(self, em, **kwds):
        em.connect(self.record_event)
        self.result = None
        return em(**kwds)

    def record_event(self, ev, key=None):
        # get a copy of all event attributes because these may change
        # as the event is passed around; we want to know exactly what the event
        # looked like when it reached this callback.
        names = [name for name in dir(ev) if name[0] != '_']
        attrs = {}
        for name in names:
            val = getattr(ev, name)
            if name == 'source':
                attrs[name] = val
            elif name == 'sources':
                attrs[name] = val[:]
            else:
                try:
                    attrs[name] = copy.deepcopy(val)
                except:
                    try:
                        attrs[name] = copy.copy(val)
                    except:
                        attrs[name] = val
        if key is None:
            self.result = ev, attrs
        else:
            if not hasattr(self, 'result') or self.result is None:
                self.result = {}
            self.result[key] = ev, attrs

    def assert_result(self, key=None, **kwds):
        assert (hasattr(self, 'result') and self.result is not None), \
            "No event recorded"

        if key is None:
            event, event_attrs = self.result
        else:
            event, event_attrs = self.result[key]

        assert isinstance(event, Event), "Emitted object is not Event instance"

        for name, val in kwds.items():
            if name == 'event':
                assert event is val, "Event objects do not match"

            elif name == 'event_class':
                assert isinstance(event, val), \
                    "Emitted object is not instance of %s" % val.__name__

            else:
                attr = event_attrs[name]
                assert (attr == val), "Event.%s != %s  (%s)" % (
                    name, str(val), str(attr))
