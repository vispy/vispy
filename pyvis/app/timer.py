import pyvis.event
import pyvis



class Timer(object):
    """Timer used to schedule events in the future or on a repeating schedule.
    """
    def __init__(self, interval=0.0, connect=None, iterations=-1, start=False, app=None):
        self.timeout = pyvis.event.EventEmitter()
        self.timeout.defaults['source'] = self
        
        # Get app instance and make sure that it has an associated backend 
        app = pyvis.app.default_app if app is None else app
        app.use()
        
        # Instantiate the backed with the right class
        self._timer = app.backend_module.TimerBackend(self)
        
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
        
        
    def _timeout(self, *args):
        # called when the backend timer has triggered.
        if not self.running:
            return
        if self.max_iterations >= 0 and self.iter_count >= self.max_iterations:
            self.stop()
            return
        self.timeout(iteration=self.iter_count)
        self.iter_count += 1



class TimerBackend(object):
        
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


        