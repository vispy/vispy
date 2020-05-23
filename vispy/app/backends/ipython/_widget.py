# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

try:
    from ipywidgets.widgets import DOMWidget, register
    from traitlets import Unicode, Int, Bool, Dict
except Exception as exp:
    # Init dummy objects needed to import this module without errors.
    # These are all overwritten with imports from IPython (on success)
    DOMWidget = object

    def _noop(x):
        return x
    
    register = _noop

    class _MockTraitlet(object):
        def __init__(self, *args, **kwargs):
            pass

        def tag(self, *args, **kwargs):
            pass

    Unicode = Int = Float = Bool = Dict = _MockTraitlet
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


@register
class VispyWidget(DOMWidget):
    _view_name = Unicode("VispyView").tag(sync=True)
    _view_module = Unicode('vispy').tag(sync=True)
    _view_module_version = Unicode('~0.3.0').tag(sync=True)
    _model_name = Unicode('VispyModel').tag(sync=True)
    _model_module = Unicode('vispy').tag(sync=True)
    _model_module_version = Unicode('~0.3.0').tag(sync=True)

    #height/width of the widget is managed by IPython.
    #it's a string and can be anything valid in CSS.
    #here we only manage the size of the viewport.
    width = Int().tag(sync=True)
    height = Int().tag(sync=True)
    resizable = Bool(value=True).tag(sync=True)
    webgl_config = Dict(value={}).tag(sync=True)

    def __init__(self, **kwargs):
        if DOMWidget is object:
            raise ImportError("'ipywidgets' must be installed to use the notebook backend.")
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

    def events_received(self, widget, content, buffers):
        if content['msg_type'] == 'init':
            self.canvas_backend._reinit_widget()
        elif content['msg_type'] == 'events':
            events = content['contents']
            for ev in events:
                self.gen_event(ev)
        elif content['msg_type'] == 'status':
            if content['contents'] == 'removed':
                # Stop all timers associated to the widget.
                _stop_timers(self.canvas_backend._vispy_canvas)

    def send_glir_commands(self, commands):
        # older versions of ipython (<3.0) use base64
        # array_serialization = 'base64'
        array_serialization = 'binary'
        msg = create_glir_message(commands, array_serialization)
        msg['array_serialization'] = array_serialization
        if array_serialization == 'base64':
            self.send(msg)
        elif array_serialization == 'binary':
            # Remove the buffers from the JSON message: they will be sent
            # independently via binary WebSocket.
            self.send(msg, buffers=msg.pop('buffers', None))
