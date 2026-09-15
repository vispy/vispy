import numpy as np
import pandas as pd

from datetime import datetime
from vispy import scene, app
from vispy.color import ColorArray

if __name__ == "__main__":

    # app.use_app("pyglet")

    def update(ev):
        global i
        pos11[:, 1] = np.random.normal(loc=140, scale=5, size=N)
        pos12[:, 1] = np.random.normal(loc=120, scale=5, size=N)
        pos13[:, 1] = np.random.normal(loc=100, scale=5, size=N)
        pos14[:, 1] = np.random.normal(loc=80, scale=5, size=N)
        pos15[:, 1] = np.random.normal(loc=60, scale=5, size=N)

        line11.set_data(pos=pos11, color=ColorArray('yellow'))
        line12.set_data(pos=pos12, color=ColorArray('blue'))
        line13.set_data(pos=pos13, color=(1, 0.1, 0.))
        line14.set_data(pos=pos14, color=(0.25, 0.8, 0.))
        line15.set_data(pos=pos15, color=(1, 1, 1))

    N = 1200

    pos11 = np.zeros((N, 2), dtype=np.float32)
    pos12 = np.zeros((N, 2), dtype=np.float32)
    pos13 = np.zeros((N, 2), dtype=np.float32)
    pos14 = np.zeros((N, 2), dtype=np.float32)
    pos15 = np.zeros((N, 2), dtype=np.float32)


    x_lim = [0., 120.]
    y_lim1 = [50., 150.]
    y_lim2 = [50., 150.]
    y_lim3 = [50., 150.]
    y_lim4 = [50., 150.]
    y_lim5 = [50., 150.]

    pos11[:, 0] = np.linspace(x_lim[0], x_lim[1], N)
    pos11[:, 1] = np.random.normal(loc=120, size=N)
    pos12[:, 0] = np.linspace(x_lim[0], x_lim[1], N)
    pos12[:, 1] = np.random.normal(loc=100, size=N)
    pos13[:, 0] = np.linspace(x_lim[0], x_lim[1], N)
    pos13[:, 1] = np.random.normal(loc=80, size=N)
    pos14[:, 0] = np.linspace(x_lim[0], x_lim[1], N)
    pos14[:, 1] = np.random.normal(loc=60, size=N)
    pos15[:, 0] = np.linspace(x_lim[0], x_lim[1], N)
    pos15[:, 1] = np.random.normal(loc=140, size=N)


    color = np.ones((N, 4), dtype=np.float32)
    color[:, 0] = np.linspace(0, 1, N)
    color[:, 1] = color[::-1, 0]

    canvas = scene.SceneCanvas(keys='interactive', vsync=True)
    canvas.size = 1920, 1080
    canvas.show()

    grid = canvas.central_widget.add_grid()
    grid.padding = 10

    vb1 = grid.add_view(row=0, col=1, camera='panzoom')


    x_axis1 = scene.AxisWidget(orientation='bottom', axis_mapping=pd.date_range(start ='1-1-2018', periods = 24, freq="4D").tolist(), date_format_string='%m/%d/%Y, %H:%M:%S.%f')

    x_axis1.stretch = (1, 0.1)
    grid.add_widget(x_axis1, row=1, col=1)
    x_axis1.link_view(vb1)
    y_axis1 = scene.AxisWidget(orientation='left')
    y_axis1.stretch = (0.1, 1)
    grid.add_widget(y_axis1, row=0, col=0)
    y_axis1.link_view(vb1)


    grid_lines1 = scene.visuals.GridLines(parent=vb1.scene)

    line11 = scene.Line(pos11, ColorArray('yellow'), parent=vb1.scene, width=0.8)
    line12 = scene.Line(pos12, ColorArray('blue'), parent=vb1.scene, width=0.8)
    line13 = scene.Line(pos13, (1, 0.1, 0.), parent=vb1.scene, width=0.8)
    line14 = scene.Line(pos14, (0.25, 0.8, 0.), parent=vb1.scene, width=0.8)
    line15 = scene.Line(pos15, (0, 0, 0), parent=vb1.scene, width=0.8)


    vb1.camera.set_range()

    timer = app.Timer()
    timer.connect(update)
    timer.start(0)

    app.run()