import pyvis.event
import pyvis

class Timer(object):
    """Timer used to schedule events in the future or on a repeating schedule.
    """
    def __init__(self, backend=None, interval=0.0, connect=None, iterations=-1, start=False):
        self.timeout = pyvis.event.EventEmitter()
        self.timeout.defaults['source'] = self
        
        if backend is None:
            backend = pyvis.config['default_backend']
        self._timer = TimerBackend._pyvis_create(backend, self)
        self._interval = interval
        self._running = False
        self.iter_count = 0
        self.max_iterations = iterations
        if connect is not None:
            self.timeout.connect(connect)
        if start:
            self.start()

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, val):
        self._interval = val
        if self.running:
            self.stop()
            self.start()

    @property
    def running(self):
        return self._running

    def start(self, interval=None, iterations=None):
        """Start the timer. 

        A timeout event will be generated every *interval* seconds.
        If *interval* is None, then self.interval will be used.
        
        If *iterations* is specified, the timer will stop after 
        emitting that number of events. If unspecified, then 
        the previous value of self.iterations will be used. If the value is 
        negative, then the timer will continue running until stop() is called.
        """
        self.iter_count = 0
        if interval is not None:
            self.interval = interval
        if iterations is not None:
            self.max_iterations = iterations
        self._timer._pyvis_start(self.interval)
        self._running = True
        
        
    def stop(self):
        """Stop the timer."""
        self._timer._pyvis_stop()
        self._running = False
        
    def run_event_loop(self):
        """Execute the event loop for this Timer's backend.
        """
        return self._timer._pyvis_run()
        
    def quit_event_loop(self):
        """Exit the event loop for this Timer's backend.
        """
        return self._timer._pyvis_quit()
        
        
    def _timeout(self):
        ## called when the backend timer has triggered.
        if not self.running:
            return
        if self.max_iterations >= 0 and self.iter_count >= self.max_iterations:
            self.stop()
            return
        self.timeout(iteration=self.iter_count)
        self.iter_count += 1
        
class TimerBackend(object):
    @classmethod
    def _pyvis_create(cls, backend, timer):
        """Create a new TimerBackend instance from the named backend.
        (options are 'qt', 'pyglet', 'gtk', ...)
        
        This is equivalent to::
        
            import pyvis.opengl.backends.<backend> as B
            return B.<Backend>Timer(timer)
        """
        mod_name = 'pyvis.canvas.backends.' + backend
        __import__(mod_name)
        mod = getattr(pyvis.canvas.backends, backend)
        return getattr(mod, backend.capitalize()+"TimerBackend")(timer)
        
    def __init__(self, timer):
        self._pyvis_timer = timer

    def _pyvis_start(self, interval):
        raise Exception("Method must be reimplemented in subclass.")
        
    def _pyvis_stop(self):
        raise Exception("Method must be reimplemented in subclass.")

    def _pyvis_run(self):
        raise Exception("Method must be reimplemented in subclass.")
        
    def _pyvis_quit(self):
        raise Exception("Method must be reimplemented in subclass.")


        