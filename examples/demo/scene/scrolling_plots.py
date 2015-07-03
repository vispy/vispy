from vispy import app, scene, visuals, gloo, plot
import numpy as np


win = scene.SceneCanvas(keys='interactive', show=True, size=(1024, 768))
grid = win.central_widget.add_grid()
view = grid.add_view(0, 1)
view.camera = scene.MagnifyCamera(mag=1, size_factor=0.5, radius_ratio=0.6)
#view.camera = 'panzoom'

# Add axes
yax = scene.AxisWidget(orientation='left')
yax.stretch = (0.05, 1)
grid.add_widget(yax, 0, 0)
yax.link_view(view)

xax = scene.AxisWidget(orientation='bottom')
xax.stretch = (1, 0.05)
grid.add_widget(xax, 1, 1)
xax.link_view(view)


N = 10000
M = 2000
cols = int(N**0.5)
view.camera.rect = (0, 0, cols, N/cols)

lines = scene.ScrollingLines(n_lines=N, line_size=M, columns=cols, dt=0.8/M,
                             cell_size=(1, 8), parent=view.scene)
lines.transform = scene.STTransform(scale=(1, 1/8.))

def update(ev):
    m = 10
    data = np.zeros((N, m))
    data = np.random.normal(size=(N, m), scale=0.3)
    data[data > 1] += 4
    lines.roll_data(data)

timer = app.Timer(connect=update, interval=0)
timer.start()


if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        app.run()
