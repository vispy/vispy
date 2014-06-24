import re
from vispy.scene.shaders.parsing import re_identifier


def test_identifier():
    assert(re.match('('+re_identifier+')', 'Ax2_d3__7').groups()[0]
           == 'Ax2_d3__7')
    assert(re.match('('+re_identifier+')', '_Ax2_d3__7').groups()[0]
           == '_Ax2_d3__7')
    assert(re.match(re_identifier, '7Ax2_d3__7') is None)
    assert(re.match('('+re_identifier+')', 'x,y').groups()[0] == 'x')
    assert(re.match('('+re_identifier+')', 'x y').groups()[0] == 'x')
