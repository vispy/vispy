# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import unittest
import copy

from vispy.util.event import Event, EventEmitter, EmitterGroup
from vispy.util import use_log_level
from vispy.testing import run_tests_if_main, assert_true, assert_raises


class BasicEvent(Event):
    pass


class TypedEvent(Event):

    def __init__(self, **kwargs):
        kwargs['type'] = 'typed_event'
        Event.__init__(self, **kwargs)


class TestGroups(unittest.TestCase):

    def test_group_construction(self):
        """EmitterGroup basic construction"""
        grp = EmitterGroup(em1=Event,
                           em2=BasicEvent,
                           em3=TypedEvent)

        grp.em1.connect(self.record_event)
        grp.em2.connect(self.record_event)
        grp.em3.connect(self.record_event)
        self.result = None
        ev = grp.em1()
        self.assert_result(event=ev, type='em1', event_class=Event)
        ev = grp.em2()
        self.assert_result(event=ev, type='em2', event_class=BasicEvent)
        ev = grp.em3()
        self.assert_result(
            event=ev,
            type='typed_event',
            event_class=TypedEvent)

    def test_group_add_emitter(self):
        """EmitterGroup.add"""
        grp = EmitterGroup(em1=Event)
        grp.em1.connect(self.record_event)
        self.result = None
        ev = grp.em1()
        self.assert_result(event=ev, type='em1')

        grp.add(em2=BasicEvent)
        grp.em2.connect(self.record_event)
        ev = grp.em2()
        self.assert_result(event=ev, type='em2', event_class=BasicEvent)

        grp.add(em3=TypedEvent)
        grp.em3.connect(self.record_event)
        ev = grp.em3(test_key=2)
        self.assert_result(
            event=ev,
            type='typed_event',
            event_class=TypedEvent,
            test_key=2)

        try:
            grp.add(em3=Event)
            assert False, "Double-added emitter"
        except ValueError:
            pass

        try:
            grp.add(add=Event)
            assert False, "Added event with invalid name"
        except ValueError:
            pass

    def test_group_block(self):
        """EmitterGroup.block_all"""
        grp = EmitterGroup(em1=Event, em2=Event)

        def cb(ev):
            self.result = 1
        grp.em1.connect(self.record_event)
        grp.em2.connect(self.record_event)
        grp.connect(cb)

        self.result = None
        grp.block_all()
        try:
            grp.em1()
            grp.em2()
            grp(type='test_event')
        finally:
            grp.unblock_all()
        assert self.result is None

    def test_group_ignore(self):
        """EmitterGroup.block_all"""
        grp = EmitterGroup(em1=Event)
        grp.em1.connect(self.error_event)
        with use_log_level('warning', record=True, print_msg=False) as l:
            grp.em1()
        assert_true(len(l) >= 1)
        grp.ignore_callback_errors = False
        assert_raises(RuntimeError, grp.em1)
        grp.ignore_callback_errors = True
        with use_log_level('warning', record=True, print_msg=False) as l:
            grp.em1()
        assert_true(len(l) >= 1)

    def test_group_disconnect(self):
        """EmitterGroup.disconnect"""
        grp = EmitterGroup(em1=Event)

        assert len(grp.em1.callbacks) == 0, grp.em1.callbacks
        grp.connect(self.record_event)
        assert len(grp.em1.callbacks) == 1
        grp.add(em2=Event)
        assert len(grp.em2.callbacks) == 1
        grp.disconnect()
        assert len(grp.em1.callbacks) == 0
        assert len(grp.em2.callbacks) == 0

    def test_group_autoconnect(self):
        """EmitterGroup auto-connect"""
        class Source:

            def on_em1(self, ev):
                self.result = 1

            def em2_event(self, ev):
                self.result = 2

            def em3_event(self, ev):
                self.result = 3
        src = Source()
        grp = EmitterGroup(source=src, em1=Event, auto_connect=False)
        src.result = None
        grp.em1()
        assert src.result is None

        grp = EmitterGroup(source=src, em1=Event, auto_connect=True)
        src.result = None
        grp.em1()
        assert src.result == 1

        grp.auto_connect_format = "%s_event"
        grp.add(em2=Event)
        src.result = None
        grp.em2()
        assert src.result == 2

        grp.add(em3=Event, auto_connect=False)
        src.result = None
        grp.em3()
        assert src.result is None

    def test_add_custom_emitter(self):
        class Emitter(EventEmitter):

            def _prepare_event(self, *args, **kwargs):
                ev = super(Emitter, self)._prepare_event(*args, **kwargs)
                ev.test_key = 1
                return ev

        class Source:
            pass
        src = Source()

        grp = EmitterGroup(source=src, em1=Emitter(type='test_event1'))
        grp.em1.connect(self.record_event)
        self.result = None
        ev = grp.em1()
        self.assert_result(
            event=ev,
            test_key=1,
            type='test_event1',
            source=src)

        grp.add(em2=Emitter(type='test_event2'))
        grp.em2.connect(self.record_event)
        self.result = None
        ev = grp.em2()
        self.assert_result(
            event=ev,
            test_key=1,
            type='test_event2',
            source=src)

    def test_group_connect(self):
        grp = EmitterGroup(source=self, em1=Event)
        grp.connect(self.record_event)
        self.result = None
        ev = grp.em1(test_key=1)
        self.assert_result(
            event=ev,
            source=self,
            sources=[
                self,
                self],
            test_key=1)

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
                except Exception:
                    try:
                        attrs[name] = copy.copy(val)
                    except Exception:
                        attrs[name] = val
        if key is None:
            self.result = ev, attrs
        else:
            if not hasattr(self, 'result') or self.result is None:
                self.result = {}
            self.result[key] = ev, attrs

    def error_event(self, ev, key=None):
        raise RuntimeError('Errored')

    def assert_result(self, key=None, **kwargs):
        assert (hasattr(self, 'result') and self.result is not None), \
            "No event recorded"

        if key is None:
            event, event_attrs = self.result
        else:
            event, event_attrs = self.result[key]

        assert isinstance(event, Event), "Emitted object is not Event instance"

        for name, val in kwargs.items():
            if name == 'event':
                assert event is val, "Event objects do not match"

            elif name == 'event_class':
                assert isinstance(event, val), \
                    "Emitted object is not instance of %s" % val.__name__

            else:
                attr = event_attrs[name]
                assert (attr == val), "Event.%s != %s  (%s)" % (
                    name, str(val), str(attr))


run_tests_if_main()
