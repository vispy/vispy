# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
About this technique
--------------------

In Python, we define the six faces of a cuboid to draw, as well as
texture cooridnates corresponding with the vertices of the cuboid. In
the vertex shader, we establish the ray direction and pass it to the
fragment shader as a varying. In the fragment shader, we have the
texture coordinate as the starting point of the ray, and we know the
ray direction. We then calculate the number of steps and use that number
in a for-loop while we iterate through the volume. Each iteration we
keep track of some voxel information. When the cast is done, we may do
some final processing. Depending on the render style, the calculations
at teach iteration and the post-processing may differ.

It is important for the texture interpolation in 'linear', since with
nearest the result look very ugly. The wrapping should be clamp_to_edge
to avoid artifacts when the ray takes a small step outside the volume.

The ray direction is established by mapping the vertex to the document
coordinate frame, taking one step in z, and mapping the coordinate back.
The ray is expressed in coordinates local to the volume (i.e. texture
coordinates).

To calculate the number of steps, we calculate the distance between the
starting point and six planes corresponding to the faces of the cuboid.
The planes are placed slightly outside of the cuboid, resulting in sensible
output for rays that are faced in the wrong direction, allowing us to 
discard the front-facing sides of the cuboid by discarting fragments for
which the number of steps is very small.

"""

from .. import gloo
from . import Visual
from .shaders import Function, ModularProgram

import numpy as np

# todo: tweak iso rendering to reduce stripy artifacts
# todo: implement more render styles (port from visvis)
# todo: colormapping
# todo: allow anisotropic data
# todo: what to do about lighting? ambi/diffuse/spec/shinynes on each visual?

# Vertex shader
vertex_template = """
attribute vec3 a_position;
attribute vec3 a_texcoord;
uniform vec3 u_shape;
uniform float u_cameraclip;

varying vec3 v_texcoord;
varying vec3 v_ray;
varying vec4 v_clipplane;

void main() {
    v_texcoord = a_texcoord;
    gl_Position = $transform(vec4(a_position, 1.0));
    
    // Project local vertex coordinate to camera position. Then do a step
    // backward (in cam coords) and project back. Voila, we get our ray vector.
    // This vector does not interpolate nicely between vertices when 
    // we have perspective view transform. Therefore we create a grid of 
    // vertices rather than one quad per face.
    vec4 pos_in_cam1 = $viewtransformf(vec4(a_position, 1.0));
    vec4 pos_in_cam2 = pos_in_cam1 + vec4(0.0, 0.0, 1.0, 0.0); // step backward
    vec4 position2 = $viewtransformi(vec4(pos_in_cam2.xyz, 1.0));
    
    // Calculate ray. In the fragment shader we do another normalization
    // and scale for texture coords; interpolation does not maintain
    // vector length
    v_ray = normalize(a_position - position2.xyz);
    
    // Calculate a clip plane (in texture coordinates) for the camera
    // position, in case that the camera is inside the volume.
    pos_in_cam1.zw = vec2(u_cameraclip, 1.0);
    vec3 cameraposinvol = $viewtransformi(pos_in_cam1).xyz;
    cameraposinvol /= u_shape;  // express in texture coords
    v_clipplane.xyz = v_ray;
    v_clipplane.w = dot(v_clipplane.xyz, cameraposinvol);
}
"""

# Fragment shader
fragment_template = """
// uniforms
uniform sampler3D u_volumetex;
uniform vec3 u_shape;
uniform float u_threshold;
uniform float u_relative_step_size;

//varyings
varying vec3 v_texcoord;
varying vec3 v_ray;
varying vec4 v_clipplane;

// uniforms for lighting. Hard coded until we figure out how to do lights
const vec4 u_ambient = vec4(0.2, 0.4, 0.2, 1.0);
const vec4 u_diffuse = vec4(0.8, 0.2, 0.2, 1.0);
const vec4 u_specular = vec4(1.0, 1.0, 1.0, 1.0);
const float u_shininess = 40.0;

//varying vec3 lightDirs[1];
//varying vec3 V; // view direction

vec4 calculateColor(vec4, vec3, vec3);

void main() {
    
    // Discart front facing
    if (!gl_FrontFacing)
        discard;
    
    // Uncomment this to show a grid of the backfaces
    //vec3 pcd = v_texcoord * u_shape;
    //for (int d=0; d<3; d++)
    //    if (pcd[d] > 1 && pcd[d] < (u_shape[d]-1) && sin(pcd[d]) > 0.9)
    //            discard;
    
    // Get ray in texture coordinates
    vec3 ray = normalize(v_ray);
    ray /= u_shape;
    ray *= u_relative_step_size; // performance vs quality
    ray *= -1.0; // flip: we cast rays from back to front
    
    /// Get begin location and number of steps to cast ray
    vec3 edgeloc = v_texcoord;
    int nsteps = $calculate_steps(edgeloc, ray, v_clipplane);
    
    // Instead of discarting based on gl_FrontFacing, we can also discard
    // on number of steps.
    //if (nsteps < 4)
    //    discard;
    
    // For testing: show the number of steps. This helps to establish
    // whether the rays are correctly oriented
    //gl_FragColor = vec4(0.0, nsteps / 3.0 / u_shape.x, 1.0, 1.0);
    //return;
    
    // prepare for raycasting
    vec3 loc; // current position
    vec4 color; // current color
    
    $before_loop
    
    // This outer loop seems necessary on some systems for large
    // datasets. Ugly, but it works ...
    int i = nsteps;
    while (i > 0) {
        for (i=i; i>0; i--)
        {
            // Calculate location and sample color
            loc = edgeloc + float(i) * ray;
            color = texture3D(u_volumetex, loc);
            float val = color.g;
            
            $in_loop
        }
    }
    
    $after_loop
    
    /* Set depth value - from visvis TODO
    int iter_depth = int(maxi);
    // Calculate end position in world coordinates
    vec4 position2 = vertexPosition;
    position2.xyz += ray*shape*float(iter_depth);
    // Project to device coordinates and set fragment depth
    vec4 iproj = gl_ModelViewProjectionMatrix * position2;
    iproj.z /= iproj.w;
    gl_FragDepth = (iproj.z+1.0)/2.0;
    */
}


float colorToVal(vec4 color1)
{
    return color1.g; // todo: why did I have this abstraction in visvis?
}

vec4 calculateColor(vec4 betterColor, vec3 loc, vec3 step)
{   
    // Calculate color by incorporating lighting
    vec4 color1;
    vec4 color2;
    
    // View direction
    vec3 V = normalize(v_ray);
    
    // calculate normal vector from gradient
    vec3 N; // normal
    color1 = texture3D( u_volumetex, loc+vec3(-step[0],0.0,0.0) );
    color2 = texture3D( u_volumetex, loc+vec3(step[0],0.0,0.0) );
    N[0] = colorToVal(color1) - colorToVal(color2);
    betterColor = max(max(color1, color2),betterColor);
    color1 = texture3D( u_volumetex, loc+vec3(0.0,-step[1],0.0) );
    color2 = texture3D( u_volumetex, loc+vec3(0.0,step[1],0.0) );
    N[1] = colorToVal(color1) - colorToVal(color2);
    betterColor = max(max(color1, color2),betterColor);
    color1 = texture3D( u_volumetex, loc+vec3(0.0,0.0,-step[2]) );
    color2 = texture3D( u_volumetex, loc+vec3(0.0,0.0,step[2]) );
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
        vec3 L = normalize(v_ray);  //lightDirs[i]; 
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

"""

# Code for calculating number of required steps
calc_steps = """

float d2P(vec3, vec3, vec4);

int calculate_steps(vec3 edgeLoc, vec3 ray, vec4 extra_clipplane)
{
    // Given the start pos, returns the number of steps towards the closest
    // face that is in front of the given ray.
    
    // Check for all six planes how many rays fit from the start point.
    // We operate in texture coordinate here (0..1)
    // Take the minimum value (not counting negative and invalid).
    float smallest = 999999.0;
    float eps = 0.000001;
    smallest = min(smallest, d2P(edgeLoc, ray, vec4(1.0, 0.0, 0.0, 0.0-eps)));
    smallest = min(smallest, d2P(edgeLoc, ray, vec4(0.0, 1.0, 0.0, 0.0-eps)));
    smallest = min(smallest, d2P(edgeLoc, ray, vec4(0.0, 0.0, 1.0, 0.0-eps)));
    smallest = min(smallest, d2P(edgeLoc, ray, vec4(1.0, 0.0, 0.0, 1.0+eps)));
    smallest = min(smallest, d2P(edgeLoc, ray, vec4(0.0, 1.0, 0.0, 1.0+eps)));
    smallest = min(smallest, d2P(edgeLoc, ray, vec4(0.0, 0.0, 1.0, 1.0+eps)));
    smallest = min(smallest, d2P(edgeLoc, ray, extra_clipplane));
    
    // Just in case, set extremely hight value to 0
    smallest *= float(smallest < 10000.0);
    
    // Make int and return
    return int(smallest + 0.5);
}

float d2P(vec3 p, vec3 d, vec4 P)
{
    // calculate the distance of a point p to a plane P along direction d.
    // plane P is defined as ax + by + cz = d
    // return ~inf if negative
    
    // calculate nominator and denominator
    float nom = - (dot(P.xyz, p) - P.a);
    float denom =  dot(P.xyz, d);
    
    // Turn negative and invalid values into a very high value
    // A negative value means that the current face lies behind the ray. 
    // Invalid values can occur for combinations of face and start point
    float invalid = float(nom == 0.0 || denom == 0.0 || nom * denom <= 0.0);
    return (((1.0-invalid) * nom   + invalid * 999999.0) / 
            ((1.0-invalid) * denom + invalid * 1.0));
}
"""


SNIPPETS_MIP = dict(
    before_loop="""
        float maxval = -99999.0; // The maximum encountered value
        float maxi = 0.0;  // Where the maximum value was encountered
        vec4 maxcolor; // The color found at the maximum value 
        """,
    in_loop="""
        float r = float(val > maxval);
        maxval = (1.0 - r) * maxval + r * val;
        maxi = (1.0 - r) * maxi + r * float(i);
        maxcolor = (1.0 - r) * maxcolor + r * color;
        """,
    after_loop="""
        gl_FragColor = vec4(maxval, maxval, maxval, 1.0);
        """,
)

SNIPPETS_ISO = dict(
    before_loop="""
        int iso_samples = 0;
        vec4 color3 = vec4(0.0);  // final color
        vec3 step = 1.5 / u_shape;  // step to sample derivative
    """,
    in_loop="""
        if (val > u_threshold || iso_samples > 0) {
            vec4 color2 = calculateColor(color, loc, step);
            float a = color2.a * max(0.0, 1.0-color3.a);
            color3.rgb += color2.rgb * a;
            color3.a += a; // color3.a counts total color contribution.
            
            iso_samples += 1;
            if (iso_samples >= 1) {
                i = 0;
                break;
            }
        }
        """,
    after_loop="""
        // Drop fragment if we did triger the threshold
        if (iso_samples == 0)
            discard; 
        // Calculate color
        color3.rgb /= color3.a;
        color3.a = min(1.0, color3.a);
        gl_FragColor = color3;
        """,
)


class VolumeVisual(Visual):
    """ Displays a 3D Volume
    
    Parameters
    ----------
    vol : ndarray
        The volume to display. Must be ndim==2.
    clim : tuple of two floats
        The contrast limits. The values in the volume are mapped to
        black and white corresponding to these values. Default maps
        between min and max.
    style : {'mip', 'iso'}
        The render style to use. See corresponding docs for details.
        Default 'mip'.
    threshold : float
        The threshold to use for the isosurafce render style. By default
        the mean of the given volume is used.
    relative_step_size : float
        The relative step size to step through the volume. Default 0.8.
        Increase to e.g. 1.5 to increase performance, at the cost of
        quality.
    
    """
    
    _vb_dtype = dtype = [('a_position', np.float32, 3),
                         ('a_texcoord', np.float32, 3), ]
    
    def __init__(self, vol, clim=None, style='mip', threshold=None, 
                 relative_step_size=0.8):
        
        # Variable to determine clipping plane when inside the volume.
        # This value represents the z-value in view coordinates, but
        # other than that I am not sure what the value should be. 10.0
        # seems to work with the demos I tried ...
        self._cameraclip = 10.0
        
        # Cache for vertex data
        self._vertex_cache_id = ()
        
        # Storage of information of volume
        self._vol_shape = ()
        self._clim = None
        
        # Create gloo objects
        self._program = ModularProgram(vertex_template, fragment_template)
        self._vbo = None
        self._tex = gloo.Texture3D((10, 10, 10), interpolation='linear', 
                                   wrapping='clamp_to_edge')
        #
        self._program['u_volumetex'] = self._tex
        self._program.frag['calculate_steps'] = Function(calc_steps)
        
        # Set data
        self.set_data(vol, clim)
        
        # Set params
        self.style = style
        self.relative_step_size = relative_step_size
        self.threshold = threshold if (threshold is not None) else vol.mean()
    
    def set_data(self, vol, clim=None):
        """ Set the volume data. 
        """
        # Check volume
        if not isinstance(vol, np.ndarray):
            raise ValueError('Volume visual needs a numpy array.')
        if not ((vol.ndim == 3) or (vol.ndim == 4 and vol.shape[-1] <= 4)):
            raise ValueError('Volume visual needs a 3D image.')
        
        # Handle clim
        if clim is not None:
            if not isinstance(clim, tuple) or not len(clim) == 2:
                raise ValueError('clim must be a 2-element tuple')
            self._clim = clim
        if self._clim is None:
            self._clim = vol.min(), vol.max()
        
        # Apply clim
        vol = np.array(vol, dtype='float32', copy=False)
        vol -= self._clim[0]
        vol *= 1.0 / (self._clim[1] - self._clim[0])
        
        # Apply to texture
        self._tex.set_data(vol)  # will be efficient if vol is same shape
        self._program['u_shape'] = vol.shape[2], vol.shape[1], vol.shape[0]
        self._vol_shape = vol.shape[:3]
    
    @property
    def clim(self):
        """ The contrast limits that were applied to the volume data.
        Settable via set_data().
        """
        return self._clim
    
    @property
    def style(self):
        """ The rende style to use:
        
        * mip: maxiumum intensity projection. Cast a ray and display the
          maximum value that was encountered.
        * iso: isosurface. Cast a ray until a certain threshold is encountered.
          At that location, lighning calculations are performed to give the
          visual appearance of a surface.  
        * more to come ...
        """
        return self._style
    
    @style.setter
    def style(self, style):
        # Check and save
        known_styles = ('mip', 'iso', 'ray')
        if style not in known_styles:
            raise ValueError('Volume render style should be in %r, not %r' %
                             (known_styles, style))
        self._style = style
        # Get rid of specific variables - they may become invalid
        self._program['u_threshold'] = None
        # Modify glsl
        snippet_dict = {'mip': SNIPPETS_MIP, 'iso': SNIPPETS_ISO}[style]
        for key, snippet in snippet_dict.items():
            self._program.frag[key] = snippet
    
    @property
    def threshold(self):
        """ The threshold value to apply for the isosurface render style.
        """
        return self._threshold
    
    @threshold.setter
    def threshold(self, value):
        self._threshold = float(value)
    
    @property
    def relative_step_size(self):
        """ The relative step size used during raycasting.
        
        Larger values yield higher performance at reduced quality. If
        set > 2.0 the ray skips entire voxels. Recommended values are
        between 0.5 and 1.5. The amount of quality degredation depends
        on the render style.
        """
        return self._relative_step_size
    
    @relative_step_size.setter
    def relative_step_size(self, value):
        value = float(value)
        if value < 0.1:
            raise ValueError('relative_step_size cannot be smaller than 0.1')
        self._relative_step_size = value
    
    def _create_vertex_data(self, partition_count):
        """ Create and set positions and texture coords from the given shape
        
        We have six faces with 1 quad (2 triangles) each, resulting in
        6*2*3 = 36 vertices in total. However, for perspective
        projection (or other nonlinear transformations) we need a denser
        grid in order to avoid wobly effects.
        """
        
        # Get cache id. If a match, we don't have to do anything
        vertex_cache_id = self._vol_shape + (partition_count, )
        if vertex_cache_id == self._vertex_cache_id:
            return
        else:
            self._vertex_cache_id = vertex_cache_id
        
        shape = self._vol_shape
        
        # Get corner coordinates. The -0.5 offset is to center
        # pixels/voxels. This works correctly for anisotropic data.
        x0, x1 = -0.5, shape[2] - 0.5
        y0, y1 = -0.5, shape[1] - 0.5
        z0, z1 = -0.5, shape[0] - 0.5
        
        # Prepare texture coordinates
        t0, t1 = 0, 1
        
        # We draw the six planes of the cuboid. In the fragment shader
        # we decide whether to draw or discart the face. We cast rays
        # from the back faces to the front. Fragments on the front faces
        # are discarted.
        
        # Define the 8 corners of the cube.
        tex_coord0, ver_coord0 = [], []
        # bottom
        tex_coord0.append((t0, t0, t0))
        ver_coord0.append((x0, y0, z0))  # 0
        tex_coord0.append((t1, t0, t0))
        ver_coord0.append((x1, y0, z0))  # 1
        tex_coord0.append((t1, t1, t0))
        ver_coord0.append((x1, y1, z0))  # 2
        tex_coord0.append((t0, t1, t0))
        ver_coord0.append((x0, y1, z0))  # 3
        # top
        tex_coord0.append((t0, t0, t1))
        ver_coord0.append((x0, y0, z1))  # 4    
        tex_coord0.append((t0, t1, t1))
        ver_coord0.append((x0, y1, z1))  # 5
        tex_coord0.append((t1, t1, t1))
        ver_coord0.append((x1, y1, z1))  # 6
        tex_coord0.append((t1, t0, t1))
        ver_coord0.append((x1, y0, z1))  # 7
        
        # Unwrap the vertices. 4 vertices per side = 24 vertices
        # Warning: dont mess up the list with indices; theyre carefully
        # chosen to yield  front facing faces.
        tex_coord, ver_coord = [], []
        for i in [0, 1, 2, 3, 
                  4, 5, 6, 7, 
                  3, 2, 6, 5, 
                  0, 4, 7, 1, 
                  0, 3, 5, 4, 
                  1, 7, 6, 2]:
            tex_coord.append(tex_coord0[i])
            ver_coord.append(ver_coord0[i])
        
        # Partition quads in smaller quads
        for iter in range(partition_count):
            tex_coord, ver_coord = self._partition_quads(tex_coord, ver_coord)
        
        # Convert from quads to triangles
        tex_coord, ver_coord = self._quads_to_triangles(tex_coord, ver_coord)
        
        # Turn into structured array
        N = len(tex_coord)
        data = np.empty(N, self._vb_dtype)
        data['a_position'] = np.array(ver_coord)
        data['a_texcoord'] = np.array(tex_coord)
        
        print('vertex data shape', data.shape)
        
        # Apply
        if self._vbo is None or self._vbo.size != data.size:
            if self._vbo is not None:
                self._vbo.delete()
            self._vbo = gloo.VertexBuffer(data)
            self._program.bind(self._vbo)
        else:
            # set_data() would be nice, but because our data is structured,
            # when the vbo needs resizing, the views are invalidated
            self._vbo.set_data(data)
    
    def _partition_quads(self, tex_coord1, ver_coord1):
        """ Partition each quad in 4 smaller quads. 
        """
        tex_coord1 = np.array(tex_coord1)
        ver_coord1 = np.array(ver_coord1)
        #
        tex_coord2, ver_coord2 = [], []
        for iQuad in range(int(len(tex_coord1) / 4)):
            io = iQuad * 4
            for i1 in range(4):
                for i2 in range(4):
                    i3 = (i1 + i2) % 4
                    tex_coord2.append(0.5 * (tex_coord1[io+i1] + 
                                             tex_coord1[io+i3]))
                    ver_coord2.append(0.5 * (ver_coord1[io+i1] + 
                                             ver_coord1[io+i3]))
        return tex_coord2, ver_coord2
    
    def _quads_to_triangles(self, tex_coord1, ver_coord1):
        """ Convert quads to triangles.
        """
        #   0 - 1
        #   |   |
        #   3 - 2
        tex_coord2, ver_coord2 = [], []
        for i0 in range(0, len(tex_coord1), 4):
            for i in (0, 1, 2):
                tex_coord2.append(tex_coord1[i0 + i])
                ver_coord2.append(ver_coord1[i0 + i])
            for i in (0, 2, 3):
                tex_coord2.append(tex_coord1[i0 + i])
                ver_coord2.append(ver_coord1[i0 + i])
        return tex_coord2, ver_coord2
    
    def _quad_partition_count(self, camera):
        """ Select the density of the vertices for the cube to render.
        Higher field of view yields higher partition-count.
        """
        if hasattr(camera, 'fov'):
            fov = camera.fov
        else:
            return 0
        
        if fov <= 10:
            return 0
        elif fov <= 20:
            return 1
        elif fov <= 40:
            return 2
        elif fov <= 80:
            return 3
        else:
            return 4
    
    def bounds(self, mode, axis):
        # Not sure if this is right. Do I need to take the transform if this
        # node into account?
        # Also, this method has no docstring, and I don't want to repeat
        # the docstring here. Maybe Visual implements _bounds that subclasses
        # can implement?
        return 0, self._vol_shape[axis]
    
    def draw(self, transforms):
        
        full_tr = transforms.get_full_transform()
        self._program.vert['transform'] = full_tr
        self._program['u_cameraclip'] = self._cameraclip
        self._program['u_relative_step_size'] = self._relative_step_size
        
        # Try getting partition count
        pc = 0
        if hasattr(transforms, 'viewbox') and transforms.viewbox:
            pc = self._quad_partition_count(transforms.viewbox.camera)
        
        # Ensure we have vertices
        self._create_vertex_data(pc)
        
        # Get and set transforms
        view_tr_f = transforms.visual_to_document
        view_tr_i = view_tr_f.inverse
        self._program.vert['viewtransformf'] = view_tr_f
        self._program.vert['viewtransformi'] = view_tr_i
        
        # Set attributes that are specific to certain styles
        self._program.build_if_needed()
        if self._style == 'iso':
            self._program['u_threshold'] = self._threshold
        
        # Draw!
        self._program.draw('triangles')
