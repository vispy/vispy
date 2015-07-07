from vispy import app, scene, plot
from vispy.util.filter import gaussian_filter
import numpy as np


# Generate M trials of signal
print("Generating data..")
M = 100
N = 10000
dt = 1e-3
maxt = (N - 1) * dt
t = np.linspace(0, maxt, N).reshape(1, N)
pos = np.empty((M, N), dtype=np.float32)
pos[:] = np.sin(t * 10.) * 0.3
pos[:] += np.sin((t + 0.3) * 20.) * 0.15
pos[:] += gaussian_filter(np.random.normal(size=(M,N))*0.2, (0.4, 8))
pos[:] += gaussian_filter(np.random.normal(size=(M,N))*0.005, (0, 1))

# find trigger locations
print("Triggering..")
trig = []
for i in range(M):
    # find every location that crosses threshold
    ind = np.argwhere((pos[i,1:]>0) & (pos[i,:-1]<0))[:,0]
    # select the location closest to t=maxt/2
    ind2 = np.argmin(np.abs(t[0, ind] - (maxt / 2.)))
    trig.append(ind[ind2])

win = scene.SceneCanvas(keys='interactive', show=True)
view = win.central_widget.add_view(camera='panzoom')
grid = scene.GridLines(parent=view.scene)


nplots = 100
pos_offset = np.zeros((nplots, 3), dtype=np.float32)
color = np.empty((nplots, 4), dtype=np.ubyte)
color[:] = [[20, 255, 50, 0]]
color[:, 3] = 0
plots = scene.ScrollingLines(n_lines=nplots, line_size=N, dx=dt, color=color,
                             pos_offset=pos_offset, parent=view.scene)
plots.set_gl_state('additive', line_width=2)

view.camera.rect = (-1, -0.6, 2, 1.2)

plot_ptr = 0
data_ptr = 0



def update(ev):
    global plot_ptr, data_ptr, plots, pos, pos_offset, color, nplots
    
    plots.set_data(plot_ptr, pos[data_ptr])
    dx = -trig[data_ptr] * dt
    
    color[..., 3] *= 0.96
    color[plot_ptr, 3] = 100
    plots.set_color(color)
    
    pos_offset[plot_ptr] = (dx, 0, 0)
    plots.set_pos_offset(pos_offset)
    
    data_ptr = (data_ptr + 1) % M
    plot_ptr = (plot_ptr + 1) % nplots
    win.update()
    
@win.connect
def on_key_press(ev):
    if ev.key == 'Space':
        if timer.running:
            timer.stop()
        else:
            timer.start()

timer = app.Timer(interval='auto', connect=update)
timer.start()

if __name__ == '__main__':
    app.run()
