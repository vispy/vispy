var VispyCanvas = require('./vispycanvas.js');
var gloo = require('./gloo.js');
var events = require('./events.js');

var Vispy = function() {
    // Constructor of the Vispy library.
    this.events = events;
    this.gloo = gloo;
    this._is_loop_running = false;
    // List of canvases on the page.
    this._canvases = [];
};

Vispy.prototype.init = function(canvas_id) {
    var canvas_el;
    canvas_el = $(canvas_id);
    // Initialize the canvas.
    var canvas = new VispyCanvas(canvas_el);

    canvas.deactivate_context_menu();

    // Initialize events.
    this.events.init(canvas);

    // Initialize WebGL.
    this.gloo.init(canvas);

    // Register the canvas.
    this.register(canvas);

    return canvas;
};

Vispy.prototype.register = function(canvas) {
    /* Register a canvas. */
    this._canvases.push(canvas);
    // console.debug("Register canvas", canvas);
};

Vispy.prototype.unregister = function(canvas) {
    /* Unregister a canvas. */
    var index = this._canvases.indexOf(canvas);
    if (index > -1) {
        this._canvases.splice(index, 1);
    }
    // console.debug("Unregister canvas", canvas);
};


/* Event loop */
Vispy.prototype.start_event_loop = function() {

    // Do not start the event loop twice.
    if (this._is_loop_running) return;

    window.requestAnimFrame = (function(){
          return  window.requestAnimationFrame       ||
                  window.webkitRequestAnimationFrame ||
                  window.mozRequestAnimationFrame    ||
                  function(c){
                    window.setTimeout(c, 1000.0 / 60.0);
                  };
    })();

    // "that" is the current Vispy instance.
    var that = this;
    (function animloop() {
        that._request_id = requestAnimFrame(animloop);
        try {
            // Call event_tick() on all active canvases.
            for (var i = 0; i < that._canvases.length; i++) {
                that._canvases[i].event_tick();
            }
        }
        catch(err) {
            that.stop_event_loop();
            throw (err);
        }
    })();

    this._is_loop_running = true;
    console.debug("Event loop started.");
};

Vispy.prototype.stop_event_loop = function() {
    window.cancelAnimationFrame(this._request_id);
    this._is_loop_running = false;
    console.debug("Event loop stopped.");
};


module.exports = new Vispy();
