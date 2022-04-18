import numpy as np
import vispy.plot as vp
from vispy.color import get_colormap

# load example data
from vispy.io import load_data_file
data = np.load(load_data_file('electrophys/iv_curve.npz'))['arr_0']
data *= 1000  # V -> mV
dt = 1e-4  # this data is sampled at 10 kHz

# create figure with plot
fig = vp.Fig()
plt = fig[0, 0]
plt._configure_2d()
plt.title.text = 'Current Clamp Recording'
plt.ylabel.text = 'Membrane Potential (mV)'
plt.xlabel.text = 'Time (ms)'
selected = None

# plot data
cmap = get_colormap('hsl', value=0.5)
colors = cmap.map(np.linspace(0.1, 0.9, data.shape[0]))
t = np.arange(data.shape[1]) * (dt * 1000)
for i, y in enumerate(data):
    line = plt.plot((t, y), color=colors[i])
    line.interactive = True
    line.unfreeze()  # make it so we can add a new property to the instance
    line.data_index = i
    line.freeze()


# Build visuals used for cursor
cursor_text = vp.Text("", pos=(0, 0), anchor_x='left', anchor_y='center',
                      font_size=8, parent=plt.view.scene)
cursor_line = vp.Line(parent=plt.view.scene)
cursor_symbol = vp.Markers(pos=np.array([[0, 0]]), parent=plt.view.scene)
cursor_line.visible = False
cursor_symbol.visible = False
cursor_line.order = 10
cursor_symbol.order = 11
cursor_text.order = 10


@fig.connect
def on_mouse_press(event):
    global selected, fig
    if event.handled or event.button != 1:
        return
    if selected is not None:
        selected.set_data(width=1)
    selected = None
    for v in fig.visuals_at(event.pos):
        if isinstance(v, vp.LinePlot):
            selected = v
            break
    if selected is not None:
        selected.set_data(width=3)
        update_cursor(event.pos)


@fig.connect
def on_mouse_move(event):
    update_cursor(event.pos)


def update_cursor(pos):
    global selected, cursor, data, dt, plt
    if selected is None:
        cursor_text.visible = False
        cursor_line.visible = False
        cursor_symbol.visible = False
    else:
        # get data for the selected trace
        trace = data[selected.data_index]

        # map the mouse position to data coordinates
        tr = fig.scene.node_transform(selected)
        pos = tr.map(pos)

        # get interpolated y coordinate
        x = min(max(pos[0], t[0]), t[-2])
        ind = x / (dt * 1000)
        i = int(np.floor(ind))
        s = ind - i
        y = trace[i] * (1 - s) + trace[i + 1] * s 

        # update cursor
        cursor_text.text = "x=%0.2f ms, y=%0.2f mV" % (x, y)
        offset = np.diff(tr.map([[0, 0], [10, 0]]), axis=0)[0, 0]
        cursor_text.pos = x + offset, y
        rect = plt.view.camera.rect
        cursor_line.set_data(np.array([[x, rect.bottom], [x, rect.top]]))
        cursor_symbol.set_data(pos=np.array([[x, y]]), symbol='+',
                               face_color='b')
        cursor_text.visible = True
        cursor_line.visible = True
        cursor_symbol.visible = True


if __name__ == '__main__':
    fig.app.run()
