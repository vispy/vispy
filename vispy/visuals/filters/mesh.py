from ..shaders import Function
from ...color import Color
from ...gloo import VertexBuffer

import numpy as np


shading_vertex_template = """
varying vec3 v_normal_vec;
varying vec3 v_light_vec;
varying vec3 v_eye_vec;
varying vec4 v_pos_scene;

varying vec4 v_ambientk;
varying vec4 v_light_color;

void prepare_shading() {
    v_ambientk = $ambientk;
    v_light_color = $light_color;

    // TODO: Find a way to get the original position from the main vertex
    //       shader instead of inversing the transformation.
    vec4 pos_scene = $render2scene(gl_Position);
    v_pos_scene = pos_scene; // Used for flat shading only in the fragment.
    vec4 normal_scene = $visual2scene(vec4($normal, 1.0));
    vec4 origin_scene = $visual2scene(vec4(0.0, 0.0, 0.0, 1.0));

    normal_scene /= normal_scene.w;
    origin_scene /= origin_scene.w;

    vec3 normal = normalize(normal_scene.xyz - origin_scene.xyz);
    v_normal_vec = normal; //VARYING COPY

    vec4 pos_front = $scene2doc(pos_scene);
    pos_front.z += 0.01;
    pos_front = $doc2scene(pos_front);
    pos_front /= pos_front.w;

    vec4 pos_back = $scene2doc(pos_scene);
    pos_back.z -= 0.01;
    pos_back = $doc2scene(pos_back);
    pos_back /= pos_back.w;

    vec3 eye = normalize(pos_front.xyz - pos_back.xyz);
    v_eye_vec = eye; //VARYING COPY

    vec3 light = normalize($light_dir.xyz);
    v_light_vec = light; //VARYING COPY
}
"""

shading_fragment_template = """
varying vec3 v_normal_vec;
varying vec3 v_light_vec;
varying vec3 v_eye_vec;
varying vec4 v_pos_scene;

varying vec4 v_ambientk;
varying vec4 v_light_color;

void shade() {
    //DIFFUSE
    vec3 normal;
    if ($flat_shading == 1) {
        vec3 u = dFdx(v_pos_scene.xyz);
        vec3 v = dFdy(v_pos_scene.xyz);
        normal = normalize(cross(u, v));
    } else {
        normal = v_normal_vec;
    }
    float diffusek = dot(v_light_vec, normal);
    // clamp, because 0 < theta < pi/2
    diffusek  = clamp(diffusek, 0.0, 1.0);
    vec4 diffuse_color = v_light_color * diffusek;

    //SPECULAR
    //reflect light wrt normal for the reflected ray, then
    //find the angle made with the eye
    float speculark = 0.0;
    if ($shininess > 0) {
        speculark = dot(reflect(v_light_vec, v_normal_vec), v_eye_vec);
        speculark = clamp(speculark, 0.0, 1.0);
        //raise to the material's shininess, multiply with a
        //small factor for spread
        speculark = 20.0 * pow(speculark, 1.0 / $shininess);
    }
    vec4 specular_color = v_light_color * speculark;
    if ($shading_enabled == 1) {
        gl_FragColor *= v_ambientk + diffuse_color;
        gl_FragColor += specular_color;
    }
}
"""  # noqa


class ShadingFilter(object):

    def __init__(self, shading='flat', enabled=True, light_dir=(10, 5, -5),
                 light_color=(1, 1, 1, 1), ambient_light_color=(.3, .3, .3, 1),
                 shininess=5e-3):
        self._attached = False
        self._shading = shading
        self._enabled = True
        self._light_dir = light_dir
        self._light_color = Color(light_color)
        self._ambient_light_color = Color(ambient_light_color)
        self._shininess = shininess

        self.vcode = Function(shading_vertex_template)
        self._normals = VertexBuffer(np.zeros((0, 3), dtype=np.float32))
        self.vcode['normal'] = self._normals

        self.fcode = Function(shading_fragment_template)

        self.vertex_program = self.vcode()
        self.fragment_program = self.fcode()

    @property
    def shading(self):
        """The shading method."""
        return self._shading

    @shading.setter
    def shading(self, shading):
        assert shading in (None, 'flat', 'smooth')
        self._shading = shading
        self._update_data()

    @property
    def enabled(self):
        """True to enable shading."""
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled
        self._update_data()

    @property
    def light_dir(self):
        """The light direction."""
        return self._light_dir

    @light_dir.setter
    def light_dir(self, direction):
        direction = np.array(direction, float).ravel()
        if direction.size != 3 or not np.isfinite(direction).all():
            raise ValueError('Invalid direction %s' % direction)
        self._light_dir = tuple(direction)
        self._update_data()

    @property
    def light_color(self):
        """The light color."""
        return self._light_color

    @light_color.setter
    def light_color(self, light_color):
        self._light_color = Color(light_color)
        self._update_data()

    @property
    def ambient_light_color(self):
        """The ambient light color."""
        return self._ambient_light_color

    @ambient_light_color.setter
    def ambient_light_color(self, color):
        self._ambient_light_color = Color(color)

    @property
    def shininess(self):
        """The shininess."""
        return self._shininess

    @shininess.setter
    def shininess(self, shininess):
        self._shininess = shininess
        self._update_data()

    def _update_data(self):
        if not self._attached:
            return
        self.vcode['light_dir'] = self._light_dir
        self.vcode['light_color'] = self._light_color.rgba
        self.vcode['ambientk'] = self._ambient_light_color.rgba
        self.fcode['shininess'] = self._shininess
        self.fcode['flat_shading'] = 1 if self._shading == 'flat' else 0
        self.fcode['shading_enabled'] = 1 if self._shading is not None else 0

    def _attach(self, visual):
        # vertex shader
        vert_post = visual._get_hook('vert', 'post')
        vert_post.add(self.vertex_program)
        normals = visual.mesh_data.get_vertex_normals()
        self._normals.set_data(normals, convert=True)
        render2scene = visual.transforms.get_transform('render', 'scene')
        visual2scene = visual.transforms.get_transform('visual', 'scene')
        scene2doc = visual.transforms.get_transform('scene', 'document')
        doc2scene = visual.transforms.get_transform('document', 'scene')
        self.vcode['render2scene'] = render2scene
        self.vcode['visual2scene'] = visual2scene
        self.vcode['scene2doc'] = scene2doc
        self.vcode['doc2scene'] = doc2scene

        # fragment shader
        frag_post = visual._get_hook('frag', 'post')
        frag_post.add(self.fragment_program)

        self._attached = True
        self._update_data()

    def _detach(self, visual):
        visual._get_hook('vert', 'post').remove(self.vertex_program)
        visual._get_hook('frag', 'post').remove(self.fragment_program)
