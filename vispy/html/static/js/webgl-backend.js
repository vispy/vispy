

// VispyWidget code
define(function(require) {
    "use strict";

    function _inline_glir_commands(commands, buffers) {
        // Put back the buffers within the GLIR commands before passing them
        // to the GLIR JavaScript interpretor.
        for (var i = 0; i < commands.length; i++) {
            var command = commands[i];
            if (command[0] == 'DATA') {
                var buffer_index = command[3]['buffer_index'];
                command[3] = buffers[buffer_index];
            }
        }
        return commands;
    }

    var vispy = require("/nbextensions/vispy/vispy.min.js");
    var widget = require("widgets/js/widget");

    var VispyView = widget.DOMWidgetView.extend({

        initialize: function (parameters) {
            VispyView.__super__.initialize.apply(this, [parameters]);

            this.model.on('msg:custom', this.on_msg, this);

            // Track canvas size changes.
            this.model.on('change:width', this.size_changed, this);
            this.model.on('change:height', this.size_changed, this);
        },

        render: function() {
            var that = this;

            var canvas = $('<canvas></canvas>');
            // canvas.css('border', '1px solid rgb(171, 171, 171)');
            canvas.css('background-color', '#000');
            canvas.attr('tabindex', '1');
            this.$el.append(canvas);
            this.$canvas = canvas;

            // Initialize the VispyCanvas.
            this.c = vispy.init(canvas);

            this.c.on_resize(function (e) {
                that.model.set('width', e.size[0]);
                that.model.set('height', e.size[1]);
                that.touch();
            });

            // Start the event loop.
            this.c.on_event_tick(function() {
                // This callback function will be called at each JS tick,
                // before the GLIR commands are flushed.

                // Retrieve and flush the event queue.
                var events = that.c.event_queue.get();

                that.c.event_queue.clear();
                // Send the events if the queue is not empty.
                if (events.length > 0) {
                    // Create the message.
                    var msg = {
                        msg_type: 'events',
                        contents: events
                    };
                    // console.debug(events);
                    // Send the message with the events to Python.
                    that.send(msg);
                }
            });

            vispy.start_event_loop();
            var msg = { msg_type: 'init' };
            this.send(msg);
            // Make sure the size is correctly set up upon first display.
            this.size_changed();
            this.c.resize();
            this.c.resizable();
        },

        on_msg: function(comm_msg) {
            var buffers = comm_msg.buffers;
            var msg = comm_msg; //.content.data.content;
            if (msg == undefined) return;
            // Receive and execute the GLIR commands.
            if (msg.msg_type == 'glir_commands') {
                var commands = msg.commands;
                // Get the buffers messages.
                if (msg.array_serialization == 'base64') {
                    var buffers_msg = msg.buffers;
                }
                else if (msg.array_serialization == 'binary') {
                    // Need to put the raw binary buffers in JavaScript
                    // objects for the inline commands.
                    var buffers_msg = [];
                    for (var i = 0; i < buffers.length; i++) {
                        buffers_msg[i] = {
                            'storage_type': 'binary',
                            'buffer': buffers[i]
                        };
                    }
                }

                // Make the GLIR commands ready for the JavaScript parser
                // by inlining the buffers.
                var commands_inlined = _inline_glir_commands(
                    commands, buffers_msg);
                for (var i = 0; i < commands_inlined.length; i++) {
                    var command = commands[i];
                    // Replace
                    // console.debug(command);
                    this.c.command(command);
                }
            }
        },

        // When the model's size changes.
        size_changed: function() {
            var size = [this.model.get('width'), this.model.get('height')];
            this.$canvas.css('width', size[0] + 'px');
            this.$canvas.css('height', size[1] + 'px');
        },

        remove: function() {
            vispy.unregister(this.c);
            // Inform Python that the widget has been removed.
            this.send({
                msg_type: 'status',
                contents: 'removed'
            });
        }
    });

    //IPython.WidgetManager.register_widget_view('VispyView', VispyView);
    return { 'VispyView' : VispyView };
});
