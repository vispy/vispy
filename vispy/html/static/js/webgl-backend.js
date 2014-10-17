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

var VISPY_DEBUG = true;

// VispyWidget code
require(["widgets/js/widget", "widgets/js/manager"],
    function(widget, manager){
        var VispyView = IPython.DOMWidgetView.extend({
            render: function(){ 

                var canvas = $('<canvas></canvas>');
                canvas.css('width', '500px').css('height', '200px');
                this.$el.append(canvas);

                var c = vispy.init(canvas);
                //c.command(['FUNC', 'clearColor', 0, 0, 0, 1]);
                //c.command(['FUNC', 'clear', 'COLOR_BUFFER_BIT | DEPTH_BUFFER_BIT']);
                
                this.c = c;

                var that = this;
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
                    // Send the message.
                    that.send(msg);
                    
                });
            },

            on_msg: function(msg) {
                // Receive the GLIR commands
                if (msg.msg_type == 'glir_commands') {
                    var commands = msg.contents;
                    for (var i = 0; i < commands.length; i++) {
                        var command = commands[i];
                        this.c.command(command);
                    }
                }
            }
        });

        IPython.WidgetManager.register_widget_view('VispyView', VispyView);
});

