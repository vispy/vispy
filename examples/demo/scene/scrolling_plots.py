from vispy import app, scene
from vispy.util import filter 
import numpy as np

win = scene.SceneCanvas(keys='interactive', show=True)
view = win.central_widget.add_view()
view.camera = 'panzoom'

N = 50
M = 20000
view.camera.rect = (0, -5, 10, N*10 + 5)

lines = []
for i in range(N):
    l = scene.Line(parent=view.scene)
    lines.append(l)
    l.transform = scene.STTransform(translate=(0, i*10))

data = np.empty((N, M*2))
data[:, :M] = np.random.normal(size=(N, M), scale=30)
data[:, :M] = filter.gaussian_filter(data[:, :M], (1, 100))
data[:, :M] += np.random.normal(size=(N, M), scale=6)
data[:, :M] = filter.gaussian_filter(data[:, :M], (0, 10))
data[:, :M] += np.random.normal(size=(N, M), scale=0.6)
data[:, M:] = data[:, :M]

ptr = 0
def update(ev):
    global ptr
    d = np.empty((M, 2))
    d[:, 0] = np.linspace(0, 10, M)
    for i, l in enumerate(lines):
        d[:, 1] = data[i, ptr:ptr+M]
        l.set_data(d.copy())
    ptr = (ptr + 100) % M

timer = app.Timer(connect=update, interval=0.03)
timer.start()


if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        app.run()
