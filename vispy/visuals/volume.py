# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
About this technique
--------------------

In Python, we define the six faces of a cuboid to draw, as well as
texture cooridnates corresponding with the vertices of the cuboid.
The back faces of the cuboid are drawn (and front faces are culled)
because only the back faces are visible when the camera is inside the
volume.

In the vertex shader, we intersect the view ray with the near and far
clipping planes. In the fragment shader, we use these two points to
compute the ray direction and then compute the position of the front
cuboid surface (or near clipping plane) along the view ray.

Next we calculate the number of steps to walk from the front surface
to the back surface and iterate over these positions in a for-loop.
At each iteration, the fragment color or other voxel information is
updated depending on the selected rendering method.

It is important for the texture interpolation is 'linear' for most volumes,
since with 'nearest' the result can look very ugly; however for volumes with
discrete data 'nearest' is sometimes appropriate. The wrapping should be
clamp_to_edge to avoid artifacts when the ray takes a small step outside the
volume.

The ray direction is established by mapping the vertex to the document
coordinate frame, adjusting z to +/-1, and mapping the coordinate back.
The ray is expressed in coordinates local to the volume (i.e. texture
coordinates).

"""
from functools import lru_cache

from ._scalable_textures import CPUScaledTexture3D, GPUScaledTextured3D
from ..gloo import VertexBuffer, IndexBuffer
from ..gloo.texture import should_cast_to_f32
from . import Visual
from .shaders import Function
from ..color import get_colormap

import numpy as np

# todo: implement more render methods (port from visvis)
# todo: allow anisotropic data
# todo: what to do about lighting? ambi/diffuse/spec/shinynes on each visual?


_VERTEX_SHADER = """
attribute vec3 a_position;
uniform vec3 u_shape;

varying vec3 v_position;
varying vec4 v_nearpos;
varying vec4 v_farpos;

void main() {
    v_position = a_position;

    // Project local vertex coordinate to camera position. Then do a step
    // backward (in cam coords) and project back. Voila, we get our ray vector.
    vec4 pos_in_cam = $viewtransformf(vec4(v_position, 1));

    // intersection of ray and near clipping plane (z = -1 in clip coords)
    pos_in_cam.z = -pos_in_cam.w;
    v_nearpos = $viewtransformi(pos_in_cam);

    // intersection of ray and far clipping plane (z = +1 in clip coords)
    pos_in_cam.z = pos_in_cam.w;
    v_farpos = $viewtransformi(pos_in_cam);

    gl_Position = $transform(vec4(v_position, 1.0));
}
"""  # noqa

_FRAGMENT_SHADER = """
// uniforms
uniform $sampler_type u_volumetex;
uniform vec3 u_shape;
uniform vec2 clim;
uniform float gamma;
uniform float u_threshold;
uniform float u_attenuation;
uniform float u_relative_step_size;

//varyings
varying vec3 v_position;
varying vec4 v_nearpos;
varying vec4 v_farpos;

// uniforms for lighting. Hard coded until we figure out how to do lights
const vec4 u_ambient = vec4(0.2, 0.2, 0.2, 1.0);
const vec4 u_diffuse = vec4(0.8, 0.2, 0.2, 1.0);
const vec4 u_specular = vec4(1.0, 1.0, 1.0, 1.0);
const float u_shininess = 40.0;

// uniforms for plane definition. Defined in data coordinates.
uniform vec3 u_plane_normal;
uniform vec3 u_plane_position;
uniform float u_plane_thickness;

//varying vec3 lightDirs[1];

// global holding view direction in local coordinates
vec3 view_ray;

float rand(vec2 co)
{
    // Create a pseudo-random number between 0 and 1.
    // http://stackoverflow.com/questions/4200224
    return fract(sin(dot(co.xy ,vec2(12.9898, 78.233))) * 43758.5453);
}

float colorToVal(vec4 color1)
{
    return color1.r; // todo: why did I have this abstraction in visvis?
}

vec4 applyColormap(float data) {
    data = clamp(data, min(clim.x, clim.y), max(clim.x, clim.y));
    data = (data - clim.x) / (clim.y - clim.x);
    vec4 color = $cmap(pow(data, gamma));
    return color;
}


vec4 calculateColor(vec4 betterColor, vec3 loc, vec3 step)
{   
    // Calculate color by incorporating lighting
    vec4 color1;
    vec4 color2;

    // View direction
    vec3 V = normalize(view_ray);

    // calculate normal vector from gradient
    vec3 N; // normal
    color1 = $sample( u_volumetex, loc+vec3(-step[0],0.0,0.0) );
    color2 = $sample( u_volumetex, loc+vec3(step[0],0.0,0.0) );
    N[0] = colorToVal(color1) - colorToVal(color2);
    betterColor = max(max(color1, color2),betterColor);
    color1 = $sample( u_volumetex, loc+vec3(0.0,-step[1],0.0) );
    color2 = $sample( u_volumetex, loc+vec3(0.0,step[1],0.0) );
    N[1] = colorToVal(color1) - colorToVal(color2);
    betterColor = max(max(color1, color2),betterColor);
    color1 = $sample( u_volumetex, loc+vec3(0.0,0.0,-step[2]) );
    color2 = $sample( u_volumetex, loc+vec3(0.0,0.0,step[2]) );
    N[2] = colorToVal(color1) - colorToVal(color2);
    betterColor = max(max(color1, color2),betterColor);
    float gm = length(N); // gradient magnitude
    N = normalize(N);

    // Flip normal so it points towards viewer
    float Nselect = float(dot(N,V) > 0.0);
    N = (2.0*Nselect - 1.0) * N;  // ==  Nselect * N - (1.0-Nselect)*N;

    // Get color of the texture (albeido)
    color1 = betterColor;
    color2 = color1;
    // todo: parametrise color1_to_color2

    // Init colors
    vec4 ambient_color = vec4(0.0, 0.0, 0.0, 0.0);
    vec4 diffuse_color = vec4(0.0, 0.0, 0.0, 0.0);
    vec4 specular_color = vec4(0.0, 0.0, 0.0, 0.0);
    vec4 final_color;

    // todo: allow multiple light, define lights on viewvox or subscene
    int nlights = 1; 
    for (int i=0; i<nlights; i++)
    { 
        // Get light direction (make sure to prevent zero devision)
        vec3 L = normalize(view_ray);  //lightDirs[i]; 
        float lightEnabled = float( length(L) > 0.0 );
        L = normalize(L+(1.0-lightEnabled));

        // Calculate lighting properties
        float lambertTerm = clamp( dot(N,L), 0.0, 1.0 );
        vec3 H = normalize(L+V); // Halfway vector
        float specularTerm = pow( max(dot(H,N),0.0), u_shininess);

        // Calculate mask
        float mask1 = lightEnabled;

        // Calculate colors
        ambient_color +=  mask1 * u_ambient;  // * gl_LightSource[i].ambient;
        diffuse_color +=  mask1 * lambertTerm;
        specular_color += mask1 * specularTerm * u_specular;
    }

    // Calculate final color by componing different components
    final_color = color2 * ( ambient_color + diffuse_color) + specular_color;
    final_color.a = color2.a;

    // Done
    return final_color;
}


vec3 intersectLinePlane(vec3 linePosition, 
                        vec3 lineVector, 
                        vec3 planePosition, 
                        vec3 planeNormal) {
    // function to find the intersection between a line and a plane
    // line is defined by position and vector
    // plane is defined by position and normal vector
    // https://en.wikipedia.org/wiki/Line%E2%80%93plane_intersection

    // find scale factor for line vector
    float scaleFactor = dot(planePosition - linePosition, planeNormal) / 
                        dot(lineVector, planeNormal);

    // calculate intersection
    return linePosition + ( scaleFactor * lineVector );
}

// for some reason, this has to be the last function in order for the
// filters to be inserted in the correct place...

void main() {
    vec3 farpos = v_farpos.xyz / v_farpos.w;
    vec3 nearpos = v_nearpos.xyz / v_nearpos.w;

    // Calculate unit vector pointing in the view direction through this
    // fragment.
    view_ray = normalize(farpos.xyz - nearpos.xyz);

    // Keep track of wheter a surface was found (used for depth)
    // Need to do it before raycasting setup because the "plane" mode needs to set
    // the depth during that phase.
    vec3 surface_point;
    bool surface_found = false;
    
    // Set up the ray casting
    // This snippet must define three variables:
    // vec3 start_loc - the starting location of the ray in texture coordinates
    // vec3 step - the step vector in texture coordinates
    // int nsteps - the number of steps to make through the texture
    
    $raycasting_setup

    // For testing: show the number of steps. This helps to establish
    // whether the rays are correctly oriented
    //gl_FragColor = vec4(0.0, f_nsteps / 3.0 / u_shape.x, 1.0, 1.0);
    //return;

    $before_loop

    // This outer loop seems necessary on some systems for large
    // datasets. Ugly, but it works ...
    vec3 loc = start_loc;
    int iter = 0;

    // Keep track of whether texture has been sampled
    int texture_sampled = 0;

    while (iter < nsteps) {
        for (iter=iter; iter<nsteps; iter++)
        {
            // Only sample volume if loc is not clipped by clipping planes
            float distance_from_clip = $clip_with_planes(loc, u_shape);
            if (distance_from_clip >= 0)
            {
                // Get sample color
                vec4 color = $sample(u_volumetex, loc);
                float val = color.r;
                texture_sampled = 1;

                $in_loop
            }
            // Advance location deeper into the volume
            loc += step;
        }
    }
    
    // discard fragment if texture not sampled
    if ( texture_sampled != 1 ) {
        discard;
    }
    
    $after_loop

    if (surface_found == true) {
        // if a surface was found, use it to set the depth buffer
        vec4 position2 = vec4(surface_point, 1);
        vec4 iproj = $viewtransformf(position2);
        iproj.z /= iproj.w;
        gl_FragDepth = (iproj.z+1.0)/2.0;
    }
    else {
        gl_FragDepth = gl_FragCoord.z;
    }

}


"""  # noqa

_RAYCASTING_SETUP_VOLUME = """
    // Compute the distance to the front surface or near clipping plane
    float distance = dot(nearpos-v_position, view_ray);
    distance = max(distance, min((-0.5 - v_position.x) / view_ray.x,
                            (u_shape.x - 0.5 - v_position.x) / view_ray.x));
    distance = max(distance, min((-0.5 - v_position.y) / view_ray.y,
                            (u_shape.y - 0.5 - v_position.y) / view_ray.y));
    distance = max(distance, min((-0.5 - v_position.z) / view_ray.z,
                            (u_shape.z - 0.5 - v_position.z) / view_ray.z));

    // Now we have the starting position on the front surface
    vec3 front = v_position + view_ray * distance;

    // Decide how many steps to take
    int nsteps = int(-distance / u_relative_step_size + 0.5);
    float f_nsteps = float(nsteps);
    if( nsteps < 1 )
        discard;

    // Get starting location and step vector in texture coordinates
    vec3 step = ((v_position - front) / u_shape) / f_nsteps;
    // 0.5 offset needed to get back to correct texture coordinates (vispy#2239)
    vec3 start_loc = (front + 0.5) / u_shape;
"""

_RAYCASTING_SETUP_PLANE = """
    // find intersection of view ray with plane in data coordinates
    // 0.5 offset needed to get back to correct texture coordinates (vispy#2239)
    vec3 intersection = intersectLinePlane(v_position.xyz, view_ray,
                                           u_plane_position, u_plane_normal);
    // and texture coordinates
    vec3 intersection_tex = (intersection + 0.5) / u_shape;

    // discard if intersection not in texture

    float out_of_bounds = 0;

    out_of_bounds += float(intersection_tex.x > 1);
    out_of_bounds += float(intersection_tex.x < 0);
    out_of_bounds += float(intersection_tex.y > 1);
    out_of_bounds += float(intersection_tex.y < 0);
    out_of_bounds += float(intersection_tex.z > 1);
    out_of_bounds += float(intersection_tex.z < 0);

    if (out_of_bounds > 0) {
        discard;
    }


    // Decide how many steps to take
    int nsteps = int(u_plane_thickness / u_relative_step_size + 0.5);
    float f_nsteps = float(nsteps);
    if( nsteps < 1 )
        discard;

    // Get step vector and starting location in texture coordinates
    // step vector is along plane normal
    vec3 N = normalize(u_plane_normal);
    vec3 step = N / u_shape;
    vec3 start_loc = intersection_tex - ((step * f_nsteps) / 2);

    // Set depth value
    surface_point = intersection;
    surface_found = true;
"""


_MIP_SNIPPETS = dict(
    before_loop="""
        float maxval = -99999.0; // The maximum encountered value
        int maxi = -1;  // Where the maximum value was encountered
        """,
    in_loop="""
        if( val > maxval ) {
            maxval = val;
            maxi = iter;
        }
        """,
    after_loop="""
        // Refine search for max value, but only if anything was found
        if ( maxi > -1 ) {
            loc = start_loc + step * (float(maxi) - 0.5);
            for (int i=0; i<10; i++) {
                maxval = max(maxval, $sample(u_volumetex, loc).r);
                loc += step * 0.1;
            }
            gl_FragColor = applyColormap(maxval);
        }
        """,
)

_ATTENUATED_MIP_SNIPPETS = dict(
    before_loop="""
        float maxval = -99999.0; // The maximum encountered value
        float sumval = 0.0; // The sum of the encountered values
        float scaled = 0.0; // The scaled value
        int maxi = 0;  // Where the maximum value was encountered
        vec3 maxloc = vec3(0.0);  // Location where the maximum value was encountered
        """,
    in_loop="""
        sumval = sumval + val;
        scaled = val * exp(-u_attenuation * (sumval - 1) / u_relative_step_size);
        if( scaled > maxval ) {
            maxval = scaled;
            maxi = iter;
            maxloc = loc;
        }
        """,
    after_loop="""
        gl_FragColor = applyColormap(maxval);
        """,
)

_MINIP_SNIPPETS = dict(
    before_loop="""
        float minval = 99999.0; // The minimum encountered value
        int mini = -1;  // Where the minimum value was encountered
        """,
    in_loop="""
        if( val < minval ) {
            minval = val;
            mini = iter;
        }
        """,
    after_loop="""
        // Refine search for min value, but only if anything was found
        if ( mini > -1 ) {
            loc = start_loc + step * (float(mini) - 0.5);
            for (int i=0; i<10; i++) {
                minval = min(minval, $sample(u_volumetex, loc).r);
                loc += step * 0.1;
            }
            gl_FragColor = applyColormap(minval);
        }
        """,
)

_TRANSLUCENT_SNIPPETS = dict(
    before_loop="""
        vec4 integrated_color = vec4(0., 0., 0., 0.);
        """,
    in_loop="""
            color = applyColormap(val);
            float a1 = integrated_color.a;
            float a2 = color.a * (1 - a1);
            float alpha = max(a1 + a2, 0.001);

            // Doesn't work.. GLSL optimizer bug?
            //integrated_color = (integrated_color * a1 / alpha) +
            //                   (color * a2 / alpha);
            // This should be identical but does work correctly:
            integrated_color *= a1 / alpha;
            integrated_color += color * a2 / alpha;

            integrated_color.a = alpha;

            if( alpha > 0.99 ){
                // stop integrating if the fragment becomes opaque
                iter = nsteps;
            }
        """,
    after_loop="""
        gl_FragColor = integrated_color;
        """,
)

_ADDITIVE_SNIPPETS = dict(
    before_loop="""
        vec4 integrated_color = vec4(0., 0., 0., 0.);
        """,
    in_loop="""
        color = applyColormap(val);

        integrated_color = 1.0 - (1.0 - integrated_color) * (1.0 - color);
        """,
    after_loop="""
        gl_FragColor = integrated_color;
        """,
)

_ISO_SNIPPETS = dict(
    before_loop="""
        vec4 color3 = vec4(0.0);  // final color
        vec3 dstep = 1.5 / u_shape;  // step to sample derivative
        gl_FragColor = vec4(0.0);
    """,
    in_loop="""
        if (val > u_threshold-0.2) {
            // Take the last interval in smaller steps
            vec3 iloc = loc - step;
            for (int i=0; i<10; i++) {
                color = $sample(u_volumetex, iloc);
                if (color.r > u_threshold) {
                    color = calculateColor(color, iloc, dstep);
                    gl_FragColor = applyColormap(color.r);

                    // set the variables for the depth buffer
                    surface_point = iloc * u_shape;
                    surface_found = true;

                    iter = nsteps;
                    break;
                }
                iloc += step * 0.1;
            }
        }
        """,
    after_loop="""

        if (!surface_found) {
            discard;
        }

        """,
)


_AVG_SNIPPETS = dict(
    before_loop="""
        float n = 0; // Counter for encountered values
        float meanval = 0.0; // The mean of encountered values
        float prev_mean = 0.0; // Variable to store the previous incremental mean
        """,
    in_loop="""
        // Incremental mean value used for numerical stability
        n += 1; // Increment the counter
        prev_mean = meanval; // Update the mean for previous iteration
        meanval = prev_mean + (val - prev_mean) / n; // Calculate the mean
        """,
    after_loop="""
        // Apply colormap on mean value
        gl_FragColor = applyColormap(meanval);
        """,
)


class VolumeVisual(Visual):
    """Displays a 3D Volume

    Parameters
    ----------
    vol : ndarray
        The volume to display. Must be ndim==3. Array is assumed to be stored
        as ``(z, y, x)``.
    clim : str | tuple
        Limits to use for the colormap. I.e. the values that map to black and white
        in a gray colormap. Can be 'auto' to auto-set bounds to
        the min and max of the data. If not given or None, 'auto' is used.
    method : {'mip', 'attenuated_mip', 'minip', 'translucent', 'additive',
        'iso', 'average'}
        The render method to use. See corresponding docs for details.
        Default 'mip'.
    threshold : float
        The threshold to use for the isosurface render method. By default
        the mean of the given volume is used.
    attenuation: float
        The attenuation rate to apply for the attenuated mip render method.
        Default: 1.0.
    relative_step_size : float
        The relative step size to step through the volume. Default 0.8.
        Increase to e.g. 1.5 to increase performance, at the cost of
        quality.
    cmap : str
        Colormap to use.
    gamma : float
        Gamma to use during colormap lookup.  Final color will be cmap(val**gamma).
        by default: 1.
    interpolation : {'linear', 'nearest'}
        Selects method of image interpolation.
    texture_format : numpy.dtype | str | None
        How to store data on the GPU. OpenGL allows for many different storage
        formats and schemes for the low-level texture data stored in the GPU.
        Most common is unsigned integers or floating point numbers.
        Unsigned integers are the most widely supported while other formats
        may not be supported on older versions of OpenGL or with older GPUs.
        Default value is ``None`` which means data will be scaled on the
        CPU and the result stored in the GPU as an unsigned integer. If a
        numpy dtype object, an internal texture format will be chosen to
        support that dtype and data will *not* be scaled on the CPU. Not all
        dtypes are supported. If a string, then
        it must be one of the OpenGL internalformat strings described in the
        table on this page: https://www.khronos.org/registry/OpenGL-Refpages/gl4/html/glTexImage2D.xhtml
        The name should have `GL_` removed and be lowercase (ex.
        `GL_R32F` becomes ``'r32f'``). Lastly, this can also be the string
        ``'auto'`` which will use the data type of the provided volume data
        to determine the internalformat of the texture.
        When this is specified (not ``None``) data is scaled on the
        GPU which allows for faster color limit changes. Additionally, when
        32-bit float data is provided it won't be copied before being
        transferred to the GPU. Note this visual is limited to "luminance"
        formatted data (single band). This is equivalent to `GL_RED` format
        in OpenGL 4.0.
    raycasting_mode : {'volume', 'plane'}
        Whether to cast a ray through the whole volume or perpendicular to a
        plane through the volume defined.
    plane_position : ArrayLike
        A (3,) array containing a position on a plane of interest in the volume.
        The position is defined in data coordinates. Only relevant in
        raycasting_mode = 'plane'.
    plane_normal : ArrayLike
        A (3,) array containing a vector normal to the plane of interest in the
        volume. The normal vector is defined in data coordinates. Only relevant
        in raycasting_mode = 'plane'.
    plane_thickness : float
        A value defining the total length of the ray perpendicular to the
        plane interrogated during rendering. Defined in data coordinates.
        Only relevant in raycasting_mode = 'plane'.


    .. versionchanged: 0.7

        Deprecate 'emulate_texture' keyword argument.

    """

    _interpolation_methods = ['linear', 'nearest']

    _rendering_methods = {
        'mip': _MIP_SNIPPETS,
        'minip': _MINIP_SNIPPETS,
        'attenuated_mip': _ATTENUATED_MIP_SNIPPETS,
        'iso': _ISO_SNIPPETS,
        'translucent': _TRANSLUCENT_SNIPPETS,
        'additive': _ADDITIVE_SNIPPETS,
        'average': _AVG_SNIPPETS
    }

    _raycasting_modes = {
        'volume': _RAYCASTING_SETUP_VOLUME,
        'plane': _RAYCASTING_SETUP_PLANE
    }

    _shaders = {
        'vertex': _VERTEX_SHADER,
        'fragment': _FRAGMENT_SHADER,
    }

    def __init__(self, vol, clim="auto", method='mip', threshold=None,
                 attenuation=1.0, relative_step_size=0.8, cmap='grays',
                 gamma=1.0, interpolation='linear', texture_format=None,
                 raycasting_mode='volume', plane_position=None,
                 plane_normal=None, plane_thickness=1.0, clipping_planes=None,
                 clipping_planes_coord_system='scene'):

        tr = ['visual', 'scene', 'document', 'canvas', 'framebuffer', 'render']
        if clipping_planes_coord_system not in tr:
            raise ValueError(f'Invalid coordinate system {clipping_planes_coord_system}. Must be one of {tr}.')
        self._clipping_planes_coord_system = clipping_planes_coord_system
        self._clip_transform = None
        # Storage of information of volume
        self._vol_shape = ()
        self._gamma = gamma
        self._raycasting_mode = raycasting_mode
        self._need_vertex_update = True
        # Set the colormap
        self._cmap = get_colormap(cmap)
        self._is_zyx = True

        # Create gloo objects
        self._vertices = VertexBuffer()

        self._interpolation = interpolation
        self._texture = self._create_texture(texture_format, vol)
        # used to store current data for later CPU-side scaling if
        # texture_format is None
        self._last_data = None

        # Create program
        Visual.__init__(self, vcode=self._shaders['vertex'], fcode=self._shaders['fragment'])
        self.shared_program['u_volumetex'] = self._texture
        self.shared_program['a_position'] = self._vertices
        self.shared_program['gamma'] = self._gamma
        self._draw_mode = 'triangle_strip'
        self._index_buffer = IndexBuffer()

        # Only show back faces of cuboid. This is required because if we are
        # inside the volume, then the front faces are outside of the clipping
        # box and will not be drawn.
        self.set_gl_state('translucent', cull_face=False)

        # Apply clim and set data at the same time
        self.set_data(vol, clim or "auto")

        # Set params
        self.raycasting_mode = raycasting_mode
        self.method = method
        self.relative_step_size = relative_step_size
        self.threshold = threshold if threshold is not None else vol.mean()
        self.attenuation = attenuation

        # Set plane params
        if plane_position is None:
            self.plane_position = [x / 2 for x in vol.shape]
        else:
            self.plane_position = plane_position
        if plane_normal is None:
            self.plane_normal = [1, 0, 0]
        else:
            self.plane_normal = plane_normal
        self.plane_thickness = plane_thickness

        self.clipping_planes = clipping_planes

        self.freeze()

    def _create_texture(self, texture_format, data):
        if texture_format is not None:
            tex_cls = GPUScaledTextured3D
        else:
            tex_cls = CPUScaledTexture3D

        # clamp_to_edge means any texture coordinates outside of 0-1 should be
        # clamped to 0 and 1.
        # NOTE: This doesn't actually set the data in the texture. Only
        # creates a placeholder texture that will be resized later on.
        return tex_cls(data, interpolation=self._interpolation,
                       internalformat=texture_format,
                       format='luminance',
                       wrapping='clamp_to_edge')

    def set_data(self, vol, clim=None, copy=True):
        """Set the volume data.

        Parameters
        ----------
        vol : ndarray
            The 3D volume.
        clim : tuple
            Colormap limits to use (min, max). None will use the min and max
            values. Defaults to ``None``.
        copy : bool
            Whether to copy the input volume prior to applying clim
            normalization on the CPU. Has no effect if visual was created
            with 'texture_format' not equal to None as data is not modified
            on the CPU and data must already be copied to the GPU.
            Data must be 32-bit floating point data to completely avoid any
            data copying when scaling on the CPU. Defaults to ``True`` for
            CPU scaled data. It is forced to ``False`` for GPU scaled data.

        """
        # Check volume
        if not isinstance(vol, np.ndarray):
            raise ValueError('Volume visual needs a numpy array.')
        if not ((vol.ndim == 3) or (vol.ndim == 4 and vol.shape[-1] > 1)):
            raise ValueError('Volume visual needs a 3D array.')
        if isinstance(self._texture, GPUScaledTextured3D):
            copy = False

        if clim is not None and clim != self._texture.clim:
            self._texture.set_clim(clim)

        # Apply to texture
        if should_cast_to_f32(vol.dtype):
            vol = vol.astype(np.float32)
        self._texture.check_data_format(vol)
        self._last_data = vol
        self._texture.scale_and_set_data(vol, copy=copy)  # will be efficient if vol is same shape
        self.shared_program['clim'] = self._texture.clim_normalized
        self.shared_program['u_shape'] = (vol.shape[2], vol.shape[1],
                                          vol.shape[0])

        shape = vol.shape[:3]
        if self._vol_shape != shape:
            self._vol_shape = shape
            self._need_vertex_update = True
        self._vol_shape = shape

    @property
    def interpolation_methods(self):
        return self._interpolation_methods

    @property
    def rendering_methods(self):
        return list(self._rendering_methods)

    @property
    def raycasting_modes(self):
        return list(self._raycasting_modes)

    @property
    def clim(self):
        """The contrast limits that were applied to the volume data.

        Volume display is mapped from black to white with these values.
        Settable via set_data() as well as @clim.setter.
        """
        return self._texture.clim

    @clim.setter
    def clim(self, value):
        """Set contrast limits used when rendering the image.

        ``value`` should be a 2-tuple of floats (min_clim, max_clim), where each value is
        within the range set by self.clim. If the new value is outside of the (min, max)
        range of the clims previously used to normalize the texture data, then data will
        be renormalized using set_data.
        """
        if self._texture.set_clim(value):
            self.set_data(self._last_data, clim=value)
        self.shared_program['clim'] = self._texture.clim_normalized
        self.update()

    @property
    def gamma(self):
        """The gamma used when rendering the image."""
        return self._gamma

    @gamma.setter
    def gamma(self, value):
        """Set gamma used when rendering the image."""
        if value <= 0:
            raise ValueError("gamma must be > 0")
        self._gamma = float(value)
        self.shared_program['gamma'] = self._gamma
        self.update()

    @property
    def cmap(self):
        return self._cmap

    @cmap.setter
    def cmap(self, cmap):
        self._cmap = get_colormap(cmap)
        self.shared_program.frag['cmap'] = Function(self._cmap.glsl_map)
        self.shared_program['texture2D_LUT'] = self.cmap.texture_lut()
        self.update()

    @property
    def interpolation(self):
        """The interpolation method to use

        Current options are:

            * linear: this method is appropriate for most volumes as it creates
              nice looking visuals.
            * nearest: this method is appropriate for volumes with discrete
              data where additional interpolation does not make sense.
        """
        return self._interpolation

    @interpolation.setter
    def interpolation(self, interp):
        if interp not in self._interpolation_methods:
            raise ValueError(
                "interpolation must be one of %s"
                % ', '.join(self._interpolation_methods)
            )
        if self._interpolation != interp:
            self._interpolation = interp
            self._texture.interpolation = self._interpolation
            self.update()

    @staticmethod
    @lru_cache(maxsize=10)
    def _build_clipping_planes_func(n_planes):
        """Build the code snippet used to clip the volume based on self.clipping_planes."""
        func_template = '''
            float clip_planes(vec3 loc, vec3 vol_shape) {{
                vec3 loc_transf = $clip_transform(vec4(loc, 1)).xyz;
                float distance_from_clip = 1.0;
                {clips};
                return distance_from_clip;
            }}
        '''
        # the vertex is considered clipped if on the "negative" side of the plane
        clip_template = '''
            vec3 relative_vec{idx} = loc_transf - ( $clipping_plane_pos{idx} / vol_shape );
            float distance_from_clip{idx} = dot(relative_vec{idx}, ($clipping_plane_norm{idx} * vol_shape));
            distance_from_clip = min(distance_from_clip{idx}, distance_from_clip);
            '''
        all_clips = []
        for idx in range(n_planes):
            all_clips.append(clip_template.format(idx=idx))
        formatted_code = func_template.format(clips=''.join(all_clips))
        return Function(formatted_code)

    @property
    def clipping_planes(self):
        """The set of planes used to clip the volume. Values on the negative side of the normal are discarded.

        Each plane is defined by a position and a normal vector (magnitude is irrelevant). Shape: (n_planes, 2, 3).
        The order is xyz, as opposed to data's zyx (for consistency with the rest of vispy)

        Example: one plane in position (0, 0, 0) and with normal (0, 0, 1),
        and a plane in position (1, 1, 1) with normal (0, 1, 0):

        >>> volume.clipping_planes = np.array([
        >>>     [[0, 0, 0], [0, 0, 1]],
        >>>     [[1, 1, 1], [0, 1, 0]],
        >>> ])

        """
        return self._clipping_planes

    @clipping_planes.setter
    def clipping_planes(self, value):
        if value is None:
            value = np.empty([0, 2, 3])
        self._clipping_planes = value

        self._clip_func = self._build_clipping_planes_func(len(value))
        self.shared_program.frag['clip_with_planes'] = self._clip_func

        self._clip_func['clip_transform'] = self._clip_transform
        for idx, plane in enumerate(value):
            self._clip_func[f'clipping_plane_pos{idx}'] = tuple(plane[0])
            self._clip_func[f'clipping_plane_norm{idx}'] = tuple(plane[1])
        self.update()

    @property
    def clipping_planes_coord_system(self):
        """
        Coordinate system used by the clipping planes (see visuals.transforms.transform_system.py)
        """
        return self._clipping_planes_coord_system

    @property
    def _before_loop_snippet(self):
        return self._rendering_methods[self.method]['before_loop']

    @property
    def _in_loop_snippet(self):
        return self._rendering_methods[self.method]['in_loop']

    @property
    def _after_loop_snippet(self):
        return self._rendering_methods[self.method]['after_loop']

    @property
    def method(self):
        """The render method to use

        Current options are:

            * translucent: voxel colors are blended along the view ray until
              the result is opaque.
            * mip: maxiumum intensity projection. Cast a ray and display the
              maximum value that was encountered.
            * minip: minimum intensity projection. Cast a ray and display the
              minimum value that was encountered.
            * attenuated_mip: attenuated maximum intensity projection. Cast a
              ray and display the maximum value encountered. Values are
              attenuated as the ray moves deeper into the volume.
            * additive: voxel colors are added along the view ray until
              the result is saturated.
            * iso: isosurface. Cast a ray until a certain threshold is
              encountered. At that location, lighning calculations are
              performed to give the visual appearance of a surface.
            * average: average intensity projection. Cast a ray and display the
              average of values that were encountered.
        """
        return self._method

    @method.setter
    def method(self, method):
        # Check and save
        known_methods = list(self._rendering_methods.keys())
        if method not in known_methods:
            raise ValueError('Volume render method should be in %r, not %r' %
                             (known_methods, method))
        self._method = method

        # $sample needs to be unset and re-set, since it's present inside the snippets.
        #       Program should probably be able to do this automatically
        self.shared_program.frag['sample'] = None
        self.shared_program.frag['raycasting_setup'] = self._raycasting_setup_snippet
        self.shared_program.frag['before_loop'] = self._before_loop_snippet
        self.shared_program.frag['in_loop'] = self._in_loop_snippet
        self.shared_program.frag['after_loop'] = self._after_loop_snippet
        self.shared_program.frag['sampler_type'] = self._texture.glsl_sampler_type
        self.shared_program.frag['sample'] = self._texture.glsl_sample
        self.shared_program.frag['cmap'] = Function(self._cmap.glsl_map)
        self.shared_program['texture2D_LUT'] = self.cmap.texture_lut()
        self.update()

    @property
    def _raycasting_setup_snippet(self):
        return self._raycasting_modes[self.raycasting_mode]

    @property
    def raycasting_mode(self):
        """The raycasting mode to use.

        This defines whether to cast a ray through the whole volume or
        perpendicular to a plane through the volume.
        must be in {'volume', 'plane'}
        """
        return self._raycasting_mode

    @raycasting_mode.setter
    def raycasting_mode(self, value: str):
        valid_raycasting_modes = self._raycasting_modes.keys()
        if value not in valid_raycasting_modes:
            raise ValueError(f"Raycasting mode should be in {valid_raycasting_modes}, not {value}")
        self._raycasting_mode = value
        self.shared_program.frag['raycasting_setup'] = self._raycasting_setup_snippet
        self.update()

    @property
    def threshold(self):
        """The threshold value to apply for the isosurface render method."""
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        self._threshold = float(value)
        self.shared_program['u_threshold'] = self._threshold
        self.update()

    @property
    def attenuation(self):
        """The attenuation rate to apply for the attenuated mip render method."""
        return self._attenuation

    @attenuation.setter
    def attenuation(self, value):
        self._attenuation = float(value)
        self.shared_program['u_attenuation'] = self._attenuation
        self.update()

    @property
    def relative_step_size(self):
        """The relative step size used during raycasting.

        Larger values yield higher performance at reduced quality. If
        set > 2.0 the ray skips entire voxels. Recommended values are
        between 0.5 and 1.5. The amount of quality degredation depends
        on the render method.
        """
        return self._relative_step_size

    @relative_step_size.setter
    def relative_step_size(self, value):
        value = float(value)
        if value < 0.1:
            raise ValueError('relative_step_size cannot be smaller than 0.1')
        self._relative_step_size = value
        self.shared_program['u_relative_step_size'] = value

    @property
    def plane_position(self):
        """Position on a plane through the volume.

        A (3,) array containing a position on a plane of interest in the volume.
        The position is defined in data coordinates. Only relevant in
        raycasting_mode = 'plane'.
        """
        return self._plane_position

    @plane_position.setter
    def plane_position(self, value):
        value = np.array(value, dtype=np.float32).ravel()
        if value.shape != (3, ):
            raise ValueError('plane_position must be a 3 element array-like object')
        self._plane_position = value
        self.shared_program['u_plane_position'] = value[::-1]
        self.update()

    @property
    def plane_normal(self):
        """Direction normal to a plane through the volume.

        A (3,) array containing a vector normal to the plane of interest in the
        volume. The normal vector is defined in data coordinates. Only relevant
        in raycasting_mode = 'plane'.
        """
        return self._plane_normal

    @plane_normal.setter
    def plane_normal(self, value):
        value = np.array(value, dtype=np.float32).ravel()
        if value.shape != (3, ):
            raise ValueError('plane_normal must be a 3 element array-like object')
        self._plane_normal = value
        self.shared_program['u_plane_normal'] = value[::-1]
        self.update()

    @property
    def plane_thickness(self):
        """Thickness of a plane through the volume.

        A value defining the total length of the ray perpendicular to the
        plane interrogated during rendering. Defined in data coordinates.
        Only relevant in raycasting_mode = 'plane'.
        """
        return self._plane_thickness

    @plane_thickness.setter
    def plane_thickness(self, value: float):
        value = float(value)
        if value < 1:
            raise ValueError('plane_thickness should be at least 1.0')
        self._plane_thickness = value
        self.shared_program['u_plane_thickness'] = value
        self.update()

    def _create_vertex_data(self):
        """Create and set positions and texture coords from the given shape

        We have six faces with 1 quad (2 triangles) each, resulting in
        6*2*3 = 36 vertices in total.
        """
        shape = self._vol_shape

        # Get corner coordinates. The -0.5 offset is to center
        # pixels/voxels. This works correctly for anisotropic data.
        x0, x1 = -0.5, shape[2] - 0.5
        y0, y1 = -0.5, shape[1] - 0.5
        z0, z1 = -0.5, shape[0] - 0.5

        pos = np.array([
            [x0, y0, z0],
            [x1, y0, z0],
            [x0, y1, z0],
            [x1, y1, z0],
            [x0, y0, z1],
            [x1, y0, z1],
            [x0, y1, z1],
            [x1, y1, z1],
        ], dtype=np.float32)

        """
          6-------7
         /|      /|
        4-------5 |
        | |     | |
        | 2-----|-3
        |/      |/
        0-------1
        """

        # Order is chosen such that normals face outward; front faces will be
        # culled.
        indices = np.array([2, 6, 0, 4, 5, 6, 7, 2, 3, 0, 1, 5, 3, 7],
                           dtype=np.uint32)

        # Apply
        self._vertices.set_data(pos)
        self._index_buffer.set_data(indices)

    def _compute_bounds(self, axis, view):
        if self._is_zyx:
            # axis=(x, y, z) -> shape(..., z, y, x)
            ndim = len(self._vol_shape)
            return 0, self._vol_shape[ndim - 1 - axis]
        else:
            # axis=(x, y, z) -> shape(x, y, z)
            return 0, self._vol_shape[axis]

    def _prepare_transforms(self, view):
        trs = view.transforms
        view.view_program.vert['transform'] = trs.get_transform()

        view_tr_f = trs.get_transform('visual', 'document')
        view_tr_i = view_tr_f.inverse
        view.view_program.vert['viewtransformf'] = view_tr_f
        view.view_program.vert['viewtransformi'] = view_tr_i
        view.view_program.frag['viewtransformf'] = view_tr_f

        self._clip_transform = trs.get_transform('visual', self._clipping_planes_coord_system)

    def _prepare_draw(self, view):
        if self._need_vertex_update:
            self._create_vertex_data()
