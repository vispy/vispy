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
    def __init__(self, visual, bounds=(0, 1, 0, 1), transform=None):
        self.clip_shader = Function(clip_frag)
        self.bounds = bounds  # (xmin, xmax, ymin, ymax)
        if transform is None:
            transform = NullTransform()
        self.set_transform(transform)
        self.attach(visual)
    
    @property
    def bounds(self):
        return self._bounds
    
    @bounds.setter
    def bounds(self, b):
        self._bounds = tuple(b[:4])
        self.clip_shader['view'] = self._bounds
        
    def attach(self, visual):
        self._visual = visual
        self._visual._line_visual._program.frag['clip'] = self.clip_shader()

    def set_transform(self, tr):
        self.clip_shader['fb_to_clip'] = tr
        
