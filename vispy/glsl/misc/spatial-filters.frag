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
    w = w*kernel_scale + kernel_bias;
    r += c1 * w;
    return r;
}

vec4 filter2D_radius1(sampler2D texture, sampler2D kernel, float index, vec2 uv, vec2 pixel) {
    vec2 texel = uv / pixel - vec2(0.5, 0.5);
    vec2 f = fract(texel);
    texel = (texel - fract(texel) + vec2(0.001, 0.001)) * pixel;
    
    vec4 t0 = filter_1D_radius1(kernel, index, f.x,
        texture2D(texture, texel + vec2(0, 0) * pixel),
        texture2D(texture, texel + vec2(1, 0) * pixel));
    vec4 t1 = filter_1D_radius1(kernel, index, f.x,
        texture2D(texture, texel + vec2(0, 1) * pixel),
        texture2D(texture, texel + vec2(1, 1) * pixel));
    return filter_1D_radius1(kernel, index, f.y, t0, t1);
}

vec4 filter3D_radius1(sampler3D texture, sampler2D kernel, float index, vec3 uv, vec3 pixel) {
    return;
}

vec4 filter1D_radius2(sampler2D kernel, float index, float x, vec4 c0, vec4 c1, vec4 c2, vec4 c3) {
    float w, w_sum = 0;
    vec4 r = vec4(0);
    w = unpack_interpolate(kernel, vec2(0.5 + (x / 2), index));
    w = w * kernel_scale + kernel_bias;
    r += c0 * w;
    w = unpack_interpolate(kernel, vec2(0.5 - (x / 2), index));
    w = w*kernel_scale + kernel_bias;
    r += c2 * w;w = unpack_interpolate(kernel, vec2(0.0 + (x / 2), index));
    w = w * kernel_scale + kernel_bias;
    r += c1 * w;
    w = unpack_interpolate(kernel, vec2(1.0 - (x / 2), index));
    w = w*kernel_scale + kernel_bias;
    r += c3 * w;
    return r;
}

vec4 filter2D_radius2(sampler2D texture, sampler2D kernel, float index, vec2 uv, vec2 pixel) {
    vec2 texel = uv / pixel - vec2(0.5, 0.5);
    vec2 f = fract(texel);
    texel = (texel - fract(texel) + vec2(0.001, 0.001)) * pixel;
    
    vec4 t0 = filter_1D_radius2(kernel, index, f.x,
        texture2D(texture, texel + vec2(-1, -1) * pixel),
        texture2D(texture, texel + vec2(0, -1) * pixel),
        texture2D(texture, texel + vec2(1, -1) * pixel),
        texture2D(texture, texel + vec2(2, -1) * pixel));
    vec4 t1 = filter_1D_radius2(kernel, index, f.x,
        texture2D(texture, texel + vec2(-1, 0) * pixel),
        texture2D(texture, texel + vec2(0, 0) * pixel),
        texture2D(texture, texel + vec2(1, 0) * pixel),
        texture2D(texture, texel + vec2(2, 0) * pixel));
    vec4 t2 = filter_1D_radius2(kernel, index, f.x,
        texture2D(texture, texel + vec2(-1, 1) * pixel),
        texture2D(texture, texel + vec2(0, 1) * pixel),
        texture2D(texture, texel + vec2(1, 1) * pixel),
        texture2D(texture, texel + vec2(2, 1) * pixel));
    vec4 t3 = filter_1D_radius2(kernel, index, f.x,
        texture2D(texture, texel + vec2(-1, 2) * pixel),
        texture2D(texture, texel + vec2(0, 2) * pixel),
        texture2D(texture, texel + vec2(1, 2) * pixel),
        texture2D(texture, texel + vec2(2, 2) * pixel));
    return filter_1D_radius2(kernel, index, f.y, t0, t1, t2, t3);
}

vec4 filter3D_radius2(sampler3D texture, sampler2D kernel, float index, vec3 uv, vec3 pixel) {
    return;
}

vec4 filter1D_radius3(sampler2D kernel, float index, float x, vec4 c0, vec4 c1, vec4 c2, vec4 c3, vec4 c4, vec4 c5) {
    float w, w_sum = 0;
    vec4 r = vec4(0);
    w = unpack_interpolate(kernel, vec2(0.6666666666666667 + (x / 3), index));
    w = w * kernel_scale + kernel_bias;
    r += c0 * w;
    w = unpack_interpolate(kernel, vec2(0.3333333333333333 - (x / 3), index));
    w = w*kernel_scale + kernel_bias;
    r += c3 * w;w = unpack_interpolate(kernel, vec2(0.33333333333333337 + (x / 3), index));
    w = w * kernel_scale + kernel_bias;
    r += c1 * w;
    w = unpack_interpolate(kernel, vec2(0.6666666666666666 - (x / 3), index));
    w = w*kernel_scale + kernel_bias;
    r += c4 * w;w = unpack_interpolate(kernel, vec2(0.0 + (x / 3), index));
    w = w * kernel_scale + kernel_bias;
    r += c2 * w;
    w = unpack_interpolate(kernel, vec2(1.0 - (x / 3), index));
    w = w*kernel_scale + kernel_bias;
    r += c5 * w;
    return r;
}

vec4 filter2D_radius3(sampler2D texture, sampler2D kernel, float index, vec2 uv, vec2 pixel) {
    vec2 texel = uv / pixel - vec2(0.5, 0.5);
    vec2 f = fract(texel);
    texel = (texel - fract(texel) + vec2(0.001, 0.001)) * pixel;
    
    vec4 t0 = filter_1D_radius3(kernel, index, f.x,
        texture2D(texture, texel + vec2(-2, -2) * pixel),
        texture2D(texture, texel + vec2(-1, -2) * pixel),
        texture2D(texture, texel + vec2(0, -2) * pixel),
        texture2D(texture, texel + vec2(1, -2) * pixel),
        texture2D(texture, texel + vec2(2, -2) * pixel),
        texture2D(texture, texel + vec2(3, -2) * pixel));
    vec4 t1 = filter_1D_radius3(kernel, index, f.x,
        texture2D(texture, texel + vec2(-2, -1) * pixel),
        texture2D(texture, texel + vec2(-1, -1) * pixel),
        texture2D(texture, texel + vec2(0, -1) * pixel),
        texture2D(texture, texel + vec2(1, -1) * pixel),
        texture2D(texture, texel + vec2(2, -1) * pixel),
        texture2D(texture, texel + vec2(3, -1) * pixel));
    vec4 t2 = filter_1D_radius3(kernel, index, f.x,
        texture2D(texture, texel + vec2(-2, 0) * pixel),
        texture2D(texture, texel + vec2(-1, 0) * pixel),
        texture2D(texture, texel + vec2(0, 0) * pixel),
        texture2D(texture, texel + vec2(1, 0) * pixel),
        texture2D(texture, texel + vec2(2, 0) * pixel),
        texture2D(texture, texel + vec2(3, 0) * pixel));
    vec4 t3 = filter_1D_radius3(kernel, index, f.x,
        texture2D(texture, texel + vec2(-2, 1) * pixel),
        texture2D(texture, texel + vec2(-1, 1) * pixel),
        texture2D(texture, texel + vec2(0, 1) * pixel),
        texture2D(texture, texel + vec2(1, 1) * pixel),
        texture2D(texture, texel + vec2(2, 1) * pixel),
        texture2D(texture, texel + vec2(3, 1) * pixel));
    vec4 t4 = filter_1D_radius3(kernel, index, f.x,
        texture2D(texture, texel + vec2(-2, 2) * pixel),
        texture2D(texture, texel + vec2(-1, 2) * pixel),
        texture2D(texture, texel + vec2(0, 2) * pixel),
        texture2D(texture, texel + vec2(1, 2) * pixel),
        texture2D(texture, texel + vec2(2, 2) * pixel),
        texture2D(texture, texel + vec2(3, 2) * pixel));
    vec4 t5 = filter_1D_radius3(kernel, index, f.x,
        texture2D(texture, texel + vec2(-2, 3) * pixel),
        texture2D(texture, texel + vec2(-1, 3) * pixel),
        texture2D(texture, texel + vec2(0, 3) * pixel),
        texture2D(texture, texel + vec2(1, 3) * pixel),
        texture2D(texture, texel + vec2(2, 3) * pixel),
        texture2D(texture, texel + vec2(3, 3) * pixel));
    return filter_1D_radius3(kernel, index, f.y, t0, t1, t2, t3, t4, t5);
}

vec4 filter3D_radius3(sampler3D texture, sampler2D kernel, float index, vec3 uv, vec3 pixel) {
    return;
}

vec4 filter1D_radius4(sampler2D kernel, float index, float x, vec4 c0, vec4 c1, vec4 c2, vec4 c3, vec4 c4, vec4 c5, vec4 c6, vec4 c7) {
    float w, w_sum = 0;
    vec4 r = vec4(0);
    w = unpack_interpolate(kernel, vec2(0.75 + (x / 4), index));
    w = w * kernel_scale + kernel_bias;
    r += c0 * w;
    w = unpack_interpolate(kernel, vec2(0.25 - (x / 4), index));
    w = w*kernel_scale + kernel_bias;
    r += c4 * w;w = unpack_interpolate(kernel, vec2(0.5 + (x / 4), index));
    w = w * kernel_scale + kernel_bias;
    r += c1 * w;
    w = unpack_interpolate(kernel, vec2(0.5 - (x / 4), index));
    w = w*kernel_scale + kernel_bias;
    r += c5 * w;w = unpack_interpolate(kernel, vec2(0.25 + (x / 4), index));
    w = w * kernel_scale + kernel_bias;
    r += c2 * w;
    w = unpack_interpolate(kernel, vec2(0.75 - (x / 4), index));
    w = w*kernel_scale + kernel_bias;
    r += c6 * w;w = unpack_interpolate(kernel, vec2(0.0 + (x / 4), index));
    w = w * kernel_scale + kernel_bias;
    r += c3 * w;
    w = unpack_interpolate(kernel, vec2(1.0 - (x / 4), index));
    w = w*kernel_scale + kernel_bias;
    r += c7 * w;
    return r;
}

vec4 filter2D_radius4(sampler2D texture, sampler2D kernel, float index, vec2 uv, vec2 pixel) {
    vec2 texel = uv / pixel - vec2(0.5, 0.5);
    vec2 f = fract(texel);
    texel = (texel - fract(texel) + vec2(0.001, 0.001)) * pixel;
    
    vec4 t0 = filter_1D_radius4(kernel, index, f.x,
        texture2D(texture, texel + vec2(-3, -3) * pixel),
        texture2D(texture, texel + vec2(-2, -3) * pixel),
        texture2D(texture, texel + vec2(-1, -3) * pixel),
        texture2D(texture, texel + vec2(0, -3) * pixel),
        texture2D(texture, texel + vec2(1, -3) * pixel),
        texture2D(texture, texel + vec2(2, -3) * pixel),
        texture2D(texture, texel + vec2(3, -3) * pixel),
        texture2D(texture, texel + vec2(4, -3) * pixel));
    vec4 t1 = filter_1D_radius4(kernel, index, f.x,
        texture2D(texture, texel + vec2(-3, -2) * pixel),
        texture2D(texture, texel + vec2(-2, -2) * pixel),
        texture2D(texture, texel + vec2(-1, -2) * pixel),
        texture2D(texture, texel + vec2(0, -2) * pixel),
        texture2D(texture, texel + vec2(1, -2) * pixel),
        texture2D(texture, texel + vec2(2, -2) * pixel),
        texture2D(texture, texel + vec2(3, -2) * pixel),
        texture2D(texture, texel + vec2(4, -2) * pixel));
    vec4 t2 = filter_1D_radius4(kernel, index, f.x,
        texture2D(texture, texel + vec2(-3, -1) * pixel),
        texture2D(texture, texel + vec2(-2, -1) * pixel),
        texture2D(texture, texel + vec2(-1, -1) * pixel),
        texture2D(texture, texel + vec2(0, -1) * pixel),
        texture2D(texture, texel + vec2(1, -1) * pixel),
        texture2D(texture, texel + vec2(2, -1) * pixel),
        texture2D(texture, texel + vec2(3, -1) * pixel),
        texture2D(texture, texel + vec2(4, -1) * pixel));
    vec4 t3 = filter_1D_radius4(kernel, index, f.x,
        texture2D(texture, texel + vec2(-3, 0) * pixel),
        texture2D(texture, texel + vec2(-2, 0) * pixel),
        texture2D(texture, texel + vec2(-1, 0) * pixel),
        texture2D(texture, texel + vec2(0, 0) * pixel),
        texture2D(texture, texel + vec2(1, 0) * pixel),
        texture2D(texture, texel + vec2(2, 0) * pixel),
        texture2D(texture, texel + vec2(3, 0) * pixel),
        texture2D(texture, texel + vec2(4, 0) * pixel));
    vec4 t4 = filter_1D_radius4(kernel, index, f.x,
        texture2D(texture, texel + vec2(-3, 1) * pixel),
        texture2D(texture, texel + vec2(-2, 1) * pixel),
        texture2D(texture, texel + vec2(-1, 1) * pixel),
        texture2D(texture, texel + vec2(0, 1) * pixel),
        texture2D(texture, texel + vec2(1, 1) * pixel),
        texture2D(texture, texel + vec2(2, 1) * pixel),
        texture2D(texture, texel + vec2(3, 1) * pixel),
        texture2D(texture, texel + vec2(4, 1) * pixel));
    vec4 t5 = filter_1D_radius4(kernel, index, f.x,
        texture2D(texture, texel + vec2(-3, 2) * pixel),
        texture2D(texture, texel + vec2(-2, 2) * pixel),
        texture2D(texture, texel + vec2(-1, 2) * pixel),
        texture2D(texture, texel + vec2(0, 2) * pixel),
        texture2D(texture, texel + vec2(1, 2) * pixel),
        texture2D(texture, texel + vec2(2, 2) * pixel),
        texture2D(texture, texel + vec2(3, 2) * pixel),
        texture2D(texture, texel + vec2(4, 2) * pixel));
    vec4 t6 = filter_1D_radius4(kernel, index, f.x,
        texture2D(texture, texel + vec2(-3, 3) * pixel),
        texture2D(texture, texel + vec2(-2, 3) * pixel),
        texture2D(texture, texel + vec2(-1, 3) * pixel),
        texture2D(texture, texel + vec2(0, 3) * pixel),
        texture2D(texture, texel + vec2(1, 3) * pixel),
        texture2D(texture, texel + vec2(2, 3) * pixel),
        texture2D(texture, texel + vec2(3, 3) * pixel),
        texture2D(texture, texel + vec2(4, 3) * pixel));
    vec4 t7 = filter_1D_radius4(kernel, index, f.x,
        texture2D(texture, texel + vec2(-3, 4) * pixel),
        texture2D(texture, texel + vec2(-2, 4) * pixel),
        texture2D(texture, texel + vec2(-1, 4) * pixel),
        texture2D(texture, texel + vec2(0, 4) * pixel),
        texture2D(texture, texel + vec2(1, 4) * pixel),
        texture2D(texture, texel + vec2(2, 4) * pixel),
        texture2D(texture, texel + vec2(3, 4) * pixel),
        texture2D(texture, texel + vec2(4, 4) * pixel));
    return filter_1D_radius4(kernel, index, f.y, t0, t1, t2, t3, t4, t5, t6, t7);
}

vec4 filter3D_radius4(sampler3D texture, sampler2D kernel, float index, vec3 uv, vec3 pixel) {
    return;
}

vec4 Nearest2D(sampler2D texture, vec2 shape, vec2 uv) {
    return texture2D(texture, uv);
}

vec4 Nearest3D(sampler3D texture, vec3 shape, vec3 uv) {
    return texture3D(texture, uv);
}

vec4 Bilinear2D(sampler2D texture, vec2 shape, vec2 uv) {
    return filter2D_radius1(texture, u_kernel, 0.03125, uv, 1 / shape);
}

vec4 Bilinear3D(sampler3D texture, vec3 shape, vec3 uv) {
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

vec4 Bicubic2D(sampler2D texture, vec2 shape, vec2 uv) {
    return filter2D_radius2(texture, u_kernel, 0.40625, uv, 1 / shape);
}

vec4 Bicubic3D(sampler3D texture, vec3 shape, vec3 uv) {
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
