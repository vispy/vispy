// ------------------------------------
// Automatically generated, do not edit
// ------------------------------------
const float kernel_bias  = -0.23437733388100893;
const float kernel_scale = 1.2419743353536359;
const float kernel_size = 1024;
const vec4 bits = vec4(1, 0.00390625, 1.52587890625e-05, 5.960464477539063e-08);
uniform sampler2D u_kernel;

float unpack_unit(vec4 rgba) {
    // return rgba.r;  // uncomment this for r32f debugging
    return dot(rgba, bits);
}

float unpack_ieee(vec4 rgba) {
    // return rgba.r;  // uncomment this for r32f debugging
    rgba.rgba = rgba.abgr * 255;
    float sign = 1 - step(128 , rgba[0]) * 2;
    float exponent = 2 * mod(rgba[0] , 128) + step(128 , rgba[1]) - 127;
    float mantissa = mod(rgba[1] , 128) * 65536 + rgba[2] * 256 + rgba[3] + float(0x800000);
    return sign * exp2(exponent) * (mantissa * exp2(-23.));
}


float unpack_interpolate(sampler2D kernel, vec2 uv) {
    // return texture2D(kernel, uv).r;  //uncomment this for r32f debug without interpolation
    float kpixel = 1. / kernel_size;
    float u = uv.x / kpixel;
    float v = uv.y;
    float uf = fract(u);
    u = (u - uf) * kpixel;
    float d0 = unpack_unit(texture2D(kernel, vec2(u, v)));
    float d1 = unpack_unit(texture2D(kernel, vec2(u + 1. * kpixel, v)));
    return mix(d0, d1, uf);
}

vec4 filter1D_radius1(sampler2D kernel, float index, float x, vec4 c0, vec4 c1) {
    float w, w_sum = 0;
    vec4 r = vec4(0);
    
    w = unpack_interpolate(kernel, vec2(0.0 + (x / 1), index));
    w = w * kernel_scale + kernel_bias;
    r += c0 * w;
    w = unpack_interpolate(kernel, vec2(1.0 - (x / 1), index));
    w = w * kernel_scale + kernel_bias;
    r += c1 * w;
    return r;
}

vec4 filter2D_radius1(sampler2D texture, sampler2D kernel, float index, vec2 uv, vec2 pixel) {
    vec2 texel = uv / pixel - vec2(0.5);
    vec2 f = fract(texel);
    texel = (texel - fract(texel) + vec2(0.001)) * pixel;
    
    vec4 t0 = filter1D_radius1(kernel, index, f.x,
        texture2D(texture, texel + vec2(0, 0) * pixel),
        texture2D(texture, texel + vec2(1, 0) * pixel));
    vec4 t1 = filter1D_radius1(kernel, index, f.x,
        texture2D(texture, texel + vec2(0, 1) * pixel),
        texture2D(texture, texel + vec2(1, 1) * pixel));
    return filter1D_radius1(kernel, index, f.y, t0, t1);
}

vec4 filter3D_radius1(sampler3D texture, sampler2D kernel, float index, vec3 uv, vec3 pixel) {
    vec3 texel = uv / pixel - vec3(0.5);
    vec3 f = fract(texel);
    texel = (texel - fract(texel) + vec3(0.001)) * pixel;
    
    vec4 t00 = filter1D_radius1(kernel, index, f.x,
        texture3D(texture, texel + vec3(0, 0, 0) * pixel),
        texture3D(texture, texel + vec3(1, 0, 0) * pixel));
    vec4 t01 = filter1D_radius1(kernel, index, f.x,
        texture3D(texture, texel + vec3(0, 1, 0) * pixel),
        texture3D(texture, texel + vec3(1, 1, 0) * pixel));
    vec4 t10 = filter1D_radius1(kernel, index, f.x,
        texture3D(texture, texel + vec3(0, 0, 1) * pixel),
        texture3D(texture, texel + vec3(1, 0, 1) * pixel));
    vec4 t11 = filter1D_radius1(kernel, index, f.x,
        texture3D(texture, texel + vec3(0, 1, 1) * pixel),
        texture3D(texture, texel + vec3(1, 1, 1) * pixel));
    
    vec4 t0 = filter1D_radius1(kernel, index, f.y, t00, t01);
    vec4 t1 = filter1D_radius1(kernel, index, f.y, t10, t11);
    return filter1D_radius1(kernel, index, f.z, t0, t1);
}

vec4 filter1D_radius2(sampler2D kernel, float index, float x, vec4 c0, vec4 c1, vec4 c2, vec4 c3) {
    float w, w_sum = 0;
    vec4 r = vec4(0);
    
    w = unpack_interpolate(kernel, vec2(0.5 + (x / 2), index));
    w = w * kernel_scale + kernel_bias;
    r += c0 * w;
    w = unpack_interpolate(kernel, vec2(0.5 - (x / 2), index));
    w = w * kernel_scale + kernel_bias;
    r += c2 * w;
    w = unpack_interpolate(kernel, vec2(0.0 + (x / 2), index));
    w = w * kernel_scale + kernel_bias;
    r += c1 * w;
    w = unpack_interpolate(kernel, vec2(1.0 - (x / 2), index));
    w = w * kernel_scale + kernel_bias;
    r += c3 * w;
    return r;
}

vec4 filter2D_radius2(sampler2D texture, sampler2D kernel, float index, vec2 uv, vec2 pixel) {
    vec2 texel = uv / pixel - vec2(0.5);
    vec2 f = fract(texel);
    texel = (texel - fract(texel) + vec2(0.001)) * pixel;
    
    vec4 t0 = filter1D_radius2(kernel, index, f.x,
        texture2D(texture, texel + vec2(-1, -1) * pixel),
        texture2D(texture, texel + vec2(0, -1) * pixel),
        texture2D(texture, texel + vec2(1, -1) * pixel),
        texture2D(texture, texel + vec2(2, -1) * pixel));
    vec4 t1 = filter1D_radius2(kernel, index, f.x,
        texture2D(texture, texel + vec2(-1, 0) * pixel),
        texture2D(texture, texel + vec2(0, 0) * pixel),
        texture2D(texture, texel + vec2(1, 0) * pixel),
        texture2D(texture, texel + vec2(2, 0) * pixel));
    vec4 t2 = filter1D_radius2(kernel, index, f.x,
        texture2D(texture, texel + vec2(-1, 1) * pixel),
        texture2D(texture, texel + vec2(0, 1) * pixel),
        texture2D(texture, texel + vec2(1, 1) * pixel),
        texture2D(texture, texel + vec2(2, 1) * pixel));
    vec4 t3 = filter1D_radius2(kernel, index, f.x,
        texture2D(texture, texel + vec2(-1, 2) * pixel),
        texture2D(texture, texel + vec2(0, 2) * pixel),
        texture2D(texture, texel + vec2(1, 2) * pixel),
        texture2D(texture, texel + vec2(2, 2) * pixel));
    return filter1D_radius2(kernel, index, f.y, t0, t1, t2, t3);
}

vec4 filter3D_radius2(sampler3D texture, sampler2D kernel, float index, vec3 uv, vec3 pixel) {
    vec3 texel = uv / pixel - vec3(0.5);
    vec3 f = fract(texel);
    texel = (texel - fract(texel) + vec3(0.001)) * pixel;
    
    vec4 t00 = filter1D_radius2(kernel, index, f.x,
        texture3D(texture, texel + vec3(-1, -1, -1) * pixel),
        texture3D(texture, texel + vec3(0, -1, -1) * pixel),
        texture3D(texture, texel + vec3(1, -1, -1) * pixel),
        texture3D(texture, texel + vec3(2, -1, -1) * pixel));
    vec4 t01 = filter1D_radius2(kernel, index, f.x,
        texture3D(texture, texel + vec3(-1, 0, -1) * pixel),
        texture3D(texture, texel + vec3(0, 0, -1) * pixel),
        texture3D(texture, texel + vec3(1, 0, -1) * pixel),
        texture3D(texture, texel + vec3(2, 0, -1) * pixel));
    vec4 t02 = filter1D_radius2(kernel, index, f.x,
        texture3D(texture, texel + vec3(-1, 1, -1) * pixel),
        texture3D(texture, texel + vec3(0, 1, -1) * pixel),
        texture3D(texture, texel + vec3(1, 1, -1) * pixel),
        texture3D(texture, texel + vec3(2, 1, -1) * pixel));
    vec4 t03 = filter1D_radius2(kernel, index, f.x,
        texture3D(texture, texel + vec3(-1, 2, -1) * pixel),
        texture3D(texture, texel + vec3(0, 2, -1) * pixel),
        texture3D(texture, texel + vec3(1, 2, -1) * pixel),
        texture3D(texture, texel + vec3(2, 2, -1) * pixel));
    vec4 t10 = filter1D_radius2(kernel, index, f.x,
        texture3D(texture, texel + vec3(-1, -1, 0) * pixel),
        texture3D(texture, texel + vec3(0, -1, 0) * pixel),
        texture3D(texture, texel + vec3(1, -1, 0) * pixel),
        texture3D(texture, texel + vec3(2, -1, 0) * pixel));
    vec4 t11 = filter1D_radius2(kernel, index, f.x,
        texture3D(texture, texel + vec3(-1, 0, 0) * pixel),
        texture3D(texture, texel + vec3(0, 0, 0) * pixel),
        texture3D(texture, texel + vec3(1, 0, 0) * pixel),
        texture3D(texture, texel + vec3(2, 0, 0) * pixel));
    vec4 t12 = filter1D_radius2(kernel, index, f.x,
        texture3D(texture, texel + vec3(-1, 1, 0) * pixel),
        texture3D(texture, texel + vec3(0, 1, 0) * pixel),
        texture3D(texture, texel + vec3(1, 1, 0) * pixel),
        texture3D(texture, texel + vec3(2, 1, 0) * pixel));
    vec4 t13 = filter1D_radius2(kernel, index, f.x,
        texture3D(texture, texel + vec3(-1, 2, 0) * pixel),
        texture3D(texture, texel + vec3(0, 2, 0) * pixel),
        texture3D(texture, texel + vec3(1, 2, 0) * pixel),
        texture3D(texture, texel + vec3(2, 2, 0) * pixel));
    vec4 t20 = filter1D_radius2(kernel, index, f.x,
        texture3D(texture, texel + vec3(-1, -1, 1) * pixel),
        texture3D(texture, texel + vec3(0, -1, 1) * pixel),
        texture3D(texture, texel + vec3(1, -1, 1) * pixel),
        texture3D(texture, texel + vec3(2, -1, 1) * pixel));
    vec4 t21 = filter1D_radius2(kernel, index, f.x,
        texture3D(texture, texel + vec3(-1, 0, 1) * pixel),
        texture3D(texture, texel + vec3(0, 0, 1) * pixel),
        texture3D(texture, texel + vec3(1, 0, 1) * pixel),
        texture3D(texture, texel + vec3(2, 0, 1) * pixel));
    vec4 t22 = filter1D_radius2(kernel, index, f.x,
        texture3D(texture, texel + vec3(-1, 1, 1) * pixel),
        texture3D(texture, texel + vec3(0, 1, 1) * pixel),
        texture3D(texture, texel + vec3(1, 1, 1) * pixel),
        texture3D(texture, texel + vec3(2, 1, 1) * pixel));
    vec4 t23 = filter1D_radius2(kernel, index, f.x,
        texture3D(texture, texel + vec3(-1, 2, 1) * pixel),
        texture3D(texture, texel + vec3(0, 2, 1) * pixel),
        texture3D(texture, texel + vec3(1, 2, 1) * pixel),
        texture3D(texture, texel + vec3(2, 2, 1) * pixel));
    vec4 t30 = filter1D_radius2(kernel, index, f.x,
        texture3D(texture, texel + vec3(-1, -1, 2) * pixel),
        texture3D(texture, texel + vec3(0, -1, 2) * pixel),
        texture3D(texture, texel + vec3(1, -1, 2) * pixel),
        texture3D(texture, texel + vec3(2, -1, 2) * pixel));
    vec4 t31 = filter1D_radius2(kernel, index, f.x,
        texture3D(texture, texel + vec3(-1, 0, 2) * pixel),
        texture3D(texture, texel + vec3(0, 0, 2) * pixel),
        texture3D(texture, texel + vec3(1, 0, 2) * pixel),
        texture3D(texture, texel + vec3(2, 0, 2) * pixel));
    vec4 t32 = filter1D_radius2(kernel, index, f.x,
        texture3D(texture, texel + vec3(-1, 1, 2) * pixel),
        texture3D(texture, texel + vec3(0, 1, 2) * pixel),
        texture3D(texture, texel + vec3(1, 1, 2) * pixel),
        texture3D(texture, texel + vec3(2, 1, 2) * pixel));
    vec4 t33 = filter1D_radius2(kernel, index, f.x,
        texture3D(texture, texel + vec3(-1, 2, 2) * pixel),
        texture3D(texture, texel + vec3(0, 2, 2) * pixel),
        texture3D(texture, texel + vec3(1, 2, 2) * pixel),
        texture3D(texture, texel + vec3(2, 2, 2) * pixel));
    
    vec4 t0 = filter1D_radius2(kernel, index, f.y, t00, t01, t02, t03);
    vec4 t1 = filter1D_radius2(kernel, index, f.y, t10, t11, t12, t13);
    vec4 t2 = filter1D_radius2(kernel, index, f.y, t20, t21, t22, t23);
    vec4 t3 = filter1D_radius2(kernel, index, f.y, t30, t31, t32, t33);
    return filter1D_radius2(kernel, index, f.z, t0, t1, t2, t3);
}

vec4 filter1D_radius3(sampler2D kernel, float index, float x, vec4 c0, vec4 c1, vec4 c2, vec4 c3, vec4 c4, vec4 c5) {
    float w, w_sum = 0;
    vec4 r = vec4(0);
    
    w = unpack_interpolate(kernel, vec2(0.6666666666666667 + (x / 3), index));
    w = w * kernel_scale + kernel_bias;
    r += c0 * w;
    w = unpack_interpolate(kernel, vec2(0.3333333333333333 - (x / 3), index));
    w = w * kernel_scale + kernel_bias;
    r += c3 * w;
    w = unpack_interpolate(kernel, vec2(0.33333333333333337 + (x / 3), index));
    w = w * kernel_scale + kernel_bias;
    r += c1 * w;
    w = unpack_interpolate(kernel, vec2(0.6666666666666666 - (x / 3), index));
    w = w * kernel_scale + kernel_bias;
    r += c4 * w;
    w = unpack_interpolate(kernel, vec2(0.0 + (x / 3), index));
    w = w * kernel_scale + kernel_bias;
    r += c2 * w;
    w = unpack_interpolate(kernel, vec2(1.0 - (x / 3), index));
    w = w * kernel_scale + kernel_bias;
    r += c5 * w;
    return r;
}

vec4 filter2D_radius3(sampler2D texture, sampler2D kernel, float index, vec2 uv, vec2 pixel) {
    vec2 texel = uv / pixel - vec2(0.5);
    vec2 f = fract(texel);
    texel = (texel - fract(texel) + vec2(0.001)) * pixel;
    
    vec4 t0 = filter1D_radius3(kernel, index, f.x,
        texture2D(texture, texel + vec2(-2, -2) * pixel),
        texture2D(texture, texel + vec2(-1, -2) * pixel),
        texture2D(texture, texel + vec2(0, -2) * pixel),
        texture2D(texture, texel + vec2(1, -2) * pixel),
        texture2D(texture, texel + vec2(2, -2) * pixel),
        texture2D(texture, texel + vec2(3, -2) * pixel));
    vec4 t1 = filter1D_radius3(kernel, index, f.x,
        texture2D(texture, texel + vec2(-2, -1) * pixel),
        texture2D(texture, texel + vec2(-1, -1) * pixel),
        texture2D(texture, texel + vec2(0, -1) * pixel),
        texture2D(texture, texel + vec2(1, -1) * pixel),
        texture2D(texture, texel + vec2(2, -1) * pixel),
        texture2D(texture, texel + vec2(3, -1) * pixel));
    vec4 t2 = filter1D_radius3(kernel, index, f.x,
        texture2D(texture, texel + vec2(-2, 0) * pixel),
        texture2D(texture, texel + vec2(-1, 0) * pixel),
        texture2D(texture, texel + vec2(0, 0) * pixel),
        texture2D(texture, texel + vec2(1, 0) * pixel),
        texture2D(texture, texel + vec2(2, 0) * pixel),
        texture2D(texture, texel + vec2(3, 0) * pixel));
    vec4 t3 = filter1D_radius3(kernel, index, f.x,
        texture2D(texture, texel + vec2(-2, 1) * pixel),
        texture2D(texture, texel + vec2(-1, 1) * pixel),
        texture2D(texture, texel + vec2(0, 1) * pixel),
        texture2D(texture, texel + vec2(1, 1) * pixel),
        texture2D(texture, texel + vec2(2, 1) * pixel),
        texture2D(texture, texel + vec2(3, 1) * pixel));
    vec4 t4 = filter1D_radius3(kernel, index, f.x,
        texture2D(texture, texel + vec2(-2, 2) * pixel),
        texture2D(texture, texel + vec2(-1, 2) * pixel),
        texture2D(texture, texel + vec2(0, 2) * pixel),
        texture2D(texture, texel + vec2(1, 2) * pixel),
        texture2D(texture, texel + vec2(2, 2) * pixel),
        texture2D(texture, texel + vec2(3, 2) * pixel));
    vec4 t5 = filter1D_radius3(kernel, index, f.x,
        texture2D(texture, texel + vec2(-2, 3) * pixel),
        texture2D(texture, texel + vec2(-1, 3) * pixel),
        texture2D(texture, texel + vec2(0, 3) * pixel),
        texture2D(texture, texel + vec2(1, 3) * pixel),
        texture2D(texture, texel + vec2(2, 3) * pixel),
        texture2D(texture, texel + vec2(3, 3) * pixel));
    return filter1D_radius3(kernel, index, f.y, t0, t1, t2, t3, t4, t5);
}

vec4 filter3D_radius3(sampler3D texture, sampler2D kernel, float index, vec3 uv, vec3 pixel) {
    vec3 texel = uv / pixel - vec3(0.5);
    vec3 f = fract(texel);
    texel = (texel - fract(texel) + vec3(0.001)) * pixel;
    
    vec4 t00 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, -2, -2) * pixel),
        texture3D(texture, texel + vec3(-1, -2, -2) * pixel),
        texture3D(texture, texel + vec3(0, -2, -2) * pixel),
        texture3D(texture, texel + vec3(1, -2, -2) * pixel),
        texture3D(texture, texel + vec3(2, -2, -2) * pixel),
        texture3D(texture, texel + vec3(3, -2, -2) * pixel));
    vec4 t01 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, -1, -2) * pixel),
        texture3D(texture, texel + vec3(-1, -1, -2) * pixel),
        texture3D(texture, texel + vec3(0, -1, -2) * pixel),
        texture3D(texture, texel + vec3(1, -1, -2) * pixel),
        texture3D(texture, texel + vec3(2, -1, -2) * pixel),
        texture3D(texture, texel + vec3(3, -1, -2) * pixel));
    vec4 t02 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 0, -2) * pixel),
        texture3D(texture, texel + vec3(-1, 0, -2) * pixel),
        texture3D(texture, texel + vec3(0, 0, -2) * pixel),
        texture3D(texture, texel + vec3(1, 0, -2) * pixel),
        texture3D(texture, texel + vec3(2, 0, -2) * pixel),
        texture3D(texture, texel + vec3(3, 0, -2) * pixel));
    vec4 t03 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 1, -2) * pixel),
        texture3D(texture, texel + vec3(-1, 1, -2) * pixel),
        texture3D(texture, texel + vec3(0, 1, -2) * pixel),
        texture3D(texture, texel + vec3(1, 1, -2) * pixel),
        texture3D(texture, texel + vec3(2, 1, -2) * pixel),
        texture3D(texture, texel + vec3(3, 1, -2) * pixel));
    vec4 t04 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 2, -2) * pixel),
        texture3D(texture, texel + vec3(-1, 2, -2) * pixel),
        texture3D(texture, texel + vec3(0, 2, -2) * pixel),
        texture3D(texture, texel + vec3(1, 2, -2) * pixel),
        texture3D(texture, texel + vec3(2, 2, -2) * pixel),
        texture3D(texture, texel + vec3(3, 2, -2) * pixel));
    vec4 t05 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 3, -2) * pixel),
        texture3D(texture, texel + vec3(-1, 3, -2) * pixel),
        texture3D(texture, texel + vec3(0, 3, -2) * pixel),
        texture3D(texture, texel + vec3(1, 3, -2) * pixel),
        texture3D(texture, texel + vec3(2, 3, -2) * pixel),
        texture3D(texture, texel + vec3(3, 3, -2) * pixel));
    vec4 t10 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, -2, -1) * pixel),
        texture3D(texture, texel + vec3(-1, -2, -1) * pixel),
        texture3D(texture, texel + vec3(0, -2, -1) * pixel),
        texture3D(texture, texel + vec3(1, -2, -1) * pixel),
        texture3D(texture, texel + vec3(2, -2, -1) * pixel),
        texture3D(texture, texel + vec3(3, -2, -1) * pixel));
    vec4 t11 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, -1, -1) * pixel),
        texture3D(texture, texel + vec3(-1, -1, -1) * pixel),
        texture3D(texture, texel + vec3(0, -1, -1) * pixel),
        texture3D(texture, texel + vec3(1, -1, -1) * pixel),
        texture3D(texture, texel + vec3(2, -1, -1) * pixel),
        texture3D(texture, texel + vec3(3, -1, -1) * pixel));
    vec4 t12 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 0, -1) * pixel),
        texture3D(texture, texel + vec3(-1, 0, -1) * pixel),
        texture3D(texture, texel + vec3(0, 0, -1) * pixel),
        texture3D(texture, texel + vec3(1, 0, -1) * pixel),
        texture3D(texture, texel + vec3(2, 0, -1) * pixel),
        texture3D(texture, texel + vec3(3, 0, -1) * pixel));
    vec4 t13 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 1, -1) * pixel),
        texture3D(texture, texel + vec3(-1, 1, -1) * pixel),
        texture3D(texture, texel + vec3(0, 1, -1) * pixel),
        texture3D(texture, texel + vec3(1, 1, -1) * pixel),
        texture3D(texture, texel + vec3(2, 1, -1) * pixel),
        texture3D(texture, texel + vec3(3, 1, -1) * pixel));
    vec4 t14 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 2, -1) * pixel),
        texture3D(texture, texel + vec3(-1, 2, -1) * pixel),
        texture3D(texture, texel + vec3(0, 2, -1) * pixel),
        texture3D(texture, texel + vec3(1, 2, -1) * pixel),
        texture3D(texture, texel + vec3(2, 2, -1) * pixel),
        texture3D(texture, texel + vec3(3, 2, -1) * pixel));
    vec4 t15 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 3, -1) * pixel),
        texture3D(texture, texel + vec3(-1, 3, -1) * pixel),
        texture3D(texture, texel + vec3(0, 3, -1) * pixel),
        texture3D(texture, texel + vec3(1, 3, -1) * pixel),
        texture3D(texture, texel + vec3(2, 3, -1) * pixel),
        texture3D(texture, texel + vec3(3, 3, -1) * pixel));
    vec4 t20 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, -2, 0) * pixel),
        texture3D(texture, texel + vec3(-1, -2, 0) * pixel),
        texture3D(texture, texel + vec3(0, -2, 0) * pixel),
        texture3D(texture, texel + vec3(1, -2, 0) * pixel),
        texture3D(texture, texel + vec3(2, -2, 0) * pixel),
        texture3D(texture, texel + vec3(3, -2, 0) * pixel));
    vec4 t21 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, -1, 0) * pixel),
        texture3D(texture, texel + vec3(-1, -1, 0) * pixel),
        texture3D(texture, texel + vec3(0, -1, 0) * pixel),
        texture3D(texture, texel + vec3(1, -1, 0) * pixel),
        texture3D(texture, texel + vec3(2, -1, 0) * pixel),
        texture3D(texture, texel + vec3(3, -1, 0) * pixel));
    vec4 t22 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 0, 0) * pixel),
        texture3D(texture, texel + vec3(-1, 0, 0) * pixel),
        texture3D(texture, texel + vec3(0, 0, 0) * pixel),
        texture3D(texture, texel + vec3(1, 0, 0) * pixel),
        texture3D(texture, texel + vec3(2, 0, 0) * pixel),
        texture3D(texture, texel + vec3(3, 0, 0) * pixel));
    vec4 t23 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 1, 0) * pixel),
        texture3D(texture, texel + vec3(-1, 1, 0) * pixel),
        texture3D(texture, texel + vec3(0, 1, 0) * pixel),
        texture3D(texture, texel + vec3(1, 1, 0) * pixel),
        texture3D(texture, texel + vec3(2, 1, 0) * pixel),
        texture3D(texture, texel + vec3(3, 1, 0) * pixel));
    vec4 t24 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 2, 0) * pixel),
        texture3D(texture, texel + vec3(-1, 2, 0) * pixel),
        texture3D(texture, texel + vec3(0, 2, 0) * pixel),
        texture3D(texture, texel + vec3(1, 2, 0) * pixel),
        texture3D(texture, texel + vec3(2, 2, 0) * pixel),
        texture3D(texture, texel + vec3(3, 2, 0) * pixel));
    vec4 t25 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 3, 0) * pixel),
        texture3D(texture, texel + vec3(-1, 3, 0) * pixel),
        texture3D(texture, texel + vec3(0, 3, 0) * pixel),
        texture3D(texture, texel + vec3(1, 3, 0) * pixel),
        texture3D(texture, texel + vec3(2, 3, 0) * pixel),
        texture3D(texture, texel + vec3(3, 3, 0) * pixel));
    vec4 t30 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, -2, 1) * pixel),
        texture3D(texture, texel + vec3(-1, -2, 1) * pixel),
        texture3D(texture, texel + vec3(0, -2, 1) * pixel),
        texture3D(texture, texel + vec3(1, -2, 1) * pixel),
        texture3D(texture, texel + vec3(2, -2, 1) * pixel),
        texture3D(texture, texel + vec3(3, -2, 1) * pixel));
    vec4 t31 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, -1, 1) * pixel),
        texture3D(texture, texel + vec3(-1, -1, 1) * pixel),
        texture3D(texture, texel + vec3(0, -1, 1) * pixel),
        texture3D(texture, texel + vec3(1, -1, 1) * pixel),
        texture3D(texture, texel + vec3(2, -1, 1) * pixel),
        texture3D(texture, texel + vec3(3, -1, 1) * pixel));
    vec4 t32 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 0, 1) * pixel),
        texture3D(texture, texel + vec3(-1, 0, 1) * pixel),
        texture3D(texture, texel + vec3(0, 0, 1) * pixel),
        texture3D(texture, texel + vec3(1, 0, 1) * pixel),
        texture3D(texture, texel + vec3(2, 0, 1) * pixel),
        texture3D(texture, texel + vec3(3, 0, 1) * pixel));
    vec4 t33 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 1, 1) * pixel),
        texture3D(texture, texel + vec3(-1, 1, 1) * pixel),
        texture3D(texture, texel + vec3(0, 1, 1) * pixel),
        texture3D(texture, texel + vec3(1, 1, 1) * pixel),
        texture3D(texture, texel + vec3(2, 1, 1) * pixel),
        texture3D(texture, texel + vec3(3, 1, 1) * pixel));
    vec4 t34 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 2, 1) * pixel),
        texture3D(texture, texel + vec3(-1, 2, 1) * pixel),
        texture3D(texture, texel + vec3(0, 2, 1) * pixel),
        texture3D(texture, texel + vec3(1, 2, 1) * pixel),
        texture3D(texture, texel + vec3(2, 2, 1) * pixel),
        texture3D(texture, texel + vec3(3, 2, 1) * pixel));
    vec4 t35 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 3, 1) * pixel),
        texture3D(texture, texel + vec3(-1, 3, 1) * pixel),
        texture3D(texture, texel + vec3(0, 3, 1) * pixel),
        texture3D(texture, texel + vec3(1, 3, 1) * pixel),
        texture3D(texture, texel + vec3(2, 3, 1) * pixel),
        texture3D(texture, texel + vec3(3, 3, 1) * pixel));
    vec4 t40 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, -2, 2) * pixel),
        texture3D(texture, texel + vec3(-1, -2, 2) * pixel),
        texture3D(texture, texel + vec3(0, -2, 2) * pixel),
        texture3D(texture, texel + vec3(1, -2, 2) * pixel),
        texture3D(texture, texel + vec3(2, -2, 2) * pixel),
        texture3D(texture, texel + vec3(3, -2, 2) * pixel));
    vec4 t41 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, -1, 2) * pixel),
        texture3D(texture, texel + vec3(-1, -1, 2) * pixel),
        texture3D(texture, texel + vec3(0, -1, 2) * pixel),
        texture3D(texture, texel + vec3(1, -1, 2) * pixel),
        texture3D(texture, texel + vec3(2, -1, 2) * pixel),
        texture3D(texture, texel + vec3(3, -1, 2) * pixel));
    vec4 t42 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 0, 2) * pixel),
        texture3D(texture, texel + vec3(-1, 0, 2) * pixel),
        texture3D(texture, texel + vec3(0, 0, 2) * pixel),
        texture3D(texture, texel + vec3(1, 0, 2) * pixel),
        texture3D(texture, texel + vec3(2, 0, 2) * pixel),
        texture3D(texture, texel + vec3(3, 0, 2) * pixel));
    vec4 t43 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 1, 2) * pixel),
        texture3D(texture, texel + vec3(-1, 1, 2) * pixel),
        texture3D(texture, texel + vec3(0, 1, 2) * pixel),
        texture3D(texture, texel + vec3(1, 1, 2) * pixel),
        texture3D(texture, texel + vec3(2, 1, 2) * pixel),
        texture3D(texture, texel + vec3(3, 1, 2) * pixel));
    vec4 t44 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 2, 2) * pixel),
        texture3D(texture, texel + vec3(-1, 2, 2) * pixel),
        texture3D(texture, texel + vec3(0, 2, 2) * pixel),
        texture3D(texture, texel + vec3(1, 2, 2) * pixel),
        texture3D(texture, texel + vec3(2, 2, 2) * pixel),
        texture3D(texture, texel + vec3(3, 2, 2) * pixel));
    vec4 t45 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 3, 2) * pixel),
        texture3D(texture, texel + vec3(-1, 3, 2) * pixel),
        texture3D(texture, texel + vec3(0, 3, 2) * pixel),
        texture3D(texture, texel + vec3(1, 3, 2) * pixel),
        texture3D(texture, texel + vec3(2, 3, 2) * pixel),
        texture3D(texture, texel + vec3(3, 3, 2) * pixel));
    vec4 t50 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, -2, 3) * pixel),
        texture3D(texture, texel + vec3(-1, -2, 3) * pixel),
        texture3D(texture, texel + vec3(0, -2, 3) * pixel),
        texture3D(texture, texel + vec3(1, -2, 3) * pixel),
        texture3D(texture, texel + vec3(2, -2, 3) * pixel),
        texture3D(texture, texel + vec3(3, -2, 3) * pixel));
    vec4 t51 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, -1, 3) * pixel),
        texture3D(texture, texel + vec3(-1, -1, 3) * pixel),
        texture3D(texture, texel + vec3(0, -1, 3) * pixel),
        texture3D(texture, texel + vec3(1, -1, 3) * pixel),
        texture3D(texture, texel + vec3(2, -1, 3) * pixel),
        texture3D(texture, texel + vec3(3, -1, 3) * pixel));
    vec4 t52 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 0, 3) * pixel),
        texture3D(texture, texel + vec3(-1, 0, 3) * pixel),
        texture3D(texture, texel + vec3(0, 0, 3) * pixel),
        texture3D(texture, texel + vec3(1, 0, 3) * pixel),
        texture3D(texture, texel + vec3(2, 0, 3) * pixel),
        texture3D(texture, texel + vec3(3, 0, 3) * pixel));
    vec4 t53 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 1, 3) * pixel),
        texture3D(texture, texel + vec3(-1, 1, 3) * pixel),
        texture3D(texture, texel + vec3(0, 1, 3) * pixel),
        texture3D(texture, texel + vec3(1, 1, 3) * pixel),
        texture3D(texture, texel + vec3(2, 1, 3) * pixel),
        texture3D(texture, texel + vec3(3, 1, 3) * pixel));
    vec4 t54 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 2, 3) * pixel),
        texture3D(texture, texel + vec3(-1, 2, 3) * pixel),
        texture3D(texture, texel + vec3(0, 2, 3) * pixel),
        texture3D(texture, texel + vec3(1, 2, 3) * pixel),
        texture3D(texture, texel + vec3(2, 2, 3) * pixel),
        texture3D(texture, texel + vec3(3, 2, 3) * pixel));
    vec4 t55 = filter1D_radius3(kernel, index, f.x,
        texture3D(texture, texel + vec3(-2, 3, 3) * pixel),
        texture3D(texture, texel + vec3(-1, 3, 3) * pixel),
        texture3D(texture, texel + vec3(0, 3, 3) * pixel),
        texture3D(texture, texel + vec3(1, 3, 3) * pixel),
        texture3D(texture, texel + vec3(2, 3, 3) * pixel),
        texture3D(texture, texel + vec3(3, 3, 3) * pixel));
    
    vec4 t0 = filter1D_radius3(kernel, index, f.y, t00, t01, t02, t03, t04, t05);
    vec4 t1 = filter1D_radius3(kernel, index, f.y, t10, t11, t12, t13, t14, t15);
    vec4 t2 = filter1D_radius3(kernel, index, f.y, t20, t21, t22, t23, t24, t25);
    vec4 t3 = filter1D_radius3(kernel, index, f.y, t30, t31, t32, t33, t34, t35);
    vec4 t4 = filter1D_radius3(kernel, index, f.y, t40, t41, t42, t43, t44, t45);
    vec4 t5 = filter1D_radius3(kernel, index, f.y, t50, t51, t52, t53, t54, t55);
    return filter1D_radius3(kernel, index, f.z, t0, t1, t2, t3, t4, t5);
}

vec4 filter1D_radius4(sampler2D kernel, float index, float x, vec4 c0, vec4 c1, vec4 c2, vec4 c3, vec4 c4, vec4 c5, vec4 c6, vec4 c7) {
    float w, w_sum = 0;
    vec4 r = vec4(0);
    
    w = unpack_interpolate(kernel, vec2(0.75 + (x / 4), index));
    w = w * kernel_scale + kernel_bias;
    r += c0 * w;
    w = unpack_interpolate(kernel, vec2(0.25 - (x / 4), index));
    w = w * kernel_scale + kernel_bias;
    r += c4 * w;
    w = unpack_interpolate(kernel, vec2(0.5 + (x / 4), index));
    w = w * kernel_scale + kernel_bias;
    r += c1 * w;
    w = unpack_interpolate(kernel, vec2(0.5 - (x / 4), index));
    w = w * kernel_scale + kernel_bias;
    r += c5 * w;
    w = unpack_interpolate(kernel, vec2(0.25 + (x / 4), index));
    w = w * kernel_scale + kernel_bias;
    r += c2 * w;
    w = unpack_interpolate(kernel, vec2(0.75 - (x / 4), index));
    w = w * kernel_scale + kernel_bias;
    r += c6 * w;
    w = unpack_interpolate(kernel, vec2(0.0 + (x / 4), index));
    w = w * kernel_scale + kernel_bias;
    r += c3 * w;
    w = unpack_interpolate(kernel, vec2(1.0 - (x / 4), index));
    w = w * kernel_scale + kernel_bias;
    r += c7 * w;
    return r;
}

vec4 filter2D_radius4(sampler2D texture, sampler2D kernel, float index, vec2 uv, vec2 pixel) {
    vec2 texel = uv / pixel - vec2(0.5);
    vec2 f = fract(texel);
    texel = (texel - fract(texel) + vec2(0.001)) * pixel;
    
    vec4 t0 = filter1D_radius4(kernel, index, f.x,
        texture2D(texture, texel + vec2(-3, -3) * pixel),
        texture2D(texture, texel + vec2(-2, -3) * pixel),
        texture2D(texture, texel + vec2(-1, -3) * pixel),
        texture2D(texture, texel + vec2(0, -3) * pixel),
        texture2D(texture, texel + vec2(1, -3) * pixel),
        texture2D(texture, texel + vec2(2, -3) * pixel),
        texture2D(texture, texel + vec2(3, -3) * pixel),
        texture2D(texture, texel + vec2(4, -3) * pixel));
    vec4 t1 = filter1D_radius4(kernel, index, f.x,
        texture2D(texture, texel + vec2(-3, -2) * pixel),
        texture2D(texture, texel + vec2(-2, -2) * pixel),
        texture2D(texture, texel + vec2(-1, -2) * pixel),
        texture2D(texture, texel + vec2(0, -2) * pixel),
        texture2D(texture, texel + vec2(1, -2) * pixel),
        texture2D(texture, texel + vec2(2, -2) * pixel),
        texture2D(texture, texel + vec2(3, -2) * pixel),
        texture2D(texture, texel + vec2(4, -2) * pixel));
    vec4 t2 = filter1D_radius4(kernel, index, f.x,
        texture2D(texture, texel + vec2(-3, -1) * pixel),
        texture2D(texture, texel + vec2(-2, -1) * pixel),
        texture2D(texture, texel + vec2(-1, -1) * pixel),
        texture2D(texture, texel + vec2(0, -1) * pixel),
        texture2D(texture, texel + vec2(1, -1) * pixel),
        texture2D(texture, texel + vec2(2, -1) * pixel),
        texture2D(texture, texel + vec2(3, -1) * pixel),
        texture2D(texture, texel + vec2(4, -1) * pixel));
    vec4 t3 = filter1D_radius4(kernel, index, f.x,
        texture2D(texture, texel + vec2(-3, 0) * pixel),
        texture2D(texture, texel + vec2(-2, 0) * pixel),
        texture2D(texture, texel + vec2(-1, 0) * pixel),
        texture2D(texture, texel + vec2(0, 0) * pixel),
        texture2D(texture, texel + vec2(1, 0) * pixel),
        texture2D(texture, texel + vec2(2, 0) * pixel),
        texture2D(texture, texel + vec2(3, 0) * pixel),
        texture2D(texture, texel + vec2(4, 0) * pixel));
    vec4 t4 = filter1D_radius4(kernel, index, f.x,
        texture2D(texture, texel + vec2(-3, 1) * pixel),
        texture2D(texture, texel + vec2(-2, 1) * pixel),
        texture2D(texture, texel + vec2(-1, 1) * pixel),
        texture2D(texture, texel + vec2(0, 1) * pixel),
        texture2D(texture, texel + vec2(1, 1) * pixel),
        texture2D(texture, texel + vec2(2, 1) * pixel),
        texture2D(texture, texel + vec2(3, 1) * pixel),
        texture2D(texture, texel + vec2(4, 1) * pixel));
    vec4 t5 = filter1D_radius4(kernel, index, f.x,
        texture2D(texture, texel + vec2(-3, 2) * pixel),
        texture2D(texture, texel + vec2(-2, 2) * pixel),
        texture2D(texture, texel + vec2(-1, 2) * pixel),
        texture2D(texture, texel + vec2(0, 2) * pixel),
        texture2D(texture, texel + vec2(1, 2) * pixel),
        texture2D(texture, texel + vec2(2, 2) * pixel),
        texture2D(texture, texel + vec2(3, 2) * pixel),
        texture2D(texture, texel + vec2(4, 2) * pixel));
    vec4 t6 = filter1D_radius4(kernel, index, f.x,
        texture2D(texture, texel + vec2(-3, 3) * pixel),
        texture2D(texture, texel + vec2(-2, 3) * pixel),
        texture2D(texture, texel + vec2(-1, 3) * pixel),
        texture2D(texture, texel + vec2(0, 3) * pixel),
        texture2D(texture, texel + vec2(1, 3) * pixel),
        texture2D(texture, texel + vec2(2, 3) * pixel),
        texture2D(texture, texel + vec2(3, 3) * pixel),
        texture2D(texture, texel + vec2(4, 3) * pixel));
    vec4 t7 = filter1D_radius4(kernel, index, f.x,
        texture2D(texture, texel + vec2(-3, 4) * pixel),
        texture2D(texture, texel + vec2(-2, 4) * pixel),
        texture2D(texture, texel + vec2(-1, 4) * pixel),
        texture2D(texture, texel + vec2(0, 4) * pixel),
        texture2D(texture, texel + vec2(1, 4) * pixel),
        texture2D(texture, texel + vec2(2, 4) * pixel),
        texture2D(texture, texel + vec2(3, 4) * pixel),
        texture2D(texture, texel + vec2(4, 4) * pixel));
    return filter1D_radius4(kernel, index, f.y, t0, t1, t2, t3, t4, t5, t6, t7);
}

vec4 filter3D_radius4(sampler3D texture, sampler2D kernel, float index, vec3 uv, vec3 pixel) {
    vec3 texel = uv / pixel - vec3(0.5);
    vec3 f = fract(texel);
    texel = (texel - fract(texel) + vec3(0.001)) * pixel;
    
    vec4 t00 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -3, -3) * pixel),
        texture3D(texture, texel + vec3(-2, -3, -3) * pixel),
        texture3D(texture, texel + vec3(-1, -3, -3) * pixel),
        texture3D(texture, texel + vec3(0, -3, -3) * pixel),
        texture3D(texture, texel + vec3(1, -3, -3) * pixel),
        texture3D(texture, texel + vec3(2, -3, -3) * pixel),
        texture3D(texture, texel + vec3(3, -3, -3) * pixel),
        texture3D(texture, texel + vec3(4, -3, -3) * pixel));
    vec4 t01 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -2, -3) * pixel),
        texture3D(texture, texel + vec3(-2, -2, -3) * pixel),
        texture3D(texture, texel + vec3(-1, -2, -3) * pixel),
        texture3D(texture, texel + vec3(0, -2, -3) * pixel),
        texture3D(texture, texel + vec3(1, -2, -3) * pixel),
        texture3D(texture, texel + vec3(2, -2, -3) * pixel),
        texture3D(texture, texel + vec3(3, -2, -3) * pixel),
        texture3D(texture, texel + vec3(4, -2, -3) * pixel));
    vec4 t02 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -1, -3) * pixel),
        texture3D(texture, texel + vec3(-2, -1, -3) * pixel),
        texture3D(texture, texel + vec3(-1, -1, -3) * pixel),
        texture3D(texture, texel + vec3(0, -1, -3) * pixel),
        texture3D(texture, texel + vec3(1, -1, -3) * pixel),
        texture3D(texture, texel + vec3(2, -1, -3) * pixel),
        texture3D(texture, texel + vec3(3, -1, -3) * pixel),
        texture3D(texture, texel + vec3(4, -1, -3) * pixel));
    vec4 t03 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 0, -3) * pixel),
        texture3D(texture, texel + vec3(-2, 0, -3) * pixel),
        texture3D(texture, texel + vec3(-1, 0, -3) * pixel),
        texture3D(texture, texel + vec3(0, 0, -3) * pixel),
        texture3D(texture, texel + vec3(1, 0, -3) * pixel),
        texture3D(texture, texel + vec3(2, 0, -3) * pixel),
        texture3D(texture, texel + vec3(3, 0, -3) * pixel),
        texture3D(texture, texel + vec3(4, 0, -3) * pixel));
    vec4 t04 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 1, -3) * pixel),
        texture3D(texture, texel + vec3(-2, 1, -3) * pixel),
        texture3D(texture, texel + vec3(-1, 1, -3) * pixel),
        texture3D(texture, texel + vec3(0, 1, -3) * pixel),
        texture3D(texture, texel + vec3(1, 1, -3) * pixel),
        texture3D(texture, texel + vec3(2, 1, -3) * pixel),
        texture3D(texture, texel + vec3(3, 1, -3) * pixel),
        texture3D(texture, texel + vec3(4, 1, -3) * pixel));
    vec4 t05 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 2, -3) * pixel),
        texture3D(texture, texel + vec3(-2, 2, -3) * pixel),
        texture3D(texture, texel + vec3(-1, 2, -3) * pixel),
        texture3D(texture, texel + vec3(0, 2, -3) * pixel),
        texture3D(texture, texel + vec3(1, 2, -3) * pixel),
        texture3D(texture, texel + vec3(2, 2, -3) * pixel),
        texture3D(texture, texel + vec3(3, 2, -3) * pixel),
        texture3D(texture, texel + vec3(4, 2, -3) * pixel));
    vec4 t06 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 3, -3) * pixel),
        texture3D(texture, texel + vec3(-2, 3, -3) * pixel),
        texture3D(texture, texel + vec3(-1, 3, -3) * pixel),
        texture3D(texture, texel + vec3(0, 3, -3) * pixel),
        texture3D(texture, texel + vec3(1, 3, -3) * pixel),
        texture3D(texture, texel + vec3(2, 3, -3) * pixel),
        texture3D(texture, texel + vec3(3, 3, -3) * pixel),
        texture3D(texture, texel + vec3(4, 3, -3) * pixel));
    vec4 t07 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 4, -3) * pixel),
        texture3D(texture, texel + vec3(-2, 4, -3) * pixel),
        texture3D(texture, texel + vec3(-1, 4, -3) * pixel),
        texture3D(texture, texel + vec3(0, 4, -3) * pixel),
        texture3D(texture, texel + vec3(1, 4, -3) * pixel),
        texture3D(texture, texel + vec3(2, 4, -3) * pixel),
        texture3D(texture, texel + vec3(3, 4, -3) * pixel),
        texture3D(texture, texel + vec3(4, 4, -3) * pixel));
    vec4 t10 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -3, -2) * pixel),
        texture3D(texture, texel + vec3(-2, -3, -2) * pixel),
        texture3D(texture, texel + vec3(-1, -3, -2) * pixel),
        texture3D(texture, texel + vec3(0, -3, -2) * pixel),
        texture3D(texture, texel + vec3(1, -3, -2) * pixel),
        texture3D(texture, texel + vec3(2, -3, -2) * pixel),
        texture3D(texture, texel + vec3(3, -3, -2) * pixel),
        texture3D(texture, texel + vec3(4, -3, -2) * pixel));
    vec4 t11 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -2, -2) * pixel),
        texture3D(texture, texel + vec3(-2, -2, -2) * pixel),
        texture3D(texture, texel + vec3(-1, -2, -2) * pixel),
        texture3D(texture, texel + vec3(0, -2, -2) * pixel),
        texture3D(texture, texel + vec3(1, -2, -2) * pixel),
        texture3D(texture, texel + vec3(2, -2, -2) * pixel),
        texture3D(texture, texel + vec3(3, -2, -2) * pixel),
        texture3D(texture, texel + vec3(4, -2, -2) * pixel));
    vec4 t12 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -1, -2) * pixel),
        texture3D(texture, texel + vec3(-2, -1, -2) * pixel),
        texture3D(texture, texel + vec3(-1, -1, -2) * pixel),
        texture3D(texture, texel + vec3(0, -1, -2) * pixel),
        texture3D(texture, texel + vec3(1, -1, -2) * pixel),
        texture3D(texture, texel + vec3(2, -1, -2) * pixel),
        texture3D(texture, texel + vec3(3, -1, -2) * pixel),
        texture3D(texture, texel + vec3(4, -1, -2) * pixel));
    vec4 t13 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 0, -2) * pixel),
        texture3D(texture, texel + vec3(-2, 0, -2) * pixel),
        texture3D(texture, texel + vec3(-1, 0, -2) * pixel),
        texture3D(texture, texel + vec3(0, 0, -2) * pixel),
        texture3D(texture, texel + vec3(1, 0, -2) * pixel),
        texture3D(texture, texel + vec3(2, 0, -2) * pixel),
        texture3D(texture, texel + vec3(3, 0, -2) * pixel),
        texture3D(texture, texel + vec3(4, 0, -2) * pixel));
    vec4 t14 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 1, -2) * pixel),
        texture3D(texture, texel + vec3(-2, 1, -2) * pixel),
        texture3D(texture, texel + vec3(-1, 1, -2) * pixel),
        texture3D(texture, texel + vec3(0, 1, -2) * pixel),
        texture3D(texture, texel + vec3(1, 1, -2) * pixel),
        texture3D(texture, texel + vec3(2, 1, -2) * pixel),
        texture3D(texture, texel + vec3(3, 1, -2) * pixel),
        texture3D(texture, texel + vec3(4, 1, -2) * pixel));
    vec4 t15 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 2, -2) * pixel),
        texture3D(texture, texel + vec3(-2, 2, -2) * pixel),
        texture3D(texture, texel + vec3(-1, 2, -2) * pixel),
        texture3D(texture, texel + vec3(0, 2, -2) * pixel),
        texture3D(texture, texel + vec3(1, 2, -2) * pixel),
        texture3D(texture, texel + vec3(2, 2, -2) * pixel),
        texture3D(texture, texel + vec3(3, 2, -2) * pixel),
        texture3D(texture, texel + vec3(4, 2, -2) * pixel));
    vec4 t16 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 3, -2) * pixel),
        texture3D(texture, texel + vec3(-2, 3, -2) * pixel),
        texture3D(texture, texel + vec3(-1, 3, -2) * pixel),
        texture3D(texture, texel + vec3(0, 3, -2) * pixel),
        texture3D(texture, texel + vec3(1, 3, -2) * pixel),
        texture3D(texture, texel + vec3(2, 3, -2) * pixel),
        texture3D(texture, texel + vec3(3, 3, -2) * pixel),
        texture3D(texture, texel + vec3(4, 3, -2) * pixel));
    vec4 t17 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 4, -2) * pixel),
        texture3D(texture, texel + vec3(-2, 4, -2) * pixel),
        texture3D(texture, texel + vec3(-1, 4, -2) * pixel),
        texture3D(texture, texel + vec3(0, 4, -2) * pixel),
        texture3D(texture, texel + vec3(1, 4, -2) * pixel),
        texture3D(texture, texel + vec3(2, 4, -2) * pixel),
        texture3D(texture, texel + vec3(3, 4, -2) * pixel),
        texture3D(texture, texel + vec3(4, 4, -2) * pixel));
    vec4 t20 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -3, -1) * pixel),
        texture3D(texture, texel + vec3(-2, -3, -1) * pixel),
        texture3D(texture, texel + vec3(-1, -3, -1) * pixel),
        texture3D(texture, texel + vec3(0, -3, -1) * pixel),
        texture3D(texture, texel + vec3(1, -3, -1) * pixel),
        texture3D(texture, texel + vec3(2, -3, -1) * pixel),
        texture3D(texture, texel + vec3(3, -3, -1) * pixel),
        texture3D(texture, texel + vec3(4, -3, -1) * pixel));
    vec4 t21 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -2, -1) * pixel),
        texture3D(texture, texel + vec3(-2, -2, -1) * pixel),
        texture3D(texture, texel + vec3(-1, -2, -1) * pixel),
        texture3D(texture, texel + vec3(0, -2, -1) * pixel),
        texture3D(texture, texel + vec3(1, -2, -1) * pixel),
        texture3D(texture, texel + vec3(2, -2, -1) * pixel),
        texture3D(texture, texel + vec3(3, -2, -1) * pixel),
        texture3D(texture, texel + vec3(4, -2, -1) * pixel));
    vec4 t22 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -1, -1) * pixel),
        texture3D(texture, texel + vec3(-2, -1, -1) * pixel),
        texture3D(texture, texel + vec3(-1, -1, -1) * pixel),
        texture3D(texture, texel + vec3(0, -1, -1) * pixel),
        texture3D(texture, texel + vec3(1, -1, -1) * pixel),
        texture3D(texture, texel + vec3(2, -1, -1) * pixel),
        texture3D(texture, texel + vec3(3, -1, -1) * pixel),
        texture3D(texture, texel + vec3(4, -1, -1) * pixel));
    vec4 t23 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 0, -1) * pixel),
        texture3D(texture, texel + vec3(-2, 0, -1) * pixel),
        texture3D(texture, texel + vec3(-1, 0, -1) * pixel),
        texture3D(texture, texel + vec3(0, 0, -1) * pixel),
        texture3D(texture, texel + vec3(1, 0, -1) * pixel),
        texture3D(texture, texel + vec3(2, 0, -1) * pixel),
        texture3D(texture, texel + vec3(3, 0, -1) * pixel),
        texture3D(texture, texel + vec3(4, 0, -1) * pixel));
    vec4 t24 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 1, -1) * pixel),
        texture3D(texture, texel + vec3(-2, 1, -1) * pixel),
        texture3D(texture, texel + vec3(-1, 1, -1) * pixel),
        texture3D(texture, texel + vec3(0, 1, -1) * pixel),
        texture3D(texture, texel + vec3(1, 1, -1) * pixel),
        texture3D(texture, texel + vec3(2, 1, -1) * pixel),
        texture3D(texture, texel + vec3(3, 1, -1) * pixel),
        texture3D(texture, texel + vec3(4, 1, -1) * pixel));
    vec4 t25 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 2, -1) * pixel),
        texture3D(texture, texel + vec3(-2, 2, -1) * pixel),
        texture3D(texture, texel + vec3(-1, 2, -1) * pixel),
        texture3D(texture, texel + vec3(0, 2, -1) * pixel),
        texture3D(texture, texel + vec3(1, 2, -1) * pixel),
        texture3D(texture, texel + vec3(2, 2, -1) * pixel),
        texture3D(texture, texel + vec3(3, 2, -1) * pixel),
        texture3D(texture, texel + vec3(4, 2, -1) * pixel));
    vec4 t26 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 3, -1) * pixel),
        texture3D(texture, texel + vec3(-2, 3, -1) * pixel),
        texture3D(texture, texel + vec3(-1, 3, -1) * pixel),
        texture3D(texture, texel + vec3(0, 3, -1) * pixel),
        texture3D(texture, texel + vec3(1, 3, -1) * pixel),
        texture3D(texture, texel + vec3(2, 3, -1) * pixel),
        texture3D(texture, texel + vec3(3, 3, -1) * pixel),
        texture3D(texture, texel + vec3(4, 3, -1) * pixel));
    vec4 t27 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 4, -1) * pixel),
        texture3D(texture, texel + vec3(-2, 4, -1) * pixel),
        texture3D(texture, texel + vec3(-1, 4, -1) * pixel),
        texture3D(texture, texel + vec3(0, 4, -1) * pixel),
        texture3D(texture, texel + vec3(1, 4, -1) * pixel),
        texture3D(texture, texel + vec3(2, 4, -1) * pixel),
        texture3D(texture, texel + vec3(3, 4, -1) * pixel),
        texture3D(texture, texel + vec3(4, 4, -1) * pixel));
    vec4 t30 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -3, 0) * pixel),
        texture3D(texture, texel + vec3(-2, -3, 0) * pixel),
        texture3D(texture, texel + vec3(-1, -3, 0) * pixel),
        texture3D(texture, texel + vec3(0, -3, 0) * pixel),
        texture3D(texture, texel + vec3(1, -3, 0) * pixel),
        texture3D(texture, texel + vec3(2, -3, 0) * pixel),
        texture3D(texture, texel + vec3(3, -3, 0) * pixel),
        texture3D(texture, texel + vec3(4, -3, 0) * pixel));
    vec4 t31 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -2, 0) * pixel),
        texture3D(texture, texel + vec3(-2, -2, 0) * pixel),
        texture3D(texture, texel + vec3(-1, -2, 0) * pixel),
        texture3D(texture, texel + vec3(0, -2, 0) * pixel),
        texture3D(texture, texel + vec3(1, -2, 0) * pixel),
        texture3D(texture, texel + vec3(2, -2, 0) * pixel),
        texture3D(texture, texel + vec3(3, -2, 0) * pixel),
        texture3D(texture, texel + vec3(4, -2, 0) * pixel));
    vec4 t32 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -1, 0) * pixel),
        texture3D(texture, texel + vec3(-2, -1, 0) * pixel),
        texture3D(texture, texel + vec3(-1, -1, 0) * pixel),
        texture3D(texture, texel + vec3(0, -1, 0) * pixel),
        texture3D(texture, texel + vec3(1, -1, 0) * pixel),
        texture3D(texture, texel + vec3(2, -1, 0) * pixel),
        texture3D(texture, texel + vec3(3, -1, 0) * pixel),
        texture3D(texture, texel + vec3(4, -1, 0) * pixel));
    vec4 t33 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 0, 0) * pixel),
        texture3D(texture, texel + vec3(-2, 0, 0) * pixel),
        texture3D(texture, texel + vec3(-1, 0, 0) * pixel),
        texture3D(texture, texel + vec3(0, 0, 0) * pixel),
        texture3D(texture, texel + vec3(1, 0, 0) * pixel),
        texture3D(texture, texel + vec3(2, 0, 0) * pixel),
        texture3D(texture, texel + vec3(3, 0, 0) * pixel),
        texture3D(texture, texel + vec3(4, 0, 0) * pixel));
    vec4 t34 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 1, 0) * pixel),
        texture3D(texture, texel + vec3(-2, 1, 0) * pixel),
        texture3D(texture, texel + vec3(-1, 1, 0) * pixel),
        texture3D(texture, texel + vec3(0, 1, 0) * pixel),
        texture3D(texture, texel + vec3(1, 1, 0) * pixel),
        texture3D(texture, texel + vec3(2, 1, 0) * pixel),
        texture3D(texture, texel + vec3(3, 1, 0) * pixel),
        texture3D(texture, texel + vec3(4, 1, 0) * pixel));
    vec4 t35 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 2, 0) * pixel),
        texture3D(texture, texel + vec3(-2, 2, 0) * pixel),
        texture3D(texture, texel + vec3(-1, 2, 0) * pixel),
        texture3D(texture, texel + vec3(0, 2, 0) * pixel),
        texture3D(texture, texel + vec3(1, 2, 0) * pixel),
        texture3D(texture, texel + vec3(2, 2, 0) * pixel),
        texture3D(texture, texel + vec3(3, 2, 0) * pixel),
        texture3D(texture, texel + vec3(4, 2, 0) * pixel));
    vec4 t36 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 3, 0) * pixel),
        texture3D(texture, texel + vec3(-2, 3, 0) * pixel),
        texture3D(texture, texel + vec3(-1, 3, 0) * pixel),
        texture3D(texture, texel + vec3(0, 3, 0) * pixel),
        texture3D(texture, texel + vec3(1, 3, 0) * pixel),
        texture3D(texture, texel + vec3(2, 3, 0) * pixel),
        texture3D(texture, texel + vec3(3, 3, 0) * pixel),
        texture3D(texture, texel + vec3(4, 3, 0) * pixel));
    vec4 t37 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 4, 0) * pixel),
        texture3D(texture, texel + vec3(-2, 4, 0) * pixel),
        texture3D(texture, texel + vec3(-1, 4, 0) * pixel),
        texture3D(texture, texel + vec3(0, 4, 0) * pixel),
        texture3D(texture, texel + vec3(1, 4, 0) * pixel),
        texture3D(texture, texel + vec3(2, 4, 0) * pixel),
        texture3D(texture, texel + vec3(3, 4, 0) * pixel),
        texture3D(texture, texel + vec3(4, 4, 0) * pixel));
    vec4 t40 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -3, 1) * pixel),
        texture3D(texture, texel + vec3(-2, -3, 1) * pixel),
        texture3D(texture, texel + vec3(-1, -3, 1) * pixel),
        texture3D(texture, texel + vec3(0, -3, 1) * pixel),
        texture3D(texture, texel + vec3(1, -3, 1) * pixel),
        texture3D(texture, texel + vec3(2, -3, 1) * pixel),
        texture3D(texture, texel + vec3(3, -3, 1) * pixel),
        texture3D(texture, texel + vec3(4, -3, 1) * pixel));
    vec4 t41 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -2, 1) * pixel),
        texture3D(texture, texel + vec3(-2, -2, 1) * pixel),
        texture3D(texture, texel + vec3(-1, -2, 1) * pixel),
        texture3D(texture, texel + vec3(0, -2, 1) * pixel),
        texture3D(texture, texel + vec3(1, -2, 1) * pixel),
        texture3D(texture, texel + vec3(2, -2, 1) * pixel),
        texture3D(texture, texel + vec3(3, -2, 1) * pixel),
        texture3D(texture, texel + vec3(4, -2, 1) * pixel));
    vec4 t42 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -1, 1) * pixel),
        texture3D(texture, texel + vec3(-2, -1, 1) * pixel),
        texture3D(texture, texel + vec3(-1, -1, 1) * pixel),
        texture3D(texture, texel + vec3(0, -1, 1) * pixel),
        texture3D(texture, texel + vec3(1, -1, 1) * pixel),
        texture3D(texture, texel + vec3(2, -1, 1) * pixel),
        texture3D(texture, texel + vec3(3, -1, 1) * pixel),
        texture3D(texture, texel + vec3(4, -1, 1) * pixel));
    vec4 t43 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 0, 1) * pixel),
        texture3D(texture, texel + vec3(-2, 0, 1) * pixel),
        texture3D(texture, texel + vec3(-1, 0, 1) * pixel),
        texture3D(texture, texel + vec3(0, 0, 1) * pixel),
        texture3D(texture, texel + vec3(1, 0, 1) * pixel),
        texture3D(texture, texel + vec3(2, 0, 1) * pixel),
        texture3D(texture, texel + vec3(3, 0, 1) * pixel),
        texture3D(texture, texel + vec3(4, 0, 1) * pixel));
    vec4 t44 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 1, 1) * pixel),
        texture3D(texture, texel + vec3(-2, 1, 1) * pixel),
        texture3D(texture, texel + vec3(-1, 1, 1) * pixel),
        texture3D(texture, texel + vec3(0, 1, 1) * pixel),
        texture3D(texture, texel + vec3(1, 1, 1) * pixel),
        texture3D(texture, texel + vec3(2, 1, 1) * pixel),
        texture3D(texture, texel + vec3(3, 1, 1) * pixel),
        texture3D(texture, texel + vec3(4, 1, 1) * pixel));
    vec4 t45 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 2, 1) * pixel),
        texture3D(texture, texel + vec3(-2, 2, 1) * pixel),
        texture3D(texture, texel + vec3(-1, 2, 1) * pixel),
        texture3D(texture, texel + vec3(0, 2, 1) * pixel),
        texture3D(texture, texel + vec3(1, 2, 1) * pixel),
        texture3D(texture, texel + vec3(2, 2, 1) * pixel),
        texture3D(texture, texel + vec3(3, 2, 1) * pixel),
        texture3D(texture, texel + vec3(4, 2, 1) * pixel));
    vec4 t46 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 3, 1) * pixel),
        texture3D(texture, texel + vec3(-2, 3, 1) * pixel),
        texture3D(texture, texel + vec3(-1, 3, 1) * pixel),
        texture3D(texture, texel + vec3(0, 3, 1) * pixel),
        texture3D(texture, texel + vec3(1, 3, 1) * pixel),
        texture3D(texture, texel + vec3(2, 3, 1) * pixel),
        texture3D(texture, texel + vec3(3, 3, 1) * pixel),
        texture3D(texture, texel + vec3(4, 3, 1) * pixel));
    vec4 t47 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 4, 1) * pixel),
        texture3D(texture, texel + vec3(-2, 4, 1) * pixel),
        texture3D(texture, texel + vec3(-1, 4, 1) * pixel),
        texture3D(texture, texel + vec3(0, 4, 1) * pixel),
        texture3D(texture, texel + vec3(1, 4, 1) * pixel),
        texture3D(texture, texel + vec3(2, 4, 1) * pixel),
        texture3D(texture, texel + vec3(3, 4, 1) * pixel),
        texture3D(texture, texel + vec3(4, 4, 1) * pixel));
    vec4 t50 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -3, 2) * pixel),
        texture3D(texture, texel + vec3(-2, -3, 2) * pixel),
        texture3D(texture, texel + vec3(-1, -3, 2) * pixel),
        texture3D(texture, texel + vec3(0, -3, 2) * pixel),
        texture3D(texture, texel + vec3(1, -3, 2) * pixel),
        texture3D(texture, texel + vec3(2, -3, 2) * pixel),
        texture3D(texture, texel + vec3(3, -3, 2) * pixel),
        texture3D(texture, texel + vec3(4, -3, 2) * pixel));
    vec4 t51 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -2, 2) * pixel),
        texture3D(texture, texel + vec3(-2, -2, 2) * pixel),
        texture3D(texture, texel + vec3(-1, -2, 2) * pixel),
        texture3D(texture, texel + vec3(0, -2, 2) * pixel),
        texture3D(texture, texel + vec3(1, -2, 2) * pixel),
        texture3D(texture, texel + vec3(2, -2, 2) * pixel),
        texture3D(texture, texel + vec3(3, -2, 2) * pixel),
        texture3D(texture, texel + vec3(4, -2, 2) * pixel));
    vec4 t52 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -1, 2) * pixel),
        texture3D(texture, texel + vec3(-2, -1, 2) * pixel),
        texture3D(texture, texel + vec3(-1, -1, 2) * pixel),
        texture3D(texture, texel + vec3(0, -1, 2) * pixel),
        texture3D(texture, texel + vec3(1, -1, 2) * pixel),
        texture3D(texture, texel + vec3(2, -1, 2) * pixel),
        texture3D(texture, texel + vec3(3, -1, 2) * pixel),
        texture3D(texture, texel + vec3(4, -1, 2) * pixel));
    vec4 t53 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 0, 2) * pixel),
        texture3D(texture, texel + vec3(-2, 0, 2) * pixel),
        texture3D(texture, texel + vec3(-1, 0, 2) * pixel),
        texture3D(texture, texel + vec3(0, 0, 2) * pixel),
        texture3D(texture, texel + vec3(1, 0, 2) * pixel),
        texture3D(texture, texel + vec3(2, 0, 2) * pixel),
        texture3D(texture, texel + vec3(3, 0, 2) * pixel),
        texture3D(texture, texel + vec3(4, 0, 2) * pixel));
    vec4 t54 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 1, 2) * pixel),
        texture3D(texture, texel + vec3(-2, 1, 2) * pixel),
        texture3D(texture, texel + vec3(-1, 1, 2) * pixel),
        texture3D(texture, texel + vec3(0, 1, 2) * pixel),
        texture3D(texture, texel + vec3(1, 1, 2) * pixel),
        texture3D(texture, texel + vec3(2, 1, 2) * pixel),
        texture3D(texture, texel + vec3(3, 1, 2) * pixel),
        texture3D(texture, texel + vec3(4, 1, 2) * pixel));
    vec4 t55 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 2, 2) * pixel),
        texture3D(texture, texel + vec3(-2, 2, 2) * pixel),
        texture3D(texture, texel + vec3(-1, 2, 2) * pixel),
        texture3D(texture, texel + vec3(0, 2, 2) * pixel),
        texture3D(texture, texel + vec3(1, 2, 2) * pixel),
        texture3D(texture, texel + vec3(2, 2, 2) * pixel),
        texture3D(texture, texel + vec3(3, 2, 2) * pixel),
        texture3D(texture, texel + vec3(4, 2, 2) * pixel));
    vec4 t56 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 3, 2) * pixel),
        texture3D(texture, texel + vec3(-2, 3, 2) * pixel),
        texture3D(texture, texel + vec3(-1, 3, 2) * pixel),
        texture3D(texture, texel + vec3(0, 3, 2) * pixel),
        texture3D(texture, texel + vec3(1, 3, 2) * pixel),
        texture3D(texture, texel + vec3(2, 3, 2) * pixel),
        texture3D(texture, texel + vec3(3, 3, 2) * pixel),
        texture3D(texture, texel + vec3(4, 3, 2) * pixel));
    vec4 t57 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 4, 2) * pixel),
        texture3D(texture, texel + vec3(-2, 4, 2) * pixel),
        texture3D(texture, texel + vec3(-1, 4, 2) * pixel),
        texture3D(texture, texel + vec3(0, 4, 2) * pixel),
        texture3D(texture, texel + vec3(1, 4, 2) * pixel),
        texture3D(texture, texel + vec3(2, 4, 2) * pixel),
        texture3D(texture, texel + vec3(3, 4, 2) * pixel),
        texture3D(texture, texel + vec3(4, 4, 2) * pixel));
    vec4 t60 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -3, 3) * pixel),
        texture3D(texture, texel + vec3(-2, -3, 3) * pixel),
        texture3D(texture, texel + vec3(-1, -3, 3) * pixel),
        texture3D(texture, texel + vec3(0, -3, 3) * pixel),
        texture3D(texture, texel + vec3(1, -3, 3) * pixel),
        texture3D(texture, texel + vec3(2, -3, 3) * pixel),
        texture3D(texture, texel + vec3(3, -3, 3) * pixel),
        texture3D(texture, texel + vec3(4, -3, 3) * pixel));
    vec4 t61 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -2, 3) * pixel),
        texture3D(texture, texel + vec3(-2, -2, 3) * pixel),
        texture3D(texture, texel + vec3(-1, -2, 3) * pixel),
        texture3D(texture, texel + vec3(0, -2, 3) * pixel),
        texture3D(texture, texel + vec3(1, -2, 3) * pixel),
        texture3D(texture, texel + vec3(2, -2, 3) * pixel),
        texture3D(texture, texel + vec3(3, -2, 3) * pixel),
        texture3D(texture, texel + vec3(4, -2, 3) * pixel));
    vec4 t62 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -1, 3) * pixel),
        texture3D(texture, texel + vec3(-2, -1, 3) * pixel),
        texture3D(texture, texel + vec3(-1, -1, 3) * pixel),
        texture3D(texture, texel + vec3(0, -1, 3) * pixel),
        texture3D(texture, texel + vec3(1, -1, 3) * pixel),
        texture3D(texture, texel + vec3(2, -1, 3) * pixel),
        texture3D(texture, texel + vec3(3, -1, 3) * pixel),
        texture3D(texture, texel + vec3(4, -1, 3) * pixel));
    vec4 t63 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 0, 3) * pixel),
        texture3D(texture, texel + vec3(-2, 0, 3) * pixel),
        texture3D(texture, texel + vec3(-1, 0, 3) * pixel),
        texture3D(texture, texel + vec3(0, 0, 3) * pixel),
        texture3D(texture, texel + vec3(1, 0, 3) * pixel),
        texture3D(texture, texel + vec3(2, 0, 3) * pixel),
        texture3D(texture, texel + vec3(3, 0, 3) * pixel),
        texture3D(texture, texel + vec3(4, 0, 3) * pixel));
    vec4 t64 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 1, 3) * pixel),
        texture3D(texture, texel + vec3(-2, 1, 3) * pixel),
        texture3D(texture, texel + vec3(-1, 1, 3) * pixel),
        texture3D(texture, texel + vec3(0, 1, 3) * pixel),
        texture3D(texture, texel + vec3(1, 1, 3) * pixel),
        texture3D(texture, texel + vec3(2, 1, 3) * pixel),
        texture3D(texture, texel + vec3(3, 1, 3) * pixel),
        texture3D(texture, texel + vec3(4, 1, 3) * pixel));
    vec4 t65 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 2, 3) * pixel),
        texture3D(texture, texel + vec3(-2, 2, 3) * pixel),
        texture3D(texture, texel + vec3(-1, 2, 3) * pixel),
        texture3D(texture, texel + vec3(0, 2, 3) * pixel),
        texture3D(texture, texel + vec3(1, 2, 3) * pixel),
        texture3D(texture, texel + vec3(2, 2, 3) * pixel),
        texture3D(texture, texel + vec3(3, 2, 3) * pixel),
        texture3D(texture, texel + vec3(4, 2, 3) * pixel));
    vec4 t66 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 3, 3) * pixel),
        texture3D(texture, texel + vec3(-2, 3, 3) * pixel),
        texture3D(texture, texel + vec3(-1, 3, 3) * pixel),
        texture3D(texture, texel + vec3(0, 3, 3) * pixel),
        texture3D(texture, texel + vec3(1, 3, 3) * pixel),
        texture3D(texture, texel + vec3(2, 3, 3) * pixel),
        texture3D(texture, texel + vec3(3, 3, 3) * pixel),
        texture3D(texture, texel + vec3(4, 3, 3) * pixel));
    vec4 t67 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 4, 3) * pixel),
        texture3D(texture, texel + vec3(-2, 4, 3) * pixel),
        texture3D(texture, texel + vec3(-1, 4, 3) * pixel),
        texture3D(texture, texel + vec3(0, 4, 3) * pixel),
        texture3D(texture, texel + vec3(1, 4, 3) * pixel),
        texture3D(texture, texel + vec3(2, 4, 3) * pixel),
        texture3D(texture, texel + vec3(3, 4, 3) * pixel),
        texture3D(texture, texel + vec3(4, 4, 3) * pixel));
    vec4 t70 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -3, 4) * pixel),
        texture3D(texture, texel + vec3(-2, -3, 4) * pixel),
        texture3D(texture, texel + vec3(-1, -3, 4) * pixel),
        texture3D(texture, texel + vec3(0, -3, 4) * pixel),
        texture3D(texture, texel + vec3(1, -3, 4) * pixel),
        texture3D(texture, texel + vec3(2, -3, 4) * pixel),
        texture3D(texture, texel + vec3(3, -3, 4) * pixel),
        texture3D(texture, texel + vec3(4, -3, 4) * pixel));
    vec4 t71 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -2, 4) * pixel),
        texture3D(texture, texel + vec3(-2, -2, 4) * pixel),
        texture3D(texture, texel + vec3(-1, -2, 4) * pixel),
        texture3D(texture, texel + vec3(0, -2, 4) * pixel),
        texture3D(texture, texel + vec3(1, -2, 4) * pixel),
        texture3D(texture, texel + vec3(2, -2, 4) * pixel),
        texture3D(texture, texel + vec3(3, -2, 4) * pixel),
        texture3D(texture, texel + vec3(4, -2, 4) * pixel));
    vec4 t72 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, -1, 4) * pixel),
        texture3D(texture, texel + vec3(-2, -1, 4) * pixel),
        texture3D(texture, texel + vec3(-1, -1, 4) * pixel),
        texture3D(texture, texel + vec3(0, -1, 4) * pixel),
        texture3D(texture, texel + vec3(1, -1, 4) * pixel),
        texture3D(texture, texel + vec3(2, -1, 4) * pixel),
        texture3D(texture, texel + vec3(3, -1, 4) * pixel),
        texture3D(texture, texel + vec3(4, -1, 4) * pixel));
    vec4 t73 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 0, 4) * pixel),
        texture3D(texture, texel + vec3(-2, 0, 4) * pixel),
        texture3D(texture, texel + vec3(-1, 0, 4) * pixel),
        texture3D(texture, texel + vec3(0, 0, 4) * pixel),
        texture3D(texture, texel + vec3(1, 0, 4) * pixel),
        texture3D(texture, texel + vec3(2, 0, 4) * pixel),
        texture3D(texture, texel + vec3(3, 0, 4) * pixel),
        texture3D(texture, texel + vec3(4, 0, 4) * pixel));
    vec4 t74 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 1, 4) * pixel),
        texture3D(texture, texel + vec3(-2, 1, 4) * pixel),
        texture3D(texture, texel + vec3(-1, 1, 4) * pixel),
        texture3D(texture, texel + vec3(0, 1, 4) * pixel),
        texture3D(texture, texel + vec3(1, 1, 4) * pixel),
        texture3D(texture, texel + vec3(2, 1, 4) * pixel),
        texture3D(texture, texel + vec3(3, 1, 4) * pixel),
        texture3D(texture, texel + vec3(4, 1, 4) * pixel));
    vec4 t75 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 2, 4) * pixel),
        texture3D(texture, texel + vec3(-2, 2, 4) * pixel),
        texture3D(texture, texel + vec3(-1, 2, 4) * pixel),
        texture3D(texture, texel + vec3(0, 2, 4) * pixel),
        texture3D(texture, texel + vec3(1, 2, 4) * pixel),
        texture3D(texture, texel + vec3(2, 2, 4) * pixel),
        texture3D(texture, texel + vec3(3, 2, 4) * pixel),
        texture3D(texture, texel + vec3(4, 2, 4) * pixel));
    vec4 t76 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 3, 4) * pixel),
        texture3D(texture, texel + vec3(-2, 3, 4) * pixel),
        texture3D(texture, texel + vec3(-1, 3, 4) * pixel),
        texture3D(texture, texel + vec3(0, 3, 4) * pixel),
        texture3D(texture, texel + vec3(1, 3, 4) * pixel),
        texture3D(texture, texel + vec3(2, 3, 4) * pixel),
        texture3D(texture, texel + vec3(3, 3, 4) * pixel),
        texture3D(texture, texel + vec3(4, 3, 4) * pixel));
    vec4 t77 = filter1D_radius4(kernel, index, f.x,
        texture3D(texture, texel + vec3(-3, 4, 4) * pixel),
        texture3D(texture, texel + vec3(-2, 4, 4) * pixel),
        texture3D(texture, texel + vec3(-1, 4, 4) * pixel),
        texture3D(texture, texel + vec3(0, 4, 4) * pixel),
        texture3D(texture, texel + vec3(1, 4, 4) * pixel),
        texture3D(texture, texel + vec3(2, 4, 4) * pixel),
        texture3D(texture, texel + vec3(3, 4, 4) * pixel),
        texture3D(texture, texel + vec3(4, 4, 4) * pixel));
    
    vec4 t0 = filter1D_radius4(kernel, index, f.y, t00, t01, t02, t03, t04, t05, t06, t07);
    vec4 t1 = filter1D_radius4(kernel, index, f.y, t10, t11, t12, t13, t14, t15, t16, t17);
    vec4 t2 = filter1D_radius4(kernel, index, f.y, t20, t21, t22, t23, t24, t25, t26, t27);
    vec4 t3 = filter1D_radius4(kernel, index, f.y, t30, t31, t32, t33, t34, t35, t36, t37);
    vec4 t4 = filter1D_radius4(kernel, index, f.y, t40, t41, t42, t43, t44, t45, t46, t47);
    vec4 t5 = filter1D_radius4(kernel, index, f.y, t50, t51, t52, t53, t54, t55, t56, t57);
    vec4 t6 = filter1D_radius4(kernel, index, f.y, t60, t61, t62, t63, t64, t65, t66, t67);
    vec4 t7 = filter1D_radius4(kernel, index, f.y, t70, t71, t72, t73, t74, t75, t76, t77);
    return filter1D_radius4(kernel, index, f.z, t0, t1, t2, t3, t4, t5, t6, t7);
}

vec4 Nearest2D(sampler2D texture, vec2 shape, vec2 uv) {
    return texture2D(texture, uv);
}

vec4 Nearest3D(sampler3D texture, vec3 shape, vec3 uv) {
    return texture3D(texture, uv);
}

vec4 Linear2D(sampler2D texture, vec2 shape, vec2 uv) {
    return filter2D_radius1(texture, u_kernel, 0.03125, uv, 1 / shape);
}

vec4 Linear3D(sampler3D texture, vec3 shape, vec3 uv) {
    return filter3D_radius1(texture, u_kernel, 0.03125, uv, 1 / shape);
}

vec4 Hanning2D(sampler2D texture, vec2 shape, vec2 uv) {
    return filter2D_radius1(texture, u_kernel, 0.09375, uv, 1 / shape);
}

vec4 Hanning3D(sampler3D texture, vec3 shape, vec3 uv) {
    return filter3D_radius1(texture, u_kernel, 0.09375, uv, 1 / shape);
}

vec4 Hamming2D(sampler2D texture, vec2 shape, vec2 uv) {
    return filter2D_radius1(texture, u_kernel, 0.15625, uv, 1 / shape);
}

vec4 Hamming3D(sampler3D texture, vec3 shape, vec3 uv) {
    return filter3D_radius1(texture, u_kernel, 0.15625, uv, 1 / shape);
}

vec4 Hermite2D(sampler2D texture, vec2 shape, vec2 uv) {
    return filter2D_radius1(texture, u_kernel, 0.21875, uv, 1 / shape);
}

vec4 Hermite3D(sampler3D texture, vec3 shape, vec3 uv) {
    return filter3D_radius1(texture, u_kernel, 0.21875, uv, 1 / shape);
}

vec4 Kaiser2D(sampler2D texture, vec2 shape, vec2 uv) {
    return filter2D_radius1(texture, u_kernel, 0.28125, uv, 1 / shape);
}

vec4 Kaiser3D(sampler3D texture, vec3 shape, vec3 uv) {
    return filter3D_radius1(texture, u_kernel, 0.28125, uv, 1 / shape);
}

vec4 Quadric2D(sampler2D texture, vec2 shape, vec2 uv) {
    return filter2D_radius2(texture, u_kernel, 0.34375, uv, 1 / shape);
}

vec4 Quadric3D(sampler3D texture, vec3 shape, vec3 uv) {
    return filter3D_radius2(texture, u_kernel, 0.34375, uv, 1 / shape);
}

vec4 Cubic2D(sampler2D texture, vec2 shape, vec2 uv) {
    return filter2D_radius2(texture, u_kernel, 0.40625, uv, 1 / shape);
}

vec4 Cubic3D(sampler3D texture, vec3 shape, vec3 uv) {
    return filter3D_radius2(texture, u_kernel, 0.40625, uv, 1 / shape);
}

vec4 CatRom2D(sampler2D texture, vec2 shape, vec2 uv) {
    return filter2D_radius2(texture, u_kernel, 0.46875, uv, 1 / shape);
}

vec4 CatRom3D(sampler3D texture, vec3 shape, vec3 uv) {
    return filter3D_radius2(texture, u_kernel, 0.46875, uv, 1 / shape);
}

vec4 Mitchell2D(sampler2D texture, vec2 shape, vec2 uv) {
    return filter2D_radius2(texture, u_kernel, 0.53125, uv, 1 / shape);
}

vec4 Mitchell3D(sampler3D texture, vec3 shape, vec3 uv) {
    return filter3D_radius2(texture, u_kernel, 0.53125, uv, 1 / shape);
}

vec4 Spline162D(sampler2D texture, vec2 shape, vec2 uv) {
    return filter2D_radius2(texture, u_kernel, 0.59375, uv, 1 / shape);
}

vec4 Spline163D(sampler3D texture, vec3 shape, vec3 uv) {
    return filter3D_radius2(texture, u_kernel, 0.59375, uv, 1 / shape);
}

vec4 Spline362D(sampler2D texture, vec2 shape, vec2 uv) {
    return filter2D_radius3(texture, u_kernel, 0.65625, uv, 1 / shape);
}

vec4 Spline363D(sampler3D texture, vec3 shape, vec3 uv) {
    return filter3D_radius3(texture, u_kernel, 0.65625, uv, 1 / shape);
}

vec4 Gaussian2D(sampler2D texture, vec2 shape, vec2 uv) {
    return filter2D_radius2(texture, u_kernel, 0.71875, uv, 1 / shape);
}

vec4 Gaussian3D(sampler3D texture, vec3 shape, vec3 uv) {
    return filter3D_radius2(texture, u_kernel, 0.71875, uv, 1 / shape);
}

vec4 Bessel2D(sampler2D texture, vec2 shape, vec2 uv) {
    return filter2D_radius4(texture, u_kernel, 0.78125, uv, 1 / shape);
}

vec4 Bessel3D(sampler3D texture, vec3 shape, vec3 uv) {
    return filter3D_radius4(texture, u_kernel, 0.78125, uv, 1 / shape);
}

vec4 Sinc2D(sampler2D texture, vec2 shape, vec2 uv) {
    return filter2D_radius4(texture, u_kernel, 0.84375, uv, 1 / shape);
}

vec4 Sinc3D(sampler3D texture, vec3 shape, vec3 uv) {
    return filter3D_radius4(texture, u_kernel, 0.84375, uv, 1 / shape);
}

vec4 Lanczos2D(sampler2D texture, vec2 shape, vec2 uv) {
    return filter2D_radius4(texture, u_kernel, 0.90625, uv, 1 / shape);
}

vec4 Lanczos3D(sampler3D texture, vec3 shape, vec3 uv) {
    return filter3D_radius4(texture, u_kernel, 0.90625, uv, 1 / shape);
}

vec4 Blackman2D(sampler2D texture, vec2 shape, vec2 uv) {
    return filter2D_radius4(texture, u_kernel, 0.96875, uv, 1 / shape);
}

vec4 Blackman3D(sampler3D texture, vec3 shape, vec3 uv) {
    return filter3D_radius4(texture, u_kernel, 0.96875, uv, 1 / shape);
}
