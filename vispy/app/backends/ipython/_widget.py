# -*- coding: utf-8 -*-
# Copyright (c) 2014, 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

try:
    from IPython.html.widgets import DOMWidget
    from IPython.utils.traitlets import Unicode, Int, Bool
except Exception as exp:
    # Init dummy objects needed to import this module withour errors.
    # These are all overwritten with imports from IPython (on success)
    DOMWidget = object
    Unicode = Int = Float = Bool = lambda *args, **kwargs: None
    available, testable, why_not, which = False, False, str(exp), None
else:
    available, testable, why_not, which = True, False, None, None
from ....app.backends._ipynb_util import create_glir_message
from ....app import Timer


# ---------------------------------------------------------- IPython Widget ---
def _stop_timers(canvas):
    """Stop all timers in a canvas."""
    for attr in dir(canvas):
        try:
            attr_obj = getattr(canvas, attr)
        except NotImplementedError:
            # This try/except is needed because canvas.position raises
            # an error (it is not implemented in this backend).
            attr_obj = None
        if isinstance(attr_obj, Timer):
            attr_obj.stop()


class VispyWidget(DOMWidget):
    _view_name = Unicode("VispyView", sync=True)
    _view_module = Unicode('/nbextensions/vispy/webgl-backend.js', sync=True)

    #height/width of the widget is managed by IPython.
    #it's a string and can be anything valid in CSS.
    #here we only manage the size of the viewport.
    width = Int(sync=True)
    height = Int(sync=True)
    resizable = Bool(value=True, sync=True)

    def __init__(self, **kwargs):
        super(VispyWidget, self).__init__(**kwargs)
        self.on_msg(self.events_received)
        self.canvas = None
        self.canvas_backend = None
        self.gen_event = None

    def set_canvas(self, canvas):
        self.width, self.height = canvas._backend._default_size
        self.canvas = canvas
        self.canvas_backend = self.canvas._backend
        self.canvas_backend.set_widget(self)
        self.gen_event = self.canvas_backend._gen_event
        #setup the backend widget then.

    # In IPython < 4, these callbacks are given two arguments; in
    # IPython/jupyter 4, they take 3. events_received is variadic to
    # accommodate both cases.
    def events_received(self, _, msg, *args):
        if msg['msg_type'] == 'init':
            self.canvas_backend._reinit_widget()
        elif msg['msg_type'] == 'events':
            events = msg['contents']
            for ev in events:
                self.gen_event(ev)
        elif msg['msg_type'] == 'status':
            if msg['contents'] == 'removed':
                # Stop all timers associated to the widget.
                _stop_timers(self.canvas_backend._vispy_canvas)

    def send_glir_commands(self, commands):
        # TODO: check whether binary websocket is available (ipython >= 3)
        # Until IPython 3.0 is released, use base64.
        array_serialization = 'base64'
        # array_serialization = 'binary'
        if array_serialization == 'base64':
            msg = create_glir_message(commands, 'base64')
            msg['array_serialization'] = 'base64'
            self.send(msg)
        elif array_serialization == 'binary':
            msg = create_glir_message(commands, 'binary')
            msg['array_serialization'] = 'binary'
            # Remove the buffers from the JSON message: they will be sent
            # independently via binary WebSocket.
            buffers = msg.pop('buffers')
            self.comm.send({"method": "custom", "content": msg},
                           buffers=buffers)
