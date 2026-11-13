from vispy import scene, app
import numpy as np
import random

N = 1000

if N % 2 == 1:
    print('N cant be odd!')
    exit(0)

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 600, 600
canvas.show()

grid = canvas.central_widget.add_grid()

viewbox = grid.add_view(row=0, col=1, camera='panzoom')

y_axis = scene.AxisWidget(orientation='left')
y_axis.stretch = (0.1, 1)
widget_y_axis = grid.add_widget(y_axis, row=0, col=0)
y_axis.link_view(viewbox)

x_axis = scene.AxisWidget(orientation='bottom')
x_axis.stretch = (1, 0.1)
widget_x_axis = grid.add_widget(x_axis, row=1, col=1)
x_axis.link_view(viewbox)

c = []
for i in range(N - int(N / 2)):
    c.append([0, 1, 0])
for j in range(int(N / 2)):
    c.append([1, 0, 0])

i = 1

pie = scene.Circle(N, 2, color=np.array(c), parent=viewbox.scene)

viewbox.camera.set_range()


def update(ev):
    global pie, N
    j = random.randint(1, N)
    a = []
    for _ in range(j):
        a.append([0, 1, 0])
    for _ in range(N - j):
        a.append([1, 0, 0])

    pie.update_data(N, 2, color=np.array(a))    

timer = app.Timer()
timer.connect(update)
timer.start(1)

if __name__ == '__main__':
    app.run()
