// ------------------------------------
// Automatically generated, do not edit
// ------------------------------------

const float kernel_bias  = -0.234377;
const float kernel_scale = 1.241974;
const float kernel_size = 1024.000000;
const vec4 bits = vec4(1.0, 1.0/256.0, 1.0/(256.0*256.0), 1.0/(256.0*256.0*256.0));
uniform sampler2D u_kernel;

float
unpack_unit(vec4 rgba)
{
    // return rgba.r;  // uncomment this for r32f debugging
    return dot(rgba, bits);
}

float
unpack_ieee(vec4 rgba)
{
    // return rgba.r;  // uncomment this for r32f debugging
    rgba.rgba = rgba.abgr * 255;
    float sign = 1.0 - step(128.0,rgba[0])*2.0;
    float exponent = 2.0 * mod(rgba[0],128.0) + step(128.0,rgba[1]) - 127.0;
    float mantissa = mod(rgba[1],128.0)*65536.0 + rgba[2]*256.0 + rgba[3] + float(0x800000);
    return sign * exp2(exponent) * (mantissa * exp2(-23));
}

float
unpack_interpolate(sampler2D kernel, vec2 uv)
{
    // return texture2D(kernel, uv).r; //uncomment this for r32f debug without interpolation
    float kpixel = 1/kernel_size;
    float u = uv.x / kpixel;
    float v = uv.y;
    float uf = fract(u);
    u = (u - uf) * kpixel;

    float d0 = unpack_unit(texture2D(kernel, vec2(u, v)));
    float d1 = unpack_unit(texture2D(kernel, vec2(u + 1 * kpixel, v)));
    return mix(d0, d1, uf);
}

vec4
filter1D_radius1( sampler2D kernel, float index, float x, vec4 c0, vec4 c1 )
{
    float w, w_sum = 0.0;
    vec4 r = vec4(0.0,0.0,0.0,0.0);
    w = unpack_interpolate(kernel, vec2(0.000000+(x/1.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c0 * w;
    w = unpack_interpolate(kernel, vec2(1.000000-(x/1.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c1 * w;
    return r;
}

vec4
filter2D_radius1(sampler2D texture, sampler2D kernel, float index, vec2 uv, vec2 pixel)
{
    vec2 texel = uv/pixel - vec2(0.5, 0.5) ;
    vec2 f = fract(texel);
    texel = (texel-fract(texel) + vec2(0.001, 0.001)) * pixel;
    vec4 t0 = filter1D_radius1(kernel, index, f.x,
        texture2D( texture, texel + vec2(0, 0) * pixel),
        texture2D( texture, texel + vec2(1, 0) * pixel));
    vec4 t1 = filter1D_radius1(kernel, index, f.x,
        texture2D( texture, texel + vec2(0, 1) * pixel),
        texture2D( texture, texel + vec2(1, 1) * pixel));
    return filter1D_radius1(kernel, index, f.y, t0, t1);
}

vec4
filter1D_radius2( sampler2D kernel, float index, float x, vec4 c0, vec4 c1, vec4 c2, vec4 c3 )
{
    float w, w_sum = 0.0;
    vec4 r = vec4(0.0,0.0,0.0,0.0);
    w = unpack_interpolate(kernel, vec2(0.500000+(x/2.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c0 * w;
    w = unpack_interpolate(kernel, vec2(0.500000-(x/2.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c2 * w;
    w = unpack_interpolate(kernel, vec2(0.000000+(x/2.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c1 * w;
    w = unpack_interpolate(kernel, vec2(1.000000-(x/2.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c3 * w;
    return r;
}

vec4
filter2D_radius2(sampler2D texture, sampler2D kernel, float index, vec2 uv, vec2 pixel)
{
    vec2 texel = uv/pixel - vec2(0.5, 0.5) ;
    vec2 f = fract(texel);
    texel = (texel-fract(texel) + vec2(0.001, 0.001)) * pixel;
    vec4 t0 = filter1D_radius2(kernel, index, f.x,
        texture2D( texture, texel + vec2(-1, -1) * pixel),
        texture2D( texture, texel + vec2(0, -1) * pixel),
        texture2D( texture, texel + vec2(1, -1) * pixel),
        texture2D( texture, texel + vec2(2, -1) * pixel));
    vec4 t1 = filter1D_radius2(kernel, index, f.x,
        texture2D( texture, texel + vec2(-1, 0) * pixel),
        texture2D( texture, texel + vec2(0, 0) * pixel),
        texture2D( texture, texel + vec2(1, 0) * pixel),
        texture2D( texture, texel + vec2(2, 0) * pixel));
    vec4 t2 = filter1D_radius2(kernel, index, f.x,
        texture2D( texture, texel + vec2(-1, 1) * pixel),
        texture2D( texture, texel + vec2(0, 1) * pixel),
        texture2D( texture, texel + vec2(1, 1) * pixel),
        texture2D( texture, texel + vec2(2, 1) * pixel));
    vec4 t3 = filter1D_radius2(kernel, index, f.x,
        texture2D( texture, texel + vec2(-1, 2) * pixel),
        texture2D( texture, texel + vec2(0, 2) * pixel),
        texture2D( texture, texel + vec2(1, 2) * pixel),
        texture2D( texture, texel + vec2(2, 2) * pixel));
    return filter1D_radius2(kernel, index, f.y, t0, t1, t2, t3);
}

vec4
filter1D_radius3( sampler2D kernel, float index, float x, vec4 c0, vec4 c1, vec4 c2, vec4 c3, vec4 c4, vec4 c5 )
{
    float w, w_sum = 0.0;
    vec4 r = vec4(0.0,0.0,0.0,0.0);
    w = unpack_interpolate(kernel, vec2(0.666667+(x/3.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c0 * w;
    w = unpack_interpolate(kernel, vec2(0.333333-(x/3.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c3 * w;
    w = unpack_interpolate(kernel, vec2(0.333333+(x/3.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c1 * w;
    w = unpack_interpolate(kernel, vec2(0.666667-(x/3.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c4 * w;
    w = unpack_interpolate(kernel, vec2(0.000000+(x/3.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c2 * w;
    w = unpack_interpolate(kernel, vec2(1.000000-(x/3.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c5 * w;
    return r;
}

vec4
filter2D_radius3(sampler2D texture, sampler2D kernel, float index, vec2 uv, vec2 pixel)
{
    vec2 texel = uv/pixel - vec2(0.5, 0.5) ;
    vec2 f = fract(texel);
    texel = (texel-fract(texel) + vec2(0.001, 0.001)) * pixel;
    vec4 t0 = filter1D_radius3(kernel, index, f.x,
        texture2D( texture, texel + vec2(-2, -2) * pixel),
        texture2D( texture, texel + vec2(-1, -2) * pixel),
        texture2D( texture, texel + vec2(0, -2) * pixel),
        texture2D( texture, texel + vec2(1, -2) * pixel),
        texture2D( texture, texel + vec2(2, -2) * pixel),
        texture2D( texture, texel + vec2(3, -2) * pixel));
    vec4 t1 = filter1D_radius3(kernel, index, f.x,
        texture2D( texture, texel + vec2(-2, -1) * pixel),
        texture2D( texture, texel + vec2(-1, -1) * pixel),
        texture2D( texture, texel + vec2(0, -1) * pixel),
        texture2D( texture, texel + vec2(1, -1) * pixel),
        texture2D( texture, texel + vec2(2, -1) * pixel),
        texture2D( texture, texel + vec2(3, -1) * pixel));
    vec4 t2 = filter1D_radius3(kernel, index, f.x,
        texture2D( texture, texel + vec2(-2, 0) * pixel),
        texture2D( texture, texel + vec2(-1, 0) * pixel),
        texture2D( texture, texel + vec2(0, 0) * pixel),
        texture2D( texture, texel + vec2(1, 0) * pixel),
        texture2D( texture, texel + vec2(2, 0) * pixel),
        texture2D( texture, texel + vec2(3, 0) * pixel));
    vec4 t3 = filter1D_radius3(kernel, index, f.x,
        texture2D( texture, texel + vec2(-2, 1) * pixel),
        texture2D( texture, texel + vec2(-1, 1) * pixel),
        texture2D( texture, texel + vec2(0, 1) * pixel),
        texture2D( texture, texel + vec2(1, 1) * pixel),
        texture2D( texture, texel + vec2(2, 1) * pixel),
        texture2D( texture, texel + vec2(3, 1) * pixel));
    vec4 t4 = filter1D_radius3(kernel, index, f.x,
        texture2D( texture, texel + vec2(-2, 2) * pixel),
        texture2D( texture, texel + vec2(-1, 2) * pixel),
        texture2D( texture, texel + vec2(0, 2) * pixel),
        texture2D( texture, texel + vec2(1, 2) * pixel),
        texture2D( texture, texel + vec2(2, 2) * pixel),
        texture2D( texture, texel + vec2(3, 2) * pixel));
    vec4 t5 = filter1D_radius3(kernel, index, f.x,
        texture2D( texture, texel + vec2(-2, 3) * pixel),
        texture2D( texture, texel + vec2(-1, 3) * pixel),
        texture2D( texture, texel + vec2(0, 3) * pixel),
        texture2D( texture, texel + vec2(1, 3) * pixel),
        texture2D( texture, texel + vec2(2, 3) * pixel),
        texture2D( texture, texel + vec2(3, 3) * pixel));
    return filter1D_radius3(kernel, index, f.y, t0, t1, t2, t3, t4, t5);
}

vec4
filter1D_radius4( sampler2D kernel, float index, float x, vec4 c0, vec4 c1, vec4 c2, vec4 c3, vec4 c4, vec4 c5, vec4 c6, vec4 c7 )
{
    float w, w_sum = 0.0;
    vec4 r = vec4(0.0,0.0,0.0,0.0);
    w = unpack_interpolate(kernel, vec2(0.750000+(x/4.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c0 * w;
    w = unpack_interpolate(kernel, vec2(0.250000-(x/4.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c4 * w;
    w = unpack_interpolate(kernel, vec2(0.500000+(x/4.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c1 * w;
    w = unpack_interpolate(kernel, vec2(0.500000-(x/4.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c5 * w;
    w = unpack_interpolate(kernel, vec2(0.250000+(x/4.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c2 * w;
    w = unpack_interpolate(kernel, vec2(0.750000-(x/4.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c6 * w;
    w = unpack_interpolate(kernel, vec2(0.000000+(x/4.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c3 * w;
    w = unpack_interpolate(kernel, vec2(1.000000-(x/4.0), index));
    w = w*kernel_scale + kernel_bias;
    r += c7 * w;
    return r;
}

vec4
filter2D_radius4(sampler2D texture, sampler2D kernel, float index, vec2 uv, vec2 pixel)
{
    vec2 texel = uv/pixel - vec2(0.5, 0.5) ;
    vec2 f = fract(texel);
    texel = (texel-fract(texel) + vec2(0.001, 0.001)) * pixel;
    vec4 t0 = filter1D_radius4(kernel, index, f.x,
        texture2D( texture, texel + vec2(-3, -3) * pixel),
        texture2D( texture, texel + vec2(-2, -3) * pixel),
        texture2D( texture, texel + vec2(-1, -3) * pixel),
        texture2D( texture, texel + vec2(0, -3) * pixel),
        texture2D( texture, texel + vec2(1, -3) * pixel),
        texture2D( texture, texel + vec2(2, -3) * pixel),
        texture2D( texture, texel + vec2(3, -3) * pixel),
        texture2D( texture, texel + vec2(4, -3) * pixel));
    vec4 t1 = filter1D_radius4(kernel, index, f.x,
        texture2D( texture, texel + vec2(-3, -2) * pixel),
        texture2D( texture, texel + vec2(-2, -2) * pixel),
        texture2D( texture, texel + vec2(-1, -2) * pixel),
        texture2D( texture, texel + vec2(0, -2) * pixel),
        texture2D( texture, texel + vec2(1, -2) * pixel),
        texture2D( texture, texel + vec2(2, -2) * pixel),
        texture2D( texture, texel + vec2(3, -2) * pixel),
        texture2D( texture, texel + vec2(4, -2) * pixel));
    vec4 t2 = filter1D_radius4(kernel, index, f.x,
        texture2D( texture, texel + vec2(-3, -1) * pixel),
        texture2D( texture, texel + vec2(-2, -1) * pixel),
        texture2D( texture, texel + vec2(-1, -1) * pixel),
        texture2D( texture, texel + vec2(0, -1) * pixel),
        texture2D( texture, texel + vec2(1, -1) * pixel),
        texture2D( texture, texel + vec2(2, -1) * pixel),
        texture2D( texture, texel + vec2(3, -1) * pixel),
        texture2D( texture, texel + vec2(4, -1) * pixel));
    vec4 t3 = filter1D_radius4(kernel, index, f.x,
        texture2D( texture, texel + vec2(-3, 0) * pixel),
        texture2D( texture, texel + vec2(-2, 0) * pixel),
        texture2D( texture, texel + vec2(-1, 0) * pixel),
        texture2D( texture, texel + vec2(0, 0) * pixel),
        texture2D( texture, texel + vec2(1, 0) * pixel),
        texture2D( texture, texel + vec2(2, 0) * pixel),
        texture2D( texture, texel + vec2(3, 0) * pixel),
        texture2D( texture, texel + vec2(4, 0) * pixel));
    vec4 t4 = filter1D_radius4(kernel, index, f.x,
        texture2D( texture, texel + vec2(-3, 1) * pixel),
        texture2D( texture, texel + vec2(-2, 1) * pixel),
        texture2D( texture, texel + vec2(-1, 1) * pixel),
        texture2D( texture, texel + vec2(0, 1) * pixel),
        texture2D( texture, texel + vec2(1, 1) * pixel),
        texture2D( texture, texel + vec2(2, 1) * pixel),
        texture2D( texture, texel + vec2(3, 1) * pixel),
        texture2D( texture, texel + vec2(4, 1) * pixel));
    vec4 t5 = filter1D_radius4(kernel, index, f.x,
        texture2D( texture, texel + vec2(-3, 2) * pixel),
        texture2D( texture, texel + vec2(-2, 2) * pixel),
        texture2D( texture, texel + vec2(-1, 2) * pixel),
        texture2D( texture, texel + vec2(0, 2) * pixel),
        texture2D( texture, texel + vec2(1, 2) * pixel),
        texture2D( texture, texel + vec2(2, 2) * pixel),
        texture2D( texture, texel + vec2(3, 2) * pixel),
        texture2D( texture, texel + vec2(4, 2) * pixel));
    vec4 t6 = filter1D_radius4(kernel, index, f.x,
        texture2D( texture, texel + vec2(-3, 3) * pixel),
        texture2D( texture, texel + vec2(-2, 3) * pixel),
        texture2D( texture, texel + vec2(-1, 3) * pixel),
        texture2D( texture, texel + vec2(0, 3) * pixel),
        texture2D( texture, texel + vec2(1, 3) * pixel),
        texture2D( texture, texel + vec2(2, 3) * pixel),
        texture2D( texture, texel + vec2(3, 3) * pixel),
        texture2D( texture, texel + vec2(4, 3) * pixel));
    vec4 t7 = filter1D_radius4(kernel, index, f.x,
        texture2D( texture, texel + vec2(-3, 4) * pixel),
        texture2D( texture, texel + vec2(-2, 4) * pixel),
        texture2D( texture, texel + vec2(-1, 4) * pixel),
        texture2D( texture, texel + vec2(0, 4) * pixel),
        texture2D( texture, texel + vec2(1, 4) * pixel),
        texture2D( texture, texel + vec2(2, 4) * pixel),
        texture2D( texture, texel + vec2(3, 4) * pixel),
        texture2D( texture, texel + vec2(4, 4) * pixel));
    return filter1D_radius4(kernel, index, f.y, t0, t1, t2, t3, t4, t5, t6, t7);
}

vec4 Nearest(sampler2D texture, vec2 shape, vec2 uv)
{ return texture2D(texture,uv); }

vec4 Bilinear(sampler2D texture, vec2 shape, vec2 uv)
{ return filter2D_radius1(texture, u_kernel, 0.031250, uv, 1.0/shape); }

vec4 Hanning(sampler2D texture, vec2 shape, vec2 uv)
{ return filter2D_radius1(texture, u_kernel, 0.093750, uv, 1.0/shape); }

vec4 Hamming(sampler2D texture, vec2 shape, vec2 uv)
{ return filter2D_radius1(texture, u_kernel, 0.156250, uv, 1.0/shape); }

vec4 Hermite(sampler2D texture, vec2 shape, vec2 uv)
{ return filter2D_radius1(texture, u_kernel, 0.218750, uv, 1.0/shape); }

vec4 Kaiser(sampler2D texture, vec2 shape, vec2 uv)
{ return filter2D_radius1(texture, u_kernel, 0.281250, uv, 1.0/shape); }

vec4 Quadric(sampler2D texture, vec2 shape, vec2 uv)
{ return filter2D_radius2(texture, u_kernel, 0.343750, uv, 1.0/shape); }

vec4 Bicubic(sampler2D texture, vec2 shape, vec2 uv)
{ return filter2D_radius2(texture, u_kernel, 0.406250, uv, 1.0/shape); }

vec4 CatRom(sampler2D texture, vec2 shape, vec2 uv)
{ return filter2D_radius2(texture, u_kernel, 0.468750, uv, 1.0/shape); }

vec4 Mitchell(sampler2D texture, vec2 shape, vec2 uv)
{ return filter2D_radius2(texture, u_kernel, 0.531250, uv, 1.0/shape); }

vec4 Spline16(sampler2D texture, vec2 shape, vec2 uv)
{ return filter2D_radius2(texture, u_kernel, 0.593750, uv, 1.0/shape); }

vec4 Spline36(sampler2D texture, vec2 shape, vec2 uv)
{ return filter2D_radius3(texture, u_kernel, 0.656250, uv, 1.0/shape); }

vec4 Gaussian(sampler2D texture, vec2 shape, vec2 uv)
{ return filter2D_radius2(texture, u_kernel, 0.718750, uv, 1.0/shape); }

vec4 Bessel(sampler2D texture, vec2 shape, vec2 uv)
{ return filter2D_radius4(texture, u_kernel, 0.781250, uv, 1.0/shape); }

vec4 Sinc(sampler2D texture, vec2 shape, vec2 uv)
{ return filter2D_radius4(texture, u_kernel, 0.843750, uv, 1.0/shape); }

vec4 Lanczos(sampler2D texture, vec2 shape, vec2 uv)
{ return filter2D_radius4(texture, u_kernel, 0.906250, uv, 1.0/shape); }

vec4 Blackman(sampler2D texture, vec2 shape, vec2 uv)
{ return filter2D_radius4(texture, u_kernel, 0.968750, uv, 1.0/shape); }

