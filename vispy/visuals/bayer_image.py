import numpy as np
from .image import ImageVisual

VERT_SHADER = """
#version 130

attribute vec2 a_position;
attribute vec2 a_texcoord;
varying vec2 v_texcoord;

/** (w,h,1/w,1/h) */
uniform vec4            image_size;

/** Pixel position of the first red pixel in the Bayer pattern.  [{0,1}, {0, 1}]*/
uniform vec2            first_red;

/** .xy = Pixel being sampled in the fragment shader on the range [0, 1]
    .zw = ...on the range [0, image_size], offset by first_red */
out vec4            center;

/** center.x + (-2/w, -1/w, 1/w, 2/w); These are the x-positions of the adjacent pixels.*/
out vec4            xCoord;

/** center.y + (-2/h, -1/h, 1/h, 2/h); These are the y-positions of the adjacent pixels.*/
out vec4            yCoord;

void main(void) {
    v_texcoord = a_texcoord;

    center.xy = a_texcoord.xy;
    //center.zw = a_position.xy * image_size.xy + first_red;
    center.zw = a_position.xy + first_red;
    // center.zw = a_position.xy + first_red;

    vec2 invSize = image_size.zw;
    xCoord = center.x + vec4(-2.0 * invSize.x, -invSize.x, invSize.x, 2.0 * invSize.x);
    yCoord = center.y + vec4(-2.0 * invSize.y, -invSize.y, invSize.y, 2.0 * invSize.y);

    gl_Position = $transform(vec4(a_position, 0., 1.));
}

"""

FRAG_SHADER = """
#version 130

uniform sampler2D       u_texture;

in vec4            center;
in vec4            yCoord;
in vec4            xCoord;

void main(void) {

    #define fetch(x, y) texture2D(u_texture, vec2(x, y)).r

    float C = texture2D(u_texture, center.xy).r; // ( 0, 0)
    const vec4 kC = vec4( 4.0,  6.0,  5.0,  5.0) / 8.0;

    // Determine which of four types of pixels we are on.
    vec2 alternate = mod(floor(center.zw), 2.0);

    vec4 Dvec = vec4(
        fetch(xCoord[1], yCoord[1]),  // (-1,-1)
        fetch(xCoord[1], yCoord[2]),  // (-1, 1)
        fetch(xCoord[2], yCoord[1]),  // ( 1,-1)
        fetch(xCoord[2], yCoord[2])); // ( 1, 1)

    vec4 PATTERN = (kC.xyz * C).xyzz;

    // Can also be a dot product with (1,1,1,1) on hardware where that is
    // specially optimized.
    // Equivalent to: D = Dvec[0] + Dvec[1] + Dvec[2] + Dvec[3];
    Dvec.xy += Dvec.zw;
    Dvec.x  += Dvec.y;

    vec4 value = vec4(
        fetch(center.x, yCoord[0]),   // ( 0,-2)
        fetch(center.x, yCoord[1]),   // ( 0,-1)
        fetch(xCoord[0], center.y),   // (-1, 0)
        fetch(xCoord[1], center.y));  // (-2, 0)

    vec4 temp = vec4(
        fetch(center.x, yCoord[3]),   // ( 0, 2)
        fetch(center.x, yCoord[2]),   // ( 0, 1)
        fetch(xCoord[3], center.y),   // ( 2, 0)
        fetch(xCoord[2], center.y));  // ( 1, 0)

    // Even the simplest compilers should be able to constant-fold these to avoid the division.
    // Note that on scalar processors these constants force computation of some identical products twice.
    const vec4 kA = vec4(-1.0, -1.5,  0.5, -1.0) / 8.0;
    const vec4 kB = vec4( 2.0,  0.0,  0.0,  4.0) / 8.0;
    const vec4 kD = vec4( 0.0,  2.0, -1.0, -1.0) / 8.0;

    // Conserve constant registers and take advantage of free swizzle on load
    #define kE (kA.xywz)
    #define kF (kB.xywz)

    value += temp;

    // There are five filter patterns (identity, cross, checker,
    // theta, phi).  Precompute the terms from all of them and then
    // use swizzles to assign to color channels.
    //
    // Channel   Matches
    //   x       cross   (e.g., EE G)
    //   y       checker (e.g., EE B)
    //   z       theta   (e.g., EO R)
    //   w       phi     (e.g., EO R)

    #define A (value[0])
    #define B (value[1])
    #define D (Dvec.x)
    #define E (value[2])
    #define F (value[3])

    // Avoid zero elements. On a scalar processor this saves two MADDs and it has no
    // effect on a vector processor.
    PATTERN.yzw += (kD.yz * D).xyy;

    PATTERN += (kA.xyz * A).xyzx + (kE.xyw * E).xyxz;
    PATTERN.xw  += kB.xw * B;
    PATTERN.xz  += kF.xz * F;

    gl_FragColor = (alternate.y == 0.0) ?
        ((alternate.x == 0.0) ?
            vec4(C, PATTERN.xy, 1) :
            vec4(PATTERN.z, C, PATTERN.w, 1)) :
        ((alternate.x == 0.0) ?
            vec4(PATTERN.w, C, PATTERN.z, 1) :
            vec4(PATTERN.yx, C, 1));
}
"""


class BayerImageVisual(ImageVisual):
    def __init__(self, *args,
                 _vcode=VERT_SHADER, _fcode=FRAG_SHADER, bayer_pattern='bggr',
                 **kwargs):
        """Similar to ImageVisual, but images from bayer sensors are provided.

        This Visual is similar to that of an ImageVisual, with the only
        exception that the raw image from a bayer image sensor is provided.

        Intermediate values are interpolated using the
        Malvar-He-Cutler Bayer demosaicing algorithm using OpenCL [1].

        The only new parameter compared to the ``ImageVisual`` is the
        ``bayer_pattern``.

        Parameters
        ==========
        bayer_pattern: ['bggr', 'rggb', 'gbrg', 'grgb']
            One of 4 different possible bayer patterns. The first charater
            describes the chromaticity of the pixel in the upper left corner.
            The last character describes the chromaticity of the pixel in the
            lower right corner of the image.

        Notes
        =====
        _[1]:  Morgan McGuire (2008) Efficient, High-Quality Bayer
        Demosaic Filtering on GPUs, Journal of Graphics Tools, 13:4, 1-16,
        DOI: 10.1080/2151237X.2008.10129267

        """

        valid_bayer_patterns = ['bggr', 'rggb', 'gbrg', 'grbg']
        if bayer_pattern not in valid_bayer_patterns:
            raise ValueError(
                f"Invalid bayer_pattern received ({bayer_pattern}). "
                f"bayer_pattern must be in {valid_bayer_patterns}")

        self.bayer_pattern = bayer_pattern
        self._first_red = np.unravel_index(
            self.bayer_pattern.find('r'), (2, 2))

        super().__init__(*args, _vcode=_vcode, _fcode=_fcode, **kwargs)

        # only subdivide is supported
        # too lazy to parse args and kwargs to make it correct for now.
        if self.method == 'impostor':
            raise NotImplementedError('method=impostor is not supported.')
        elif self.method == 'auto':
            self.method = 'subdivide'
        # The image visual has color transforms, but this image is inherently
        # RGB, so we disable the color stuff.
        self._need_colortransform_update = False

    @property
    def cmap(self):
        return None

    @cmap.setter
    def cmap(self, value):
        pass

    def _update_method(self, view):
        """Decide which method to use for *view* and configure it accordingly.
        """
        method = self._method
        if method == 'auto':
            if view.transforms.get_transform().Linear:
                method = 'subdivide'
            else:
                method = 'impostor'
        view._method_used = method

        if method == 'subdivide':
            # view.view_program['method'] = 0
            view.view_program['a_position'] = self._subdiv_position
            view.view_program['a_texcoord'] = self._subdiv_texcoord
        elif method == 'impostor':
            # impostor was never tested
            # view.view_program['method'] = 1
            view.view_program['a_position'] = self._impostor_coords
            view.view_program['a_texcoord'] = self._impostor_coords
        else:
            raise ValueError("Unknown image draw method '%s'" % method)

        self.shared_program['first_red'] = self._first_red

        self.shared_program['image_size'] = [
            self.size[0], self.size[1], 1/self.size[0], 1/self.size[1]]

        view._need_method_update = False
        self._prepare_transforms(view)

    def _prepare_transforms(self, view):
        # TODO: remove this when we fix 'impostor'
        # I have a feeling it is because i removed the $transform
        # code path from impostor
        trs = view.transforms
        prg = view.view_program
        method = view._method_used
        if method == 'subdivide':
            prg.vert['transform'] = trs.get_transform()
            # prg.frag['transform'] = self._null_tr
        else:  # 'impostor'
            # TODO: this code path was never tested
            prg.vert['transform'] = self._null_tr
            # prg.frag['transform'] = trs.get_transform().inverse

    # TODO: remove this when interpolation becomes part of
    # The interpolation code could be transferred to a dedicated filter
    # function in visuals/filters as discussed in #1051
    def _build_interpolation(self):
        """Rebuild the _data_lookup_fn using different interpolations within
        the shader
        """
        self.shared_program['u_texture'] = self._texture
        self._need_interpolation_update = False

    def _build_texture(self):
        self._texture.set_data(self._data)
        self._need_texture_upload = False
