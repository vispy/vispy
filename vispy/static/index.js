define(["@jupyter-widgets/base"], function(__WEBPACK_EXTERNAL_MODULE__jupyter_widgets_base__) { return /******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = "./lib/index.js");
/******/ })
/************************************************************************/
/******/ ({

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

// Entry point for the notebook bundle containing custom model definitions.
//
// Setup notebook base URL
//
// Some static assets may be required by the custom widget javascript. The base
// url for the notebook is not known at build time and is therefore computed
// dynamically.
__webpack_require__.p = document.querySelector('body').getAttribute('data-base-url') + 'nbextensions/vispy/';

// Export widget models and views, and the npm package version number.
// module.exports.vispy = require('./vispy.min.js');
module.exports.VispyView = __webpack_require__(/*! ./webgl-backend.js */ "./lib/webgl-backend.js").VispyView;
module.exports['version'] = __webpack_require__(/*! ../package.json */ "./package.json").version;


/***/ }),

/***/ "./lib/vispy.min.js":
/*!**************************!*\
  !*** ./lib/vispy.min.js ***!
  \**************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

var require;var require;(function(f){if(true){module.exports=f()}else { var g; }})(function(){var define,module,exports;return (function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return require(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
function decode_base64(base64) {
    var binary_string =  window.atob(base64);
    var len = binary_string.length;
    var bytes = new Uint8Array( len );
    for (var i = 0; i < len; i++)        {
        var ascii = binary_string.charCodeAt(i);
        bytes[i] = ascii;
    }
    return bytes.buffer;
}

// Mapping between user-friendly data type string, and typed array classes.
var _typed_array_map = {
    'float32': Float32Array,
    'int8': Int8Array,
    'int16': Int16Array,
    'int32': Int32Array,
    'uint8': Uint8Array,
    'uint16': Uint16Array,
    'uint32': Uint32Array,
};


function to_array_buffer(data) {
    // Return a TypedArray from a JSON object describing a data buffer.
    // storage_type is one of 'javascript_array', 'javascript_typed_array',
    // 'base64', 'png'
    var storage_type = data["storage_type"];

    // data can also be just a normal typed array, in which case we just return
    // the argument value.
    if (storage_type == undefined) {
        return data;
    }

    var data_type = data["data_type"];
    var contents = data["buffer"];

    if (storage_type == "javascript_array") {
        // A regular JavaScript array, the type must be specified in 'data_type'.
        return _typed_array_map[data_type](contents);
    }
    else if (storage_type == "javascript_typed_array" ||
             storage_type == "array_buffer") {
        // A JavaScript Typedarray.
        return contents;
    }
    else if (storage_type == "binary") {
        // "binary" means that binary WebSocket has been used
        // A JavaScript ArrayBuffer referenced by the data view.
        return contents.buffer;
    }
    else if (storage_type == "base64") {
        var array = decode_base64(contents);
        return array;
    }
}

module.exports = {
    to_array_buffer: to_array_buffer
};

},{}],2:[function(require,module,exports){
var VispyCanvas = require('./vispycanvas.js');

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
    if (c._eventinfo.is_button_pressed)
        var button = _button_map[e.button];
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
    }
    return event;
}

function gen_resize_event(c, size) {
    var event = {
        'type': 'resize',
        'size': size,
    }
    return event;
}

function gen_paint_event(c) {
    var event = {
        'type': 'paint',
    }
    return event;
}

function gen_initialize_event(c) {
    var event = {
        'type': 'initialize',
    }
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
    }
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
}
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
}

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
}
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
}
EventQueue.prototype.get = function() {
    return this._queue;
}
Object.defineProperty(EventQueue.prototype, "length", {
    get: function() { return this._queue.length; },
});


/* Canvas initialization */
function init_app(c) {

    // Generate a resize event when the user resizes the canvas with
    // jQuery resizable.
    c.$el.resize(function(e) {
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
    }

    // HACK: boolean stating whether a mouse button is pressed.
    // This is necessary because e.button==0 in two cases: no
    // button is pressed, or the left button is pressed.
    c._eventinfo.is_button_pressed = 0;

    c.$el.mousemove(function(e) {
        var event = gen_mouse_event(c, e, 'mouse_move');

        // Vispy callbacks.
        c._mouse_move(event);

        // Save the last event.
        // c._eventinfo.last_event = event;
        c.event_queue.append(event);
    });
    c.$el.mousedown(function(e) {
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
    c.$el.mouseup(function(e) {
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
    c.$el.click(function(e) {
        // Reset the last press event.
        c._eventinfo.press_event = null;
    });
    c.$el.dblclick(function(e) {

        // Reset the last press event.
        c._eventinfo.press_event = null;
    });
    // This requires the mouse wheel jquery plugin.
    if (c.$el.mousewheel != undefined) {
        c.$el.mousewheel(function(e) {
            var event = gen_mouse_event(c, e, 'mouse_wheel');
            event.delta = [e.deltaX * e.deltaFactor * .01,
                           e.deltaY * e.deltaFactor * .01];

            // Vispy callbacks.
            c._mouse_wheel(event);

            // Save the last event.
            // c._eventinfo.last_event = event;
            c.event_queue.append(event);

            e.preventDefault();
            e.stopPropagation();
        });
    }

    c.$el.keydown(function(e) {
        var event = gen_key_event(c, e, 'key_press');

        // Vispy callbacks.
        c._key_press(event);

        // Save the last event.
        // c._eventinfo.last_event = event;
        c.event_queue.append(event);
    });
    c.$el.keyup(function(e) {
        var event = gen_key_event(c, e, 'key_release');

        // Vispy callbacks.
        c._key_release(event);

        // Save the last event.
        // c._eventinfo.last_event = event;
        c.event_queue.append(event);
    });

    c.$el.mouseout(function(e) {
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

},{"./vispycanvas.js":9}],3:[function(require,module,exports){
var VispyCanvas = require('./vispycanvas.js');
var util = require('./util.js');
var data = require('./data.js');

var debug = util.debug;
var to_array_buffer = data.to_array_buffer;
var JUST_DELETED = 'JUST_DELETED';

/* WebGL utility functions */
function viewport(c) {
    c.gl.viewport(0, 0, c.width(), c.height());
}

function clear(c, color) {
    c.gl.clearColor(color[0], color[1], color[2], color[3]);
    c.gl.clear(c.gl.COLOR_BUFFER_BIT);
}

function compile_shader(c, shader, source) {
    // TODO: Convert desktop GLSL code if needed
    console.log(typeof source);
    if (typeof source !== 'string') {
        // assume we have a buffer
        source = String.fromCharCode.apply(null, new Uint8Array(source));

    }
    source = source.replace(/\\n/g, "\n");

    c.gl.shaderSource(shader, source);
    c.gl.compileShader(shader);

    if (!c.gl.getShaderParameter(shader, c.gl.COMPILE_STATUS))
    {
        console.error(c.gl.getShaderInfoLog(shader));
        return false;
    }

    return true;
}

function create_attribute(c, program, name) {
    var attribute_handle = c.gl.getAttribLocation(program, name);
    return attribute_handle;
}

function activate_attribute(c, attribute_handle, vbo_id, type, stride, offset) {
    // attribute_handle: attribute handle
    // vbo_id
    // type: float, vec3, etc.
    // stride: 0 by default
    // offset: 0 by default
    var _attribute_info = get_attribute_info(type);
    var attribute_type = _attribute_info[0];  // FLOAT, INT or BOOL
    var ndim = _attribute_info[1]; // 1, 2, 3 or 4

    _vbo_info = c._ns[vbo_id];
    var vbo_handle = _vbo_info.handle;

    c.gl.enableVertexAttribArray(attribute_handle);
    c.gl.bindBuffer(c.gl.ARRAY_BUFFER, vbo_handle);
    c.gl.vertexAttribPointer(attribute_handle, ndim,
                             c.gl[attribute_type],
                             false, stride, offset);
}

function deactivate_attribute(c, attribute_handle) {
    // c.gl.bindBuffer(c.gl.GL_ARRAY_BUFFER, 0);
    c.gl.disableVertexAttribArray(attribute_handle);
}

function activate_texture(c, texture_handle, sampler_handle, texture_index) {
    if (texture_handle === JUST_DELETED) {
        return;
    }
    c.gl.activeTexture(c.gl.TEXTURE0 + texture_index);
    c.gl.bindTexture(c.gl.TEXTURE_2D, texture_handle);
    // c.gl.uniform1i(sampler_handle, 0);
}

function deactivate_texture(c, texture_handle, sampler_handle, texture_index) {
    c.gl.activeTexture(c.gl.TEXTURE0 + texture_index);
    c.gl.bindTexture(c.gl.TEXTURE_2D, null);
}

function _get_alignment(width) {
    /* Determines a textures byte alignment.

    If the width isn't a power of 2
    we need to adjust the byte alignment of the image.
    The image height is unimportant

    www.opengl.org/wiki/Common_Mistakes#Texture_upload_and_pixel_reads

    we know the alignment is appropriate
    if we can divide the width by the
    alignment cleanly
    valid alignments are 1,2,4 and 8
    4 is the default

    */
    var alignments = [8, 4, 2, 1];
    for (var i = 0; i < alignments.length; i++) {
        if (width % alignments[i] == 0) {
            return alignments[i];
        }
    }
}

function set_texture_data(c, object_handle, gl_type, format, width, height, array, offset, shape, dtype) {
    c.gl.bindTexture(gl_type, object_handle);

    // TODO: choose a better alignment
    c.gl.pixelStorei(c.gl.UNPACK_ALIGNMENT, 1);

    if (array === null) {
        // special texture attached to frame buffer to be rendered to
        c.gl.texImage2D(gl_type, 0, format, width, height, 0, format, c.gl.UNSIGNED_BYTE, array);
    } else if (array.getContext) {
        // A canvas object
        c.gl.texImage2D(gl_type, 0, c.gl.RGBA, c.gl.RGBA, c.gl.UNSIGNED_BYTE, array);
    } else if (array.canvas) {
        // A context object
        c.gl.texImage2D(gl_type, 0, c.gl.RGBA, c.gl.RGBA, c.gl.UNSIGNED_BYTE, array.canvas);
    } else {
        var array_view;
        if (dtype == c.gl.FLOAT) {
            array_view = new Float32Array(array);
        } else {
            array_view = new Uint8Array(array);
        }

        // if this isn't initializing the texture (texImage2D) then see if we
        // can set just part of the texture
        if (offset && shape && ((shape[0] !== height) || (shape[1] !== width))) {
            var width = shape[shape.length - 2] * shape[shape.length - 1];
            var alignment = _get_alignment(width);
            c.gl.pixelStorei(c.gl.UNPACK_ALIGNMENT, alignment);
            c.gl.texSubImage2D(gl_type, 0, offset[1], offset[0],
                shape[1], shape[0], format, dtype, array_view);
        } else {
            c.gl.pixelStorei(c.gl.UNPACK_ALIGNMENT, 1);
            c.gl.texImage2D(gl_type, 0, format, width, height, 0,
                format, dtype, array_view);
        }
    }
}

function set_buffer_data(c, object_handle, gl_type, offset, array, reuse) {
    // Bind the buffer before setting the data.
    c.gl.bindBuffer(gl_type, object_handle);

    // Upload the data.
    if (!reuse) {
        // The existing buffer was empty: we create it.
        c.gl.bufferData(gl_type, array, c.gl.STATIC_DRAW);
    }
    else {
        // We reuse the existing buffer.
        c.gl.bufferSubData(gl_type, offset, array);
    }
}

function set_uniform(c, uniform_handle, uniform_function, value) {
    // Get a TypedArray.
    array = to_array_buffer(value);

    if (uniform_function.indexOf('Matrix') > 0) {
        // Matrix uniforms.
        c.gl[uniform_function](uniform_handle, false, array);
    }
    else {
        // Scalar uniforms.
        c.gl[uniform_function](uniform_handle, array);
    }
}

var _dtype_to_gl_dtype = {
    'float32': 'FLOAT',
    'uint8': 'UNSIGNED_BYTE',
};
function get_gl_dtype(dtype) {
    return _dtype_to_gl_dtype[dtype];
}

var _attribute_type_map = {
    'float': ['FLOAT', 1],
    'vec2': ['FLOAT', 2],
    'vec3': ['FLOAT', 3],
    'vec4': ['FLOAT', 4],

    'int': ['INT', 1],
    'ivec2': ['INT', 2],
    'ivec3': ['INT', 3],
    'ivec4': ['INT', 4],
};
function get_attribute_info(type) {
    // type: vec2, ivec3, float, etc.
    return _attribute_type_map[type];
}

var _uniform_type_map = {
    'float': 'uniform1fv',
    'vec2': 'uniform2fv',
    'vec3': 'uniform3fv',
    'vec4': 'uniform4fv',

    'int': 'uniform1iv',
    'ivec2': 'uniform2iv',
    'ivec3': 'uniform3iv',
    'ivec4': 'uniform4iv',

    'mat2': 'uniformMatrix2fv',
    'mat3': 'uniformMatrix3fv',
    'mat4': 'uniformMatrix4fv',
};
function get_uniform_function(type) {
    // Find OpenGL uniform function.
    return _uniform_type_map[type];
}

var _gl_type_map = {
    VertexBuffer: 'ARRAY_BUFFER',
    IndexBuffer: 'ELEMENT_ARRAY_BUFFER',
    Texture2D: 'TEXTURE_2D',
};

function get_gl_type(object_type) {
    return _gl_type_map[object_type];
}

var _gl_attachment_map = {
    'color': ['COLOR_ATTACHMENT0', 'RGBA4'],
    'depth': ['DEPTH_ATTACHMENT', 'DEPTH_COMPONENT16'],
    'stencil': ['STENCIL_ATTACHMENT', 'STENCIL_INDEX8'],
};

function get_attachment_type(type_str) {
    return _gl_attachment_map[type_str][0];
}

function get_attachment_format(type_str) {
    return _gl_attachment_map[type_str][1];
}

function parse_enum(c, str) {
    // Parse an enum or combination of enums stored in a string.
    var strs = str.split('|');
    var value = 0;
    for (var i = 0; i < strs.length; i++) {
        var name = strs[i].toUpperCase().trim();
        value = value | c.gl[name];
    }
    return value;
}

function validate_framebuffer(c) {
    var status = c.gl.checkFramebufferStatus(c.gl.FRAMEBUFFER);
    if (status == c.gl.FRAMEBUFFER_COMPLETE) {
        return;
    }
    // c.gl.FRAMEBUFFER_INCOMPLETE_FORMATS: // not in es 2.0
    //     'Internal format of attachment is not renderable.'
    if (status == c.gl.FRAMEBUFFER_INCOMPLETE_ATTACHMENT) {
        throw 'FrameBuffer attachments are incomplete.';
    }
    else if (status == c.gl.FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT) {
        throw 'No valid attachments in the FrameBuffer.';
    }
    else if (status == c.gl.FRAMEBUFFER_INCOMPLETE_DIMENSIONS) {
        throw 'attachments do not have the same width and height.';
    }
    else if (status == c.gl.FRAMEBUFFER_UNSUPPORTED) {
        throw 'Combination of internal formats used by attachments is not supported.';
    }
    else {
        throw 'Unknown framebuffer error' + status;
    }
}

function activate_framebuffer(c, framebuffer_id) {
    var fb = c._ns[framebuffer_id];
    var stack = c.env.fb_stack;
    if (stack.length == 0) {
        stack.push(null);
    }

    if (stack[stack.length - 1] === fb.handle) {
        debug("Frame buffer already active {0}".format(framebuffer_id));
        return;
    }
    debug("Binding frame buffer {0}.".format(framebuffer_id));
    c.gl.bindFramebuffer(c.gl.FRAMEBUFFER, fb.handle);
    stack.push(fb.handle);
}

function deactivate_framebuffer(c, framebuffer_id) {
    var fb = c._ns[framebuffer_id];
    var stack = c.env.fb_stack;
    if (stack.length == 0) {
        stack.push(null);
    }

    while (stack[stack.length - 1] === fb.handle) {
        // Deactivate current frame buffer
        stack.pop(); // 'unbind' current buffer
    }
    // Activate previous frame buffer
    // NOTE: out of bounds index if trying to unbind the default (null) framebuffer
    debug("Binding previous frame buffer");
    c.gl.bindFramebuffer(c.gl.FRAMEBUFFER, stack[stack.length - 1]);
}

function init_env_cache(c) {
    c.env = {
        'fb_stack': [],
    };
}


/* Glir queue prototype */
function GlirQueue() {
    this._queue = [];
}
GlirQueue.prototype.clear = function() {
    this._queue = [];
};
GlirQueue.prototype.append = function(e) {
    this._queue.push(e);
};
GlirQueue.prototype.append_multi = function(es) {
    for (var i = 0; i < es.length; i++) {
        this._queue.push(es[i]);
    }
};
GlirQueue.prototype.get = function() {
    return this._queue;
};
Object.defineProperty(GlirQueue.prototype, "length", {
    get: function() { return this._queue.length; },
});


/* Vispy canvas GLIR methods */
VispyCanvas.prototype.set_deferred = function(deferred) {
    this._deferred = deferred;
};

VispyCanvas.prototype.execute_pending_commands = function() {
    /* Return the number of executed GLIR commands. */
    var q = this.glir_queue.get();
    var execute_up_to = -1;
    if (q.length == 0) {
        return 0;
    }

    // Only start executing if we see a SWAP command
    // Any 'draw' command (clear, draw, etc) will cause the browser to
    // swap the webgl drawing buffers. If we start executing draw commands
    // before we are ready for the buffers to swap we could get an incomplete
    // canvas (only 'clear' being completed, less than all of the
    // expected objects being drawn, etc).
    // This technically only happens if not all the GLIR commands were
    // received by the time this animation loop started.
    for (var i = 0; i < q.length; i++) {
        if (q[i][0] === 'SWAP') {
            execute_up_to = i;
            break;
        }
    }
    // Execute all commands up to and including the SWAP
    for (i = 0; i <= execute_up_to; i++) {
        this.command(q[i], false);
    }

    if (execute_up_to >= 0) {
        debug("Processed {0} events.".format(execute_up_to + 1));
        // this.glir_queue.clear();
        this.glir_queue._queue = this.glir_queue._queue.slice(execute_up_to + 1);
    }
    return execute_up_to + 1;
};

VispyCanvas.prototype.command = function(command, deferred) {
    if (deferred === undefined) {
        deferred = this._deferred;
    }
    var method = command[0].toLowerCase();
    if (deferred) {
        this.glir_queue.append(command);
    }
    else {
        this.glir[method](this, command.slice(1));
    }
};


/* Creation of vispy.gloo.glir */
var glir = function() { };

glir.prototype.init = function(c) {
    // Namespace with the table of all symbols used by GLIR.

    // The key is user-specified and is named the **id**.
    // The WebGL internal handle is called the **handle**.

    // For each id key, the value is an object with the following properties:
    // * object_type ('VertexBuffer', 'Program', etc.)
    // * handle (the WebGL internal handle, for all objects)
    // * data_type (for Buffers)
    // * offset (for Buffers)
    // * attributes (for Programs)
    // * uniforms (for Programs)
    c._ns = {};
    // Deferred mode is enabled by default.
    c._deferred = true;
    // Per-context storage for GLIR objects (framebuffer stack, etc)
    init_env_cache(c);
    c.glir_queue = new GlirQueue();
    c.glir = this;
};

glir.prototype.current = function(c, args) {
    init_env_cache(c);
    c.gl.bindFramebuffer(c.gl.FRAMEBUFFER, null);
};

glir.prototype.swap = function(c, args) {

};

glir.prototype.create = function(c, args) {
    var id = args[0];
    var cls = args[1];
    if (cls == 'VertexBuffer') {
        debug("Creating vertex buffer '{0}'.".format(id));
        c._ns[id] = {
            object_type: cls,
            handle: c.gl.createBuffer(),
            size: 0,  // current size of the buffer
        };
    }
    else if (cls == 'IndexBuffer') {
        debug("Creating index buffer '{0}'.".format(id));
        c._ns[id] = {
            object_type: cls,
            handle: c.gl.createBuffer(),
            size: 0,  // current size of the buffer
        };
    }
    else if (cls == 'FrameBuffer') {
        debug("Creating frame buffer '{0}'.".format(id));
        c._ns[id] = {
            object_type: cls,
            handle: c.gl.createFramebuffer(),
            size: 0,  // current size of the buffer
            validated: false,
        };
    }
    else if (cls == 'RenderBuffer') {
        debug("Creating render buffer '{0}'.".format(id));
        c._ns[id] = {
            object_type: cls,
            handle: c.gl.createRenderbuffer(),
            size: 0,  // current size of the buffer
        };
    }
    else if (cls == 'Texture2D') {
        debug("Creating texture '{0}'.".format(id));
        c._ns[id] = {
            object_type: cls,
            handle: c.gl.createTexture(),
            size: 0,  // current size of the texture
            shape: [],
        };
    }
    else if (cls == 'Program') {
        debug("Creating program '{0}'.".format(id));
        c._ns[id] = {
            object_type: cls,
            handle: c.gl.createProgram(),
            attributes: {},
            uniforms: {},
            textures: {}, // map texture_id -> sampler_name, sampler_handle, number, handle
            texture_uniforms: {}, // map sampler_name -> texture_id
        };
    }
    else if (cls == 'VertexShader') {
        debug("Creating VertexShader '{0}'.".format(id));
        c._ns[id] = {
            object_type: cls,
            handle: c.gl.createShader(c.gl['VERTEX_SHADER']),
        };
    }
    else if (cls == 'FragmentShader') {
        debug("Creating FragmentShader '{0}'.".format(id));
        c._ns[id] = {
            object_type: cls,
            handle: c.gl.createShader(c.gl['FRAGMENT_SHADER']),
        };
    }
};

glir.prototype.delete = function(c, args) {
    var id = args[0];
    var cls = c._ns[id].object_type;
    var handle = c._ns[id].handle;
    c._ns[id].handle = JUST_DELETED;
    if (cls == 'VertexBuffer') {
        debug("Deleting vertex buffer '{0}'.".format(id));
        c.gl.deleteBuffer(handle);
    }
    else if (cls == 'IndexBuffer') {
        debug("Deleting index buffer '{0}'.".format(id));
        c.gl.deleteBuffer(handle);
    }
    else if (cls == 'FrameBuffer') {
        debug("Deleting frame buffer '{0}'.".format(id));
        c.gl.deleteFramebuffer(handle);
    }
    else if (cls == 'RenderBuffer') {
        debug("Deleting render buffer '{0}'.".format(id));
        c.gl.deleteRenderbuffer(handle);
    }
    else if (cls == 'Texture2D') {
        debug("Deleting texture '{0}'.".format(id));
        c.gl.deleteTexture(handle);
    }
    else if (cls == 'Program') {
        debug("Deleting program '{0}'.".format(id));
        c.gl.deleteProgram(handle);
    }
    else if (cls.indexOf('Shader') >= 0) {
        debug("Deleting shader '{0}'.".format(id));
        c.gl.deleteShader(handle);
    }
};

glir.prototype.size = function(c, args) {
    var object_id = args[0];
    var size = args[1];  // WARNING: size must be in bytes!
    var format = args[2];
    var object = c._ns[object_id];
    var object_handle = object.handle;
    var object_type = object.object_type;
    var gl_type = c.gl[get_gl_type(object_type)];

    // Textures.
    if (object_type.indexOf('Texture') >= 0) {
        // format is 'LUMINANCE', 'ALPHA', 'LUMINANCE_ALPHA', 'RGB' or 'RGBA'
        object.format = format.toUpperCase();
        debug("Setting texture size to {1} for '{0}'.".format(object_id, size));
        // HACK: it doesn't seem we can change the texture size without
        // allocating a buffer in WebGL, so we just store the size and
        // format in the object, and we'll use this information in the
        // subsequent DATA call.
    }
    else if (object_type == 'RenderBuffer') {
        c.gl.bindRenderbuffer(c.gl.RENDERBUFFER, object_handle);
        object.format = c.gl[get_attachment_format(format)];
        // size is Y, X, Z
        // assume Y is rows (height), X is columns (width)
        // assume Z is color information (ignored)
        c.gl.renderbufferStorage(c.gl.RENDERBUFFER, object.format, size[1], size[0]);
        c.gl.bindRenderbuffer(c.gl.RENDERBUFFER, null);
    }
    // Buffers
    else
    {
        debug("Setting buffer size to {1} for '{0}'.".format(object_id, size));
        // Reuse the buffer if the existing size is not null.
        set_buffer_data(c, object_handle, gl_type, 0, size, false);
    }
    // Save the size.
    object.size = size;
};

glir.prototype.data = function(c, args) {
    var object_id = args[0];
    var offset = args[1];
    var data = args[2];
    var object = c._ns[object_id];
    var object_type = object.object_type; // VertexBuffer, IndexBuffer, or Texture2D
    var object_handle = object.handle;
    var gl_type = c.gl[get_gl_type(object_type)];
    // Get a TypedArray.
    var array = to_array_buffer(data);

    if (object_type.indexOf('Shader') >= 0) {
        // Compile shader code to shader object
        compile_shader(c, object_handle, array);
    }
    // Textures.
    else if (object_type.indexOf('Texture') >= 0) {
        // The texture shape was specified in SIZE
        var shape = object.size;
        // WARNING: this is height and then width, not the other way
        // around.
        var height = shape[0];
        var width = shape[1];

        // The texture format was specified in SIZE.
        var format = c.gl[object.format];

        debug("Setting texture data for '{0}'.".format(object_id));
        // `data.shape` comes from notebook backend and vispy webgl extension
        // without it, subimage texture writes do not work
        var gl_dtype = c.gl[get_gl_dtype(data.dtype)];
        set_texture_data(c, object_handle, gl_type, format, width, height, array, offset, data.shape, gl_dtype);
        object.shape = shape;
    }
    // Buffers
    else
    {
        debug("Setting buffer data for '{0}'.".format(object_id));
        // Reuse the buffer if the existing size is not null.
        set_buffer_data(c, object_handle, gl_type, offset, array, object.size > 0);
        object.size = array.byteLength;
    }
};

glir.prototype.attribute = function(c, args) {
    var program_id = args[0];
    var name = args[1];
    var type = args[2];
    // TODO: support non-VBO data
    var vbo_id = args[3][0];
    var stride = args[3][1];
    var offset = args[3][2];

    var program_handle = c._ns[program_id].handle;

    debug("Creating attribute '{0}' for program '{1}'.".format(
            name, program_id
        ));
    var attribute_handle = create_attribute(c, program_handle, name);

    // Store the attribute handle in the attributes array of the program.
    c._ns[program_id].attributes[name] = {
        handle: attribute_handle,
        type: type,
        vbo_id: vbo_id,
        stride: stride,
        offset: offset,
    };
};

glir.prototype.uniform = function(c, args) {
    var program_id = args[0];
    var name = args[1];
    var type = args[2];
    var value = args[3];

    var program_handle = c._ns[program_id].handle;

    c.gl.useProgram(program_handle);

    // Check the cache.
    if (c._ns[program_id].uniforms[name] == undefined) {
        // If necessary, we create the uniform and cache both its handle and
        // GL function.
        debug("Creating uniform '{0}' for program '{1}'.".format(
                name, program_id
            ));
        var uniform_handle = c.gl.getUniformLocation(program_handle, name);
        var uniform_function = get_uniform_function(type);
        // We cache the uniform handle and the uniform function name as well.
        c._ns[program_id].uniforms[name] = [uniform_handle, uniform_function];
    }

    debug("Setting uniform '{0}' to '{1}' with {2} elements.".format(
            name, value, value.length
        ));
    var uniform_info = c._ns[program_id].uniforms[name];
    var uniform_handle = uniform_info[0];
    var uniform_function = uniform_info[1];
    set_uniform(c, uniform_handle, uniform_function, value);
};

glir.prototype.texture = function(c, args) {
    var program_id = args[0];
    var sampler_name = args[1];
    var texture_id = args[2];

    var program = c._ns[program_id];
    var program_handle = program.handle;
    var texture_handle = c._ns[texture_id].handle;

    if (texture_handle === JUST_DELETED) {
        debug("Removing texture '{0}' from program '{1}'".format(
            texture_id, program_id
        ));
        delete program.textures[texture_id];
        return;
    }

    debug("Initializing texture '{0}' for program '{1}'.".format(
        texture_id, program_id));

    // FIXME: Probably should store textures by sampler name, not texture id
    if (program.texture_uniforms.hasOwnProperty(sampler_name)) {
        // This program has had this sampler uniform name set before
        // Let's remove the old one
        debug('Removing previously assigned texture for \'{0}\''.format(sampler_name))
        delete program.textures[program.texture_uniforms[sampler_name]];
    }

    // Set the sampler uniform value.
    var sampler_handle = c.gl.getUniformLocation(program_handle, sampler_name);
    program.texture_uniforms[sampler_name] = texture_id;

    c._ns[program_id].textures[texture_id] = {
        sampler_name: sampler_name,
        sampler_handle: sampler_handle,
        number: -1, // assigned later
        handle: texture_handle,
    };
};

glir.prototype.interpolation = function(c, args) {
    var texture_id = args[0];
    var min = args[1].toUpperCase();
    var mag = args[2].toUpperCase();
    var texture_handle = c._ns[texture_id].handle;

    var gl_type = c.gl.TEXTURE_2D;
    c.gl.bindTexture(gl_type, texture_handle);
    c.gl.texParameteri(gl_type, c.gl.TEXTURE_MIN_FILTER, c.gl[min]);
    c.gl.texParameteri(gl_type, c.gl.TEXTURE_MAG_FILTER, c.gl[mag]);
    c.gl.bindTexture(gl_type, null);
};

glir.prototype.wrapping = function(c, args) {
    var texture_id = args[0];
    var wrapping = args[1];
    var texture_handle = c._ns[texture_id].handle;

    var gl_type = c.gl.TEXTURE_2D;
    c.gl.bindTexture(gl_type, texture_handle);
    c.gl.texParameteri(gl_type, c.gl.TEXTURE_WRAP_S,
                       c.gl[wrapping[0].toUpperCase()]);
    c.gl.texParameteri(gl_type, c.gl.TEXTURE_WRAP_T,
                       c.gl[wrapping[1].toUpperCase()]);
    c.gl.bindTexture(gl_type, null);
};

glir.prototype.draw = function(c, args) {
    var program_id = args[0];
    var mode = args[1].toUpperCase();
    var selection = args[2];

    var program_handle = c._ns[program_id].handle;
    var attributes = c._ns[program_id].attributes;
    var textures = c._ns[program_id].textures;
    var texture_number = 0;

    // Activate the program.
    c.gl.useProgram(program_handle);

    // Activate all attributes in the program.
    for (attribute_name in attributes) {
        var attribute = attributes[attribute_name];
        debug("Activating attribute '{0}' for program '{1}'.".format(
            attribute_name, program_id));
        activate_attribute(c, attribute.handle, attribute.vbo_id,
            attribute.type, attribute.stride, attribute.offset);
    }

    // Activate all textures in the program.
    for (texture_id in textures) {
        var texture = textures[texture_id];
        if (c._ns[texture_id].handle === JUST_DELETED) {
            debug("Ignoring texture '{0}' from program '{1}'".format(
                texture_id, program_id
            ));
            texture.handle = JUST_DELETED;
            continue;
        }
        texture.number = texture_number;
        texture_number += 1;
        debug("Activating texture '{0}' for program '{1}' as number '{2}'.".format(
            texture_id, program_id, texture.number));
        activate_texture(c, texture.handle, texture.sampler_handle, texture.number);
        c.gl.uniform1i(texture.sampler_handle, texture.number);
    }

    // Draw the program.
    if (selection.length == 2) {
        // Draw the program without index buffer.
        var start = selection[0];
        var count = selection[1];
        debug("Rendering program '{0}' with {1}.".format(
            program_id, mode));
        c.gl.drawArrays(c.gl[mode], start, count);
    }
    else if (selection.length == 3) {
        // Draw the program with index buffer.
        var index_buffer_id = selection[0];
        var index_buffer_type = selection[1];
        var count = selection[2];
        // Get the index buffer handle from the namespace.
        var index_buffer_handle = c._ns[index_buffer_id].handle;
        debug("Rendering program '{0}' with {1} and index buffer '{2}' of type '{3}'.".format(
            program_id, mode, index_buffer_id, index_buffer_type));
        // Activate the index buffer.
        c.gl.bindBuffer(c.gl.ELEMENT_ARRAY_BUFFER, index_buffer_handle);
        c.gl.drawElements(c.gl[mode], count, c.gl[index_buffer_type], 0);
    }

    // Deactivate attributes.
    for (attribute_name in attributes) {
        debug("Deactivating attribute '{0}' for program '{1}'.".format(
            attribute_name, program_id));
        deactivate_attribute(c, attributes[attribute_name].handle);
    }

    // Deactivate textures.
    var new_textures = {};
    for (texture_id in textures) {
        var texture = textures[texture_id];
        debug("Deactivating texture '{0}' for program '{1}'.".format(
            texture_id, program_id));
        deactivate_texture(c, texture.handle, texture.sampler_handle, texture.number);

        // Don't include any of the textures that were deleted in this program
        if (c._ns[texture_id].handle != JUST_DELETED) {
            new_textures[texture_id] = texture;
        }
    }
    c._ns[program_id].textures = new_textures;
};

glir.prototype.attach = function(c, args) {
    // framebuffer or shader object ID
    var dst_id = args[0];
    var dst_obj = c._ns[dst_id];
    var dst_type = dst_obj.object_type;
    var dst_handle = dst_obj.handle;
    if (dst_type == 'Program') {
        // attaching to program, must be a shader we're attaching
        var shader_id = args[1];
        var shader_handle = c._ns[shader_id].handle;
        c.gl.attachShader(dst_handle, shader_handle);
        return;
    }

    // Attach to framebuffer
    var object_id = args[2];
    var attach_type = c.gl[get_attachment_type(args[1])];
    var object;
    activate_framebuffer(c, dst_id);
    if (object_id == 0) {
        debug('Attaching RenderBuffer object {0} to framebuffer {1}'.format(object_id, dst_id));
        c.gl.framebufferRenderbuffer(c.gl.FRAMEBUFFER, attach_type, c.gl.RENDERBUFFER, null);
    } else {
        object = c._ns[object_id];
        debug('Attaching {0} object {1} to framebuffer {2} for {3}'.format(object.object_type, object_id, dst_id, args[1]));
        if (object.object_type == 'RenderBuffer') {
            c.gl.bindRenderbuffer(c.gl.RENDERBUFFER, object.handle);
            c.gl.framebufferRenderbuffer(c.gl.FRAMEBUFFER, attach_type, c.gl.RENDERBUFFER, object.handle);
            c.gl.bindRenderbuffer(c.gl.RENDERBUFFER, null);
        }
        else if (object.object_type == 'Texture2D') {
            // null or undefined
            if (object.shape.length == 0) {
                debug('Setting empty texture data to unset texture before attaching to framebuffer');
                set_texture_data(c, object.handle, c.gl.TEXTURE_2D,
                    c.gl[object.format], object.size[1], object.size[0], null);
            }
            // INFO: 0 is for mipmap level 0 (default) of the texture
            c.gl.bindTexture(c.gl.TEXTURE_2D, object.handle);
            c.gl.framebufferTexture2D(c.gl.FRAMEBUFFER, attach_type, c.gl.TEXTURE_2D, object.handle, 0);
            c.gl.bindTexture(c.gl.TEXTURE_2D, null);
        }
    }
    c._ns[dst_id].validated = false;
    deactivate_framebuffer(c, dst_id);
};

glir.prototype.link = function(c, args) {
    var program_handle = c._ns[args[0]].handle;
    c.gl.linkProgram(program_handle);

    if (!c.gl.getProgramParameter(program_handle, c.gl.LINK_STATUS))
    {
        console.warn("Could not initialise shaders on program '{0}'.".format(program_handle));
    }
};

glir.prototype.framebuffer = function(c, args) {
    var framebuffer_id = args[0];
    var bind = args[1];
    var fb = c._ns[framebuffer_id];

    if (bind) {
        debug('Binding framebuffer {0}'.format(framebuffer_id));
        activate_framebuffer(c, framebuffer_id);
        if (!fb.validated) {
            fb.validated = true;
            validate_framebuffer(c);
        }
    }
    else {
        debug('Unbinding framebuffer {0}'.format(framebuffer_id));
        deactivate_framebuffer(c, framebuffer_id);
    }
};

glir.prototype.func = function(c, args) {
    var name = args[0];
    debug("Calling {0}({1}).".format(name, args.slice(1)));

    // Handle enums: replace strings by global GL variables.
    for (var i = 1; i < args.length; i++) {
        if (typeof args[i] === 'string') {
            args[i] = parse_enum(c, args[i]);
        }
    }

    var func = c.gl[name];
    var func_args = args.slice(1);
    func.apply(c.gl, func_args);
};

module.exports = new glir();

},{"./data.js":1,"./util.js":7,"./vispycanvas.js":9}],4:[function(require,module,exports){
var glir = require('./gloo.glir.js');

function init_webgl(c) {
    // Get the DOM object, not the jQuery one.
    var canvas = c.$el.get(0);
    c.gl = canvas.getContext("webgl") ||
           canvas.getContext("experimental-webgl");
    var ext = c.gl.getExtension('OES_standard_derivatives') || c.gl.getExtension('MOZ_OES_standard_derivatives') || c.gl.getExtension('WEBKIT_OES_standard_derivatives');
    if (ext === null) {
        console.warn('Extension \'OES_standard_derivatives\' is not supported in this browser. Some features may not work as expected');
    }
    var ext = c.gl.getExtension('OES_element_index_uint') ||
        c.gl.getExtension('MOZ_OES_element_index_uint') ||
        c.gl.getExtension('WEBKIT_OES_element_index_uint');
    if (ext === null) {
        console.warn('Extension \'OES_element_index_uint\' is not supported in this browser. Some features may not work as expected');
    }
    var ext = c.gl.getExtension('OES_texture_float');
    // ||
    //     c.gl.getExtension('MOZ_OES_element_index_uint') ||
    //     c.gl.getExtension('WEBKIT_OES_element_index_uint');
    if (ext === null) {
        console.warn('Extension \'OES_texture_float\' is not supported in this browser. Some features may not work as expected');
    }

    var ext = c.gl.getExtension('OES_texture_float_linear');
    if (ext === null) {
        console.warn('Extension \'OES_texture_float_linear\' is not supported in this browser. Some features may not work as expected');
    }

    // c.gl.getExtension('EXT_shader_texture_lod');
}


/* Creation of vispy.gloo */
var gloo = function() {
    this.glir = glir;
    // Constructor.

};

gloo.prototype.init = function(c) {
    init_webgl(c);
    this.glir.init(c);
};


module.exports = new gloo();

},{"./gloo.glir.js":3}],5:[function(require,module,exports){
/*! Copyright (c) 2013 Brandon Aaron (http://brandon.aaron.sh)
 * Licensed under the MIT License (LICENSE.txt).
 *
 * Version: 3.1.12
 *
 * Requires: jQuery 1.2.2+
 */
!function(a){"function"==typeof define&&define.amd?define(["jquery"],a):"object"==typeof exports?module.exports=a:a(jQuery)}(function(a){function b(b){var g=b||window.event,h=i.call(arguments,1),j=0,l=0,m=0,n=0,o=0,p=0;if(b=a.event.fix(g),b.type="mousewheel","detail"in g&&(m=-1*g.detail),"wheelDelta"in g&&(m=g.wheelDelta),"wheelDeltaY"in g&&(m=g.wheelDeltaY),"wheelDeltaX"in g&&(l=-1*g.wheelDeltaX),"axis"in g&&g.axis===g.HORIZONTAL_AXIS&&(l=-1*m,m=0),j=0===m?l:m,"deltaY"in g&&(m=-1*g.deltaY,j=m),"deltaX"in g&&(l=g.deltaX,0===m&&(j=-1*l)),0!==m||0!==l){if(1===g.deltaMode){var q=a.data(this,"mousewheel-line-height");j*=q,m*=q,l*=q}else if(2===g.deltaMode){var r=a.data(this,"mousewheel-page-height");j*=r,m*=r,l*=r}if(n=Math.max(Math.abs(m),Math.abs(l)),(!f||f>n)&&(f=n,d(g,n)&&(f/=40)),d(g,n)&&(j/=40,l/=40,m/=40),j=Math[j>=1?"floor":"ceil"](j/f),l=Math[l>=1?"floor":"ceil"](l/f),m=Math[m>=1?"floor":"ceil"](m/f),k.settings.normalizeOffset&&this.getBoundingClientRect){var s=this.getBoundingClientRect();o=b.clientX-s.left,p=b.clientY-s.top}return b.deltaX=l,b.deltaY=m,b.deltaFactor=f,b.offsetX=o,b.offsetY=p,b.deltaMode=0,h.unshift(b,j,l,m),e&&clearTimeout(e),e=setTimeout(c,200),(a.event.dispatch||a.event.handle).apply(this,h)}}function c(){f=null}function d(a,b){return k.settings.adjustOldDeltas&&"mousewheel"===a.type&&b%120===0}var e,f,g=["wheel","mousewheel","DOMMouseScroll","MozMousePixelScroll"],h="onwheel"in document||document.documentMode>=9?["wheel"]:["mousewheel","DomMouseScroll","MozMousePixelScroll"],i=Array.prototype.slice;if(a.event.fixHooks)for(var j=g.length;j;)a.event.fixHooks[g[--j]]=a.event.mouseHooks;var k=a.event.special.mousewheel={version:"3.1.12",setup:function(){if(this.addEventListener)for(var c=h.length;c;)this.addEventListener(h[--c],b,!1);else this.onmousewheel=b;a.data(this,"mousewheel-line-height",k.getLineHeight(this)),a.data(this,"mousewheel-page-height",k.getPageHeight(this))},teardown:function(){if(this.removeEventListener)for(var c=h.length;c;)this.removeEventListener(h[--c],b,!1);else this.onmousewheel=null;a.removeData(this,"mousewheel-line-height"),a.removeData(this,"mousewheel-page-height")},getLineHeight:function(b){var c=a(b),d=c["offsetParent"in a.fn?"offsetParent":"parent"]();return d.length||(d=a("body")),parseInt(d.css("fontSize"),10)||parseInt(c.css("fontSize"),10)||16},getPageHeight:function(b){return a(b).height()},settings:{adjustOldDeltas:!0,normalizeOffset:!0}};a.fn.extend({mousewheel:function(a){return a?this.bind("mousewheel",a):this.trigger("mousewheel")},unmousewheel:function(a){return this.unbind("mousewheel",a)}})});
},{}],6:[function(require,module,exports){
/*!
* screenfull
* v1.2.0 - 2014-04-29
* (c) Sindre Sorhus; MIT License
*/
!function(){"use strict";var a="undefined"!=typeof module&&module.exports,b="undefined"!=typeof Element&&"ALLOW_KEYBOARD_INPUT"in Element,c=function(){for(var a,b,c=[["requestFullscreen","exitFullscreen","fullscreenElement","fullscreenEnabled","fullscreenchange","fullscreenerror"],["webkitRequestFullscreen","webkitExitFullscreen","webkitFullscreenElement","webkitFullscreenEnabled","webkitfullscreenchange","webkitfullscreenerror"],["webkitRequestFullScreen","webkitCancelFullScreen","webkitCurrentFullScreenElement","webkitCancelFullScreen","webkitfullscreenchange","webkitfullscreenerror"],["mozRequestFullScreen","mozCancelFullScreen","mozFullScreenElement","mozFullScreenEnabled","mozfullscreenchange","mozfullscreenerror"],["msRequestFullscreen","msExitFullscreen","msFullscreenElement","msFullscreenEnabled","MSFullscreenChange","MSFullscreenError"]],d=0,e=c.length,f={};e>d;d++)if(a=c[d],a&&a[1]in document){for(d=0,b=a.length;b>d;d++)f[c[0][d]]=a[d];return f}return!1}(),d={request:function(a){var d=c.requestFullscreen;a=a||document.documentElement,/5\.1[\.\d]* Safari/.test(navigator.userAgent)?a[d]():a[d](b&&Element.ALLOW_KEYBOARD_INPUT)},exit:function(){document[c.exitFullscreen]()},toggle:function(a){this.isFullscreen?this.exit():this.request(a)},onchange:function(){},onerror:function(){},raw:c};return c?(Object.defineProperties(d,{isFullscreen:{get:function(){return!!document[c.fullscreenElement]}},element:{enumerable:!0,get:function(){return document[c.fullscreenElement]}},enabled:{enumerable:!0,get:function(){return!!document[c.fullscreenEnabled]}}}),document.addEventListener(c.fullscreenchange,function(a){d.onchange.call(d,a)}),document.addEventListener(c.fullscreenerror,function(a){d.onerror.call(d,a)}),void(a?module.exports=d:window.screenfull=d)):void(a?module.exports=!1:window.screenfull=!1)}();
},{}],7:[function(require,module,exports){
if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) {
      return (typeof args[number] != 'undefined')
        ? args[number]
        : match;
    });
  };
}

if(typeof(String.prototype.trim) === "undefined")
{
    String.prototype.trim = function()
    {
        return String(this).replace(/^\s+|\s+$/g, '');
    };
}

function is_array(x) {
    return (Object.prototype.toString.call(x) === '[object Array]');
}

Array.prototype.equals = function (array) {
    // if the other array is a falsy value, return
    if (!array)
        return false;

    // compare lengths - can save a lot of time
    if (this.length != array.length)
        return false;

    for (var i = 0, l=this.length; i < l; i++) {
        // Check if we have nested arrays
        if (this[i] instanceof Array && array[i] instanceof Array) {
            // recurse into the nested arrays
            if (!this[i].equals(array[i]))
                return false;
        }
        else if (this[i] != array[i]) {
            // Warning - two different object instances will never be equal: {x:20} != {x:20}
            return false;
        }
    }
    return true;
};

if (typeof String.prototype.startsWith != 'function') {
  String.prototype.startsWith = function (str){
    return this.slice(0, str.length) == str;
  };
}

window.VISPY_DEBUG = false;
function debug(msg) {
    if (window.VISPY_DEBUG){
        console.debug(msg);
    }
}

module.exports = {debug: debug};

},{}],8:[function(require,module,exports){
var screenful = require("./lib/screenfull.min.js");
var VispyCanvas = require('./vispycanvas.js');
var gloo = require('./gloo.js');
var events = require('./events.js');
var util = require('./util.js');
var data = require('./data.js');
require("./lib/jquery.mousewheel.min.js")($);

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
                    window.setTimeout(c, 1000. / 60.);
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

},{"./data.js":1,"./events.js":2,"./gloo.js":4,"./lib/jquery.mousewheel.min.js":5,"./lib/screenfull.min.js":6,"./util.js":7,"./vispycanvas.js":9}],9:[function(require,module,exports){

var VispyCanvas = function ($el) {
    this.$el = $el;
};

module.exports = VispyCanvas;

},{}]},{},[8])(8)
});

//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCJzY3JpcHRzL2RhdGEuanMiLCJzY3JpcHRzL2V2ZW50cy5qcyIsInNjcmlwdHMvZ2xvby5nbGlyLmpzIiwic2NyaXB0cy9nbG9vLmpzIiwic2NyaXB0cy9saWIvanF1ZXJ5Lm1vdXNld2hlZWwubWluLmpzIiwic2NyaXB0cy9saWIvc2NyZWVuZnVsbC5taW4uanMiLCJzY3JpcHRzL3V0aWwuanMiLCJzY3JpcHRzL3Zpc3B5LmpzIiwic2NyaXB0cy92aXNweWNhbnZhcy5qcyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiQUFBQTtBQ0FBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FDN0RBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQzNmQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUM1NUJBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQ2hEQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQ1BBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUNMQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQzdEQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUNoR0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJmaWxlIjoiZ2VuZXJhdGVkLmpzIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXNDb250ZW50IjpbIihmdW5jdGlvbigpe2Z1bmN0aW9uIHIoZSxuLHQpe2Z1bmN0aW9uIG8oaSxmKXtpZighbltpXSl7aWYoIWVbaV0pe3ZhciBjPVwiZnVuY3Rpb25cIj09dHlwZW9mIHJlcXVpcmUmJnJlcXVpcmU7aWYoIWYmJmMpcmV0dXJuIGMoaSwhMCk7aWYodSlyZXR1cm4gdShpLCEwKTt2YXIgYT1uZXcgRXJyb3IoXCJDYW5ub3QgZmluZCBtb2R1bGUgJ1wiK2krXCInXCIpO3Rocm93IGEuY29kZT1cIk1PRFVMRV9OT1RfRk9VTkRcIixhfXZhciBwPW5baV09e2V4cG9ydHM6e319O2VbaV1bMF0uY2FsbChwLmV4cG9ydHMsZnVuY3Rpb24ocil7dmFyIG49ZVtpXVsxXVtyXTtyZXR1cm4gbyhufHxyKX0scCxwLmV4cG9ydHMscixlLG4sdCl9cmV0dXJuIG5baV0uZXhwb3J0c31mb3IodmFyIHU9XCJmdW5jdGlvblwiPT10eXBlb2YgcmVxdWlyZSYmcmVxdWlyZSxpPTA7aTx0Lmxlbmd0aDtpKyspbyh0W2ldKTtyZXR1cm4gb31yZXR1cm4gcn0pKCkiLCJmdW5jdGlvbiBkZWNvZGVfYmFzZTY0KGJhc2U2NCkge1xuICAgIHZhciBiaW5hcnlfc3RyaW5nID0gIHdpbmRvdy5hdG9iKGJhc2U2NCk7XG4gICAgdmFyIGxlbiA9IGJpbmFyeV9zdHJpbmcubGVuZ3RoO1xuICAgIHZhciBieXRlcyA9IG5ldyBVaW50OEFycmF5KCBsZW4gKTtcbiAgICBmb3IgKHZhciBpID0gMDsgaSA8IGxlbjsgaSsrKSAgICAgICAge1xuICAgICAgICB2YXIgYXNjaWkgPSBiaW5hcnlfc3RyaW5nLmNoYXJDb2RlQXQoaSk7XG4gICAgICAgIGJ5dGVzW2ldID0gYXNjaWk7XG4gICAgfVxuICAgIHJldHVybiBieXRlcy5idWZmZXI7XG59XG5cbi8vIE1hcHBpbmcgYmV0d2VlbiB1c2VyLWZyaWVuZGx5IGRhdGEgdHlwZSBzdHJpbmcsIGFuZCB0eXBlZCBhcnJheSBjbGFzc2VzLlxudmFyIF90eXBlZF9hcnJheV9tYXAgPSB7XG4gICAgJ2Zsb2F0MzInOiBGbG9hdDMyQXJyYXksXG4gICAgJ2ludDgnOiBJbnQ4QXJyYXksXG4gICAgJ2ludDE2JzogSW50MTZBcnJheSxcbiAgICAnaW50MzInOiBJbnQzMkFycmF5LFxuICAgICd1aW50OCc6IFVpbnQ4QXJyYXksXG4gICAgJ3VpbnQxNic6IFVpbnQxNkFycmF5LFxuICAgICd1aW50MzInOiBVaW50MzJBcnJheSxcbn07XG5cblxuZnVuY3Rpb24gdG9fYXJyYXlfYnVmZmVyKGRhdGEpIHtcbiAgICAvLyBSZXR1cm4gYSBUeXBlZEFycmF5IGZyb20gYSBKU09OIG9iamVjdCBkZXNjcmliaW5nIGEgZGF0YSBidWZmZXIuXG4gICAgLy8gc3RvcmFnZV90eXBlIGlzIG9uZSBvZiAnamF2YXNjcmlwdF9hcnJheScsICdqYXZhc2NyaXB0X3R5cGVkX2FycmF5JyxcbiAgICAvLyAnYmFzZTY0JywgJ3BuZydcbiAgICB2YXIgc3RvcmFnZV90eXBlID0gZGF0YVtcInN0b3JhZ2VfdHlwZVwiXTtcblxuICAgIC8vIGRhdGEgY2FuIGFsc28gYmUganVzdCBhIG5vcm1hbCB0eXBlZCBhcnJheSwgaW4gd2hpY2ggY2FzZSB3ZSBqdXN0IHJldHVyblxuICAgIC8vIHRoZSBhcmd1bWVudCB2YWx1ZS5cbiAgICBpZiAoc3RvcmFnZV90eXBlID09IHVuZGVmaW5lZCkge1xuICAgICAgICByZXR1cm4gZGF0YTtcbiAgICB9XG5cbiAgICB2YXIgZGF0YV90eXBlID0gZGF0YVtcImRhdGFfdHlwZVwiXTtcbiAgICB2YXIgY29udGVudHMgPSBkYXRhW1wiYnVmZmVyXCJdO1xuXG4gICAgaWYgKHN0b3JhZ2VfdHlwZSA9PSBcImphdmFzY3JpcHRfYXJyYXlcIikge1xuICAgICAgICAvLyBBIHJlZ3VsYXIgSmF2YVNjcmlwdCBhcnJheSwgdGhlIHR5cGUgbXVzdCBiZSBzcGVjaWZpZWQgaW4gJ2RhdGFfdHlwZScuXG4gICAgICAgIHJldHVybiBfdHlwZWRfYXJyYXlfbWFwW2RhdGFfdHlwZV0oY29udGVudHMpO1xuICAgIH1cbiAgICBlbHNlIGlmIChzdG9yYWdlX3R5cGUgPT0gXCJqYXZhc2NyaXB0X3R5cGVkX2FycmF5XCIgfHxcbiAgICAgICAgICAgICBzdG9yYWdlX3R5cGUgPT0gXCJhcnJheV9idWZmZXJcIikge1xuICAgICAgICAvLyBBIEphdmFTY3JpcHQgVHlwZWRhcnJheS5cbiAgICAgICAgcmV0dXJuIGNvbnRlbnRzO1xuICAgIH1cbiAgICBlbHNlIGlmIChzdG9yYWdlX3R5cGUgPT0gXCJiaW5hcnlcIikge1xuICAgICAgICAvLyBcImJpbmFyeVwiIG1lYW5zIHRoYXQgYmluYXJ5IFdlYlNvY2tldCBoYXMgYmVlbiB1c2VkXG4gICAgICAgIC8vIEEgSmF2YVNjcmlwdCBBcnJheUJ1ZmZlciByZWZlcmVuY2VkIGJ5IHRoZSBkYXRhIHZpZXcuXG4gICAgICAgIHJldHVybiBjb250ZW50cy5idWZmZXI7XG4gICAgfVxuICAgIGVsc2UgaWYgKHN0b3JhZ2VfdHlwZSA9PSBcImJhc2U2NFwiKSB7XG4gICAgICAgIHZhciBhcnJheSA9IGRlY29kZV9iYXNlNjQoY29udGVudHMpO1xuICAgICAgICByZXR1cm4gYXJyYXk7XG4gICAgfVxufVxuXG5tb2R1bGUuZXhwb3J0cyA9IHtcbiAgICB0b19hcnJheV9idWZmZXI6IHRvX2FycmF5X2J1ZmZlclxufTtcbiIsInZhciBWaXNweUNhbnZhcyA9IHJlcXVpcmUoJy4vdmlzcHljYW52YXMuanMnKTtcblxuLyogSW50ZXJuYWwgZnVuY3Rpb25zICovXG5mdW5jdGlvbiBnZXRfcG9zKGMsIGUpIHtcbiAgICB2YXIgcmVjdCA9IGMuZ2V0Qm91bmRpbmdDbGllbnRSZWN0KCk7XG4gICAgcmV0dXJuIFtlLmNsaWVudFggLSByZWN0LmxlZnQsXG4gICAgICAgICAgICBlLmNsaWVudFkgLSByZWN0LnRvcF07XG59XG5cbmZ1bmN0aW9uIG5vcm1hbGl6ZV9wb3MoYywgcG9zKSB7XG4gICAgcmV0dXJuIFsyKnBvc1swXS9jLndpZHRoLTEsIDEtMipwb3NbMV0vYy5oZWlnaHRdO1xufVxuXG5mdW5jdGlvbiBnZXRfbW9kaWZpZXJzKGUpIHtcbiAgICB2YXIgbW9kaWZpZXJzID0gW107XG4gICAgaWYgKGUuYWx0S2V5KSBtb2RpZmllcnMucHVzaCgnYWx0Jyk7XG4gICAgaWYgKGUuY3RybEtleSkgbW9kaWZpZXJzLnB1c2goJ2N0cmwnKTtcbiAgICBpZiAoZS5tZXRhS2V5KSBtb2RpZmllcnMucHVzaCgnbWV0YScpO1xuICAgIGlmIChlLnNoaWZ0S2V5KSBtb2RpZmllcnMucHVzaCgnc2hpZnQnKTtcbiAgICByZXR1cm4gbW9kaWZpZXJzO1xufVxuXG5mdW5jdGlvbiBnZXRfa2V5X3RleHQoa2V5bnVtKSB7XG4gICAgcmV0dXJuIFN0cmluZy5mcm9tQ2hhckNvZGUoa2V5bnVtKS50b1VwcGVyQ2FzZSgpLnRyaW0oKTtcbn1cblxuZnVuY3Rpb24gX2dldF9rZXludW0oZSl7XG4gICAgaWYod2luZG93LmV2ZW50KXsgLy8gSUVcbiAgICAgICAgcmV0dXJuIGUua2V5Q29kZTtcbiAgICB9XG4gICAgZWxzZSBpZihlLndoaWNoKXsgLy8gTmV0c2NhcGUvRmlyZWZveC9PcGVyYVxuICAgICAgICByZXR1cm4gZS53aGljaDtcbiAgICB9XG59XG5cbnZhciBfa2V5X21hcCA9IHtcbiAgICA4OiAnQkFDS1NQQUNFJyxcbiAgICA5OiAnVEFCJyxcbiAgICAxMzogJ0VOVEVSJyxcbiAgICAxNjogJ1NISUZUJyxcbiAgICAxNzogJ0NPTlRST0wnLFxuICAgIDE4OiAnQUxUJyxcbiAgICAyNzogJ0VTQ0FQRScsXG4gICAgMzI6ICdTUEFDRScsXG4gICAgMzM6ICdQQUdFVVAnLFxuICAgIDM0OiAnUEFHRURPV04nLFxuICAgIDM1OiAnRU5EJyxcbiAgICAzNjogJ0hPTUUnLFxuICAgIDM3OiAnTEVGVCcsXG4gICAgMzg6ICdVUCcsXG4gICAgMzk6ICdSSUdIVCcsXG4gICAgNDA6ICdET1dOJyxcbiAgICA0NTogJ0lOU0VSVCcsXG4gICAgNDY6ICdERUxFVEUnLFxuICAgIDkxOiAnTUVUQScsXG4gICAgOTI6ICdNRVRBJyxcbiAgICA5NjogJzAnLFxuICAgIDk3OiAnMScsXG4gICAgOTg6ICcyJyxcbiAgICA5OTogJzMnLFxuICAgIDEwMDogJzQnLFxuICAgIDEwMTogJzUnLFxuICAgIDEwMjogJzYnLFxuICAgIDEwMzogJzcnLFxuICAgIDEwNDogJzgnLFxuICAgIDEwNTogJzknLFxuICAgIDEwNjogJyonLFxuICAgIDEwNzogJysnLFxuICAgIDEwOTogJy0nLFxuICAgIDExMDogJy4nLFxuICAgIDExMTogJy8nLFxuICAgIDExMjogJ0YxJyxcbiAgICAxMTM6ICdGMicsXG4gICAgMTE0OiAnRjMnLFxuICAgIDExNTogJ0Y0JyxcbiAgICAxMTY6ICdGNScsXG4gICAgMTE3OiAnRjYnLFxuICAgIDExODogJ0Y3JyxcbiAgICAxMTk6ICdGOCcsXG4gICAgMTIwOiAnRjknLFxuICAgIDEyMTogJ0YxMCcsXG4gICAgMTIyOiAnRjExJyxcbiAgICAxMjM6ICdGMTInLFxuICAgIDE4NjogJzsnLFxuICAgIDE4NzogJz0nLFxuICAgIDE4ODogJywnLFxuICAgIDE4OTogJy0nLFxuICAgIDE5MDogJy4nLFxuICAgIDE5MTogJy8nLFxuICAgIDE5MjogJ2AnLFxuICAgIDIxOTogJ1snLFxuICAgIDIyMDogJ1xcXFwnLFxuICAgIDIyMTogJ10nLFxuICAgIDIyMjogJ1xcJycsXG59O1xuZnVuY3Rpb24gZ2V0X2tleV9jb2RlKGUpe1xuICAgIC8vIFJldHVybiBhIHN0cmluZyByZXByZXNlbnRhdGlvbiBvZiBhIGtleS4gSXQgd2lsbCBiZSBpbnRlcnByZXRlZCBieVxuICAgIC8vIFZpc3B5LlxuICAgIHZhciBrZXludW0gPSBfZ2V0X2tleW51bShlKTtcbiAgICB2YXIga2V5X2NvZGUgPSBfa2V5X21hcFtrZXludW1dO1xuICAgIGlmIChrZXlfY29kZSA9PSB1bmRlZmluZWQpIHtcbiAgICAgICAga2V5X2NvZGUgPSBnZXRfa2V5X3RleHQoa2V5bnVtKTtcbiAgICB9XG4gICAgcmV0dXJuIGtleV9jb2RlO1xufVxuXG5cbi8qIEV2ZW50IGdlbmVyYXRpb24gKi9cbnZhciBfYnV0dG9uX21hcCA9IHtcbiAgICAwOiAxLCAgIC8vIGxlZnRcbiAgICAyOiAyLCAgIC8vIHJpZ2h0XG4gICAgMTogMywgICAvLyBtaWRkbGVcbn07XG5mdW5jdGlvbiBnZW5fbW91c2VfZXZlbnQoYywgZSwgdHlwZSkge1xuICAgIGlmIChjLl9ldmVudGluZm8uaXNfYnV0dG9uX3ByZXNzZWQpXG4gICAgICAgIHZhciBidXR0b24gPSBfYnV0dG9uX21hcFtlLmJ1dHRvbl07XG4gICAgZWxzZVxuICAgICAgICBidXR0b24gPSBudWxsO1xuICAgIHZhciBwb3MgPSBnZXRfcG9zKGMuJGVsLmdldCgwKSwgZSk7XG4gICAgdmFyIG1vZGlmaWVycyA9IGdldF9tb2RpZmllcnMoZSk7XG4gICAgdmFyIHByZXNzX2V2ZW50ID0gYy5fZXZlbnRpbmZvLnByZXNzX2V2ZW50O1xuICAgIHZhciBsYXN0X2V2ZW50ID0gYy5fZXZlbnRpbmZvLmxhc3RfZXZlbnQ7XG4gICAgdmFyIGV2ZW50ID0ge1xuICAgICAgICAndHlwZSc6IHR5cGUsXG4gICAgICAgICdwb3MnOiBwb3MsXG4gICAgICAgICdidXR0b24nOiBidXR0b24sXG4gICAgICAgICdpc19kcmFnZ2luZyc6IHByZXNzX2V2ZW50ICE9IG51bGwsXG4gICAgICAgICdtb2RpZmllcnMnOiBtb2RpZmllcnMsXG4gICAgICAgICdkZWx0YSc6IG51bGwsXG4gICAgICAgICdwcmVzc19ldmVudCc6IHByZXNzX2V2ZW50LFxuXG4gICAgICAgICdsYXN0X2V2ZW50JzogbnVsbCwgIC8vIEhBQ0s6IGRpc2FibGVkIHRvIGF2b2lkIHJlY3Vyc2lvbiBwcm9ibGVtc1xuICAgIH1cbiAgICByZXR1cm4gZXZlbnQ7XG59XG5cbmZ1bmN0aW9uIGdlbl9yZXNpemVfZXZlbnQoYywgc2l6ZSkge1xuICAgIHZhciBldmVudCA9IHtcbiAgICAgICAgJ3R5cGUnOiAncmVzaXplJyxcbiAgICAgICAgJ3NpemUnOiBzaXplLFxuICAgIH1cbiAgICByZXR1cm4gZXZlbnQ7XG59XG5cbmZ1bmN0aW9uIGdlbl9wYWludF9ldmVudChjKSB7XG4gICAgdmFyIGV2ZW50ID0ge1xuICAgICAgICAndHlwZSc6ICdwYWludCcsXG4gICAgfVxuICAgIHJldHVybiBldmVudDtcbn1cblxuZnVuY3Rpb24gZ2VuX2luaXRpYWxpemVfZXZlbnQoYykge1xuICAgIHZhciBldmVudCA9IHtcbiAgICAgICAgJ3R5cGUnOiAnaW5pdGlhbGl6ZScsXG4gICAgfVxuICAgIHJldHVybiBldmVudDtcbn1cblxuZnVuY3Rpb24gZ2VuX2tleV9ldmVudChjLCBlLCB0eXBlKSB7XG4gICAgdmFyIG1vZGlmaWVycyA9IGdldF9tb2RpZmllcnMoZSk7XG4gICAgdmFyIGxhc3RfZXZlbnQgPSBjLl9ldmVudGluZm8ubGFzdF9ldmVudDtcbiAgICB2YXIgZXZlbnQgPSB7XG4gICAgICAgICd0eXBlJzogdHlwZSxcbiAgICAgICAgJ21vZGlmaWVycyc6IG1vZGlmaWVycyxcbiAgICAgICAgJ2tleV9jb2RlJzogZ2V0X2tleV9jb2RlKGUpLFxuICAgICAgICAnbGFzdF9ldmVudCc6IG51bGwsICAvLyBIQUNLOiBkaXNhYmxlZCB0byBhdm9pZCByZWN1cnNpb24gcHJvYmxlbXNcbiAgICB9XG4gICAgcmV0dXJuIGV2ZW50O1xufVxuXG5cblxuLyogSW50ZXJuYWwgY2FsbGJhY2sgZnVuY3Rpb25zICovXG5WaXNweUNhbnZhcy5wcm90b3R5cGUuX21vdXNlX3ByZXNzID0gZnVuY3Rpb24oZSkgeyB9O1xuVmlzcHlDYW52YXMucHJvdG90eXBlLl9tb3VzZV9yZWxlYXNlID0gZnVuY3Rpb24oZSkgeyB9O1xuVmlzcHlDYW52YXMucHJvdG90eXBlLl9tb3VzZV9tb3ZlID0gZnVuY3Rpb24oZSkgeyB9O1xuVmlzcHlDYW52YXMucHJvdG90eXBlLl9tb3VzZV93aGVlbCA9IGZ1bmN0aW9uKGUpIHsgfTtcblZpc3B5Q2FudmFzLnByb3RvdHlwZS5fbW91c2VfY2xpY2sgPSBmdW5jdGlvbihlKSB7IH07XG5WaXNweUNhbnZhcy5wcm90b3R5cGUuX21vdXNlX2RibGNsaWNrID0gZnVuY3Rpb24oZSkgeyB9O1xuXG5WaXNweUNhbnZhcy5wcm90b3R5cGUuX2tleV9wcmVzcyA9IGZ1bmN0aW9uKGUpIHsgfTtcblZpc3B5Q2FudmFzLnByb3RvdHlwZS5fa2V5X3JlbGVhc2UgPSBmdW5jdGlvbihlKSB7IH07XG5cblZpc3B5Q2FudmFzLnByb3RvdHlwZS5faW5pdGlhbGl6ZSA9IGZ1bmN0aW9uKGUpIHsgfTtcblZpc3B5Q2FudmFzLnByb3RvdHlwZS5fcmVzaXplID0gZnVuY3Rpb24oZSkgeyB9O1xuVmlzcHlDYW52YXMucHJvdG90eXBlLl9wYWludCA9IGZ1bmN0aW9uKGUpIHsgfTtcblZpc3B5Q2FudmFzLnByb3RvdHlwZS5fZXZlbnRfdGljayA9IGZ1bmN0aW9uKGUpIHsgfTtcblxuXG5cbi8qIFJlZ2lzdGVyaW5nIGhhbmRsZXJzICovXG5WaXNweUNhbnZhcy5wcm90b3R5cGUub25fbW91c2VfcHJlc3MgPSBmdW5jdGlvbihmKSB7XG4gICAgdGhpcy5fbW91c2VfcHJlc3MgPSBmO1xufTtcblZpc3B5Q2FudmFzLnByb3RvdHlwZS5vbl9tb3VzZV9yZWxlYXNlID0gZnVuY3Rpb24oZikge1xuICAgIHRoaXMuX21vdXNlX3JlbGVhc2UgPSBmO1xufTtcblZpc3B5Q2FudmFzLnByb3RvdHlwZS5vbl9tb3VzZV9tb3ZlID0gZnVuY3Rpb24oZikge1xuICAgIHRoaXMuX21vdXNlX21vdmUgPSBmO1xufTtcblZpc3B5Q2FudmFzLnByb3RvdHlwZS5vbl9tb3VzZV93aGVlbCA9IGZ1bmN0aW9uKGYpIHtcbiAgICB0aGlzLl9tb3VzZV93aGVlbCA9IGY7XG59O1xuVmlzcHlDYW52YXMucHJvdG90eXBlLm9uX21vdXNlX2RibGNsaWNrID0gZnVuY3Rpb24oZikge1xuICAgIHRoaXMuX21vdXNlX2RibGNsaWNrID0gZjtcbn07XG5WaXNweUNhbnZhcy5wcm90b3R5cGUub25fa2V5X3ByZXNzID0gZnVuY3Rpb24oZikge1xuICAgIHRoaXMuX2tleV9wcmVzcyA9IGY7XG59O1xuVmlzcHlDYW52YXMucHJvdG90eXBlLm9uX2tleV9yZWxlYXNlID0gZnVuY3Rpb24oZikge1xuICAgIHRoaXMuX2tleV9yZWxlYXNlID0gZjtcbn07XG5WaXNweUNhbnZhcy5wcm90b3R5cGUub25faW5pdGlhbGl6ZSA9IGZ1bmN0aW9uKGYpIHtcbiAgICB0aGlzLl9pbml0aWFsaXplID0gZjtcbn07XG5WaXNweUNhbnZhcy5wcm90b3R5cGUub25fcmVzaXplID0gZnVuY3Rpb24oZikge1xuICAgIHRoaXMuX3Jlc2l6ZSA9IGY7XG59O1xuVmlzcHlDYW52YXMucHJvdG90eXBlLm9uX3BhaW50ID0gZnVuY3Rpb24oZikge1xuICAgIHRoaXMuX3BhaW50ID0gZjtcbn07XG5WaXNweUNhbnZhcy5wcm90b3R5cGUub25fZXZlbnRfdGljayA9IGZ1bmN0aW9uKGYpIHtcbiAgICB0aGlzLl9ldmVudF90aWNrID0gZjtcbn07XG5cblxuVmlzcHlDYW52YXMucHJvdG90eXBlLmluaXRpYWxpemUgPSBmdW5jdGlvbigpIHtcbiAgICB2YXIgZXZlbnQgPSBnZW5faW5pdGlhbGl6ZV9ldmVudCh0aGlzKTtcbiAgICB0aGlzLl9zZXRfc2l6ZSgpO1xuICAgIHRoaXMuX2luaXRpYWxpemUoZXZlbnQpO1xufTtcblZpc3B5Q2FudmFzLnByb3RvdHlwZS5fc2V0X3NpemUgPSBmdW5jdGlvbihzaXplKSB7XG4gICAgaWYgKHNpemUgPT0gdW5kZWZpbmVkKSB7XG4gICAgICAgIHNpemUgPSBbdGhpcy4kZWwud2lkdGgoKSwgdGhpcy4kZWwuaGVpZ2h0KCldO1xuICAgIH1cbiAgICB0aGlzLnNpemUgPSBzaXplO1xuICAgIHRoaXMud2lkdGggPSBzaXplWzBdO1xuICAgIHRoaXMuaGVpZ2h0ID0gc2l6ZVsxXTtcbiAgICByZXR1cm4gc2l6ZTtcbn1cblZpc3B5Q2FudmFzLnByb3RvdHlwZS5wYWludCA9IGZ1bmN0aW9uKCkge1xuICAgIC8qIEFkZCBhIHBhaW50IGV2ZW50IGluIHRoZSBldmVudCBxdWV1ZS4gKi9cbiAgICB2YXIgZXZlbnQgPSBnZW5fcGFpbnRfZXZlbnQodGhpcyk7XG4gICAgdGhpcy5ldmVudF9xdWV1ZS5hcHBlbmQoZXZlbnQpO1xufTtcblZpc3B5Q2FudmFzLnByb3RvdHlwZS51cGRhdGUgPSBWaXNweUNhbnZhcy5wcm90b3R5cGUucGFpbnQ7XG5WaXNweUNhbnZhcy5wcm90b3R5cGUucmVzaXplID0gZnVuY3Rpb24oc2l6ZSkge1xuICAgIHNpemUgPSB0aGlzLl9zZXRfc2l6ZShzaXplKTtcbiAgICB2YXIgZXZlbnQgPSBnZW5fcmVzaXplX2V2ZW50KHRoaXMsIHNpemUpO1xuICAgIHRoaXMuZ2wuY2FudmFzLndpZHRoID0gc2l6ZVswXTtcbiAgICB0aGlzLmdsLmNhbnZhcy5oZWlnaHQgPSBzaXplWzFdO1xuICAgIC8vIFB1dCB0aGUgcmVzaXplIGV2ZW50IGluIHRoZSBxdWV1ZS5cbiAgICB0aGlzLmV2ZW50X3F1ZXVlLmFwcGVuZChldmVudCk7XG4gICAgdGhpcy5fcmVzaXplKGV2ZW50KTtcbn07XG5cblZpc3B5Q2FudmFzLnByb3RvdHlwZS5ldmVudF90aWNrID0gZnVuY3Rpb24oKSB7XG4gICAgdGhpcy5fZXZlbnRfdGljaygpO1xuICAgIHZhciBuY29tbWFuZHMgPSB0aGlzLmV4ZWN1dGVfcGVuZGluZ19jb21tYW5kcygpO1xuICAgIGlmIChuY29tbWFuZHMgPiAwKSB7XG4gICAgICAgIC8vIEF0IGxlYXN0IDEgR0xJUiBjb21tYW5kIGhhcyBiZWVuIGV4ZWN1dGVkIGhlcmUuXG4gICAgICAgIC8vIFdlIGNhbGwgdGhlIG9uX3BhaW50IGNhbGxiYWNrIGZ1bmN0aW9uIGhlcmUuXG4gICAgICAgIHZhciBldmVudCA9IGdlbl9wYWludF9ldmVudCh0aGlzKTtcbiAgICAgICAgdGhpcy5fcGFpbnQoZXZlbnQpO1xuICAgIH1cbn07XG5cblZpc3B5Q2FudmFzLnByb3RvdHlwZS5pc19mdWxsc2NyZWVuID0gZnVuY3Rpb24oKSB7XG4gICAgcmV0dXJuIChzY3JlZW5mdWxsLmVuYWJsZWQpICYgKHNjcmVlbmZ1bGwuaXNGdWxsc2NyZWVuKTtcbn07XG5cblZpc3B5Q2FudmFzLnByb3RvdHlwZS50b2dnbGVfZnVsbHNjcmVlbiA9IGZ1bmN0aW9uKCkge1xuICAgIGlmIChzY3JlZW5mdWxsLmVuYWJsZWQpIHtcbiAgICAgICAgaWYoc2NyZWVuZnVsbC5pc0Z1bGxzY3JlZW4pIHtcbiAgICAgICAgICAgIHNjcmVlbmZ1bGwuZXhpdCgpO1xuICAgICAgICAgICAgdGhpcy5yZXNpemUodGhpcy5fc2l6ZSk7XG4gICAgICAgIH1cbiAgICAgICAgZWxzZSB7XG4gICAgICAgICAgICB0aGlzLiRlbC53aWR0aChcIjEwMCVcIikuaGVpZ2h0KFwiMTAwJVwiKTtcbiAgICAgICAgICAgIHRoaXMuX3NpemUgPSBbdGhpcy4kZWwud2lkdGgoKSwgdGhpcy4kZWwuaGVpZ2h0KCldO1xuICAgICAgICAgICAgc2NyZWVuZnVsbC5yZXF1ZXN0KHRoaXMuJGVsWzBdKTtcbiAgICAgICAgICAgIHRoaXMucmVzaXplKFtzY3JlZW4ud2lkdGgsIHNjcmVlbi5oZWlnaHRdKTtcbiAgICAgICAgfVxuICAgIH1cbn07XG5cblZpc3B5Q2FudmFzLnByb3RvdHlwZS5kZWFjdGl2YXRlX2NvbnRleHRfbWVudSA9IGZ1bmN0aW9uKCkge1xuICAgIGRvY3VtZW50Lm9uY29udGV4dG1lbnUgPSBmdW5jdGlvbiAoKSB7IHJldHVybiBmYWxzZTsgfTtcbn1cblxuVmlzcHlDYW52YXMucHJvdG90eXBlLnJlc2l6YWJsZSA9IGZ1bmN0aW9uKCkge1xuICAgIHZhciB0aGF0ID0gdGhpcztcbiAgICB0aGlzLiRlbC5yZXNpemFibGUoe1xuICAgICAgICByZXNpemU6IGZ1bmN0aW9uKGV2ZW50LCB1aSkge1xuICAgICAgICAgICAgdGhhdC5yZXNpemUoW3VpLnNpemUud2lkdGgsIHVpLnNpemUuaGVpZ2h0XSk7XG4gICAgICAgIH1cbiAgICB9KTtcbn07XG5cblxuLyogRXZlbnQgcXVldWUgcHJvdG90eXBlICovXG5mdW5jdGlvbiBfZXZlbnRzX2Nhbl9iZV9jb21iaW5lZChlMSwgZTIpIHtcbiAgICAvLyBSZXR1cm4gdGhlIGxpc3Qgb2YgcHJvcGVydGllcyB0byBjb3B5IHRvIGUyLlxuICAgIC8vIFRoZSByZXR1cm5lZCBsaXN0IGlzIG5vbiBlbXB0eSBpZiB0aGUgdHdvIGV2ZW50cyBjYW4gYmUgY29tYmluZWQuXG4gICAgLy8gSXQgaXMgZW1wdHkgaWYgdGhlIHR3byBldmVudHMgY2Fubm90IGJlIGNvbWJpbmVkLlxuICAgIHZhciB0eXBlID0gZTEudHlwZTtcbiAgICBpZiAodHlwZSA9PSBlMi50eXBlKSB7XG4gICAgICAgIGlmICh0eXBlID09ICdtb3VzZV9tb3ZlJykge1xuICAgICAgICAgICAgaWYgKChlMS5idXR0b24gPT0gZTIuYnV0dG9uKSAmXG4gICAgICAgICAgICAgICAgKGUxLmlzX2RyYWdnaW5nID09IGUyLmlzX2RyYWdnaW5nKSAmXG4gICAgICAgICAgICAgICAgKGUxLm1vZGlmaWVycy5lcXVhbHMoZTIubW9kaWZpZXJzKSkpIHtcbiAgICAgICAgICAgICAgICByZXR1cm4gWydwb3MnXTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgICAgICBlbHNlIHtcblxuICAgICAgICB9XG4gICAgfVxuICAgIHJldHVybiBbXTtcbn1cbmZ1bmN0aW9uIEV2ZW50UXVldWUobWF4bGVuKSB7XG4gICAgaWYgKG1heGxlbiA9PSB1bmRlZmluZWQpIHtcbiAgICAgICAgbWF4bGVuID0gMTAwO1xuICAgIH1cbiAgICB0aGlzLl9xdWV1ZSA9IFtdO1xuICAgIHRoaXMubWF4bGVuID0gbWF4bGVuO1xufVxuRXZlbnRRdWV1ZS5wcm90b3R5cGUuY2xlYXIgPSBmdW5jdGlvbigpIHtcbiAgICB0aGlzLl9xdWV1ZSA9IFtdO1xufVxuRXZlbnRRdWV1ZS5wcm90b3R5cGUuYXBwZW5kID0gZnVuY3Rpb24oZSwgY29tcHJlc3MpIHtcbiAgICAvLyBDb21wcmVzc2lvbiBhbGxvd3Mgc2V2ZXJhbCBzaW1pbGFyIGNvbnNlY3V0aXZlIGV2ZW50cyB0byBiZSBtZXJnZWRcbiAgICAvLyBpbnRvIGEgc2luZ2xlIGV2ZW50LCBmb3IgcGVyZm9ybWFuY2UgcmVhc29ucyAobm90YWJseSwgJ21vdXNlX21vdmUnKS5cbiAgICB2YXIgYWRkX3RvX3F1ZXVlID0gdHJ1ZTtcbiAgICBpZiAoY29tcHJlc3MgPT0gdW5kZWZpbmVkKSB7XG4gICAgICAgIGNvbXByZXNzID0gdHJ1ZTtcbiAgICB9XG4gICAgaWYgKGNvbXByZXNzKSB7XG4gICAgICAgIC8vIElmIHRoZSBldmVudCB0eXBlIGlzIGlkZW50aWNhbCB0byB0aGUgbGFzdCBldmVudCwgd2VcbiAgICAgICAgLy8ganVzdCB1cGRhdGUgdGhlIHBhcmFtZXRlcnMgaW5zdGVhZCBvZiBwdXNoaW5nIGEgbmV3IGV2ZW50LlxuICAgICAgICB2YXIgbGFzdF9ldmVudCA9IHRoaXMuX3F1ZXVlW3RoaXMuX3F1ZXVlLmxlbmd0aCAtIDFdO1xuICAgICAgICBpZiAobGFzdF9ldmVudCAhPSB1bmRlZmluZWQpIHtcbiAgICAgICAgICAgIC8vIEdldCB0aGUgbGlzdCBvciBwcm9wZXJ0aWVzIHRvIGNvbWJpbmUuXG4gICAgICAgICAgICB2YXIgcHJvcHMgPSBfZXZlbnRzX2Nhbl9iZV9jb21iaW5lZChlLCBsYXN0X2V2ZW50KTtcbiAgICAgICAgICAgIC8vIENvbWJpbmUgdGhlIHByb3BlcnRpZXMuXG4gICAgICAgICAgICBpZiAocHJvcHMubGVuZ3RoID4gMCkge1xuICAgICAgICAgICAgICAgIGZvciAodmFyIGkgPSAwOyBpIDwgcHJvcHMubGVuZ3RoOyBpKyspIHtcbiAgICAgICAgICAgICAgICAgICAgdmFyIHByb3AgPSBwcm9wc1tpXTtcbiAgICAgICAgICAgICAgICAgICAgdGhpcy5fcXVldWVbdGhpcy5fcXVldWUubGVuZ3RoIC0gMV1bcHJvcF0gPSBlW3Byb3BdO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICAvLyBJbiB0aGlzIGNhc2UsIG5vIG5lZWQgdG8gYWRkIHRoZSBuZXcgZXZlbnQgdG8gdGhlIHF1ZXVlXG4gICAgICAgICAgICAgICAgLy8gYmVjYXVzZSB0aGUgbGFzdCBleGlzdGluZyBldmVudCBjYW4gYmUgdXBkYXRlZCAoXCJjb21iaW5lZFwiXG4gICAgICAgICAgICAgICAgLy8gd2l0aCB0aGUgbmV3IG9uZSkuXG4gICAgICAgICAgICAgICAgYWRkX3RvX3F1ZXVlID0gZmFsc2U7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICB9XG4gICAgaWYgKGFkZF90b19xdWV1ZSkge1xuICAgICAgICB0aGlzLl9xdWV1ZS5wdXNoKGUpO1xuICAgIH1cbiAgICAvLyBSZW1vdmUgdGhlIG9sZGVzdCBlbGVtZW50IGlmIHRoZSBxdWV1ZSBpcyBsb25nZXIgdGhhbiB0aGUgbWF4aW11bSBhbGxvd2VkIHNpZGUuXG4gICAgaWYgKHRoaXMuX3F1ZXVlLmxlbmd0aCA+IHRoaXMubWF4bGVuKSB7XG4gICAgICAgIHRoaXMuX3F1ZXVlLnNoaWZ0KCk7XG4gICAgICAgIC8vIFJlbW92ZSB0aGUgcmVmZXJlbmNlIHRvIHRoZSByZW1vdmVkIGV2ZW50IGluIG9yZGVyIHRvIGNsZWFuIHRoZSBHQy5cbiAgICAgICAgdGhpcy5fcXVldWVbMF0ubGFzdF9ldmVudCA9IG51bGw7XG4gICAgfVxufVxuRXZlbnRRdWV1ZS5wcm90b3R5cGUuZ2V0ID0gZnVuY3Rpb24oKSB7XG4gICAgcmV0dXJuIHRoaXMuX3F1ZXVlO1xufVxuT2JqZWN0LmRlZmluZVByb3BlcnR5KEV2ZW50UXVldWUucHJvdG90eXBlLCBcImxlbmd0aFwiLCB7XG4gICAgZ2V0OiBmdW5jdGlvbigpIHsgcmV0dXJuIHRoaXMuX3F1ZXVlLmxlbmd0aDsgfSxcbn0pO1xuXG5cbi8qIENhbnZhcyBpbml0aWFsaXphdGlvbiAqL1xuZnVuY3Rpb24gaW5pdF9hcHAoYykge1xuXG4gICAgLy8gR2VuZXJhdGUgYSByZXNpemUgZXZlbnQgd2hlbiB0aGUgdXNlciByZXNpemVzIHRoZSBjYW52YXMgd2l0aFxuICAgIC8vIGpRdWVyeSByZXNpemFibGUuXG4gICAgYy4kZWwucmVzaXplKGZ1bmN0aW9uKGUpIHtcbiAgICAgICAgICAgIGMucmVzaXplKFtlLndpZHRoKCksIGUuaGVpZ2h0KCldKTtcbiAgICAgICAgfVxuICAgICk7XG5cbiAgICBjLmV2ZW50X3F1ZXVlID0gbmV3IEV2ZW50UXVldWUoKTtcblxuICAgIC8vIFRoaXMgb2JqZWN0IHN0b3JlcyBzb21lIHN0YXRlIG5lY2Vzc2FyeSB0byBnZW5lcmF0ZSB0aGUgYXBwcm9wcmlhdGVcbiAgICAvLyBldmVudHMuXG4gICAgYy5fZXZlbnRpbmZvID0ge1xuICAgICAgICAndHlwZSc6IG51bGwsXG4gICAgICAgICdwb3MnOiBudWxsLFxuICAgICAgICAnYnV0dG9uJzogbnVsbCxcbiAgICAgICAgJ2lzX2RyYWdnaW5nJzogbnVsbCxcbiAgICAgICAgJ2tleSc6IG51bGwsXG4gICAgICAgICdtb2RpZmllcnMnOiBbXSxcbiAgICAgICAgJ3ByZXNzX2V2ZW50JzogbnVsbCxcbiAgICAgICAgJ2xhc3RfZXZlbnQnOiBudWxsLFxuICAgICAgICAnZGVsdGEnOiBudWxsLFxuICAgIH1cblxuICAgIC8vIEhBQ0s6IGJvb2xlYW4gc3RhdGluZyB3aGV0aGVyIGEgbW91c2UgYnV0dG9uIGlzIHByZXNzZWQuXG4gICAgLy8gVGhpcyBpcyBuZWNlc3NhcnkgYmVjYXVzZSBlLmJ1dHRvbj09MCBpbiB0d28gY2FzZXM6IG5vXG4gICAgLy8gYnV0dG9uIGlzIHByZXNzZWQsIG9yIHRoZSBsZWZ0IGJ1dHRvbiBpcyBwcmVzc2VkLlxuICAgIGMuX2V2ZW50aW5mby5pc19idXR0b25fcHJlc3NlZCA9IDA7XG5cbiAgICBjLiRlbC5tb3VzZW1vdmUoZnVuY3Rpb24oZSkge1xuICAgICAgICB2YXIgZXZlbnQgPSBnZW5fbW91c2VfZXZlbnQoYywgZSwgJ21vdXNlX21vdmUnKTtcblxuICAgICAgICAvLyBWaXNweSBjYWxsYmFja3MuXG4gICAgICAgIGMuX21vdXNlX21vdmUoZXZlbnQpO1xuXG4gICAgICAgIC8vIFNhdmUgdGhlIGxhc3QgZXZlbnQuXG4gICAgICAgIC8vIGMuX2V2ZW50aW5mby5sYXN0X2V2ZW50ID0gZXZlbnQ7XG4gICAgICAgIGMuZXZlbnRfcXVldWUuYXBwZW5kKGV2ZW50KTtcbiAgICB9KTtcbiAgICBjLiRlbC5tb3VzZWRvd24oZnVuY3Rpb24oZSkge1xuICAgICAgICArK2MuX2V2ZW50aW5mby5pc19idXR0b25fcHJlc3NlZDtcbiAgICAgICAgdmFyIGV2ZW50ID0gZ2VuX21vdXNlX2V2ZW50KGMsIGUsICdtb3VzZV9wcmVzcycpO1xuXG4gICAgICAgIC8vIFZpc3B5IGNhbGxiYWNrcy5cbiAgICAgICAgYy5fbW91c2VfcHJlc3MoZXZlbnQpO1xuXG4gICAgICAgIC8vIFNhdmUgdGhlIGxhc3QgcHJlc3MgZXZlbnQuXG4gICAgICAgIGMuX2V2ZW50aW5mby5wcmVzc19ldmVudCA9IGV2ZW50O1xuICAgICAgICAvLyBTYXZlIHRoZSBsYXN0IGV2ZW50LlxuICAgICAgICAvLyBjLl9ldmVudGluZm8ubGFzdF9ldmVudCA9IGV2ZW50O1xuICAgICAgICBjLmV2ZW50X3F1ZXVlLmFwcGVuZChldmVudCk7XG4gICAgfSk7XG4gICAgYy4kZWwubW91c2V1cChmdW5jdGlvbihlKSB7XG4gICAgICAgIC0tYy5fZXZlbnRpbmZvLmlzX2J1dHRvbl9wcmVzc2VkO1xuICAgICAgICB2YXIgZXZlbnQgPSBnZW5fbW91c2VfZXZlbnQoYywgZSwgJ21vdXNlX3JlbGVhc2UnKTtcblxuICAgICAgICAvLyBWaXNweSBjYWxsYmFja3MuXG4gICAgICAgIGMuX21vdXNlX3JlbGVhc2UoZXZlbnQpO1xuXG4gICAgICAgIC8vIFJlc2V0IHRoZSBsYXN0IHByZXNzIGV2ZW50LlxuICAgICAgICBjLl9ldmVudGluZm8ucHJlc3NfZXZlbnQgPSBudWxsO1xuICAgICAgICAvLyBTYXZlIHRoZSBsYXN0IGV2ZW50LlxuICAgICAgICAvLyBjLl9ldmVudGluZm8ubGFzdF9ldmVudCA9IGV2ZW50O1xuICAgICAgICBjLmV2ZW50X3F1ZXVlLmFwcGVuZChldmVudCk7XG4gICAgfSk7XG4gICAgYy4kZWwuY2xpY2soZnVuY3Rpb24oZSkge1xuICAgICAgICAvLyBSZXNldCB0aGUgbGFzdCBwcmVzcyBldmVudC5cbiAgICAgICAgYy5fZXZlbnRpbmZvLnByZXNzX2V2ZW50ID0gbnVsbDtcbiAgICB9KTtcbiAgICBjLiRlbC5kYmxjbGljayhmdW5jdGlvbihlKSB7XG5cbiAgICAgICAgLy8gUmVzZXQgdGhlIGxhc3QgcHJlc3MgZXZlbnQuXG4gICAgICAgIGMuX2V2ZW50aW5mby5wcmVzc19ldmVudCA9IG51bGw7XG4gICAgfSk7XG4gICAgLy8gVGhpcyByZXF1aXJlcyB0aGUgbW91c2Ugd2hlZWwganF1ZXJ5IHBsdWdpbi5cbiAgICBpZiAoYy4kZWwubW91c2V3aGVlbCAhPSB1bmRlZmluZWQpIHtcbiAgICAgICAgYy4kZWwubW91c2V3aGVlbChmdW5jdGlvbihlKSB7XG4gICAgICAgICAgICB2YXIgZXZlbnQgPSBnZW5fbW91c2VfZXZlbnQoYywgZSwgJ21vdXNlX3doZWVsJyk7XG4gICAgICAgICAgICBldmVudC5kZWx0YSA9IFtlLmRlbHRhWCAqIGUuZGVsdGFGYWN0b3IgKiAuMDEsXG4gICAgICAgICAgICAgICAgICAgICAgICAgICBlLmRlbHRhWSAqIGUuZGVsdGFGYWN0b3IgKiAuMDFdO1xuXG4gICAgICAgICAgICAvLyBWaXNweSBjYWxsYmFja3MuXG4gICAgICAgICAgICBjLl9tb3VzZV93aGVlbChldmVudCk7XG5cbiAgICAgICAgICAgIC8vIFNhdmUgdGhlIGxhc3QgZXZlbnQuXG4gICAgICAgICAgICAvLyBjLl9ldmVudGluZm8ubGFzdF9ldmVudCA9IGV2ZW50O1xuICAgICAgICAgICAgYy5ldmVudF9xdWV1ZS5hcHBlbmQoZXZlbnQpO1xuXG4gICAgICAgICAgICBlLnByZXZlbnREZWZhdWx0KCk7XG4gICAgICAgICAgICBlLnN0b3BQcm9wYWdhdGlvbigpO1xuICAgICAgICB9KTtcbiAgICB9XG5cbiAgICBjLiRlbC5rZXlkb3duKGZ1bmN0aW9uKGUpIHtcbiAgICAgICAgdmFyIGV2ZW50ID0gZ2VuX2tleV9ldmVudChjLCBlLCAna2V5X3ByZXNzJyk7XG5cbiAgICAgICAgLy8gVmlzcHkgY2FsbGJhY2tzLlxuICAgICAgICBjLl9rZXlfcHJlc3MoZXZlbnQpO1xuXG4gICAgICAgIC8vIFNhdmUgdGhlIGxhc3QgZXZlbnQuXG4gICAgICAgIC8vIGMuX2V2ZW50aW5mby5sYXN0X2V2ZW50ID0gZXZlbnQ7XG4gICAgICAgIGMuZXZlbnRfcXVldWUuYXBwZW5kKGV2ZW50KTtcbiAgICB9KTtcbiAgICBjLiRlbC5rZXl1cChmdW5jdGlvbihlKSB7XG4gICAgICAgIHZhciBldmVudCA9IGdlbl9rZXlfZXZlbnQoYywgZSwgJ2tleV9yZWxlYXNlJyk7XG5cbiAgICAgICAgLy8gVmlzcHkgY2FsbGJhY2tzLlxuICAgICAgICBjLl9rZXlfcmVsZWFzZShldmVudCk7XG5cbiAgICAgICAgLy8gU2F2ZSB0aGUgbGFzdCBldmVudC5cbiAgICAgICAgLy8gYy5fZXZlbnRpbmZvLmxhc3RfZXZlbnQgPSBldmVudDtcbiAgICAgICAgYy5ldmVudF9xdWV1ZS5hcHBlbmQoZXZlbnQpO1xuICAgIH0pO1xuXG4gICAgYy4kZWwubW91c2VvdXQoZnVuY3Rpb24oZSkge1xuICAgIH0pO1xufVxuXG5cbi8qIENyZWF0aW9uIG9mIHZpc3B5LmV2ZW50cyAqL1xudmFyIGV2ZW50cyA9IGZ1bmN0aW9uKCkge1xuICAgIC8vIENvbnN0cnVjdG9yLlxuXG59O1xuXG5ldmVudHMucHJvdG90eXBlLmluaXQgPSBmdW5jdGlvbihjKSB7XG4gICAgaW5pdF9hcHAoYyk7XG59O1xuXG5tb2R1bGUuZXhwb3J0cyA9IG5ldyBldmVudHMoKTtcbiIsInZhciBWaXNweUNhbnZhcyA9IHJlcXVpcmUoJy4vdmlzcHljYW52YXMuanMnKTtcbnZhciB1dGlsID0gcmVxdWlyZSgnLi91dGlsLmpzJyk7XG52YXIgZGF0YSA9IHJlcXVpcmUoJy4vZGF0YS5qcycpO1xuXG52YXIgZGVidWcgPSB1dGlsLmRlYnVnO1xudmFyIHRvX2FycmF5X2J1ZmZlciA9IGRhdGEudG9fYXJyYXlfYnVmZmVyO1xudmFyIEpVU1RfREVMRVRFRCA9ICdKVVNUX0RFTEVURUQnO1xuXG4vKiBXZWJHTCB1dGlsaXR5IGZ1bmN0aW9ucyAqL1xuZnVuY3Rpb24gdmlld3BvcnQoYykge1xuICAgIGMuZ2wudmlld3BvcnQoMCwgMCwgYy53aWR0aCgpLCBjLmhlaWdodCgpKTtcbn1cblxuZnVuY3Rpb24gY2xlYXIoYywgY29sb3IpIHtcbiAgICBjLmdsLmNsZWFyQ29sb3IoY29sb3JbMF0sIGNvbG9yWzFdLCBjb2xvclsyXSwgY29sb3JbM10pO1xuICAgIGMuZ2wuY2xlYXIoYy5nbC5DT0xPUl9CVUZGRVJfQklUKTtcbn1cblxuZnVuY3Rpb24gY29tcGlsZV9zaGFkZXIoYywgc2hhZGVyLCBzb3VyY2UpIHtcbiAgICAvLyBUT0RPOiBDb252ZXJ0IGRlc2t0b3AgR0xTTCBjb2RlIGlmIG5lZWRlZFxuICAgIGNvbnNvbGUubG9nKHR5cGVvZiBzb3VyY2UpO1xuICAgIGlmICh0eXBlb2Ygc291cmNlICE9PSAnc3RyaW5nJykge1xuICAgICAgICAvLyBhc3N1bWUgd2UgaGF2ZSBhIGJ1ZmZlclxuICAgICAgICBzb3VyY2UgPSBTdHJpbmcuZnJvbUNoYXJDb2RlLmFwcGx5KG51bGwsIG5ldyBVaW50OEFycmF5KHNvdXJjZSkpO1xuXG4gICAgfVxuICAgIHNvdXJjZSA9IHNvdXJjZS5yZXBsYWNlKC9cXFxcbi9nLCBcIlxcblwiKTtcblxuICAgIGMuZ2wuc2hhZGVyU291cmNlKHNoYWRlciwgc291cmNlKTtcbiAgICBjLmdsLmNvbXBpbGVTaGFkZXIoc2hhZGVyKTtcblxuICAgIGlmICghYy5nbC5nZXRTaGFkZXJQYXJhbWV0ZXIoc2hhZGVyLCBjLmdsLkNPTVBJTEVfU1RBVFVTKSlcbiAgICB7XG4gICAgICAgIGNvbnNvbGUuZXJyb3IoYy5nbC5nZXRTaGFkZXJJbmZvTG9nKHNoYWRlcikpO1xuICAgICAgICByZXR1cm4gZmFsc2U7XG4gICAgfVxuXG4gICAgcmV0dXJuIHRydWU7XG59XG5cbmZ1bmN0aW9uIGNyZWF0ZV9hdHRyaWJ1dGUoYywgcHJvZ3JhbSwgbmFtZSkge1xuICAgIHZhciBhdHRyaWJ1dGVfaGFuZGxlID0gYy5nbC5nZXRBdHRyaWJMb2NhdGlvbihwcm9ncmFtLCBuYW1lKTtcbiAgICByZXR1cm4gYXR0cmlidXRlX2hhbmRsZTtcbn1cblxuZnVuY3Rpb24gYWN0aXZhdGVfYXR0cmlidXRlKGMsIGF0dHJpYnV0ZV9oYW5kbGUsIHZib19pZCwgdHlwZSwgc3RyaWRlLCBvZmZzZXQpIHtcbiAgICAvLyBhdHRyaWJ1dGVfaGFuZGxlOiBhdHRyaWJ1dGUgaGFuZGxlXG4gICAgLy8gdmJvX2lkXG4gICAgLy8gdHlwZTogZmxvYXQsIHZlYzMsIGV0Yy5cbiAgICAvLyBzdHJpZGU6IDAgYnkgZGVmYXVsdFxuICAgIC8vIG9mZnNldDogMCBieSBkZWZhdWx0XG4gICAgdmFyIF9hdHRyaWJ1dGVfaW5mbyA9IGdldF9hdHRyaWJ1dGVfaW5mbyh0eXBlKTtcbiAgICB2YXIgYXR0cmlidXRlX3R5cGUgPSBfYXR0cmlidXRlX2luZm9bMF07ICAvLyBGTE9BVCwgSU5UIG9yIEJPT0xcbiAgICB2YXIgbmRpbSA9IF9hdHRyaWJ1dGVfaW5mb1sxXTsgLy8gMSwgMiwgMyBvciA0XG5cbiAgICBfdmJvX2luZm8gPSBjLl9uc1t2Ym9faWRdO1xuICAgIHZhciB2Ym9faGFuZGxlID0gX3Zib19pbmZvLmhhbmRsZTtcblxuICAgIGMuZ2wuZW5hYmxlVmVydGV4QXR0cmliQXJyYXkoYXR0cmlidXRlX2hhbmRsZSk7XG4gICAgYy5nbC5iaW5kQnVmZmVyKGMuZ2wuQVJSQVlfQlVGRkVSLCB2Ym9faGFuZGxlKTtcbiAgICBjLmdsLnZlcnRleEF0dHJpYlBvaW50ZXIoYXR0cmlidXRlX2hhbmRsZSwgbmRpbSxcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgYy5nbFthdHRyaWJ1dGVfdHlwZV0sXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgIGZhbHNlLCBzdHJpZGUsIG9mZnNldCk7XG59XG5cbmZ1bmN0aW9uIGRlYWN0aXZhdGVfYXR0cmlidXRlKGMsIGF0dHJpYnV0ZV9oYW5kbGUpIHtcbiAgICAvLyBjLmdsLmJpbmRCdWZmZXIoYy5nbC5HTF9BUlJBWV9CVUZGRVIsIDApO1xuICAgIGMuZ2wuZGlzYWJsZVZlcnRleEF0dHJpYkFycmF5KGF0dHJpYnV0ZV9oYW5kbGUpO1xufVxuXG5mdW5jdGlvbiBhY3RpdmF0ZV90ZXh0dXJlKGMsIHRleHR1cmVfaGFuZGxlLCBzYW1wbGVyX2hhbmRsZSwgdGV4dHVyZV9pbmRleCkge1xuICAgIGlmICh0ZXh0dXJlX2hhbmRsZSA9PT0gSlVTVF9ERUxFVEVEKSB7XG4gICAgICAgIHJldHVybjtcbiAgICB9XG4gICAgYy5nbC5hY3RpdmVUZXh0dXJlKGMuZ2wuVEVYVFVSRTAgKyB0ZXh0dXJlX2luZGV4KTtcbiAgICBjLmdsLmJpbmRUZXh0dXJlKGMuZ2wuVEVYVFVSRV8yRCwgdGV4dHVyZV9oYW5kbGUpO1xuICAgIC8vIGMuZ2wudW5pZm9ybTFpKHNhbXBsZXJfaGFuZGxlLCAwKTtcbn1cblxuZnVuY3Rpb24gZGVhY3RpdmF0ZV90ZXh0dXJlKGMsIHRleHR1cmVfaGFuZGxlLCBzYW1wbGVyX2hhbmRsZSwgdGV4dHVyZV9pbmRleCkge1xuICAgIGMuZ2wuYWN0aXZlVGV4dHVyZShjLmdsLlRFWFRVUkUwICsgdGV4dHVyZV9pbmRleCk7XG4gICAgYy5nbC5iaW5kVGV4dHVyZShjLmdsLlRFWFRVUkVfMkQsIG51bGwpO1xufVxuXG5mdW5jdGlvbiBfZ2V0X2FsaWdubWVudCh3aWR0aCkge1xuICAgIC8qIERldGVybWluZXMgYSB0ZXh0dXJlcyBieXRlIGFsaWdubWVudC5cblxuICAgIElmIHRoZSB3aWR0aCBpc24ndCBhIHBvd2VyIG9mIDJcbiAgICB3ZSBuZWVkIHRvIGFkanVzdCB0aGUgYnl0ZSBhbGlnbm1lbnQgb2YgdGhlIGltYWdlLlxuICAgIFRoZSBpbWFnZSBoZWlnaHQgaXMgdW5pbXBvcnRhbnRcblxuICAgIHd3dy5vcGVuZ2wub3JnL3dpa2kvQ29tbW9uX01pc3Rha2VzI1RleHR1cmVfdXBsb2FkX2FuZF9waXhlbF9yZWFkc1xuXG4gICAgd2Uga25vdyB0aGUgYWxpZ25tZW50IGlzIGFwcHJvcHJpYXRlXG4gICAgaWYgd2UgY2FuIGRpdmlkZSB0aGUgd2lkdGggYnkgdGhlXG4gICAgYWxpZ25tZW50IGNsZWFubHlcbiAgICB2YWxpZCBhbGlnbm1lbnRzIGFyZSAxLDIsNCBhbmQgOFxuICAgIDQgaXMgdGhlIGRlZmF1bHRcblxuICAgICovXG4gICAgdmFyIGFsaWdubWVudHMgPSBbOCwgNCwgMiwgMV07XG4gICAgZm9yICh2YXIgaSA9IDA7IGkgPCBhbGlnbm1lbnRzLmxlbmd0aDsgaSsrKSB7XG4gICAgICAgIGlmICh3aWR0aCAlIGFsaWdubWVudHNbaV0gPT0gMCkge1xuICAgICAgICAgICAgcmV0dXJuIGFsaWdubWVudHNbaV07XG4gICAgICAgIH1cbiAgICB9XG59XG5cbmZ1bmN0aW9uIHNldF90ZXh0dXJlX2RhdGEoYywgb2JqZWN0X2hhbmRsZSwgZ2xfdHlwZSwgZm9ybWF0LCB3aWR0aCwgaGVpZ2h0LCBhcnJheSwgb2Zmc2V0LCBzaGFwZSwgZHR5cGUpIHtcbiAgICBjLmdsLmJpbmRUZXh0dXJlKGdsX3R5cGUsIG9iamVjdF9oYW5kbGUpO1xuXG4gICAgLy8gVE9ETzogY2hvb3NlIGEgYmV0dGVyIGFsaWdubWVudFxuICAgIGMuZ2wucGl4ZWxTdG9yZWkoYy5nbC5VTlBBQ0tfQUxJR05NRU5ULCAxKTtcblxuICAgIGlmIChhcnJheSA9PT0gbnVsbCkge1xuICAgICAgICAvLyBzcGVjaWFsIHRleHR1cmUgYXR0YWNoZWQgdG8gZnJhbWUgYnVmZmVyIHRvIGJlIHJlbmRlcmVkIHRvXG4gICAgICAgIGMuZ2wudGV4SW1hZ2UyRChnbF90eXBlLCAwLCBmb3JtYXQsIHdpZHRoLCBoZWlnaHQsIDAsIGZvcm1hdCwgYy5nbC5VTlNJR05FRF9CWVRFLCBhcnJheSk7XG4gICAgfSBlbHNlIGlmIChhcnJheS5nZXRDb250ZXh0KSB7XG4gICAgICAgIC8vIEEgY2FudmFzIG9iamVjdFxuICAgICAgICBjLmdsLnRleEltYWdlMkQoZ2xfdHlwZSwgMCwgYy5nbC5SR0JBLCBjLmdsLlJHQkEsIGMuZ2wuVU5TSUdORURfQllURSwgYXJyYXkpO1xuICAgIH0gZWxzZSBpZiAoYXJyYXkuY2FudmFzKSB7XG4gICAgICAgIC8vIEEgY29udGV4dCBvYmplY3RcbiAgICAgICAgYy5nbC50ZXhJbWFnZTJEKGdsX3R5cGUsIDAsIGMuZ2wuUkdCQSwgYy5nbC5SR0JBLCBjLmdsLlVOU0lHTkVEX0JZVEUsIGFycmF5LmNhbnZhcyk7XG4gICAgfSBlbHNlIHtcbiAgICAgICAgdmFyIGFycmF5X3ZpZXc7XG4gICAgICAgIGlmIChkdHlwZSA9PSBjLmdsLkZMT0FUKSB7XG4gICAgICAgICAgICBhcnJheV92aWV3ID0gbmV3IEZsb2F0MzJBcnJheShhcnJheSk7XG4gICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICBhcnJheV92aWV3ID0gbmV3IFVpbnQ4QXJyYXkoYXJyYXkpO1xuICAgICAgICB9XG5cbiAgICAgICAgLy8gaWYgdGhpcyBpc24ndCBpbml0aWFsaXppbmcgdGhlIHRleHR1cmUgKHRleEltYWdlMkQpIHRoZW4gc2VlIGlmIHdlXG4gICAgICAgIC8vIGNhbiBzZXQganVzdCBwYXJ0IG9mIHRoZSB0ZXh0dXJlXG4gICAgICAgIGlmIChvZmZzZXQgJiYgc2hhcGUgJiYgKChzaGFwZVswXSAhPT0gaGVpZ2h0KSB8fCAoc2hhcGVbMV0gIT09IHdpZHRoKSkpIHtcbiAgICAgICAgICAgIHZhciB3aWR0aCA9IHNoYXBlW3NoYXBlLmxlbmd0aCAtIDJdICogc2hhcGVbc2hhcGUubGVuZ3RoIC0gMV07XG4gICAgICAgICAgICB2YXIgYWxpZ25tZW50ID0gX2dldF9hbGlnbm1lbnQod2lkdGgpO1xuICAgICAgICAgICAgYy5nbC5waXhlbFN0b3JlaShjLmdsLlVOUEFDS19BTElHTk1FTlQsIGFsaWdubWVudCk7XG4gICAgICAgICAgICBjLmdsLnRleFN1YkltYWdlMkQoZ2xfdHlwZSwgMCwgb2Zmc2V0WzFdLCBvZmZzZXRbMF0sXG4gICAgICAgICAgICAgICAgc2hhcGVbMV0sIHNoYXBlWzBdLCBmb3JtYXQsIGR0eXBlLCBhcnJheV92aWV3KTtcbiAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgIGMuZ2wucGl4ZWxTdG9yZWkoYy5nbC5VTlBBQ0tfQUxJR05NRU5ULCAxKTtcbiAgICAgICAgICAgIGMuZ2wudGV4SW1hZ2UyRChnbF90eXBlLCAwLCBmb3JtYXQsIHdpZHRoLCBoZWlnaHQsIDAsXG4gICAgICAgICAgICAgICAgZm9ybWF0LCBkdHlwZSwgYXJyYXlfdmlldyk7XG4gICAgICAgIH1cbiAgICB9XG59XG5cbmZ1bmN0aW9uIHNldF9idWZmZXJfZGF0YShjLCBvYmplY3RfaGFuZGxlLCBnbF90eXBlLCBvZmZzZXQsIGFycmF5LCByZXVzZSkge1xuICAgIC8vIEJpbmQgdGhlIGJ1ZmZlciBiZWZvcmUgc2V0dGluZyB0aGUgZGF0YS5cbiAgICBjLmdsLmJpbmRCdWZmZXIoZ2xfdHlwZSwgb2JqZWN0X2hhbmRsZSk7XG5cbiAgICAvLyBVcGxvYWQgdGhlIGRhdGEuXG4gICAgaWYgKCFyZXVzZSkge1xuICAgICAgICAvLyBUaGUgZXhpc3RpbmcgYnVmZmVyIHdhcyBlbXB0eTogd2UgY3JlYXRlIGl0LlxuICAgICAgICBjLmdsLmJ1ZmZlckRhdGEoZ2xfdHlwZSwgYXJyYXksIGMuZ2wuU1RBVElDX0RSQVcpO1xuICAgIH1cbiAgICBlbHNlIHtcbiAgICAgICAgLy8gV2UgcmV1c2UgdGhlIGV4aXN0aW5nIGJ1ZmZlci5cbiAgICAgICAgYy5nbC5idWZmZXJTdWJEYXRhKGdsX3R5cGUsIG9mZnNldCwgYXJyYXkpO1xuICAgIH1cbn1cblxuZnVuY3Rpb24gc2V0X3VuaWZvcm0oYywgdW5pZm9ybV9oYW5kbGUsIHVuaWZvcm1fZnVuY3Rpb24sIHZhbHVlKSB7XG4gICAgLy8gR2V0IGEgVHlwZWRBcnJheS5cbiAgICBhcnJheSA9IHRvX2FycmF5X2J1ZmZlcih2YWx1ZSk7XG5cbiAgICBpZiAodW5pZm9ybV9mdW5jdGlvbi5pbmRleE9mKCdNYXRyaXgnKSA+IDApIHtcbiAgICAgICAgLy8gTWF0cml4IHVuaWZvcm1zLlxuICAgICAgICBjLmdsW3VuaWZvcm1fZnVuY3Rpb25dKHVuaWZvcm1faGFuZGxlLCBmYWxzZSwgYXJyYXkpO1xuICAgIH1cbiAgICBlbHNlIHtcbiAgICAgICAgLy8gU2NhbGFyIHVuaWZvcm1zLlxuICAgICAgICBjLmdsW3VuaWZvcm1fZnVuY3Rpb25dKHVuaWZvcm1faGFuZGxlLCBhcnJheSk7XG4gICAgfVxufVxuXG52YXIgX2R0eXBlX3RvX2dsX2R0eXBlID0ge1xuICAgICdmbG9hdDMyJzogJ0ZMT0FUJyxcbiAgICAndWludDgnOiAnVU5TSUdORURfQllURScsXG59O1xuZnVuY3Rpb24gZ2V0X2dsX2R0eXBlKGR0eXBlKSB7XG4gICAgcmV0dXJuIF9kdHlwZV90b19nbF9kdHlwZVtkdHlwZV07XG59XG5cbnZhciBfYXR0cmlidXRlX3R5cGVfbWFwID0ge1xuICAgICdmbG9hdCc6IFsnRkxPQVQnLCAxXSxcbiAgICAndmVjMic6IFsnRkxPQVQnLCAyXSxcbiAgICAndmVjMyc6IFsnRkxPQVQnLCAzXSxcbiAgICAndmVjNCc6IFsnRkxPQVQnLCA0XSxcblxuICAgICdpbnQnOiBbJ0lOVCcsIDFdLFxuICAgICdpdmVjMic6IFsnSU5UJywgMl0sXG4gICAgJ2l2ZWMzJzogWydJTlQnLCAzXSxcbiAgICAnaXZlYzQnOiBbJ0lOVCcsIDRdLFxufTtcbmZ1bmN0aW9uIGdldF9hdHRyaWJ1dGVfaW5mbyh0eXBlKSB7XG4gICAgLy8gdHlwZTogdmVjMiwgaXZlYzMsIGZsb2F0LCBldGMuXG4gICAgcmV0dXJuIF9hdHRyaWJ1dGVfdHlwZV9tYXBbdHlwZV07XG59XG5cbnZhciBfdW5pZm9ybV90eXBlX21hcCA9IHtcbiAgICAnZmxvYXQnOiAndW5pZm9ybTFmdicsXG4gICAgJ3ZlYzInOiAndW5pZm9ybTJmdicsXG4gICAgJ3ZlYzMnOiAndW5pZm9ybTNmdicsXG4gICAgJ3ZlYzQnOiAndW5pZm9ybTRmdicsXG5cbiAgICAnaW50JzogJ3VuaWZvcm0xaXYnLFxuICAgICdpdmVjMic6ICd1bmlmb3JtMml2JyxcbiAgICAnaXZlYzMnOiAndW5pZm9ybTNpdicsXG4gICAgJ2l2ZWM0JzogJ3VuaWZvcm00aXYnLFxuXG4gICAgJ21hdDInOiAndW5pZm9ybU1hdHJpeDJmdicsXG4gICAgJ21hdDMnOiAndW5pZm9ybU1hdHJpeDNmdicsXG4gICAgJ21hdDQnOiAndW5pZm9ybU1hdHJpeDRmdicsXG59O1xuZnVuY3Rpb24gZ2V0X3VuaWZvcm1fZnVuY3Rpb24odHlwZSkge1xuICAgIC8vIEZpbmQgT3BlbkdMIHVuaWZvcm0gZnVuY3Rpb24uXG4gICAgcmV0dXJuIF91bmlmb3JtX3R5cGVfbWFwW3R5cGVdO1xufVxuXG52YXIgX2dsX3R5cGVfbWFwID0ge1xuICAgIFZlcnRleEJ1ZmZlcjogJ0FSUkFZX0JVRkZFUicsXG4gICAgSW5kZXhCdWZmZXI6ICdFTEVNRU5UX0FSUkFZX0JVRkZFUicsXG4gICAgVGV4dHVyZTJEOiAnVEVYVFVSRV8yRCcsXG59O1xuXG5mdW5jdGlvbiBnZXRfZ2xfdHlwZShvYmplY3RfdHlwZSkge1xuICAgIHJldHVybiBfZ2xfdHlwZV9tYXBbb2JqZWN0X3R5cGVdO1xufVxuXG52YXIgX2dsX2F0dGFjaG1lbnRfbWFwID0ge1xuICAgICdjb2xvcic6IFsnQ09MT1JfQVRUQUNITUVOVDAnLCAnUkdCQTQnXSxcbiAgICAnZGVwdGgnOiBbJ0RFUFRIX0FUVEFDSE1FTlQnLCAnREVQVEhfQ09NUE9ORU5UMTYnXSxcbiAgICAnc3RlbmNpbCc6IFsnU1RFTkNJTF9BVFRBQ0hNRU5UJywgJ1NURU5DSUxfSU5ERVg4J10sXG59O1xuXG5mdW5jdGlvbiBnZXRfYXR0YWNobWVudF90eXBlKHR5cGVfc3RyKSB7XG4gICAgcmV0dXJuIF9nbF9hdHRhY2htZW50X21hcFt0eXBlX3N0cl1bMF07XG59XG5cbmZ1bmN0aW9uIGdldF9hdHRhY2htZW50X2Zvcm1hdCh0eXBlX3N0cikge1xuICAgIHJldHVybiBfZ2xfYXR0YWNobWVudF9tYXBbdHlwZV9zdHJdWzFdO1xufVxuXG5mdW5jdGlvbiBwYXJzZV9lbnVtKGMsIHN0cikge1xuICAgIC8vIFBhcnNlIGFuIGVudW0gb3IgY29tYmluYXRpb24gb2YgZW51bXMgc3RvcmVkIGluIGEgc3RyaW5nLlxuICAgIHZhciBzdHJzID0gc3RyLnNwbGl0KCd8Jyk7XG4gICAgdmFyIHZhbHVlID0gMDtcbiAgICBmb3IgKHZhciBpID0gMDsgaSA8IHN0cnMubGVuZ3RoOyBpKyspIHtcbiAgICAgICAgdmFyIG5hbWUgPSBzdHJzW2ldLnRvVXBwZXJDYXNlKCkudHJpbSgpO1xuICAgICAgICB2YWx1ZSA9IHZhbHVlIHwgYy5nbFtuYW1lXTtcbiAgICB9XG4gICAgcmV0dXJuIHZhbHVlO1xufVxuXG5mdW5jdGlvbiB2YWxpZGF0ZV9mcmFtZWJ1ZmZlcihjKSB7XG4gICAgdmFyIHN0YXR1cyA9IGMuZ2wuY2hlY2tGcmFtZWJ1ZmZlclN0YXR1cyhjLmdsLkZSQU1FQlVGRkVSKTtcbiAgICBpZiAoc3RhdHVzID09IGMuZ2wuRlJBTUVCVUZGRVJfQ09NUExFVEUpIHtcbiAgICAgICAgcmV0dXJuO1xuICAgIH1cbiAgICAvLyBjLmdsLkZSQU1FQlVGRkVSX0lOQ09NUExFVEVfRk9STUFUUzogLy8gbm90IGluIGVzIDIuMFxuICAgIC8vICAgICAnSW50ZXJuYWwgZm9ybWF0IG9mIGF0dGFjaG1lbnQgaXMgbm90IHJlbmRlcmFibGUuJ1xuICAgIGlmIChzdGF0dXMgPT0gYy5nbC5GUkFNRUJVRkZFUl9JTkNPTVBMRVRFX0FUVEFDSE1FTlQpIHtcbiAgICAgICAgdGhyb3cgJ0ZyYW1lQnVmZmVyIGF0dGFjaG1lbnRzIGFyZSBpbmNvbXBsZXRlLic7XG4gICAgfVxuICAgIGVsc2UgaWYgKHN0YXR1cyA9PSBjLmdsLkZSQU1FQlVGRkVSX0lOQ09NUExFVEVfTUlTU0lOR19BVFRBQ0hNRU5UKSB7XG4gICAgICAgIHRocm93ICdObyB2YWxpZCBhdHRhY2htZW50cyBpbiB0aGUgRnJhbWVCdWZmZXIuJztcbiAgICB9XG4gICAgZWxzZSBpZiAoc3RhdHVzID09IGMuZ2wuRlJBTUVCVUZGRVJfSU5DT01QTEVURV9ESU1FTlNJT05TKSB7XG4gICAgICAgIHRocm93ICdhdHRhY2htZW50cyBkbyBub3QgaGF2ZSB0aGUgc2FtZSB3aWR0aCBhbmQgaGVpZ2h0Lic7XG4gICAgfVxuICAgIGVsc2UgaWYgKHN0YXR1cyA9PSBjLmdsLkZSQU1FQlVGRkVSX1VOU1VQUE9SVEVEKSB7XG4gICAgICAgIHRocm93ICdDb21iaW5hdGlvbiBvZiBpbnRlcm5hbCBmb3JtYXRzIHVzZWQgYnkgYXR0YWNobWVudHMgaXMgbm90IHN1cHBvcnRlZC4nO1xuICAgIH1cbiAgICBlbHNlIHtcbiAgICAgICAgdGhyb3cgJ1Vua25vd24gZnJhbWVidWZmZXIgZXJyb3InICsgc3RhdHVzO1xuICAgIH1cbn1cblxuZnVuY3Rpb24gYWN0aXZhdGVfZnJhbWVidWZmZXIoYywgZnJhbWVidWZmZXJfaWQpIHtcbiAgICB2YXIgZmIgPSBjLl9uc1tmcmFtZWJ1ZmZlcl9pZF07XG4gICAgdmFyIHN0YWNrID0gYy5lbnYuZmJfc3RhY2s7XG4gICAgaWYgKHN0YWNrLmxlbmd0aCA9PSAwKSB7XG4gICAgICAgIHN0YWNrLnB1c2gobnVsbCk7XG4gICAgfVxuXG4gICAgaWYgKHN0YWNrW3N0YWNrLmxlbmd0aCAtIDFdID09PSBmYi5oYW5kbGUpIHtcbiAgICAgICAgZGVidWcoXCJGcmFtZSBidWZmZXIgYWxyZWFkeSBhY3RpdmUgezB9XCIuZm9ybWF0KGZyYW1lYnVmZmVyX2lkKSk7XG4gICAgICAgIHJldHVybjtcbiAgICB9XG4gICAgZGVidWcoXCJCaW5kaW5nIGZyYW1lIGJ1ZmZlciB7MH0uXCIuZm9ybWF0KGZyYW1lYnVmZmVyX2lkKSk7XG4gICAgYy5nbC5iaW5kRnJhbWVidWZmZXIoYy5nbC5GUkFNRUJVRkZFUiwgZmIuaGFuZGxlKTtcbiAgICBzdGFjay5wdXNoKGZiLmhhbmRsZSk7XG59XG5cbmZ1bmN0aW9uIGRlYWN0aXZhdGVfZnJhbWVidWZmZXIoYywgZnJhbWVidWZmZXJfaWQpIHtcbiAgICB2YXIgZmIgPSBjLl9uc1tmcmFtZWJ1ZmZlcl9pZF07XG4gICAgdmFyIHN0YWNrID0gYy5lbnYuZmJfc3RhY2s7XG4gICAgaWYgKHN0YWNrLmxlbmd0aCA9PSAwKSB7XG4gICAgICAgIHN0YWNrLnB1c2gobnVsbCk7XG4gICAgfVxuXG4gICAgd2hpbGUgKHN0YWNrW3N0YWNrLmxlbmd0aCAtIDFdID09PSBmYi5oYW5kbGUpIHtcbiAgICAgICAgLy8gRGVhY3RpdmF0ZSBjdXJyZW50IGZyYW1lIGJ1ZmZlclxuICAgICAgICBzdGFjay5wb3AoKTsgLy8gJ3VuYmluZCcgY3VycmVudCBidWZmZXJcbiAgICB9XG4gICAgLy8gQWN0aXZhdGUgcHJldmlvdXMgZnJhbWUgYnVmZmVyXG4gICAgLy8gTk9URTogb3V0IG9mIGJvdW5kcyBpbmRleCBpZiB0cnlpbmcgdG8gdW5iaW5kIHRoZSBkZWZhdWx0IChudWxsKSBmcmFtZWJ1ZmZlclxuICAgIGRlYnVnKFwiQmluZGluZyBwcmV2aW91cyBmcmFtZSBidWZmZXJcIik7XG4gICAgYy5nbC5iaW5kRnJhbWVidWZmZXIoYy5nbC5GUkFNRUJVRkZFUiwgc3RhY2tbc3RhY2subGVuZ3RoIC0gMV0pO1xufVxuXG5mdW5jdGlvbiBpbml0X2Vudl9jYWNoZShjKSB7XG4gICAgYy5lbnYgPSB7XG4gICAgICAgICdmYl9zdGFjayc6IFtdLFxuICAgIH07XG59XG5cblxuLyogR2xpciBxdWV1ZSBwcm90b3R5cGUgKi9cbmZ1bmN0aW9uIEdsaXJRdWV1ZSgpIHtcbiAgICB0aGlzLl9xdWV1ZSA9IFtdO1xufVxuR2xpclF1ZXVlLnByb3RvdHlwZS5jbGVhciA9IGZ1bmN0aW9uKCkge1xuICAgIHRoaXMuX3F1ZXVlID0gW107XG59O1xuR2xpclF1ZXVlLnByb3RvdHlwZS5hcHBlbmQgPSBmdW5jdGlvbihlKSB7XG4gICAgdGhpcy5fcXVldWUucHVzaChlKTtcbn07XG5HbGlyUXVldWUucHJvdG90eXBlLmFwcGVuZF9tdWx0aSA9IGZ1bmN0aW9uKGVzKSB7XG4gICAgZm9yICh2YXIgaSA9IDA7IGkgPCBlcy5sZW5ndGg7IGkrKykge1xuICAgICAgICB0aGlzLl9xdWV1ZS5wdXNoKGVzW2ldKTtcbiAgICB9XG59O1xuR2xpclF1ZXVlLnByb3RvdHlwZS5nZXQgPSBmdW5jdGlvbigpIHtcbiAgICByZXR1cm4gdGhpcy5fcXVldWU7XG59O1xuT2JqZWN0LmRlZmluZVByb3BlcnR5KEdsaXJRdWV1ZS5wcm90b3R5cGUsIFwibGVuZ3RoXCIsIHtcbiAgICBnZXQ6IGZ1bmN0aW9uKCkgeyByZXR1cm4gdGhpcy5fcXVldWUubGVuZ3RoOyB9LFxufSk7XG5cblxuLyogVmlzcHkgY2FudmFzIEdMSVIgbWV0aG9kcyAqL1xuVmlzcHlDYW52YXMucHJvdG90eXBlLnNldF9kZWZlcnJlZCA9IGZ1bmN0aW9uKGRlZmVycmVkKSB7XG4gICAgdGhpcy5fZGVmZXJyZWQgPSBkZWZlcnJlZDtcbn07XG5cblZpc3B5Q2FudmFzLnByb3RvdHlwZS5leGVjdXRlX3BlbmRpbmdfY29tbWFuZHMgPSBmdW5jdGlvbigpIHtcbiAgICAvKiBSZXR1cm4gdGhlIG51bWJlciBvZiBleGVjdXRlZCBHTElSIGNvbW1hbmRzLiAqL1xuICAgIHZhciBxID0gdGhpcy5nbGlyX3F1ZXVlLmdldCgpO1xuICAgIHZhciBleGVjdXRlX3VwX3RvID0gLTE7XG4gICAgaWYgKHEubGVuZ3RoID09IDApIHtcbiAgICAgICAgcmV0dXJuIDA7XG4gICAgfVxuXG4gICAgLy8gT25seSBzdGFydCBleGVjdXRpbmcgaWYgd2Ugc2VlIGEgU1dBUCBjb21tYW5kXG4gICAgLy8gQW55ICdkcmF3JyBjb21tYW5kIChjbGVhciwgZHJhdywgZXRjKSB3aWxsIGNhdXNlIHRoZSBicm93c2VyIHRvXG4gICAgLy8gc3dhcCB0aGUgd2ViZ2wgZHJhd2luZyBidWZmZXJzLiBJZiB3ZSBzdGFydCBleGVjdXRpbmcgZHJhdyBjb21tYW5kc1xuICAgIC8vIGJlZm9yZSB3ZSBhcmUgcmVhZHkgZm9yIHRoZSBidWZmZXJzIHRvIHN3YXAgd2UgY291bGQgZ2V0IGFuIGluY29tcGxldGVcbiAgICAvLyBjYW52YXMgKG9ubHkgJ2NsZWFyJyBiZWluZyBjb21wbGV0ZWQsIGxlc3MgdGhhbiBhbGwgb2YgdGhlXG4gICAgLy8gZXhwZWN0ZWQgb2JqZWN0cyBiZWluZyBkcmF3biwgZXRjKS5cbiAgICAvLyBUaGlzIHRlY2huaWNhbGx5IG9ubHkgaGFwcGVucyBpZiBub3QgYWxsIHRoZSBHTElSIGNvbW1hbmRzIHdlcmVcbiAgICAvLyByZWNlaXZlZCBieSB0aGUgdGltZSB0aGlzIGFuaW1hdGlvbiBsb29wIHN0YXJ0ZWQuXG4gICAgZm9yICh2YXIgaSA9IDA7IGkgPCBxLmxlbmd0aDsgaSsrKSB7XG4gICAgICAgIGlmIChxW2ldWzBdID09PSAnU1dBUCcpIHtcbiAgICAgICAgICAgIGV4ZWN1dGVfdXBfdG8gPSBpO1xuICAgICAgICAgICAgYnJlYWs7XG4gICAgICAgIH1cbiAgICB9XG4gICAgLy8gRXhlY3V0ZSBhbGwgY29tbWFuZHMgdXAgdG8gYW5kIGluY2x1ZGluZyB0aGUgU1dBUFxuICAgIGZvciAoaSA9IDA7IGkgPD0gZXhlY3V0ZV91cF90bzsgaSsrKSB7XG4gICAgICAgIHRoaXMuY29tbWFuZChxW2ldLCBmYWxzZSk7XG4gICAgfVxuXG4gICAgaWYgKGV4ZWN1dGVfdXBfdG8gPj0gMCkge1xuICAgICAgICBkZWJ1ZyhcIlByb2Nlc3NlZCB7MH0gZXZlbnRzLlwiLmZvcm1hdChleGVjdXRlX3VwX3RvICsgMSkpO1xuICAgICAgICAvLyB0aGlzLmdsaXJfcXVldWUuY2xlYXIoKTtcbiAgICAgICAgdGhpcy5nbGlyX3F1ZXVlLl9xdWV1ZSA9IHRoaXMuZ2xpcl9xdWV1ZS5fcXVldWUuc2xpY2UoZXhlY3V0ZV91cF90byArIDEpO1xuICAgIH1cbiAgICByZXR1cm4gZXhlY3V0ZV91cF90byArIDE7XG59O1xuXG5WaXNweUNhbnZhcy5wcm90b3R5cGUuY29tbWFuZCA9IGZ1bmN0aW9uKGNvbW1hbmQsIGRlZmVycmVkKSB7XG4gICAgaWYgKGRlZmVycmVkID09PSB1bmRlZmluZWQpIHtcbiAgICAgICAgZGVmZXJyZWQgPSB0aGlzLl9kZWZlcnJlZDtcbiAgICB9XG4gICAgdmFyIG1ldGhvZCA9IGNvbW1hbmRbMF0udG9Mb3dlckNhc2UoKTtcbiAgICBpZiAoZGVmZXJyZWQpIHtcbiAgICAgICAgdGhpcy5nbGlyX3F1ZXVlLmFwcGVuZChjb21tYW5kKTtcbiAgICB9XG4gICAgZWxzZSB7XG4gICAgICAgIHRoaXMuZ2xpclttZXRob2RdKHRoaXMsIGNvbW1hbmQuc2xpY2UoMSkpO1xuICAgIH1cbn07XG5cblxuLyogQ3JlYXRpb24gb2YgdmlzcHkuZ2xvby5nbGlyICovXG52YXIgZ2xpciA9IGZ1bmN0aW9uKCkgeyB9O1xuXG5nbGlyLnByb3RvdHlwZS5pbml0ID0gZnVuY3Rpb24oYykge1xuICAgIC8vIE5hbWVzcGFjZSB3aXRoIHRoZSB0YWJsZSBvZiBhbGwgc3ltYm9scyB1c2VkIGJ5IEdMSVIuXG5cbiAgICAvLyBUaGUga2V5IGlzIHVzZXItc3BlY2lmaWVkIGFuZCBpcyBuYW1lZCB0aGUgKippZCoqLlxuICAgIC8vIFRoZSBXZWJHTCBpbnRlcm5hbCBoYW5kbGUgaXMgY2FsbGVkIHRoZSAqKmhhbmRsZSoqLlxuXG4gICAgLy8gRm9yIGVhY2ggaWQga2V5LCB0aGUgdmFsdWUgaXMgYW4gb2JqZWN0IHdpdGggdGhlIGZvbGxvd2luZyBwcm9wZXJ0aWVzOlxuICAgIC8vICogb2JqZWN0X3R5cGUgKCdWZXJ0ZXhCdWZmZXInLCAnUHJvZ3JhbScsIGV0Yy4pXG4gICAgLy8gKiBoYW5kbGUgKHRoZSBXZWJHTCBpbnRlcm5hbCBoYW5kbGUsIGZvciBhbGwgb2JqZWN0cylcbiAgICAvLyAqIGRhdGFfdHlwZSAoZm9yIEJ1ZmZlcnMpXG4gICAgLy8gKiBvZmZzZXQgKGZvciBCdWZmZXJzKVxuICAgIC8vICogYXR0cmlidXRlcyAoZm9yIFByb2dyYW1zKVxuICAgIC8vICogdW5pZm9ybXMgKGZvciBQcm9ncmFtcylcbiAgICBjLl9ucyA9IHt9O1xuICAgIC8vIERlZmVycmVkIG1vZGUgaXMgZW5hYmxlZCBieSBkZWZhdWx0LlxuICAgIGMuX2RlZmVycmVkID0gdHJ1ZTtcbiAgICAvLyBQZXItY29udGV4dCBzdG9yYWdlIGZvciBHTElSIG9iamVjdHMgKGZyYW1lYnVmZmVyIHN0YWNrLCBldGMpXG4gICAgaW5pdF9lbnZfY2FjaGUoYyk7XG4gICAgYy5nbGlyX3F1ZXVlID0gbmV3IEdsaXJRdWV1ZSgpO1xuICAgIGMuZ2xpciA9IHRoaXM7XG59O1xuXG5nbGlyLnByb3RvdHlwZS5jdXJyZW50ID0gZnVuY3Rpb24oYywgYXJncykge1xuICAgIGluaXRfZW52X2NhY2hlKGMpO1xuICAgIGMuZ2wuYmluZEZyYW1lYnVmZmVyKGMuZ2wuRlJBTUVCVUZGRVIsIG51bGwpO1xufTtcblxuZ2xpci5wcm90b3R5cGUuc3dhcCA9IGZ1bmN0aW9uKGMsIGFyZ3MpIHtcblxufTtcblxuZ2xpci5wcm90b3R5cGUuY3JlYXRlID0gZnVuY3Rpb24oYywgYXJncykge1xuICAgIHZhciBpZCA9IGFyZ3NbMF07XG4gICAgdmFyIGNscyA9IGFyZ3NbMV07XG4gICAgaWYgKGNscyA9PSAnVmVydGV4QnVmZmVyJykge1xuICAgICAgICBkZWJ1ZyhcIkNyZWF0aW5nIHZlcnRleCBidWZmZXIgJ3swfScuXCIuZm9ybWF0KGlkKSk7XG4gICAgICAgIGMuX25zW2lkXSA9IHtcbiAgICAgICAgICAgIG9iamVjdF90eXBlOiBjbHMsXG4gICAgICAgICAgICBoYW5kbGU6IGMuZ2wuY3JlYXRlQnVmZmVyKCksXG4gICAgICAgICAgICBzaXplOiAwLCAgLy8gY3VycmVudCBzaXplIG9mIHRoZSBidWZmZXJcbiAgICAgICAgfTtcbiAgICB9XG4gICAgZWxzZSBpZiAoY2xzID09ICdJbmRleEJ1ZmZlcicpIHtcbiAgICAgICAgZGVidWcoXCJDcmVhdGluZyBpbmRleCBidWZmZXIgJ3swfScuXCIuZm9ybWF0KGlkKSk7XG4gICAgICAgIGMuX25zW2lkXSA9IHtcbiAgICAgICAgICAgIG9iamVjdF90eXBlOiBjbHMsXG4gICAgICAgICAgICBoYW5kbGU6IGMuZ2wuY3JlYXRlQnVmZmVyKCksXG4gICAgICAgICAgICBzaXplOiAwLCAgLy8gY3VycmVudCBzaXplIG9mIHRoZSBidWZmZXJcbiAgICAgICAgfTtcbiAgICB9XG4gICAgZWxzZSBpZiAoY2xzID09ICdGcmFtZUJ1ZmZlcicpIHtcbiAgICAgICAgZGVidWcoXCJDcmVhdGluZyBmcmFtZSBidWZmZXIgJ3swfScuXCIuZm9ybWF0KGlkKSk7XG4gICAgICAgIGMuX25zW2lkXSA9IHtcbiAgICAgICAgICAgIG9iamVjdF90eXBlOiBjbHMsXG4gICAgICAgICAgICBoYW5kbGU6IGMuZ2wuY3JlYXRlRnJhbWVidWZmZXIoKSxcbiAgICAgICAgICAgIHNpemU6IDAsICAvLyBjdXJyZW50IHNpemUgb2YgdGhlIGJ1ZmZlclxuICAgICAgICAgICAgdmFsaWRhdGVkOiBmYWxzZSxcbiAgICAgICAgfTtcbiAgICB9XG4gICAgZWxzZSBpZiAoY2xzID09ICdSZW5kZXJCdWZmZXInKSB7XG4gICAgICAgIGRlYnVnKFwiQ3JlYXRpbmcgcmVuZGVyIGJ1ZmZlciAnezB9Jy5cIi5mb3JtYXQoaWQpKTtcbiAgICAgICAgYy5fbnNbaWRdID0ge1xuICAgICAgICAgICAgb2JqZWN0X3R5cGU6IGNscyxcbiAgICAgICAgICAgIGhhbmRsZTogYy5nbC5jcmVhdGVSZW5kZXJidWZmZXIoKSxcbiAgICAgICAgICAgIHNpemU6IDAsICAvLyBjdXJyZW50IHNpemUgb2YgdGhlIGJ1ZmZlclxuICAgICAgICB9O1xuICAgIH1cbiAgICBlbHNlIGlmIChjbHMgPT0gJ1RleHR1cmUyRCcpIHtcbiAgICAgICAgZGVidWcoXCJDcmVhdGluZyB0ZXh0dXJlICd7MH0nLlwiLmZvcm1hdChpZCkpO1xuICAgICAgICBjLl9uc1tpZF0gPSB7XG4gICAgICAgICAgICBvYmplY3RfdHlwZTogY2xzLFxuICAgICAgICAgICAgaGFuZGxlOiBjLmdsLmNyZWF0ZVRleHR1cmUoKSxcbiAgICAgICAgICAgIHNpemU6IDAsICAvLyBjdXJyZW50IHNpemUgb2YgdGhlIHRleHR1cmVcbiAgICAgICAgICAgIHNoYXBlOiBbXSxcbiAgICAgICAgfTtcbiAgICB9XG4gICAgZWxzZSBpZiAoY2xzID09ICdQcm9ncmFtJykge1xuICAgICAgICBkZWJ1ZyhcIkNyZWF0aW5nIHByb2dyYW0gJ3swfScuXCIuZm9ybWF0KGlkKSk7XG4gICAgICAgIGMuX25zW2lkXSA9IHtcbiAgICAgICAgICAgIG9iamVjdF90eXBlOiBjbHMsXG4gICAgICAgICAgICBoYW5kbGU6IGMuZ2wuY3JlYXRlUHJvZ3JhbSgpLFxuICAgICAgICAgICAgYXR0cmlidXRlczoge30sXG4gICAgICAgICAgICB1bmlmb3Jtczoge30sXG4gICAgICAgICAgICB0ZXh0dXJlczoge30sIC8vIG1hcCB0ZXh0dXJlX2lkIC0+IHNhbXBsZXJfbmFtZSwgc2FtcGxlcl9oYW5kbGUsIG51bWJlciwgaGFuZGxlXG4gICAgICAgICAgICB0ZXh0dXJlX3VuaWZvcm1zOiB7fSwgLy8gbWFwIHNhbXBsZXJfbmFtZSAtPiB0ZXh0dXJlX2lkXG4gICAgICAgIH07XG4gICAgfVxuICAgIGVsc2UgaWYgKGNscyA9PSAnVmVydGV4U2hhZGVyJykge1xuICAgICAgICBkZWJ1ZyhcIkNyZWF0aW5nIFZlcnRleFNoYWRlciAnezB9Jy5cIi5mb3JtYXQoaWQpKTtcbiAgICAgICAgYy5fbnNbaWRdID0ge1xuICAgICAgICAgICAgb2JqZWN0X3R5cGU6IGNscyxcbiAgICAgICAgICAgIGhhbmRsZTogYy5nbC5jcmVhdGVTaGFkZXIoYy5nbFsnVkVSVEVYX1NIQURFUiddKSxcbiAgICAgICAgfTtcbiAgICB9XG4gICAgZWxzZSBpZiAoY2xzID09ICdGcmFnbWVudFNoYWRlcicpIHtcbiAgICAgICAgZGVidWcoXCJDcmVhdGluZyBGcmFnbWVudFNoYWRlciAnezB9Jy5cIi5mb3JtYXQoaWQpKTtcbiAgICAgICAgYy5fbnNbaWRdID0ge1xuICAgICAgICAgICAgb2JqZWN0X3R5cGU6IGNscyxcbiAgICAgICAgICAgIGhhbmRsZTogYy5nbC5jcmVhdGVTaGFkZXIoYy5nbFsnRlJBR01FTlRfU0hBREVSJ10pLFxuICAgICAgICB9O1xuICAgIH1cbn07XG5cbmdsaXIucHJvdG90eXBlLmRlbGV0ZSA9IGZ1bmN0aW9uKGMsIGFyZ3MpIHtcbiAgICB2YXIgaWQgPSBhcmdzWzBdO1xuICAgIHZhciBjbHMgPSBjLl9uc1tpZF0ub2JqZWN0X3R5cGU7XG4gICAgdmFyIGhhbmRsZSA9IGMuX25zW2lkXS5oYW5kbGU7XG4gICAgYy5fbnNbaWRdLmhhbmRsZSA9IEpVU1RfREVMRVRFRDtcbiAgICBpZiAoY2xzID09ICdWZXJ0ZXhCdWZmZXInKSB7XG4gICAgICAgIGRlYnVnKFwiRGVsZXRpbmcgdmVydGV4IGJ1ZmZlciAnezB9Jy5cIi5mb3JtYXQoaWQpKTtcbiAgICAgICAgYy5nbC5kZWxldGVCdWZmZXIoaGFuZGxlKTtcbiAgICB9XG4gICAgZWxzZSBpZiAoY2xzID09ICdJbmRleEJ1ZmZlcicpIHtcbiAgICAgICAgZGVidWcoXCJEZWxldGluZyBpbmRleCBidWZmZXIgJ3swfScuXCIuZm9ybWF0KGlkKSk7XG4gICAgICAgIGMuZ2wuZGVsZXRlQnVmZmVyKGhhbmRsZSk7XG4gICAgfVxuICAgIGVsc2UgaWYgKGNscyA9PSAnRnJhbWVCdWZmZXInKSB7XG4gICAgICAgIGRlYnVnKFwiRGVsZXRpbmcgZnJhbWUgYnVmZmVyICd7MH0nLlwiLmZvcm1hdChpZCkpO1xuICAgICAgICBjLmdsLmRlbGV0ZUZyYW1lYnVmZmVyKGhhbmRsZSk7XG4gICAgfVxuICAgIGVsc2UgaWYgKGNscyA9PSAnUmVuZGVyQnVmZmVyJykge1xuICAgICAgICBkZWJ1ZyhcIkRlbGV0aW5nIHJlbmRlciBidWZmZXIgJ3swfScuXCIuZm9ybWF0KGlkKSk7XG4gICAgICAgIGMuZ2wuZGVsZXRlUmVuZGVyYnVmZmVyKGhhbmRsZSk7XG4gICAgfVxuICAgIGVsc2UgaWYgKGNscyA9PSAnVGV4dHVyZTJEJykge1xuICAgICAgICBkZWJ1ZyhcIkRlbGV0aW5nIHRleHR1cmUgJ3swfScuXCIuZm9ybWF0KGlkKSk7XG4gICAgICAgIGMuZ2wuZGVsZXRlVGV4dHVyZShoYW5kbGUpO1xuICAgIH1cbiAgICBlbHNlIGlmIChjbHMgPT0gJ1Byb2dyYW0nKSB7XG4gICAgICAgIGRlYnVnKFwiRGVsZXRpbmcgcHJvZ3JhbSAnezB9Jy5cIi5mb3JtYXQoaWQpKTtcbiAgICAgICAgYy5nbC5kZWxldGVQcm9ncmFtKGhhbmRsZSk7XG4gICAgfVxuICAgIGVsc2UgaWYgKGNscy5pbmRleE9mKCdTaGFkZXInKSA+PSAwKSB7XG4gICAgICAgIGRlYnVnKFwiRGVsZXRpbmcgc2hhZGVyICd7MH0nLlwiLmZvcm1hdChpZCkpO1xuICAgICAgICBjLmdsLmRlbGV0ZVNoYWRlcihoYW5kbGUpO1xuICAgIH1cbn07XG5cbmdsaXIucHJvdG90eXBlLnNpemUgPSBmdW5jdGlvbihjLCBhcmdzKSB7XG4gICAgdmFyIG9iamVjdF9pZCA9IGFyZ3NbMF07XG4gICAgdmFyIHNpemUgPSBhcmdzWzFdOyAgLy8gV0FSTklORzogc2l6ZSBtdXN0IGJlIGluIGJ5dGVzIVxuICAgIHZhciBmb3JtYXQgPSBhcmdzWzJdO1xuICAgIHZhciBvYmplY3QgPSBjLl9uc1tvYmplY3RfaWRdO1xuICAgIHZhciBvYmplY3RfaGFuZGxlID0gb2JqZWN0LmhhbmRsZTtcbiAgICB2YXIgb2JqZWN0X3R5cGUgPSBvYmplY3Qub2JqZWN0X3R5cGU7XG4gICAgdmFyIGdsX3R5cGUgPSBjLmdsW2dldF9nbF90eXBlKG9iamVjdF90eXBlKV07XG5cbiAgICAvLyBUZXh0dXJlcy5cbiAgICBpZiAob2JqZWN0X3R5cGUuaW5kZXhPZignVGV4dHVyZScpID49IDApIHtcbiAgICAgICAgLy8gZm9ybWF0IGlzICdMVU1JTkFOQ0UnLCAnQUxQSEEnLCAnTFVNSU5BTkNFX0FMUEhBJywgJ1JHQicgb3IgJ1JHQkEnXG4gICAgICAgIG9iamVjdC5mb3JtYXQgPSBmb3JtYXQudG9VcHBlckNhc2UoKTtcbiAgICAgICAgZGVidWcoXCJTZXR0aW5nIHRleHR1cmUgc2l6ZSB0byB7MX0gZm9yICd7MH0nLlwiLmZvcm1hdChvYmplY3RfaWQsIHNpemUpKTtcbiAgICAgICAgLy8gSEFDSzogaXQgZG9lc24ndCBzZWVtIHdlIGNhbiBjaGFuZ2UgdGhlIHRleHR1cmUgc2l6ZSB3aXRob3V0XG4gICAgICAgIC8vIGFsbG9jYXRpbmcgYSBidWZmZXIgaW4gV2ViR0wsIHNvIHdlIGp1c3Qgc3RvcmUgdGhlIHNpemUgYW5kXG4gICAgICAgIC8vIGZvcm1hdCBpbiB0aGUgb2JqZWN0LCBhbmQgd2UnbGwgdXNlIHRoaXMgaW5mb3JtYXRpb24gaW4gdGhlXG4gICAgICAgIC8vIHN1YnNlcXVlbnQgREFUQSBjYWxsLlxuICAgIH1cbiAgICBlbHNlIGlmIChvYmplY3RfdHlwZSA9PSAnUmVuZGVyQnVmZmVyJykge1xuICAgICAgICBjLmdsLmJpbmRSZW5kZXJidWZmZXIoYy5nbC5SRU5ERVJCVUZGRVIsIG9iamVjdF9oYW5kbGUpO1xuICAgICAgICBvYmplY3QuZm9ybWF0ID0gYy5nbFtnZXRfYXR0YWNobWVudF9mb3JtYXQoZm9ybWF0KV07XG4gICAgICAgIC8vIHNpemUgaXMgWSwgWCwgWlxuICAgICAgICAvLyBhc3N1bWUgWSBpcyByb3dzIChoZWlnaHQpLCBYIGlzIGNvbHVtbnMgKHdpZHRoKVxuICAgICAgICAvLyBhc3N1bWUgWiBpcyBjb2xvciBpbmZvcm1hdGlvbiAoaWdub3JlZClcbiAgICAgICAgYy5nbC5yZW5kZXJidWZmZXJTdG9yYWdlKGMuZ2wuUkVOREVSQlVGRkVSLCBvYmplY3QuZm9ybWF0LCBzaXplWzFdLCBzaXplWzBdKTtcbiAgICAgICAgYy5nbC5iaW5kUmVuZGVyYnVmZmVyKGMuZ2wuUkVOREVSQlVGRkVSLCBudWxsKTtcbiAgICB9XG4gICAgLy8gQnVmZmVyc1xuICAgIGVsc2VcbiAgICB7XG4gICAgICAgIGRlYnVnKFwiU2V0dGluZyBidWZmZXIgc2l6ZSB0byB7MX0gZm9yICd7MH0nLlwiLmZvcm1hdChvYmplY3RfaWQsIHNpemUpKTtcbiAgICAgICAgLy8gUmV1c2UgdGhlIGJ1ZmZlciBpZiB0aGUgZXhpc3Rpbmcgc2l6ZSBpcyBub3QgbnVsbC5cbiAgICAgICAgc2V0X2J1ZmZlcl9kYXRhKGMsIG9iamVjdF9oYW5kbGUsIGdsX3R5cGUsIDAsIHNpemUsIGZhbHNlKTtcbiAgICB9XG4gICAgLy8gU2F2ZSB0aGUgc2l6ZS5cbiAgICBvYmplY3Quc2l6ZSA9IHNpemU7XG59O1xuXG5nbGlyLnByb3RvdHlwZS5kYXRhID0gZnVuY3Rpb24oYywgYXJncykge1xuICAgIHZhciBvYmplY3RfaWQgPSBhcmdzWzBdO1xuICAgIHZhciBvZmZzZXQgPSBhcmdzWzFdO1xuICAgIHZhciBkYXRhID0gYXJnc1syXTtcbiAgICB2YXIgb2JqZWN0ID0gYy5fbnNbb2JqZWN0X2lkXTtcbiAgICB2YXIgb2JqZWN0X3R5cGUgPSBvYmplY3Qub2JqZWN0X3R5cGU7IC8vIFZlcnRleEJ1ZmZlciwgSW5kZXhCdWZmZXIsIG9yIFRleHR1cmUyRFxuICAgIHZhciBvYmplY3RfaGFuZGxlID0gb2JqZWN0LmhhbmRsZTtcbiAgICB2YXIgZ2xfdHlwZSA9IGMuZ2xbZ2V0X2dsX3R5cGUob2JqZWN0X3R5cGUpXTtcbiAgICAvLyBHZXQgYSBUeXBlZEFycmF5LlxuICAgIHZhciBhcnJheSA9IHRvX2FycmF5X2J1ZmZlcihkYXRhKTtcblxuICAgIGlmIChvYmplY3RfdHlwZS5pbmRleE9mKCdTaGFkZXInKSA+PSAwKSB7XG4gICAgICAgIC8vIENvbXBpbGUgc2hhZGVyIGNvZGUgdG8gc2hhZGVyIG9iamVjdFxuICAgICAgICBjb21waWxlX3NoYWRlcihjLCBvYmplY3RfaGFuZGxlLCBhcnJheSk7XG4gICAgfVxuICAgIC8vIFRleHR1cmVzLlxuICAgIGVsc2UgaWYgKG9iamVjdF90eXBlLmluZGV4T2YoJ1RleHR1cmUnKSA+PSAwKSB7XG4gICAgICAgIC8vIFRoZSB0ZXh0dXJlIHNoYXBlIHdhcyBzcGVjaWZpZWQgaW4gU0laRVxuICAgICAgICB2YXIgc2hhcGUgPSBvYmplY3Quc2l6ZTtcbiAgICAgICAgLy8gV0FSTklORzogdGhpcyBpcyBoZWlnaHQgYW5kIHRoZW4gd2lkdGgsIG5vdCB0aGUgb3RoZXIgd2F5XG4gICAgICAgIC8vIGFyb3VuZC5cbiAgICAgICAgdmFyIGhlaWdodCA9IHNoYXBlWzBdO1xuICAgICAgICB2YXIgd2lkdGggPSBzaGFwZVsxXTtcblxuICAgICAgICAvLyBUaGUgdGV4dHVyZSBmb3JtYXQgd2FzIHNwZWNpZmllZCBpbiBTSVpFLlxuICAgICAgICB2YXIgZm9ybWF0ID0gYy5nbFtvYmplY3QuZm9ybWF0XTtcblxuICAgICAgICBkZWJ1ZyhcIlNldHRpbmcgdGV4dHVyZSBkYXRhIGZvciAnezB9Jy5cIi5mb3JtYXQob2JqZWN0X2lkKSk7XG4gICAgICAgIC8vIGBkYXRhLnNoYXBlYCBjb21lcyBmcm9tIG5vdGVib29rIGJhY2tlbmQgYW5kIHZpc3B5IHdlYmdsIGV4dGVuc2lvblxuICAgICAgICAvLyB3aXRob3V0IGl0LCBzdWJpbWFnZSB0ZXh0dXJlIHdyaXRlcyBkbyBub3Qgd29ya1xuICAgICAgICB2YXIgZ2xfZHR5cGUgPSBjLmdsW2dldF9nbF9kdHlwZShkYXRhLmR0eXBlKV07XG4gICAgICAgIHNldF90ZXh0dXJlX2RhdGEoYywgb2JqZWN0X2hhbmRsZSwgZ2xfdHlwZSwgZm9ybWF0LCB3aWR0aCwgaGVpZ2h0LCBhcnJheSwgb2Zmc2V0LCBkYXRhLnNoYXBlLCBnbF9kdHlwZSk7XG4gICAgICAgIG9iamVjdC5zaGFwZSA9IHNoYXBlO1xuICAgIH1cbiAgICAvLyBCdWZmZXJzXG4gICAgZWxzZVxuICAgIHtcbiAgICAgICAgZGVidWcoXCJTZXR0aW5nIGJ1ZmZlciBkYXRhIGZvciAnezB9Jy5cIi5mb3JtYXQob2JqZWN0X2lkKSk7XG4gICAgICAgIC8vIFJldXNlIHRoZSBidWZmZXIgaWYgdGhlIGV4aXN0aW5nIHNpemUgaXMgbm90IG51bGwuXG4gICAgICAgIHNldF9idWZmZXJfZGF0YShjLCBvYmplY3RfaGFuZGxlLCBnbF90eXBlLCBvZmZzZXQsIGFycmF5LCBvYmplY3Quc2l6ZSA+IDApO1xuICAgICAgICBvYmplY3Quc2l6ZSA9IGFycmF5LmJ5dGVMZW5ndGg7XG4gICAgfVxufTtcblxuZ2xpci5wcm90b3R5cGUuYXR0cmlidXRlID0gZnVuY3Rpb24oYywgYXJncykge1xuICAgIHZhciBwcm9ncmFtX2lkID0gYXJnc1swXTtcbiAgICB2YXIgbmFtZSA9IGFyZ3NbMV07XG4gICAgdmFyIHR5cGUgPSBhcmdzWzJdO1xuICAgIC8vIFRPRE86IHN1cHBvcnQgbm9uLVZCTyBkYXRhXG4gICAgdmFyIHZib19pZCA9IGFyZ3NbM11bMF07XG4gICAgdmFyIHN0cmlkZSA9IGFyZ3NbM11bMV07XG4gICAgdmFyIG9mZnNldCA9IGFyZ3NbM11bMl07XG5cbiAgICB2YXIgcHJvZ3JhbV9oYW5kbGUgPSBjLl9uc1twcm9ncmFtX2lkXS5oYW5kbGU7XG5cbiAgICBkZWJ1ZyhcIkNyZWF0aW5nIGF0dHJpYnV0ZSAnezB9JyBmb3IgcHJvZ3JhbSAnezF9Jy5cIi5mb3JtYXQoXG4gICAgICAgICAgICBuYW1lLCBwcm9ncmFtX2lkXG4gICAgICAgICkpO1xuICAgIHZhciBhdHRyaWJ1dGVfaGFuZGxlID0gY3JlYXRlX2F0dHJpYnV0ZShjLCBwcm9ncmFtX2hhbmRsZSwgbmFtZSk7XG5cbiAgICAvLyBTdG9yZSB0aGUgYXR0cmlidXRlIGhhbmRsZSBpbiB0aGUgYXR0cmlidXRlcyBhcnJheSBvZiB0aGUgcHJvZ3JhbS5cbiAgICBjLl9uc1twcm9ncmFtX2lkXS5hdHRyaWJ1dGVzW25hbWVdID0ge1xuICAgICAgICBoYW5kbGU6IGF0dHJpYnV0ZV9oYW5kbGUsXG4gICAgICAgIHR5cGU6IHR5cGUsXG4gICAgICAgIHZib19pZDogdmJvX2lkLFxuICAgICAgICBzdHJpZGU6IHN0cmlkZSxcbiAgICAgICAgb2Zmc2V0OiBvZmZzZXQsXG4gICAgfTtcbn07XG5cbmdsaXIucHJvdG90eXBlLnVuaWZvcm0gPSBmdW5jdGlvbihjLCBhcmdzKSB7XG4gICAgdmFyIHByb2dyYW1faWQgPSBhcmdzWzBdO1xuICAgIHZhciBuYW1lID0gYXJnc1sxXTtcbiAgICB2YXIgdHlwZSA9IGFyZ3NbMl07XG4gICAgdmFyIHZhbHVlID0gYXJnc1szXTtcblxuICAgIHZhciBwcm9ncmFtX2hhbmRsZSA9IGMuX25zW3Byb2dyYW1faWRdLmhhbmRsZTtcblxuICAgIGMuZ2wudXNlUHJvZ3JhbShwcm9ncmFtX2hhbmRsZSk7XG5cbiAgICAvLyBDaGVjayB0aGUgY2FjaGUuXG4gICAgaWYgKGMuX25zW3Byb2dyYW1faWRdLnVuaWZvcm1zW25hbWVdID09IHVuZGVmaW5lZCkge1xuICAgICAgICAvLyBJZiBuZWNlc3NhcnksIHdlIGNyZWF0ZSB0aGUgdW5pZm9ybSBhbmQgY2FjaGUgYm90aCBpdHMgaGFuZGxlIGFuZFxuICAgICAgICAvLyBHTCBmdW5jdGlvbi5cbiAgICAgICAgZGVidWcoXCJDcmVhdGluZyB1bmlmb3JtICd7MH0nIGZvciBwcm9ncmFtICd7MX0nLlwiLmZvcm1hdChcbiAgICAgICAgICAgICAgICBuYW1lLCBwcm9ncmFtX2lkXG4gICAgICAgICAgICApKTtcbiAgICAgICAgdmFyIHVuaWZvcm1faGFuZGxlID0gYy5nbC5nZXRVbmlmb3JtTG9jYXRpb24ocHJvZ3JhbV9oYW5kbGUsIG5hbWUpO1xuICAgICAgICB2YXIgdW5pZm9ybV9mdW5jdGlvbiA9IGdldF91bmlmb3JtX2Z1bmN0aW9uKHR5cGUpO1xuICAgICAgICAvLyBXZSBjYWNoZSB0aGUgdW5pZm9ybSBoYW5kbGUgYW5kIHRoZSB1bmlmb3JtIGZ1bmN0aW9uIG5hbWUgYXMgd2VsbC5cbiAgICAgICAgYy5fbnNbcHJvZ3JhbV9pZF0udW5pZm9ybXNbbmFtZV0gPSBbdW5pZm9ybV9oYW5kbGUsIHVuaWZvcm1fZnVuY3Rpb25dO1xuICAgIH1cblxuICAgIGRlYnVnKFwiU2V0dGluZyB1bmlmb3JtICd7MH0nIHRvICd7MX0nIHdpdGggezJ9IGVsZW1lbnRzLlwiLmZvcm1hdChcbiAgICAgICAgICAgIG5hbWUsIHZhbHVlLCB2YWx1ZS5sZW5ndGhcbiAgICAgICAgKSk7XG4gICAgdmFyIHVuaWZvcm1faW5mbyA9IGMuX25zW3Byb2dyYW1faWRdLnVuaWZvcm1zW25hbWVdO1xuICAgIHZhciB1bmlmb3JtX2hhbmRsZSA9IHVuaWZvcm1faW5mb1swXTtcbiAgICB2YXIgdW5pZm9ybV9mdW5jdGlvbiA9IHVuaWZvcm1faW5mb1sxXTtcbiAgICBzZXRfdW5pZm9ybShjLCB1bmlmb3JtX2hhbmRsZSwgdW5pZm9ybV9mdW5jdGlvbiwgdmFsdWUpO1xufTtcblxuZ2xpci5wcm90b3R5cGUudGV4dHVyZSA9IGZ1bmN0aW9uKGMsIGFyZ3MpIHtcbiAgICB2YXIgcHJvZ3JhbV9pZCA9IGFyZ3NbMF07XG4gICAgdmFyIHNhbXBsZXJfbmFtZSA9IGFyZ3NbMV07XG4gICAgdmFyIHRleHR1cmVfaWQgPSBhcmdzWzJdO1xuXG4gICAgdmFyIHByb2dyYW0gPSBjLl9uc1twcm9ncmFtX2lkXTtcbiAgICB2YXIgcHJvZ3JhbV9oYW5kbGUgPSBwcm9ncmFtLmhhbmRsZTtcbiAgICB2YXIgdGV4dHVyZV9oYW5kbGUgPSBjLl9uc1t0ZXh0dXJlX2lkXS5oYW5kbGU7XG5cbiAgICBpZiAodGV4dHVyZV9oYW5kbGUgPT09IEpVU1RfREVMRVRFRCkge1xuICAgICAgICBkZWJ1ZyhcIlJlbW92aW5nIHRleHR1cmUgJ3swfScgZnJvbSBwcm9ncmFtICd7MX0nXCIuZm9ybWF0KFxuICAgICAgICAgICAgdGV4dHVyZV9pZCwgcHJvZ3JhbV9pZFxuICAgICAgICApKTtcbiAgICAgICAgZGVsZXRlIHByb2dyYW0udGV4dHVyZXNbdGV4dHVyZV9pZF07XG4gICAgICAgIHJldHVybjtcbiAgICB9XG5cbiAgICBkZWJ1ZyhcIkluaXRpYWxpemluZyB0ZXh0dXJlICd7MH0nIGZvciBwcm9ncmFtICd7MX0nLlwiLmZvcm1hdChcbiAgICAgICAgdGV4dHVyZV9pZCwgcHJvZ3JhbV9pZCkpO1xuXG4gICAgLy8gRklYTUU6IFByb2JhYmx5IHNob3VsZCBzdG9yZSB0ZXh0dXJlcyBieSBzYW1wbGVyIG5hbWUsIG5vdCB0ZXh0dXJlIGlkXG4gICAgaWYgKHByb2dyYW0udGV4dHVyZV91bmlmb3Jtcy5oYXNPd25Qcm9wZXJ0eShzYW1wbGVyX25hbWUpKSB7XG4gICAgICAgIC8vIFRoaXMgcHJvZ3JhbSBoYXMgaGFkIHRoaXMgc2FtcGxlciB1bmlmb3JtIG5hbWUgc2V0IGJlZm9yZVxuICAgICAgICAvLyBMZXQncyByZW1vdmUgdGhlIG9sZCBvbmVcbiAgICAgICAgZGVidWcoJ1JlbW92aW5nIHByZXZpb3VzbHkgYXNzaWduZWQgdGV4dHVyZSBmb3IgXFwnezB9XFwnJy5mb3JtYXQoc2FtcGxlcl9uYW1lKSlcbiAgICAgICAgZGVsZXRlIHByb2dyYW0udGV4dHVyZXNbcHJvZ3JhbS50ZXh0dXJlX3VuaWZvcm1zW3NhbXBsZXJfbmFtZV1dO1xuICAgIH1cblxuICAgIC8vIFNldCB0aGUgc2FtcGxlciB1bmlmb3JtIHZhbHVlLlxuICAgIHZhciBzYW1wbGVyX2hhbmRsZSA9IGMuZ2wuZ2V0VW5pZm9ybUxvY2F0aW9uKHByb2dyYW1faGFuZGxlLCBzYW1wbGVyX25hbWUpO1xuICAgIHByb2dyYW0udGV4dHVyZV91bmlmb3Jtc1tzYW1wbGVyX25hbWVdID0gdGV4dHVyZV9pZDtcblxuICAgIGMuX25zW3Byb2dyYW1faWRdLnRleHR1cmVzW3RleHR1cmVfaWRdID0ge1xuICAgICAgICBzYW1wbGVyX25hbWU6IHNhbXBsZXJfbmFtZSxcbiAgICAgICAgc2FtcGxlcl9oYW5kbGU6IHNhbXBsZXJfaGFuZGxlLFxuICAgICAgICBudW1iZXI6IC0xLCAvLyBhc3NpZ25lZCBsYXRlclxuICAgICAgICBoYW5kbGU6IHRleHR1cmVfaGFuZGxlLFxuICAgIH07XG59O1xuXG5nbGlyLnByb3RvdHlwZS5pbnRlcnBvbGF0aW9uID0gZnVuY3Rpb24oYywgYXJncykge1xuICAgIHZhciB0ZXh0dXJlX2lkID0gYXJnc1swXTtcbiAgICB2YXIgbWluID0gYXJnc1sxXS50b1VwcGVyQ2FzZSgpO1xuICAgIHZhciBtYWcgPSBhcmdzWzJdLnRvVXBwZXJDYXNlKCk7XG4gICAgdmFyIHRleHR1cmVfaGFuZGxlID0gYy5fbnNbdGV4dHVyZV9pZF0uaGFuZGxlO1xuXG4gICAgdmFyIGdsX3R5cGUgPSBjLmdsLlRFWFRVUkVfMkQ7XG4gICAgYy5nbC5iaW5kVGV4dHVyZShnbF90eXBlLCB0ZXh0dXJlX2hhbmRsZSk7XG4gICAgYy5nbC50ZXhQYXJhbWV0ZXJpKGdsX3R5cGUsIGMuZ2wuVEVYVFVSRV9NSU5fRklMVEVSLCBjLmdsW21pbl0pO1xuICAgIGMuZ2wudGV4UGFyYW1ldGVyaShnbF90eXBlLCBjLmdsLlRFWFRVUkVfTUFHX0ZJTFRFUiwgYy5nbFttYWddKTtcbiAgICBjLmdsLmJpbmRUZXh0dXJlKGdsX3R5cGUsIG51bGwpO1xufTtcblxuZ2xpci5wcm90b3R5cGUud3JhcHBpbmcgPSBmdW5jdGlvbihjLCBhcmdzKSB7XG4gICAgdmFyIHRleHR1cmVfaWQgPSBhcmdzWzBdO1xuICAgIHZhciB3cmFwcGluZyA9IGFyZ3NbMV07XG4gICAgdmFyIHRleHR1cmVfaGFuZGxlID0gYy5fbnNbdGV4dHVyZV9pZF0uaGFuZGxlO1xuXG4gICAgdmFyIGdsX3R5cGUgPSBjLmdsLlRFWFRVUkVfMkQ7XG4gICAgYy5nbC5iaW5kVGV4dHVyZShnbF90eXBlLCB0ZXh0dXJlX2hhbmRsZSk7XG4gICAgYy5nbC50ZXhQYXJhbWV0ZXJpKGdsX3R5cGUsIGMuZ2wuVEVYVFVSRV9XUkFQX1MsXG4gICAgICAgICAgICAgICAgICAgICAgIGMuZ2xbd3JhcHBpbmdbMF0udG9VcHBlckNhc2UoKV0pO1xuICAgIGMuZ2wudGV4UGFyYW1ldGVyaShnbF90eXBlLCBjLmdsLlRFWFRVUkVfV1JBUF9ULFxuICAgICAgICAgICAgICAgICAgICAgICBjLmdsW3dyYXBwaW5nWzFdLnRvVXBwZXJDYXNlKCldKTtcbiAgICBjLmdsLmJpbmRUZXh0dXJlKGdsX3R5cGUsIG51bGwpO1xufTtcblxuZ2xpci5wcm90b3R5cGUuZHJhdyA9IGZ1bmN0aW9uKGMsIGFyZ3MpIHtcbiAgICB2YXIgcHJvZ3JhbV9pZCA9IGFyZ3NbMF07XG4gICAgdmFyIG1vZGUgPSBhcmdzWzFdLnRvVXBwZXJDYXNlKCk7XG4gICAgdmFyIHNlbGVjdGlvbiA9IGFyZ3NbMl07XG5cbiAgICB2YXIgcHJvZ3JhbV9oYW5kbGUgPSBjLl9uc1twcm9ncmFtX2lkXS5oYW5kbGU7XG4gICAgdmFyIGF0dHJpYnV0ZXMgPSBjLl9uc1twcm9ncmFtX2lkXS5hdHRyaWJ1dGVzO1xuICAgIHZhciB0ZXh0dXJlcyA9IGMuX25zW3Byb2dyYW1faWRdLnRleHR1cmVzO1xuICAgIHZhciB0ZXh0dXJlX251bWJlciA9IDA7XG5cbiAgICAvLyBBY3RpdmF0ZSB0aGUgcHJvZ3JhbS5cbiAgICBjLmdsLnVzZVByb2dyYW0ocHJvZ3JhbV9oYW5kbGUpO1xuXG4gICAgLy8gQWN0aXZhdGUgYWxsIGF0dHJpYnV0ZXMgaW4gdGhlIHByb2dyYW0uXG4gICAgZm9yIChhdHRyaWJ1dGVfbmFtZSBpbiBhdHRyaWJ1dGVzKSB7XG4gICAgICAgIHZhciBhdHRyaWJ1dGUgPSBhdHRyaWJ1dGVzW2F0dHJpYnV0ZV9uYW1lXTtcbiAgICAgICAgZGVidWcoXCJBY3RpdmF0aW5nIGF0dHJpYnV0ZSAnezB9JyBmb3IgcHJvZ3JhbSAnezF9Jy5cIi5mb3JtYXQoXG4gICAgICAgICAgICBhdHRyaWJ1dGVfbmFtZSwgcHJvZ3JhbV9pZCkpO1xuICAgICAgICBhY3RpdmF0ZV9hdHRyaWJ1dGUoYywgYXR0cmlidXRlLmhhbmRsZSwgYXR0cmlidXRlLnZib19pZCxcbiAgICAgICAgICAgIGF0dHJpYnV0ZS50eXBlLCBhdHRyaWJ1dGUuc3RyaWRlLCBhdHRyaWJ1dGUub2Zmc2V0KTtcbiAgICB9XG5cbiAgICAvLyBBY3RpdmF0ZSBhbGwgdGV4dHVyZXMgaW4gdGhlIHByb2dyYW0uXG4gICAgZm9yICh0ZXh0dXJlX2lkIGluIHRleHR1cmVzKSB7XG4gICAgICAgIHZhciB0ZXh0dXJlID0gdGV4dHVyZXNbdGV4dHVyZV9pZF07XG4gICAgICAgIGlmIChjLl9uc1t0ZXh0dXJlX2lkXS5oYW5kbGUgPT09IEpVU1RfREVMRVRFRCkge1xuICAgICAgICAgICAgZGVidWcoXCJJZ25vcmluZyB0ZXh0dXJlICd7MH0nIGZyb20gcHJvZ3JhbSAnezF9J1wiLmZvcm1hdChcbiAgICAgICAgICAgICAgICB0ZXh0dXJlX2lkLCBwcm9ncmFtX2lkXG4gICAgICAgICAgICApKTtcbiAgICAgICAgICAgIHRleHR1cmUuaGFuZGxlID0gSlVTVF9ERUxFVEVEO1xuICAgICAgICAgICAgY29udGludWU7XG4gICAgICAgIH1cbiAgICAgICAgdGV4dHVyZS5udW1iZXIgPSB0ZXh0dXJlX251bWJlcjtcbiAgICAgICAgdGV4dHVyZV9udW1iZXIgKz0gMTtcbiAgICAgICAgZGVidWcoXCJBY3RpdmF0aW5nIHRleHR1cmUgJ3swfScgZm9yIHByb2dyYW0gJ3sxfScgYXMgbnVtYmVyICd7Mn0nLlwiLmZvcm1hdChcbiAgICAgICAgICAgIHRleHR1cmVfaWQsIHByb2dyYW1faWQsIHRleHR1cmUubnVtYmVyKSk7XG4gICAgICAgIGFjdGl2YXRlX3RleHR1cmUoYywgdGV4dHVyZS5oYW5kbGUsIHRleHR1cmUuc2FtcGxlcl9oYW5kbGUsIHRleHR1cmUubnVtYmVyKTtcbiAgICAgICAgYy5nbC51bmlmb3JtMWkodGV4dHVyZS5zYW1wbGVyX2hhbmRsZSwgdGV4dHVyZS5udW1iZXIpO1xuICAgIH1cblxuICAgIC8vIERyYXcgdGhlIHByb2dyYW0uXG4gICAgaWYgKHNlbGVjdGlvbi5sZW5ndGggPT0gMikge1xuICAgICAgICAvLyBEcmF3IHRoZSBwcm9ncmFtIHdpdGhvdXQgaW5kZXggYnVmZmVyLlxuICAgICAgICB2YXIgc3RhcnQgPSBzZWxlY3Rpb25bMF07XG4gICAgICAgIHZhciBjb3VudCA9IHNlbGVjdGlvblsxXTtcbiAgICAgICAgZGVidWcoXCJSZW5kZXJpbmcgcHJvZ3JhbSAnezB9JyB3aXRoIHsxfS5cIi5mb3JtYXQoXG4gICAgICAgICAgICBwcm9ncmFtX2lkLCBtb2RlKSk7XG4gICAgICAgIGMuZ2wuZHJhd0FycmF5cyhjLmdsW21vZGVdLCBzdGFydCwgY291bnQpO1xuICAgIH1cbiAgICBlbHNlIGlmIChzZWxlY3Rpb24ubGVuZ3RoID09IDMpIHtcbiAgICAgICAgLy8gRHJhdyB0aGUgcHJvZ3JhbSB3aXRoIGluZGV4IGJ1ZmZlci5cbiAgICAgICAgdmFyIGluZGV4X2J1ZmZlcl9pZCA9IHNlbGVjdGlvblswXTtcbiAgICAgICAgdmFyIGluZGV4X2J1ZmZlcl90eXBlID0gc2VsZWN0aW9uWzFdO1xuICAgICAgICB2YXIgY291bnQgPSBzZWxlY3Rpb25bMl07XG4gICAgICAgIC8vIEdldCB0aGUgaW5kZXggYnVmZmVyIGhhbmRsZSBmcm9tIHRoZSBuYW1lc3BhY2UuXG4gICAgICAgIHZhciBpbmRleF9idWZmZXJfaGFuZGxlID0gYy5fbnNbaW5kZXhfYnVmZmVyX2lkXS5oYW5kbGU7XG4gICAgICAgIGRlYnVnKFwiUmVuZGVyaW5nIHByb2dyYW0gJ3swfScgd2l0aCB7MX0gYW5kIGluZGV4IGJ1ZmZlciAnezJ9JyBvZiB0eXBlICd7M30nLlwiLmZvcm1hdChcbiAgICAgICAgICAgIHByb2dyYW1faWQsIG1vZGUsIGluZGV4X2J1ZmZlcl9pZCwgaW5kZXhfYnVmZmVyX3R5cGUpKTtcbiAgICAgICAgLy8gQWN0aXZhdGUgdGhlIGluZGV4IGJ1ZmZlci5cbiAgICAgICAgYy5nbC5iaW5kQnVmZmVyKGMuZ2wuRUxFTUVOVF9BUlJBWV9CVUZGRVIsIGluZGV4X2J1ZmZlcl9oYW5kbGUpO1xuICAgICAgICBjLmdsLmRyYXdFbGVtZW50cyhjLmdsW21vZGVdLCBjb3VudCwgYy5nbFtpbmRleF9idWZmZXJfdHlwZV0sIDApO1xuICAgIH1cblxuICAgIC8vIERlYWN0aXZhdGUgYXR0cmlidXRlcy5cbiAgICBmb3IgKGF0dHJpYnV0ZV9uYW1lIGluIGF0dHJpYnV0ZXMpIHtcbiAgICAgICAgZGVidWcoXCJEZWFjdGl2YXRpbmcgYXR0cmlidXRlICd7MH0nIGZvciBwcm9ncmFtICd7MX0nLlwiLmZvcm1hdChcbiAgICAgICAgICAgIGF0dHJpYnV0ZV9uYW1lLCBwcm9ncmFtX2lkKSk7XG4gICAgICAgIGRlYWN0aXZhdGVfYXR0cmlidXRlKGMsIGF0dHJpYnV0ZXNbYXR0cmlidXRlX25hbWVdLmhhbmRsZSk7XG4gICAgfVxuXG4gICAgLy8gRGVhY3RpdmF0ZSB0ZXh0dXJlcy5cbiAgICB2YXIgbmV3X3RleHR1cmVzID0ge307XG4gICAgZm9yICh0ZXh0dXJlX2lkIGluIHRleHR1cmVzKSB7XG4gICAgICAgIHZhciB0ZXh0dXJlID0gdGV4dHVyZXNbdGV4dHVyZV9pZF07XG4gICAgICAgIGRlYnVnKFwiRGVhY3RpdmF0aW5nIHRleHR1cmUgJ3swfScgZm9yIHByb2dyYW0gJ3sxfScuXCIuZm9ybWF0KFxuICAgICAgICAgICAgdGV4dHVyZV9pZCwgcHJvZ3JhbV9pZCkpO1xuICAgICAgICBkZWFjdGl2YXRlX3RleHR1cmUoYywgdGV4dHVyZS5oYW5kbGUsIHRleHR1cmUuc2FtcGxlcl9oYW5kbGUsIHRleHR1cmUubnVtYmVyKTtcblxuICAgICAgICAvLyBEb24ndCBpbmNsdWRlIGFueSBvZiB0aGUgdGV4dHVyZXMgdGhhdCB3ZXJlIGRlbGV0ZWQgaW4gdGhpcyBwcm9ncmFtXG4gICAgICAgIGlmIChjLl9uc1t0ZXh0dXJlX2lkXS5oYW5kbGUgIT0gSlVTVF9ERUxFVEVEKSB7XG4gICAgICAgICAgICBuZXdfdGV4dHVyZXNbdGV4dHVyZV9pZF0gPSB0ZXh0dXJlO1xuICAgICAgICB9XG4gICAgfVxuICAgIGMuX25zW3Byb2dyYW1faWRdLnRleHR1cmVzID0gbmV3X3RleHR1cmVzO1xufTtcblxuZ2xpci5wcm90b3R5cGUuYXR0YWNoID0gZnVuY3Rpb24oYywgYXJncykge1xuICAgIC8vIGZyYW1lYnVmZmVyIG9yIHNoYWRlciBvYmplY3QgSURcbiAgICB2YXIgZHN0X2lkID0gYXJnc1swXTtcbiAgICB2YXIgZHN0X29iaiA9IGMuX25zW2RzdF9pZF07XG4gICAgdmFyIGRzdF90eXBlID0gZHN0X29iai5vYmplY3RfdHlwZTtcbiAgICB2YXIgZHN0X2hhbmRsZSA9IGRzdF9vYmouaGFuZGxlO1xuICAgIGlmIChkc3RfdHlwZSA9PSAnUHJvZ3JhbScpIHtcbiAgICAgICAgLy8gYXR0YWNoaW5nIHRvIHByb2dyYW0sIG11c3QgYmUgYSBzaGFkZXIgd2UncmUgYXR0YWNoaW5nXG4gICAgICAgIHZhciBzaGFkZXJfaWQgPSBhcmdzWzFdO1xuICAgICAgICB2YXIgc2hhZGVyX2hhbmRsZSA9IGMuX25zW3NoYWRlcl9pZF0uaGFuZGxlO1xuICAgICAgICBjLmdsLmF0dGFjaFNoYWRlcihkc3RfaGFuZGxlLCBzaGFkZXJfaGFuZGxlKTtcbiAgICAgICAgcmV0dXJuO1xuICAgIH1cblxuICAgIC8vIEF0dGFjaCB0byBmcmFtZWJ1ZmZlclxuICAgIHZhciBvYmplY3RfaWQgPSBhcmdzWzJdO1xuICAgIHZhciBhdHRhY2hfdHlwZSA9IGMuZ2xbZ2V0X2F0dGFjaG1lbnRfdHlwZShhcmdzWzFdKV07XG4gICAgdmFyIG9iamVjdDtcbiAgICBhY3RpdmF0ZV9mcmFtZWJ1ZmZlcihjLCBkc3RfaWQpO1xuICAgIGlmIChvYmplY3RfaWQgPT0gMCkge1xuICAgICAgICBkZWJ1ZygnQXR0YWNoaW5nIFJlbmRlckJ1ZmZlciBvYmplY3QgezB9IHRvIGZyYW1lYnVmZmVyIHsxfScuZm9ybWF0KG9iamVjdF9pZCwgZHN0X2lkKSk7XG4gICAgICAgIGMuZ2wuZnJhbWVidWZmZXJSZW5kZXJidWZmZXIoYy5nbC5GUkFNRUJVRkZFUiwgYXR0YWNoX3R5cGUsIGMuZ2wuUkVOREVSQlVGRkVSLCBudWxsKTtcbiAgICB9IGVsc2Uge1xuICAgICAgICBvYmplY3QgPSBjLl9uc1tvYmplY3RfaWRdO1xuICAgICAgICBkZWJ1ZygnQXR0YWNoaW5nIHswfSBvYmplY3QgezF9IHRvIGZyYW1lYnVmZmVyIHsyfSBmb3IgezN9Jy5mb3JtYXQob2JqZWN0Lm9iamVjdF90eXBlLCBvYmplY3RfaWQsIGRzdF9pZCwgYXJnc1sxXSkpO1xuICAgICAgICBpZiAob2JqZWN0Lm9iamVjdF90eXBlID09ICdSZW5kZXJCdWZmZXInKSB7XG4gICAgICAgICAgICBjLmdsLmJpbmRSZW5kZXJidWZmZXIoYy5nbC5SRU5ERVJCVUZGRVIsIG9iamVjdC5oYW5kbGUpO1xuICAgICAgICAgICAgYy5nbC5mcmFtZWJ1ZmZlclJlbmRlcmJ1ZmZlcihjLmdsLkZSQU1FQlVGRkVSLCBhdHRhY2hfdHlwZSwgYy5nbC5SRU5ERVJCVUZGRVIsIG9iamVjdC5oYW5kbGUpO1xuICAgICAgICAgICAgYy5nbC5iaW5kUmVuZGVyYnVmZmVyKGMuZ2wuUkVOREVSQlVGRkVSLCBudWxsKTtcbiAgICAgICAgfVxuICAgICAgICBlbHNlIGlmIChvYmplY3Qub2JqZWN0X3R5cGUgPT0gJ1RleHR1cmUyRCcpIHtcbiAgICAgICAgICAgIC8vIG51bGwgb3IgdW5kZWZpbmVkXG4gICAgICAgICAgICBpZiAob2JqZWN0LnNoYXBlLmxlbmd0aCA9PSAwKSB7XG4gICAgICAgICAgICAgICAgZGVidWcoJ1NldHRpbmcgZW1wdHkgdGV4dHVyZSBkYXRhIHRvIHVuc2V0IHRleHR1cmUgYmVmb3JlIGF0dGFjaGluZyB0byBmcmFtZWJ1ZmZlcicpO1xuICAgICAgICAgICAgICAgIHNldF90ZXh0dXJlX2RhdGEoYywgb2JqZWN0LmhhbmRsZSwgYy5nbC5URVhUVVJFXzJELFxuICAgICAgICAgICAgICAgICAgICBjLmdsW29iamVjdC5mb3JtYXRdLCBvYmplY3Quc2l6ZVsxXSwgb2JqZWN0LnNpemVbMF0sIG51bGwpO1xuICAgICAgICAgICAgfVxuICAgICAgICAgICAgLy8gSU5GTzogMCBpcyBmb3IgbWlwbWFwIGxldmVsIDAgKGRlZmF1bHQpIG9mIHRoZSB0ZXh0dXJlXG4gICAgICAgICAgICBjLmdsLmJpbmRUZXh0dXJlKGMuZ2wuVEVYVFVSRV8yRCwgb2JqZWN0LmhhbmRsZSk7XG4gICAgICAgICAgICBjLmdsLmZyYW1lYnVmZmVyVGV4dHVyZTJEKGMuZ2wuRlJBTUVCVUZGRVIsIGF0dGFjaF90eXBlLCBjLmdsLlRFWFRVUkVfMkQsIG9iamVjdC5oYW5kbGUsIDApO1xuICAgICAgICAgICAgYy5nbC5iaW5kVGV4dHVyZShjLmdsLlRFWFRVUkVfMkQsIG51bGwpO1xuICAgICAgICB9XG4gICAgfVxuICAgIGMuX25zW2RzdF9pZF0udmFsaWRhdGVkID0gZmFsc2U7XG4gICAgZGVhY3RpdmF0ZV9mcmFtZWJ1ZmZlcihjLCBkc3RfaWQpO1xufTtcblxuZ2xpci5wcm90b3R5cGUubGluayA9IGZ1bmN0aW9uKGMsIGFyZ3MpIHtcbiAgICB2YXIgcHJvZ3JhbV9oYW5kbGUgPSBjLl9uc1thcmdzWzBdXS5oYW5kbGU7XG4gICAgYy5nbC5saW5rUHJvZ3JhbShwcm9ncmFtX2hhbmRsZSk7XG5cbiAgICBpZiAoIWMuZ2wuZ2V0UHJvZ3JhbVBhcmFtZXRlcihwcm9ncmFtX2hhbmRsZSwgYy5nbC5MSU5LX1NUQVRVUykpXG4gICAge1xuICAgICAgICBjb25zb2xlLndhcm4oXCJDb3VsZCBub3QgaW5pdGlhbGlzZSBzaGFkZXJzIG9uIHByb2dyYW0gJ3swfScuXCIuZm9ybWF0KHByb2dyYW1faGFuZGxlKSk7XG4gICAgfVxufTtcblxuZ2xpci5wcm90b3R5cGUuZnJhbWVidWZmZXIgPSBmdW5jdGlvbihjLCBhcmdzKSB7XG4gICAgdmFyIGZyYW1lYnVmZmVyX2lkID0gYXJnc1swXTtcbiAgICB2YXIgYmluZCA9IGFyZ3NbMV07XG4gICAgdmFyIGZiID0gYy5fbnNbZnJhbWVidWZmZXJfaWRdO1xuXG4gICAgaWYgKGJpbmQpIHtcbiAgICAgICAgZGVidWcoJ0JpbmRpbmcgZnJhbWVidWZmZXIgezB9Jy5mb3JtYXQoZnJhbWVidWZmZXJfaWQpKTtcbiAgICAgICAgYWN0aXZhdGVfZnJhbWVidWZmZXIoYywgZnJhbWVidWZmZXJfaWQpO1xuICAgICAgICBpZiAoIWZiLnZhbGlkYXRlZCkge1xuICAgICAgICAgICAgZmIudmFsaWRhdGVkID0gdHJ1ZTtcbiAgICAgICAgICAgIHZhbGlkYXRlX2ZyYW1lYnVmZmVyKGMpO1xuICAgICAgICB9XG4gICAgfVxuICAgIGVsc2Uge1xuICAgICAgICBkZWJ1ZygnVW5iaW5kaW5nIGZyYW1lYnVmZmVyIHswfScuZm9ybWF0KGZyYW1lYnVmZmVyX2lkKSk7XG4gICAgICAgIGRlYWN0aXZhdGVfZnJhbWVidWZmZXIoYywgZnJhbWVidWZmZXJfaWQpO1xuICAgIH1cbn07XG5cbmdsaXIucHJvdG90eXBlLmZ1bmMgPSBmdW5jdGlvbihjLCBhcmdzKSB7XG4gICAgdmFyIG5hbWUgPSBhcmdzWzBdO1xuICAgIGRlYnVnKFwiQ2FsbGluZyB7MH0oezF9KS5cIi5mb3JtYXQobmFtZSwgYXJncy5zbGljZSgxKSkpO1xuXG4gICAgLy8gSGFuZGxlIGVudW1zOiByZXBsYWNlIHN0cmluZ3MgYnkgZ2xvYmFsIEdMIHZhcmlhYmxlcy5cbiAgICBmb3IgKHZhciBpID0gMTsgaSA8IGFyZ3MubGVuZ3RoOyBpKyspIHtcbiAgICAgICAgaWYgKHR5cGVvZiBhcmdzW2ldID09PSAnc3RyaW5nJykge1xuICAgICAgICAgICAgYXJnc1tpXSA9IHBhcnNlX2VudW0oYywgYXJnc1tpXSk7XG4gICAgICAgIH1cbiAgICB9XG5cbiAgICB2YXIgZnVuYyA9IGMuZ2xbbmFtZV07XG4gICAgdmFyIGZ1bmNfYXJncyA9IGFyZ3Muc2xpY2UoMSk7XG4gICAgZnVuYy5hcHBseShjLmdsLCBmdW5jX2FyZ3MpO1xufTtcblxubW9kdWxlLmV4cG9ydHMgPSBuZXcgZ2xpcigpO1xuIiwidmFyIGdsaXIgPSByZXF1aXJlKCcuL2dsb28uZ2xpci5qcycpO1xuXG5mdW5jdGlvbiBpbml0X3dlYmdsKGMpIHtcbiAgICAvLyBHZXQgdGhlIERPTSBvYmplY3QsIG5vdCB0aGUgalF1ZXJ5IG9uZS5cbiAgICB2YXIgY2FudmFzID0gYy4kZWwuZ2V0KDApO1xuICAgIGMuZ2wgPSBjYW52YXMuZ2V0Q29udGV4dChcIndlYmdsXCIpIHx8XG4gICAgICAgICAgIGNhbnZhcy5nZXRDb250ZXh0KFwiZXhwZXJpbWVudGFsLXdlYmdsXCIpO1xuICAgIHZhciBleHQgPSBjLmdsLmdldEV4dGVuc2lvbignT0VTX3N0YW5kYXJkX2Rlcml2YXRpdmVzJykgfHwgYy5nbC5nZXRFeHRlbnNpb24oJ01PWl9PRVNfc3RhbmRhcmRfZGVyaXZhdGl2ZXMnKSB8fCBjLmdsLmdldEV4dGVuc2lvbignV0VCS0lUX09FU19zdGFuZGFyZF9kZXJpdmF0aXZlcycpO1xuICAgIGlmIChleHQgPT09IG51bGwpIHtcbiAgICAgICAgY29uc29sZS53YXJuKCdFeHRlbnNpb24gXFwnT0VTX3N0YW5kYXJkX2Rlcml2YXRpdmVzXFwnIGlzIG5vdCBzdXBwb3J0ZWQgaW4gdGhpcyBicm93c2VyLiBTb21lIGZlYXR1cmVzIG1heSBub3Qgd29yayBhcyBleHBlY3RlZCcpO1xuICAgIH1cbiAgICB2YXIgZXh0ID0gYy5nbC5nZXRFeHRlbnNpb24oJ09FU19lbGVtZW50X2luZGV4X3VpbnQnKSB8fFxuICAgICAgICBjLmdsLmdldEV4dGVuc2lvbignTU9aX09FU19lbGVtZW50X2luZGV4X3VpbnQnKSB8fFxuICAgICAgICBjLmdsLmdldEV4dGVuc2lvbignV0VCS0lUX09FU19lbGVtZW50X2luZGV4X3VpbnQnKTtcbiAgICBpZiAoZXh0ID09PSBudWxsKSB7XG4gICAgICAgIGNvbnNvbGUud2FybignRXh0ZW5zaW9uIFxcJ09FU19lbGVtZW50X2luZGV4X3VpbnRcXCcgaXMgbm90IHN1cHBvcnRlZCBpbiB0aGlzIGJyb3dzZXIuIFNvbWUgZmVhdHVyZXMgbWF5IG5vdCB3b3JrIGFzIGV4cGVjdGVkJyk7XG4gICAgfVxuICAgIHZhciBleHQgPSBjLmdsLmdldEV4dGVuc2lvbignT0VTX3RleHR1cmVfZmxvYXQnKTtcbiAgICAvLyB8fFxuICAgIC8vICAgICBjLmdsLmdldEV4dGVuc2lvbignTU9aX09FU19lbGVtZW50X2luZGV4X3VpbnQnKSB8fFxuICAgIC8vICAgICBjLmdsLmdldEV4dGVuc2lvbignV0VCS0lUX09FU19lbGVtZW50X2luZGV4X3VpbnQnKTtcbiAgICBpZiAoZXh0ID09PSBudWxsKSB7XG4gICAgICAgIGNvbnNvbGUud2FybignRXh0ZW5zaW9uIFxcJ09FU190ZXh0dXJlX2Zsb2F0XFwnIGlzIG5vdCBzdXBwb3J0ZWQgaW4gdGhpcyBicm93c2VyLiBTb21lIGZlYXR1cmVzIG1heSBub3Qgd29yayBhcyBleHBlY3RlZCcpO1xuICAgIH1cblxuICAgIHZhciBleHQgPSBjLmdsLmdldEV4dGVuc2lvbignT0VTX3RleHR1cmVfZmxvYXRfbGluZWFyJyk7XG4gICAgaWYgKGV4dCA9PT0gbnVsbCkge1xuICAgICAgICBjb25zb2xlLndhcm4oJ0V4dGVuc2lvbiBcXCdPRVNfdGV4dHVyZV9mbG9hdF9saW5lYXJcXCcgaXMgbm90IHN1cHBvcnRlZCBpbiB0aGlzIGJyb3dzZXIuIFNvbWUgZmVhdHVyZXMgbWF5IG5vdCB3b3JrIGFzIGV4cGVjdGVkJyk7XG4gICAgfVxuXG4gICAgLy8gYy5nbC5nZXRFeHRlbnNpb24oJ0VYVF9zaGFkZXJfdGV4dHVyZV9sb2QnKTtcbn1cblxuXG4vKiBDcmVhdGlvbiBvZiB2aXNweS5nbG9vICovXG52YXIgZ2xvbyA9IGZ1bmN0aW9uKCkge1xuICAgIHRoaXMuZ2xpciA9IGdsaXI7XG4gICAgLy8gQ29uc3RydWN0b3IuXG5cbn07XG5cbmdsb28ucHJvdG90eXBlLmluaXQgPSBmdW5jdGlvbihjKSB7XG4gICAgaW5pdF93ZWJnbChjKTtcbiAgICB0aGlzLmdsaXIuaW5pdChjKTtcbn07XG5cblxubW9kdWxlLmV4cG9ydHMgPSBuZXcgZ2xvbygpO1xuIiwiLyohIENvcHlyaWdodCAoYykgMjAxMyBCcmFuZG9uIEFhcm9uIChodHRwOi8vYnJhbmRvbi5hYXJvbi5zaClcbiAqIExpY2Vuc2VkIHVuZGVyIHRoZSBNSVQgTGljZW5zZSAoTElDRU5TRS50eHQpLlxuICpcbiAqIFZlcnNpb246IDMuMS4xMlxuICpcbiAqIFJlcXVpcmVzOiBqUXVlcnkgMS4yLjIrXG4gKi9cbiFmdW5jdGlvbihhKXtcImZ1bmN0aW9uXCI9PXR5cGVvZiBkZWZpbmUmJmRlZmluZS5hbWQ/ZGVmaW5lKFtcImpxdWVyeVwiXSxhKTpcIm9iamVjdFwiPT10eXBlb2YgZXhwb3J0cz9tb2R1bGUuZXhwb3J0cz1hOmEoalF1ZXJ5KX0oZnVuY3Rpb24oYSl7ZnVuY3Rpb24gYihiKXt2YXIgZz1ifHx3aW5kb3cuZXZlbnQsaD1pLmNhbGwoYXJndW1lbnRzLDEpLGo9MCxsPTAsbT0wLG49MCxvPTAscD0wO2lmKGI9YS5ldmVudC5maXgoZyksYi50eXBlPVwibW91c2V3aGVlbFwiLFwiZGV0YWlsXCJpbiBnJiYobT0tMSpnLmRldGFpbCksXCJ3aGVlbERlbHRhXCJpbiBnJiYobT1nLndoZWVsRGVsdGEpLFwid2hlZWxEZWx0YVlcImluIGcmJihtPWcud2hlZWxEZWx0YVkpLFwid2hlZWxEZWx0YVhcImluIGcmJihsPS0xKmcud2hlZWxEZWx0YVgpLFwiYXhpc1wiaW4gZyYmZy5heGlzPT09Zy5IT1JJWk9OVEFMX0FYSVMmJihsPS0xKm0sbT0wKSxqPTA9PT1tP2w6bSxcImRlbHRhWVwiaW4gZyYmKG09LTEqZy5kZWx0YVksaj1tKSxcImRlbHRhWFwiaW4gZyYmKGw9Zy5kZWx0YVgsMD09PW0mJihqPS0xKmwpKSwwIT09bXx8MCE9PWwpe2lmKDE9PT1nLmRlbHRhTW9kZSl7dmFyIHE9YS5kYXRhKHRoaXMsXCJtb3VzZXdoZWVsLWxpbmUtaGVpZ2h0XCIpO2oqPXEsbSo9cSxsKj1xfWVsc2UgaWYoMj09PWcuZGVsdGFNb2RlKXt2YXIgcj1hLmRhdGEodGhpcyxcIm1vdXNld2hlZWwtcGFnZS1oZWlnaHRcIik7aio9cixtKj1yLGwqPXJ9aWYobj1NYXRoLm1heChNYXRoLmFicyhtKSxNYXRoLmFicyhsKSksKCFmfHxmPm4pJiYoZj1uLGQoZyxuKSYmKGYvPTQwKSksZChnLG4pJiYoai89NDAsbC89NDAsbS89NDApLGo9TWF0aFtqPj0xP1wiZmxvb3JcIjpcImNlaWxcIl0oai9mKSxsPU1hdGhbbD49MT9cImZsb29yXCI6XCJjZWlsXCJdKGwvZiksbT1NYXRoW20+PTE/XCJmbG9vclwiOlwiY2VpbFwiXShtL2YpLGsuc2V0dGluZ3Mubm9ybWFsaXplT2Zmc2V0JiZ0aGlzLmdldEJvdW5kaW5nQ2xpZW50UmVjdCl7dmFyIHM9dGhpcy5nZXRCb3VuZGluZ0NsaWVudFJlY3QoKTtvPWIuY2xpZW50WC1zLmxlZnQscD1iLmNsaWVudFktcy50b3B9cmV0dXJuIGIuZGVsdGFYPWwsYi5kZWx0YVk9bSxiLmRlbHRhRmFjdG9yPWYsYi5vZmZzZXRYPW8sYi5vZmZzZXRZPXAsYi5kZWx0YU1vZGU9MCxoLnVuc2hpZnQoYixqLGwsbSksZSYmY2xlYXJUaW1lb3V0KGUpLGU9c2V0VGltZW91dChjLDIwMCksKGEuZXZlbnQuZGlzcGF0Y2h8fGEuZXZlbnQuaGFuZGxlKS5hcHBseSh0aGlzLGgpfX1mdW5jdGlvbiBjKCl7Zj1udWxsfWZ1bmN0aW9uIGQoYSxiKXtyZXR1cm4gay5zZXR0aW5ncy5hZGp1c3RPbGREZWx0YXMmJlwibW91c2V3aGVlbFwiPT09YS50eXBlJiZiJTEyMD09PTB9dmFyIGUsZixnPVtcIndoZWVsXCIsXCJtb3VzZXdoZWVsXCIsXCJET01Nb3VzZVNjcm9sbFwiLFwiTW96TW91c2VQaXhlbFNjcm9sbFwiXSxoPVwib253aGVlbFwiaW4gZG9jdW1lbnR8fGRvY3VtZW50LmRvY3VtZW50TW9kZT49OT9bXCJ3aGVlbFwiXTpbXCJtb3VzZXdoZWVsXCIsXCJEb21Nb3VzZVNjcm9sbFwiLFwiTW96TW91c2VQaXhlbFNjcm9sbFwiXSxpPUFycmF5LnByb3RvdHlwZS5zbGljZTtpZihhLmV2ZW50LmZpeEhvb2tzKWZvcih2YXIgaj1nLmxlbmd0aDtqOylhLmV2ZW50LmZpeEhvb2tzW2dbLS1qXV09YS5ldmVudC5tb3VzZUhvb2tzO3ZhciBrPWEuZXZlbnQuc3BlY2lhbC5tb3VzZXdoZWVsPXt2ZXJzaW9uOlwiMy4xLjEyXCIsc2V0dXA6ZnVuY3Rpb24oKXtpZih0aGlzLmFkZEV2ZW50TGlzdGVuZXIpZm9yKHZhciBjPWgubGVuZ3RoO2M7KXRoaXMuYWRkRXZlbnRMaXN0ZW5lcihoWy0tY10sYiwhMSk7ZWxzZSB0aGlzLm9ubW91c2V3aGVlbD1iO2EuZGF0YSh0aGlzLFwibW91c2V3aGVlbC1saW5lLWhlaWdodFwiLGsuZ2V0TGluZUhlaWdodCh0aGlzKSksYS5kYXRhKHRoaXMsXCJtb3VzZXdoZWVsLXBhZ2UtaGVpZ2h0XCIsay5nZXRQYWdlSGVpZ2h0KHRoaXMpKX0sdGVhcmRvd246ZnVuY3Rpb24oKXtpZih0aGlzLnJlbW92ZUV2ZW50TGlzdGVuZXIpZm9yKHZhciBjPWgubGVuZ3RoO2M7KXRoaXMucmVtb3ZlRXZlbnRMaXN0ZW5lcihoWy0tY10sYiwhMSk7ZWxzZSB0aGlzLm9ubW91c2V3aGVlbD1udWxsO2EucmVtb3ZlRGF0YSh0aGlzLFwibW91c2V3aGVlbC1saW5lLWhlaWdodFwiKSxhLnJlbW92ZURhdGEodGhpcyxcIm1vdXNld2hlZWwtcGFnZS1oZWlnaHRcIil9LGdldExpbmVIZWlnaHQ6ZnVuY3Rpb24oYil7dmFyIGM9YShiKSxkPWNbXCJvZmZzZXRQYXJlbnRcImluIGEuZm4/XCJvZmZzZXRQYXJlbnRcIjpcInBhcmVudFwiXSgpO3JldHVybiBkLmxlbmd0aHx8KGQ9YShcImJvZHlcIikpLHBhcnNlSW50KGQuY3NzKFwiZm9udFNpemVcIiksMTApfHxwYXJzZUludChjLmNzcyhcImZvbnRTaXplXCIpLDEwKXx8MTZ9LGdldFBhZ2VIZWlnaHQ6ZnVuY3Rpb24oYil7cmV0dXJuIGEoYikuaGVpZ2h0KCl9LHNldHRpbmdzOnthZGp1c3RPbGREZWx0YXM6ITAsbm9ybWFsaXplT2Zmc2V0OiEwfX07YS5mbi5leHRlbmQoe21vdXNld2hlZWw6ZnVuY3Rpb24oYSl7cmV0dXJuIGE/dGhpcy5iaW5kKFwibW91c2V3aGVlbFwiLGEpOnRoaXMudHJpZ2dlcihcIm1vdXNld2hlZWxcIil9LHVubW91c2V3aGVlbDpmdW5jdGlvbihhKXtyZXR1cm4gdGhpcy51bmJpbmQoXCJtb3VzZXdoZWVsXCIsYSl9fSl9KTsiLCIvKiFcbiogc2NyZWVuZnVsbFxuKiB2MS4yLjAgLSAyMDE0LTA0LTI5XG4qIChjKSBTaW5kcmUgU29yaHVzOyBNSVQgTGljZW5zZVxuKi9cbiFmdW5jdGlvbigpe1widXNlIHN0cmljdFwiO3ZhciBhPVwidW5kZWZpbmVkXCIhPXR5cGVvZiBtb2R1bGUmJm1vZHVsZS5leHBvcnRzLGI9XCJ1bmRlZmluZWRcIiE9dHlwZW9mIEVsZW1lbnQmJlwiQUxMT1dfS0VZQk9BUkRfSU5QVVRcImluIEVsZW1lbnQsYz1mdW5jdGlvbigpe2Zvcih2YXIgYSxiLGM9W1tcInJlcXVlc3RGdWxsc2NyZWVuXCIsXCJleGl0RnVsbHNjcmVlblwiLFwiZnVsbHNjcmVlbkVsZW1lbnRcIixcImZ1bGxzY3JlZW5FbmFibGVkXCIsXCJmdWxsc2NyZWVuY2hhbmdlXCIsXCJmdWxsc2NyZWVuZXJyb3JcIl0sW1wid2Via2l0UmVxdWVzdEZ1bGxzY3JlZW5cIixcIndlYmtpdEV4aXRGdWxsc2NyZWVuXCIsXCJ3ZWJraXRGdWxsc2NyZWVuRWxlbWVudFwiLFwid2Via2l0RnVsbHNjcmVlbkVuYWJsZWRcIixcIndlYmtpdGZ1bGxzY3JlZW5jaGFuZ2VcIixcIndlYmtpdGZ1bGxzY3JlZW5lcnJvclwiXSxbXCJ3ZWJraXRSZXF1ZXN0RnVsbFNjcmVlblwiLFwid2Via2l0Q2FuY2VsRnVsbFNjcmVlblwiLFwid2Via2l0Q3VycmVudEZ1bGxTY3JlZW5FbGVtZW50XCIsXCJ3ZWJraXRDYW5jZWxGdWxsU2NyZWVuXCIsXCJ3ZWJraXRmdWxsc2NyZWVuY2hhbmdlXCIsXCJ3ZWJraXRmdWxsc2NyZWVuZXJyb3JcIl0sW1wibW96UmVxdWVzdEZ1bGxTY3JlZW5cIixcIm1vekNhbmNlbEZ1bGxTY3JlZW5cIixcIm1vekZ1bGxTY3JlZW5FbGVtZW50XCIsXCJtb3pGdWxsU2NyZWVuRW5hYmxlZFwiLFwibW96ZnVsbHNjcmVlbmNoYW5nZVwiLFwibW96ZnVsbHNjcmVlbmVycm9yXCJdLFtcIm1zUmVxdWVzdEZ1bGxzY3JlZW5cIixcIm1zRXhpdEZ1bGxzY3JlZW5cIixcIm1zRnVsbHNjcmVlbkVsZW1lbnRcIixcIm1zRnVsbHNjcmVlbkVuYWJsZWRcIixcIk1TRnVsbHNjcmVlbkNoYW5nZVwiLFwiTVNGdWxsc2NyZWVuRXJyb3JcIl1dLGQ9MCxlPWMubGVuZ3RoLGY9e307ZT5kO2QrKylpZihhPWNbZF0sYSYmYVsxXWluIGRvY3VtZW50KXtmb3IoZD0wLGI9YS5sZW5ndGg7Yj5kO2QrKylmW2NbMF1bZF1dPWFbZF07cmV0dXJuIGZ9cmV0dXJuITF9KCksZD17cmVxdWVzdDpmdW5jdGlvbihhKXt2YXIgZD1jLnJlcXVlc3RGdWxsc2NyZWVuO2E9YXx8ZG9jdW1lbnQuZG9jdW1lbnRFbGVtZW50LC81XFwuMVtcXC5cXGRdKiBTYWZhcmkvLnRlc3QobmF2aWdhdG9yLnVzZXJBZ2VudCk/YVtkXSgpOmFbZF0oYiYmRWxlbWVudC5BTExPV19LRVlCT0FSRF9JTlBVVCl9LGV4aXQ6ZnVuY3Rpb24oKXtkb2N1bWVudFtjLmV4aXRGdWxsc2NyZWVuXSgpfSx0b2dnbGU6ZnVuY3Rpb24oYSl7dGhpcy5pc0Z1bGxzY3JlZW4/dGhpcy5leGl0KCk6dGhpcy5yZXF1ZXN0KGEpfSxvbmNoYW5nZTpmdW5jdGlvbigpe30sb25lcnJvcjpmdW5jdGlvbigpe30scmF3OmN9O3JldHVybiBjPyhPYmplY3QuZGVmaW5lUHJvcGVydGllcyhkLHtpc0Z1bGxzY3JlZW46e2dldDpmdW5jdGlvbigpe3JldHVybiEhZG9jdW1lbnRbYy5mdWxsc2NyZWVuRWxlbWVudF19fSxlbGVtZW50OntlbnVtZXJhYmxlOiEwLGdldDpmdW5jdGlvbigpe3JldHVybiBkb2N1bWVudFtjLmZ1bGxzY3JlZW5FbGVtZW50XX19LGVuYWJsZWQ6e2VudW1lcmFibGU6ITAsZ2V0OmZ1bmN0aW9uKCl7cmV0dXJuISFkb2N1bWVudFtjLmZ1bGxzY3JlZW5FbmFibGVkXX19fSksZG9jdW1lbnQuYWRkRXZlbnRMaXN0ZW5lcihjLmZ1bGxzY3JlZW5jaGFuZ2UsZnVuY3Rpb24oYSl7ZC5vbmNoYW5nZS5jYWxsKGQsYSl9KSxkb2N1bWVudC5hZGRFdmVudExpc3RlbmVyKGMuZnVsbHNjcmVlbmVycm9yLGZ1bmN0aW9uKGEpe2Qub25lcnJvci5jYWxsKGQsYSl9KSx2b2lkKGE/bW9kdWxlLmV4cG9ydHM9ZDp3aW5kb3cuc2NyZWVuZnVsbD1kKSk6dm9pZChhP21vZHVsZS5leHBvcnRzPSExOndpbmRvdy5zY3JlZW5mdWxsPSExKX0oKTsiLCJpZiAoIVN0cmluZy5wcm90b3R5cGUuZm9ybWF0KSB7XG4gIFN0cmluZy5wcm90b3R5cGUuZm9ybWF0ID0gZnVuY3Rpb24oKSB7XG4gICAgdmFyIGFyZ3MgPSBhcmd1bWVudHM7XG4gICAgcmV0dXJuIHRoaXMucmVwbGFjZSgveyhcXGQrKX0vZywgZnVuY3Rpb24obWF0Y2gsIG51bWJlcikge1xuICAgICAgcmV0dXJuICh0eXBlb2YgYXJnc1tudW1iZXJdICE9ICd1bmRlZmluZWQnKVxuICAgICAgICA/IGFyZ3NbbnVtYmVyXVxuICAgICAgICA6IG1hdGNoO1xuICAgIH0pO1xuICB9O1xufVxuXG5pZih0eXBlb2YoU3RyaW5nLnByb3RvdHlwZS50cmltKSA9PT0gXCJ1bmRlZmluZWRcIilcbntcbiAgICBTdHJpbmcucHJvdG90eXBlLnRyaW0gPSBmdW5jdGlvbigpXG4gICAge1xuICAgICAgICByZXR1cm4gU3RyaW5nKHRoaXMpLnJlcGxhY2UoL15cXHMrfFxccyskL2csICcnKTtcbiAgICB9O1xufVxuXG5mdW5jdGlvbiBpc19hcnJheSh4KSB7XG4gICAgcmV0dXJuIChPYmplY3QucHJvdG90eXBlLnRvU3RyaW5nLmNhbGwoeCkgPT09ICdbb2JqZWN0IEFycmF5XScpO1xufVxuXG5BcnJheS5wcm90b3R5cGUuZXF1YWxzID0gZnVuY3Rpb24gKGFycmF5KSB7XG4gICAgLy8gaWYgdGhlIG90aGVyIGFycmF5IGlzIGEgZmFsc3kgdmFsdWUsIHJldHVyblxuICAgIGlmICghYXJyYXkpXG4gICAgICAgIHJldHVybiBmYWxzZTtcblxuICAgIC8vIGNvbXBhcmUgbGVuZ3RocyAtIGNhbiBzYXZlIGEgbG90IG9mIHRpbWVcbiAgICBpZiAodGhpcy5sZW5ndGggIT0gYXJyYXkubGVuZ3RoKVxuICAgICAgICByZXR1cm4gZmFsc2U7XG5cbiAgICBmb3IgKHZhciBpID0gMCwgbD10aGlzLmxlbmd0aDsgaSA8IGw7IGkrKykge1xuICAgICAgICAvLyBDaGVjayBpZiB3ZSBoYXZlIG5lc3RlZCBhcnJheXNcbiAgICAgICAgaWYgKHRoaXNbaV0gaW5zdGFuY2VvZiBBcnJheSAmJiBhcnJheVtpXSBpbnN0YW5jZW9mIEFycmF5KSB7XG4gICAgICAgICAgICAvLyByZWN1cnNlIGludG8gdGhlIG5lc3RlZCBhcnJheXNcbiAgICAgICAgICAgIGlmICghdGhpc1tpXS5lcXVhbHMoYXJyYXlbaV0pKVxuICAgICAgICAgICAgICAgIHJldHVybiBmYWxzZTtcbiAgICAgICAgfVxuICAgICAgICBlbHNlIGlmICh0aGlzW2ldICE9IGFycmF5W2ldKSB7XG4gICAgICAgICAgICAvLyBXYXJuaW5nIC0gdHdvIGRpZmZlcmVudCBvYmplY3QgaW5zdGFuY2VzIHdpbGwgbmV2ZXIgYmUgZXF1YWw6IHt4OjIwfSAhPSB7eDoyMH1cbiAgICAgICAgICAgIHJldHVybiBmYWxzZTtcbiAgICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gdHJ1ZTtcbn07XG5cbmlmICh0eXBlb2YgU3RyaW5nLnByb3RvdHlwZS5zdGFydHNXaXRoICE9ICdmdW5jdGlvbicpIHtcbiAgU3RyaW5nLnByb3RvdHlwZS5zdGFydHNXaXRoID0gZnVuY3Rpb24gKHN0cil7XG4gICAgcmV0dXJuIHRoaXMuc2xpY2UoMCwgc3RyLmxlbmd0aCkgPT0gc3RyO1xuICB9O1xufVxuXG53aW5kb3cuVklTUFlfREVCVUcgPSBmYWxzZTtcbmZ1bmN0aW9uIGRlYnVnKG1zZykge1xuICAgIGlmICh3aW5kb3cuVklTUFlfREVCVUcpe1xuICAgICAgICBjb25zb2xlLmRlYnVnKG1zZyk7XG4gICAgfVxufVxuXG5tb2R1bGUuZXhwb3J0cyA9IHtkZWJ1ZzogZGVidWd9O1xuIiwidmFyIHNjcmVlbmZ1bCA9IHJlcXVpcmUoXCIuL2xpYi9zY3JlZW5mdWxsLm1pbi5qc1wiKTtcbnZhciBWaXNweUNhbnZhcyA9IHJlcXVpcmUoJy4vdmlzcHljYW52YXMuanMnKTtcbnZhciBnbG9vID0gcmVxdWlyZSgnLi9nbG9vLmpzJyk7XG52YXIgZXZlbnRzID0gcmVxdWlyZSgnLi9ldmVudHMuanMnKTtcbnZhciB1dGlsID0gcmVxdWlyZSgnLi91dGlsLmpzJyk7XG52YXIgZGF0YSA9IHJlcXVpcmUoJy4vZGF0YS5qcycpO1xucmVxdWlyZShcIi4vbGliL2pxdWVyeS5tb3VzZXdoZWVsLm1pbi5qc1wiKSgkKTtcblxudmFyIFZpc3B5ID0gZnVuY3Rpb24oKSB7XG4gICAgLy8gQ29uc3RydWN0b3Igb2YgdGhlIFZpc3B5IGxpYnJhcnkuXG4gICAgdGhpcy5ldmVudHMgPSBldmVudHM7XG4gICAgdGhpcy5nbG9vID0gZ2xvbztcbiAgICB0aGlzLl9pc19sb29wX3J1bm5pbmcgPSBmYWxzZTtcbiAgICAvLyBMaXN0IG9mIGNhbnZhc2VzIG9uIHRoZSBwYWdlLlxuICAgIHRoaXMuX2NhbnZhc2VzID0gW107XG59O1xuXG5WaXNweS5wcm90b3R5cGUuaW5pdCA9IGZ1bmN0aW9uKGNhbnZhc19pZCkge1xuICAgIHZhciBjYW52YXNfZWw7XG4gICAgY2FudmFzX2VsID0gJChjYW52YXNfaWQpO1xuICAgIC8vIEluaXRpYWxpemUgdGhlIGNhbnZhcy5cbiAgICB2YXIgY2FudmFzID0gbmV3IFZpc3B5Q2FudmFzKGNhbnZhc19lbCk7XG5cbiAgICBjYW52YXMuZGVhY3RpdmF0ZV9jb250ZXh0X21lbnUoKTtcblxuICAgIC8vIEluaXRpYWxpemUgZXZlbnRzLlxuICAgIHRoaXMuZXZlbnRzLmluaXQoY2FudmFzKTtcblxuICAgIC8vIEluaXRpYWxpemUgV2ViR0wuXG4gICAgdGhpcy5nbG9vLmluaXQoY2FudmFzKTtcblxuICAgIC8vIFJlZ2lzdGVyIHRoZSBjYW52YXMuXG4gICAgdGhpcy5yZWdpc3RlcihjYW52YXMpO1xuXG4gICAgcmV0dXJuIGNhbnZhcztcbn07XG5cblZpc3B5LnByb3RvdHlwZS5yZWdpc3RlciA9IGZ1bmN0aW9uKGNhbnZhcykge1xuICAgIC8qIFJlZ2lzdGVyIGEgY2FudmFzLiAqL1xuICAgIHRoaXMuX2NhbnZhc2VzLnB1c2goY2FudmFzKTtcbiAgICAvLyBjb25zb2xlLmRlYnVnKFwiUmVnaXN0ZXIgY2FudmFzXCIsIGNhbnZhcyk7XG59O1xuXG5WaXNweS5wcm90b3R5cGUudW5yZWdpc3RlciA9IGZ1bmN0aW9uKGNhbnZhcykge1xuICAgIC8qIFVucmVnaXN0ZXIgYSBjYW52YXMuICovXG4gICAgdmFyIGluZGV4ID0gdGhpcy5fY2FudmFzZXMuaW5kZXhPZihjYW52YXMpO1xuICAgIGlmIChpbmRleCA+IC0xKSB7XG4gICAgICAgIHRoaXMuX2NhbnZhc2VzLnNwbGljZShpbmRleCwgMSk7XG4gICAgfVxuICAgIC8vIGNvbnNvbGUuZGVidWcoXCJVbnJlZ2lzdGVyIGNhbnZhc1wiLCBjYW52YXMpO1xufTtcblxuXG4vKiBFdmVudCBsb29wICovXG5WaXNweS5wcm90b3R5cGUuc3RhcnRfZXZlbnRfbG9vcCA9IGZ1bmN0aW9uKCkge1xuXG4gICAgLy8gRG8gbm90IHN0YXJ0IHRoZSBldmVudCBsb29wIHR3aWNlLlxuICAgIGlmICh0aGlzLl9pc19sb29wX3J1bm5pbmcpIHJldHVybjtcblxuICAgIHdpbmRvdy5yZXF1ZXN0QW5pbUZyYW1lID0gKGZ1bmN0aW9uKCl7XG4gICAgICAgICAgcmV0dXJuICB3aW5kb3cucmVxdWVzdEFuaW1hdGlvbkZyYW1lICAgICAgIHx8XG4gICAgICAgICAgICAgICAgICB3aW5kb3cud2Via2l0UmVxdWVzdEFuaW1hdGlvbkZyYW1lIHx8XG4gICAgICAgICAgICAgICAgICB3aW5kb3cubW96UmVxdWVzdEFuaW1hdGlvbkZyYW1lICAgIHx8XG4gICAgICAgICAgICAgICAgICBmdW5jdGlvbihjKXtcbiAgICAgICAgICAgICAgICAgICAgd2luZG93LnNldFRpbWVvdXQoYywgMTAwMC4gLyA2MC4pO1xuICAgICAgICAgICAgICAgICAgfTtcbiAgICB9KSgpO1xuXG4gICAgLy8gXCJ0aGF0XCIgaXMgdGhlIGN1cnJlbnQgVmlzcHkgaW5zdGFuY2UuXG4gICAgdmFyIHRoYXQgPSB0aGlzO1xuICAgIChmdW5jdGlvbiBhbmltbG9vcCgpIHtcbiAgICAgICAgdGhhdC5fcmVxdWVzdF9pZCA9IHJlcXVlc3RBbmltRnJhbWUoYW5pbWxvb3ApO1xuICAgICAgICB0cnkge1xuICAgICAgICAgICAgLy8gQ2FsbCBldmVudF90aWNrKCkgb24gYWxsIGFjdGl2ZSBjYW52YXNlcy5cbiAgICAgICAgICAgIGZvciAodmFyIGkgPSAwOyBpIDwgdGhhdC5fY2FudmFzZXMubGVuZ3RoOyBpKyspIHtcbiAgICAgICAgICAgICAgICB0aGF0Ll9jYW52YXNlc1tpXS5ldmVudF90aWNrKCk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICAgICAgY2F0Y2goZXJyKSB7XG4gICAgICAgICAgICB0aGF0LnN0b3BfZXZlbnRfbG9vcCgpO1xuICAgICAgICAgICAgdGhyb3cgKGVycik7XG4gICAgICAgIH1cbiAgICB9KSgpO1xuXG4gICAgdGhpcy5faXNfbG9vcF9ydW5uaW5nID0gdHJ1ZTtcbiAgICBjb25zb2xlLmRlYnVnKFwiRXZlbnQgbG9vcCBzdGFydGVkLlwiKTtcbn07XG5cblZpc3B5LnByb3RvdHlwZS5zdG9wX2V2ZW50X2xvb3AgPSBmdW5jdGlvbigpIHtcbiAgICB3aW5kb3cuY2FuY2VsQW5pbWF0aW9uRnJhbWUodGhpcy5fcmVxdWVzdF9pZCk7XG4gICAgdGhpcy5faXNfbG9vcF9ydW5uaW5nID0gZmFsc2U7XG4gICAgY29uc29sZS5kZWJ1ZyhcIkV2ZW50IGxvb3Agc3RvcHBlZC5cIik7XG59O1xuXG5cbm1vZHVsZS5leHBvcnRzID0gbmV3IFZpc3B5KCk7XG4iLCJcbnZhciBWaXNweUNhbnZhcyA9IGZ1bmN0aW9uICgkZWwpIHtcbiAgICB0aGlzLiRlbCA9ICRlbDtcbn07XG5cbm1vZHVsZS5leHBvcnRzID0gVmlzcHlDYW52YXM7XG4iXX0=


/***/ }),

/***/ "./lib/webgl-backend.js":
/*!******************************!*\
  !*** ./lib/webgl-backend.js ***!
  \******************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var widgets = __webpack_require__(/*! @jupyter-widgets/base */ "@jupyter-widgets/base");
var vispy = __webpack_require__(/*! ./vispy.min.js */ "./lib/vispy.min.js");

function _inline_glir_commands(commands, buffers) {
    // Put back the buffers within the GLIR commands before passing them
    // to the GLIR JavaScript interpretor.
    for (var i = 0; i < commands.length; i++) {
        var command = commands[i];
        // Shader data commands are 3 elements, everything else 4
        if (command[0] == 'DATA') {
            console.info(command);
            if (command[3].shape !== undefined) {
                // already handled
                console.info("Skipping message processing, already handled...");
                continue;
            }
            var buffer_index = command[3]['buffer_index'];
            var buffer_shape = command[3]['buffer_shape'];
            var buffer_dtype = command[3]['buffer_dtype'];
            command[3] = buffers[buffer_index];
            // Add shape and type information to buffer object
            command[3].shape = buffer_shape;
            command[3].dtype = buffer_dtype;
        }
    }
    return commands;
}

// var vispy = require("/nbextensions/vispy/vispy.min.js");
// var widget, control;
// try {
//     widget = require("@jupyter-widgets/base");
//     control = require("@jupyter-widgets/controls");
// } catch (e) {
//     console.warn("Importing old ipywidgets <7.0");
//     widget = require("jupyter-js-widgets");
// }

var VispyView = widgets.DOMWidgetView.extend({

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

        on_msg: function(msg, buffers) {
            if (msg == undefined) return;
            // Receive and execute the GLIR commands.
            if (msg.msg_type == 'glir_commands') {
                var commands = msg.commands;
                // Get the buffers messages.
                if (msg.array_serialization == 'base64') {
                    var buffers_msg = msg.buffers;
                } else if (msg.array_serialization == 'binary') {
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
                console.log("on_msg: %s : %s", msg.msg_type, msg.commands);
                var commands_inlined = _inline_glir_commands(commands, buffers_msg);
                for (var i = 0; i < commands_inlined.length; i++) {
                    var command = commands[i];
                    console.debug(command);
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


module.exports = {
    VispyView: VispyView
};

/***/ }),

/***/ "./package.json":
/*!**********************!*\
  !*** ./package.json ***!
  \**********************/
/*! exports provided: name, version, description, author, license, main, repository, keywords, files, scripts, devDependencies, dependencies, default */
/***/ (function(module) {

module.exports = {"name":"vispy","version":"0.1.0","description":"A Custom Jupyter Widget Library for the VisPy Python Library","author":"Vispy Development Team","license":"BSD-3-Clause","main":"lib/index.js","repository":{"type":"git","url":"https://github.com/VisPy/vispy.git"},"keywords":["jupyter","widgets","ipython","ipywidgets"],"files":["lib/**/*.js","dist/*.js"],"scripts":{"clean":"rimraf dist/","prepare":"webpack --mode=production","test":"echo \"Error: no test specified\" && exit 1","watch":"npm-run-all -p watch:*","watch:nbextension":"webpack --watch --mode=development"},"devDependencies":{"npm-run-all":"^4.1.5","npm-watch":"^0.6.0","raw-loader":"^2.0.0","rimraf":"^2.6.3","source-map-loader":"^0.2.4","webpack":"^4.29.6","webpack-cli":"^3.3.0"},"dependencies":{"@jupyter-widgets/base":"^1.2.3","lodash":"^4.17.11"}};

/***/ }),

/***/ "@jupyter-widgets/base":
/*!****************************************!*\
  !*** external "@jupyter-widgets/base" ***!
  \****************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = __WEBPACK_EXTERNAL_MODULE__jupyter_widgets_base__;

/***/ })

/******/ })});;
//# sourceMappingURL=index.js.map