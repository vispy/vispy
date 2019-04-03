var VispyCanvas = require('./vispycanvas.js');
var screenfull = require("screenfull");
require('jquery');
require('jquery-ui/ui/widgets/resizable');

/* Internal functions */
function get_pos(c, e) {
    var rect = c.getBoundingClientRect();
    return [e.clientX - rect.left,
            e.clientY - rect.top];
}

function normalize_pos(c, pos) {
    return [2*pos[0]/c.width-1, 1-2*pos[1]/c.height];
}

function get_modifiers(e) {
    var modifiers = [];
    if (e.altKey) modifiers.push('alt');
    if (e.ctrlKey) modifiers.push('ctrl');
    if (e.metaKey) modifiers.push('meta');
    if (e.shiftKey) modifiers.push('shift');
    return modifiers;
}

function get_key_text(keynum) {
    return String.fromCharCode(keynum).toUpperCase().trim();
}

function _get_keynum(e){
    if(window.event){ // IE
        return e.keyCode;
    }
    else if(e.which){ // Netscape/Firefox/Opera
        return e.which;
    }
}

var _key_map = {
    8: 'BACKSPACE',
    9: 'TAB',
    13: 'ENTER',
    16: 'SHIFT',
    17: 'CONTROL',
    18: 'ALT',
    27: 'ESCAPE',
    32: 'SPACE',
    33: 'PAGEUP',
    34: 'PAGEDOWN',
    35: 'END',
    36: 'HOME',
    37: 'LEFT',
    38: 'UP',
    39: 'RIGHT',
    40: 'DOWN',
    45: 'INSERT',
    46: 'DELETE',
    91: 'META',
    92: 'META',
    96: '0',
    97: '1',
    98: '2',
    99: '3',
    100: '4',
    101: '5',
    102: '6',
    103: '7',
    104: '8',
    105: '9',
    106: '*',
    107: '+',
    109: '-',
    110: '.',
    111: '/',
    112: 'F1',
    113: 'F2',
    114: 'F3',
    115: 'F4',
    116: 'F5',
    117: 'F6',
    118: 'F7',
    119: 'F8',
    120: 'F9',
    121: 'F10',
    122: 'F11',
    123: 'F12',
    186: ';',
    187: '=',
    188: ',',
    189: '-',
    190: '.',
    191: '/',
    192: '`',
    219: '[',
    220: '\\',
    221: ']',
    222: '\'',
};
function get_key_code(e){
    // Return a string representation of a key. It will be interpreted by
    // Vispy.
    var keynum = _get_keynum(e);
    var key_code = _key_map[keynum];
    if (key_code == undefined) {
        key_code = get_key_text(keynum);
    }
    return key_code;
}


/* Event generation */
var _button_map = {
    0: 1,   // left
    2: 2,   // right
    1: 3,   // middle
};
function gen_mouse_event(c, e, type) {
    var button;
    if (c._eventinfo.is_button_pressed)
        button = _button_map[e.button];
    else
        button = null;
    var pos = get_pos(c.$el.get(0), e);
    var modifiers = get_modifiers(e);
    var press_event = c._eventinfo.press_event;
    var last_event = c._eventinfo.last_event;
    var event = {
        'type': type,
        'pos': pos,
        'button': button,
        'is_dragging': press_event != null,
        'modifiers': modifiers,
        'delta': null,
        'press_event': press_event,

        'last_event': null,  // HACK: disabled to avoid recursion problems
    };
    return event;
}

function gen_resize_event(c, size) {
    var event = {
        'type': 'resize',
        'size': size,
    };
    return event;
}

function gen_paint_event(c) {
    var event = {
        'type': 'paint',
    };
    return event;
}

function gen_initialize_event(c) {
    var event = {
        'type': 'initialize',
    };
    return event;
}

function gen_key_event(c, e, type) {
    var modifiers = get_modifiers(e);
    var last_event = c._eventinfo.last_event;
    var event = {
        'type': type,
        'modifiers': modifiers,
        'key_code': get_key_code(e),
        'last_event': null,  // HACK: disabled to avoid recursion problems
    };
    return event;
}



/* Internal callback functions */
VispyCanvas.prototype._mouse_press = function(e) { };
VispyCanvas.prototype._mouse_release = function(e) { };
VispyCanvas.prototype._mouse_move = function(e) { };
VispyCanvas.prototype._mouse_wheel = function(e) { };
VispyCanvas.prototype._mouse_click = function(e) { };
VispyCanvas.prototype._mouse_dblclick = function(e) { };

VispyCanvas.prototype._key_press = function(e) { };
VispyCanvas.prototype._key_release = function(e) { };

VispyCanvas.prototype._initialize = function(e) { };
VispyCanvas.prototype._resize = function(e) { };
VispyCanvas.prototype._paint = function(e) { };
VispyCanvas.prototype._event_tick = function(e) { };



/* Registering handlers */
VispyCanvas.prototype.on_mouse_press = function(f) {
    this._mouse_press = f;
};
VispyCanvas.prototype.on_mouse_release = function(f) {
    this._mouse_release = f;
};
VispyCanvas.prototype.on_mouse_move = function(f) {
    this._mouse_move = f;
};
VispyCanvas.prototype.on_mouse_wheel = function(f) {
    this._mouse_wheel = f;
};
VispyCanvas.prototype.on_mouse_dblclick = function(f) {
    this._mouse_dblclick = f;
};
VispyCanvas.prototype.on_key_press = function(f) {
    this._key_press = f;
};
VispyCanvas.prototype.on_key_release = function(f) {
    this._key_release = f;
};
VispyCanvas.prototype.on_initialize = function(f) {
    this._initialize = f;
};
VispyCanvas.prototype.on_resize = function(f) {
    this._resize = f;
};
VispyCanvas.prototype.on_paint = function(f) {
    this._paint = f;
};
VispyCanvas.prototype.on_event_tick = function(f) {
    this._event_tick = f;
};


VispyCanvas.prototype.initialize = function() {
    var event = gen_initialize_event(this);
    this._set_size();
    this._initialize(event);
};
VispyCanvas.prototype._set_size = function(size) {
    if (size == undefined) {
        size = [this.$el.width(), this.$el.height()];
    }
    this.size = size;
    this.width = size[0];
    this.height = size[1];
    return size;
};
VispyCanvas.prototype.paint = function() {
    /* Add a paint event in the event queue. */
    var event = gen_paint_event(this);
    this.event_queue.append(event);
};
VispyCanvas.prototype.update = VispyCanvas.prototype.paint;
VispyCanvas.prototype.resize = function(size) {
    size = this._set_size(size);
    var event = gen_resize_event(this, size);
    this.gl.canvas.width = size[0];
    this.gl.canvas.height = size[1];
    // Put the resize event in the queue.
    this.event_queue.append(event);
    this._resize(event);
};

VispyCanvas.prototype.event_tick = function() {
    this._event_tick();
    var ncommands = this.execute_pending_commands();
    if (ncommands > 0) {
        // At least 1 GLIR command has been executed here.
        // We call the on_paint callback function here.
        var event = gen_paint_event(this);
        this._paint(event);
    }
};

VispyCanvas.prototype.is_fullscreen = function() {
    return (screenfull.enabled) & (screenfull.isFullscreen);
};

VispyCanvas.prototype.toggle_fullscreen = function() {
    if (screenfull.enabled) {
        if(screenfull.isFullscreen) {
            screenfull.exit();
            this.resize(this._size);
        }
        else {
            this.$el.width("100%").height("100%");
            this._size = [this.$el.width(), this.$el.height()];
            screenfull.request(this.$el[0]);
            this.resize([screen.width, screen.height]);
        }
    }
};

VispyCanvas.prototype.deactivate_context_menu = function() {
    document.oncontextmenu = function () { return false; };
};

VispyCanvas.prototype.resizable = function() {
    var that = this;
    this.$el.resizable({
        resize: function(event, ui) {
            that.resize([ui.size.width, ui.size.height]);
        }
    });
};


/* Event queue prototype */
function _events_can_be_combined(e1, e2) {
    // Return the list of properties to copy to e2.
    // The returned list is non empty if the two events can be combined.
    // It is empty if the two events cannot be combined.
    var type = e1.type;
    if (type == e2.type) {
        if (type == 'mouse_move') {
            if ((e1.button == e2.button) &
                (e1.is_dragging == e2.is_dragging) &
                (e1.modifiers.equals(e2.modifiers))) {
                return ['pos'];
            }
        }
        else {

        }
    }
    return [];
}
function EventQueue(maxlen) {
    if (maxlen == undefined) {
        maxlen = 100;
    }
    this._queue = [];
    this.maxlen = maxlen;
}
EventQueue.prototype.clear = function() {
    this._queue = [];
};
EventQueue.prototype.append = function(e, compress) {
    // Compression allows several similar consecutive events to be merged
    // into a single event, for performance reasons (notably, 'mouse_move').
    var add_to_queue = true;
    if (compress == undefined) {
        compress = true;
    }
    if (compress) {
        // If the event type is identical to the last event, we
        // just update the parameters instead of pushing a new event.
        var last_event = this._queue[this._queue.length - 1];
        if (last_event != undefined) {
            // Get the list or properties to combine.
            var props = _events_can_be_combined(e, last_event);
            // Combine the properties.
            if (props.length > 0) {
                for (var i = 0; i < props.length; i++) {
                    var prop = props[i];
                    this._queue[this._queue.length - 1][prop] = e[prop];
                }
                // In this case, no need to add the new event to the queue
                // because the last existing event can be updated ("combined"
                // with the new one).
                add_to_queue = false;
            }
        }
    }
    if (add_to_queue) {
        this._queue.push(e);
    }
    // Remove the oldest element if the queue is longer than the maximum allowed side.
    if (this._queue.length > this.maxlen) {
        this._queue.shift();
        // Remove the reference to the removed event in order to clean the GC.
        this._queue[0].last_event = null;
    }
};
EventQueue.prototype.get = function() {
    return this._queue;
};
Object.defineProperty(EventQueue.prototype, "length", {
    get: function() { return this._queue.length; },
});


/* Canvas initialization */
function init_app(c) {

    // Generate a resize event when the user resizes the canvas with
    // jQuery resizable.
    c.$el.on("resize", function(e) {
            c.resize([e.width(), e.height()]);
        }
    );

    c.event_queue = new EventQueue();

    // This object stores some state necessary to generate the appropriate
    // events.
    c._eventinfo = {
        'type': null,
        'pos': null,
        'button': null,
        'is_dragging': null,
        'key': null,
        'modifiers': [],
        'press_event': null,
        'last_event': null,
        'delta': null,
    };

    // HACK: boolean stating whether a mouse button is pressed.
    // This is necessary because e.button==0 in two cases: no
    // button is pressed, or the left button is pressed.
    c._eventinfo.is_button_pressed = 0;

    c.$el.on("mousemove", function(e) {
        var event = gen_mouse_event(c, e, 'mouse_move');

        // Vispy callbacks.
        c._mouse_move(event);

        // Save the last event.
        // c._eventinfo.last_event = event;
        c.event_queue.append(event);
    });
    c.$el.on("mousedown", function(e) {
        ++c._eventinfo.is_button_pressed;
        var event = gen_mouse_event(c, e, 'mouse_press');

        // Vispy callbacks.
        c._mouse_press(event);

        // Save the last press event.
        c._eventinfo.press_event = event;
        // Save the last event.
        // c._eventinfo.last_event = event;
        c.event_queue.append(event);
    });
    c.$el.on("mouseup", function(e) {
        --c._eventinfo.is_button_pressed;
        var event = gen_mouse_event(c, e, 'mouse_release');

        // Vispy callbacks.
        c._mouse_release(event);

        // Reset the last press event.
        c._eventinfo.press_event = null;
        // Save the last event.
        // c._eventinfo.last_event = event;
        c.event_queue.append(event);
    });
    c.$el.on("click", function(e) {
        // Reset the last press event.
        c._eventinfo.press_event = null;
    });
    c.$el.on("dblclick", function(e) {

        // Reset the last press event.
        c._eventinfo.press_event = null;
    });
    // This requires the mouse wheel jquery plugin.
    c.$el.on("wheel", function(e) {
        var event = gen_mouse_event(c, e, 'mouse_wheel');
        // event.delta = [e.originalEvent.deltaX * e.deltaFactor * 0.01,
        //                e.originalEvent.deltaY * e.deltaFactor * 0.01];
        event.delta = [e.originalEvent.deltaX * 0.01,
            e.originalEvent.deltaY * 0.01];

        // Vispy callbacks.
        c._mouse_wheel(event);

        // Save the last event.
        // c._eventinfo.last_event = event;
        c.event_queue.append(event);

        e.preventDefault();
        e.stopPropagation();
    });

    c.$el.on("keydown", function(e) {
        var event = gen_key_event(c, e, 'key_press');

        // Vispy callbacks.
        c._key_press(event);

        // Save the last event.
        // c._eventinfo.last_event = event;
        c.event_queue.append(event);
    });
    c.$el.on("keyup", function(e) {
        var event = gen_key_event(c, e, 'key_release');

        // Vispy callbacks.
        c._key_release(event);

        // Save the last event.
        // c._eventinfo.last_event = event;
        c.event_queue.append(event);
    });

    c.$el.on("mouseout", function(e) {
    });
}


/* Creation of vispy.events */
var events = function() {
    // Constructor.

};

events.prototype.init = function(c) {
    init_app(c);
};

module.exports = new events();
