require.config({
        paths: {
            "jquery-mousewheel": "//cdnjs.cloudflare.com/ajax/libs/jquery-mousewheel/3.1.11/jquery.mousewheel.min",
        }
});


// Load Vispy.js in the notebook.
IPython.load_extensions("vispy.min");
// HACK: this is UGLY but I didn't find a better way to do it
var _vispy_loaded = function(vispy) {
    window.vispy = vispy;
    vispy.start_event_loop();
};
window.setTimeout(function() {
    require(["vispy"], _vispy_loaded, _vispy_loaded);
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

                // Initialize the VispyCanvas.
                this.c = vispy.init(canvas);
                this.c.resize();
                this.c.resizable();

                this.c.on_resize(function (e) {
                    that.model.set('width', e.size[0]);
                    that.model.set('height', e.size[1]);
                    that.touch();
                });

                this.size_changed();

                // Track canvas size changes.
                this.model.on('change:width', this.size_changed, this);
                this.model.on('change:height', this.size_changed, this);


                window.VISPY_DEBUG = false;

                // Start the event loop.
                this.c.event_tick = function() {
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

                    that.c.execute_pending_commands();
                };
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
            size_changed: function() {
                var size = [this.model.get('width'), this.model.get('height')];
                this.$canvas.css('width', size[0] + 'px');
                this.$canvas.css('height', size[1] + 'px');
            }
        });

        IPython.WidgetManager.register_widget_view('VispyView', VispyView);
});

