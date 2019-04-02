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
    var storage_type = data.storage_type;

    // data can also be just a normal typed array, in which case we just return
    // the argument value.
    if (storage_type == undefined) {
        return data;
    }

    var data_type = data.data_type;
    var contents = data.buffer;

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
