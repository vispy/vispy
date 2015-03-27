from ..shaders import Function
from ..transforms import NullTransform

clip_frag = """
void clip() {
    vec4 pos = $fb_to_clip(gl_FragCoord);
    if( pos.x < $view.x || pos.x > $view.y || pos.y < $view.z || pos.y > $view.w ) {
        discard;
    }
}
"""


class Clipper(object):
    def __init__(self, bounds=(0, 1, 0, 1), transform=None):
        self.clip_shader = Function(clip_frag)
        self.bounds = bounds  # (xmin, xmax, ymin, ymax)
        if transform is None:
            transform = NullTransform()
        self.set_transform(transform)
    
    @property
    def bounds(self):
        return self._bounds
    
    @bounds.setter
    def bounds(self, b):
        self._bounds = tuple(b[:4])
        self.clip_shader['view'] = self._bounds
        
    def _attach(self, visual):
        self._visual = visual
        hook = self._visual._get_hook('frag', 'pre')
        hook.append(self.clip_shader())

    def set_transform(self, tr):
        self.clip_shader['fb_to_clip'] = tr
        



alpha_frag = """
void apply_alpha() {
    gl_FragColor.a = gl_FragColor.a * $alpha;
}
"""

class Alpha(object):
    def __init__(self, alpha=1.0):
        self.shader = Function(alpha_frag)
        self.alpha = alpha
    
    @property
    def alpha(self):
        return self._alpha
    
    @alpha.setter
    def alpha(self, a):
        self._alpha = a
        self.shader['alpha'] = a
        
    def _attach(self, visual):
        self._visual = visual
        hook = self._visual._get_hook('frag', 'post')
        hook.append(self.shader())



colorfilter_frag = """
void apply_color_filter() {
    gl_FragColor = gl_FragColor * $filter;
}
"""

class ColorFilter(object):
    def __init__(self, filter=(1, 1, 1, 1)):
        self.shader = Function(colorfilter_frag)
        self.filter = filter
    
    @property
    def filter(self):
        return self._filter
    
    @filter.setter
    def filter(self, f):
        self._filter = tuple(f)
        self.shader['filter'] = self._filter
        
    def _attach(self, visual):
        self._visual = visual
        hook = self._visual._get_hook('frag', 'post')
        hook.append(self.shader())


