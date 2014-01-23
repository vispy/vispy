""" Example to experiment with special transformations; in this case
the log transform.

We overload the PointsVisual to give it a new vertex shader. In the
final entities layer, the camera will somehow communicate the transform
that it needs, which is then somehow included in the GLSL.

The projection is a combination of the log transform with a definition
of the field of view (via the transform_projection). I can imagine the
proper solution is a bit more complex.
"""

import numpy as np
from vispy import scene
from vispy import visuals


class LogCamera(scene.TwoDCamera):
    pass
    # Does nothing, but the idea is that it defines the kind of transform


class LogPointsVisual(visuals.PointsVisual):

    VERT_SHADER = """
        // Stuff that each visual must have ...
        uniform   mat4 transform_model;
        uniform   mat4 transform_view;
        uniform   mat4 transform_projection;

        attribute vec3 a_position;

        varying vec4 v_color;
        void main (void) {
            gl_Position = vec4(a_position, 1.0);

            // HERE IS THE EXTRA LINE
            // Comment this line to plot as normal
            gl_Position.y = log2(gl_Position.y);


            gl_Position = transform_projection * transform_view
                        * transform_model * gl_Position;

            v_color = vec4(1.0, 0.5, 0.0, 0.8);
            gl_PointSize = 10.0; //size;
        }
    """


class LogPointsEntity(scene.PointsEntity):
    Visual = LogPointsVisual


# Create a figure
fig = scene.CanvasWithScene()
fig.size = 600, 600
fig.show()

# Create a camera
camera = LogCamera(fig.viewbox)
camera.xlim = -100, 500
camera.ylim = -100, 500

# Create points
x = np.linspace(0, 400, 1000)
y = 2.0 ** x
z = np.zeros_like(x)
data = np.column_stack((x, y, z)).astype('float32')
points = LogPointsEntity(fig.viewbox, data)
