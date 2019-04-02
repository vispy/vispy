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
            var new_width = shape[shape.length - 2] * shape[shape.length - 1];
            var alignment = _get_alignment(new_width);
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
            handle: c.gl.createShader(c.gl.VERTEX_SHADER),
        };
    }
    else if (cls == 'FragmentShader') {
        debug("Creating FragmentShader '{0}'.".format(id));
        c._ns[id] = {
            object_type: cls,
            handle: c.gl.createShader(c.gl.FRAGMENT_SHADER),
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
    var uniform_handle;
    var uniform_function;
    var uniform_info;

    c.gl.useProgram(program_handle);

    // Check the cache.
    if (c._ns[program_id].uniforms[name] == undefined) {
        // If necessary, we create the uniform and cache both its handle and
        // GL function.
        debug("Creating uniform '{0}' for program '{1}'.".format(
                name, program_id
            ));
        uniform_handle = c.gl.getUniformLocation(program_handle, name);
        uniform_function = get_uniform_function(type);
        // We cache the uniform handle and the uniform function name as well.
        c._ns[program_id].uniforms[name] = [uniform_handle, uniform_function];
    }

    debug("Setting uniform '{0}' to '{1}' with {2} elements.".format(
            name, value, value.length
        ));
    uniform_info = c._ns[program_id].uniforms[name];
    uniform_handle = uniform_info[0];
    uniform_function = uniform_info[1];
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
        debug('Removing previously assigned texture for \'{0}\''.format(sampler_name));
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
    var texture;
    var attribute_name;
    var texture_id;

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
        texture = textures[texture_id];
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
    var count;
    if (selection.length == 2) {
        // Draw the program without index buffer.
        var start = selection[0];
        count = selection[1];
        debug("Rendering program '{0}' with {1}.".format(
            program_id, mode));
        c.gl.drawArrays(c.gl[mode], start, count);
    }
    else if (selection.length == 3) {
        // Draw the program with index buffer.
        var index_buffer_id = selection[0];
        var index_buffer_type = selection[1];
        count = selection[2];
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
        texture = textures[texture_id];
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
