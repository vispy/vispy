# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# Adapted from PyQtGraph
import sys
from . import ptime
from .. import config


class Profiler(object):
    """Simple profiler allowing directed, hierarchical measurement of time
    intervals.

    By default, profilers are disabled.  To enable profiling, set the
    environment variable `VISPYPROFILE` to a comma-separated list of
    fully-qualified names of profiled functions.

    Calling a profiler registers a message (defaulting to an increasing
    counter) that contains the time elapsed since the last call.  When the
    profiler is about to be garbage-collected, the messages are passed to the
    outer profiler if one is running, or printed to stdout otherwise.

    If `delayed` is set to False, messages are immediately printed instead.

    Example:
        def function(...):
            profiler = Profiler()
            ... do stuff ...
            profiler('did stuff')
            ... do other stuff ...
            profiler('did other stuff')
            # profiler is garbage-collected and flushed at function end

    If this function is a method of class C, setting `VISPYPROFILE` to
    "C.function" (without the module name) will enable this profiler.

    For regular functions, use the qualified name of the function, stripping
    only the initial "vispy.." prefix from the module.
    """

    _profilers = (config['profile'].split(",") if config['profile'] is not None
                  else [])
    
    _depth = 0
    _msgs = []
    # set this flag to disable all or individual profilers at runtime
    disable = False
    
    class DisabledProfiler(object):
        def __init__(self, *args, **kwds):
            pass
        
        def __call__(self, *args):
            pass
        
        def finish(self):
            pass
        
        def mark(self, msg=None):
            pass
        
    _disabled_profiler = DisabledProfiler()
        
    def __new__(cls, msg=None, disabled='env', delayed=True):
        """Optionally create a new profiler based on caller's qualname.
        """
        if (disabled is True or 
                (disabled == 'env' and len(cls._profilers) == 0)):
            return cls._disabled_profiler
                        
        # determine the qualified name of the caller function
        caller_frame = sys._getframe(1)
        try:
            caller_object_type = type(caller_frame.f_locals["self"])
        except KeyError:  # we are in a regular function
            qualifier = caller_frame.f_globals["__name__"].split(".", 1)[1]
        else:  # we are in a method
            qualifier = caller_object_type.__name__
        func_qualname = qualifier + "." + caller_frame.f_code.co_name
        if (disabled == 'env' and func_qualname not in cls._profilers and
                'all' not in cls._profilers):  # don't do anything
            return cls._disabled_profiler
        # create an actual profiling object
        cls._depth += 1
        obj = super(Profiler, cls).__new__(cls)
        obj._name = msg or func_qualname
        obj._delayed = delayed
        obj._mark_count = 0
        obj._finished = False
        obj._firstTime = obj._last_time = ptime.time()
        obj._new_msg("> Entering " + obj._name)
        return obj

    def __call__(self, msg=None, *args):
        """Register or print a new message with timing information.
        """
        if self.disable:
            return
        if msg is None:
            msg = str(self._mark_count)
        self._mark_count += 1
        new_time = ptime.time()
        elapsed = (new_time - self._last_time) * 1000
        self._new_msg("  " + msg + ": %0.4f ms", *(args + (elapsed,)))
        self._last_time = new_time
        
    def mark(self, msg=None):
        self(msg)

    def _new_msg(self, msg, *args):
        msg = "  " * (self._depth - 1) + msg
        if self._delayed:
            self._msgs.append((msg, args))
        else:
            self.flush()
            print(msg % args)

    def __del__(self):
        self.finish()
    
    def finish(self, msg=None):
        """Add a final message; flush the message list if no parent profiler.
        """
        if self._finished or self.disable:
            return        
        self._finished = True
        if msg is not None:
            self(msg)
        self._new_msg("< Exiting %s, total time: %0.4f ms", 
                      self._name, (ptime.time() - self._firstTime) * 1000)
        type(self)._depth -= 1
        if self._depth < 1:
            self.flush()
        
    def flush(self):
        if self._msgs:
            print("\n".join([m[0] % m[1] for m in self._msgs]))
            type(self)._msgs = []
