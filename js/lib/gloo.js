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
    ext = c.gl.getExtension('OES_element_index_uint') ||
        c.gl.getExtension('MOZ_OES_element_index_uint') ||
        c.gl.getExtension('WEBKIT_OES_element_index_uint');
    if (ext === null) {
        console.warn('Extension \'OES_element_index_uint\' is not supported in this browser. Some features may not work as expected');
    }
    ext = c.gl.getExtension('OES_texture_float');
    // ||
    //     c.gl.getExtension('MOZ_OES_element_index_uint') ||
    //     c.gl.getExtension('WEBKIT_OES_element_index_uint');
    if (ext === null) {
        console.warn('Extension \'OES_texture_float\' is not supported in this browser. Some features may not work as expected');
    }

    ext = c.gl.getExtension('OES_texture_float_linear');
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
