require.config({
        paths: {
            "jquery-mousewheel": "//cdnjs.cloudflare.com/ajax/libs/jquery-mousewheel/3.1.11/jquery.mousewheel.min",
        }
});


// Load Vispy.js in the notebook.
IPython.load_extensions("vispy.min");
// HACK: this is UGLY but I didn't find a better way to do it
window.setTimeout(function() {
    require(["vispy"], 
        function(vispy) {
            window.vispy = vispy;
        }, 
        function(vispy) {
           window.vispy = vispy;
        });
}, 100);

// VispyWidget code
require(["widgets/js/widget", "widgets/js/manager"],
    function(widget, manager){
        var VispyView = IPython.DOMWidgetView.extend({
            render: function(){ 
                var that = this;

                var canvas = $('<canvas></canvas>');
                // canvas.css('border', '1px solid rgb(171, 171, 171)');
                canvas.css('background-color', '#000');
                this.$el.append(canvas);
                this.$canvas = canvas;
                this.width_changed();
                this.height_changed();

                // Initialize the VispyCanvas.
                var c = vispy.init(canvas);
                this.c = c;
                c.resize();
                c.resizable();

                // Track canvas size changes.
                this.model.on('change:width', this.width_changed, this);
                this.model.on('change:height', this.height_changed, this);


                window.VISPY_DEBUG = false;

                // Start the event loop.
                c.start_event_loop(function() {
                    // Retrieve and flush the event queue.
                    var events = that.c.event_queue.get();
                    that.c.event_queue.clear();
                    if (events.length == 0) {
                        return;
                    }
                    // Create the message.
                    var msg = {
                        msg_type: 'events',
                        contents: events
                    };
                    // console.debug(events);
                    // Send the message with the events to Python.
                    that.send(msg);
                });
            },

            on_msg: function(msg) {
                // Receive and execute the GLIR commands.
                if (msg.msg_type == 'glir_commands') {
                    var commands = msg.contents;
                    for (var i = 0; i < commands.length; i++) {
                        var command = commands[i];
                        // console.debug(command);
                        this.c.command(command);
                    }
                }
            },

            // When the model's size changes.
            width_changed: function() {
                this.$canvas.css('width', this.model.get('width') + 'px');
            },
            height_changed: function() {
                this.$canvas.css('height', this.model.get('height') + 'px');
            },

        });

        IPython.WidgetManager.register_widget_view('VispyView', VispyView);
});

