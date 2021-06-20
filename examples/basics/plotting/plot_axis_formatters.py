"""Example demonstrating different tick formatters available in Vispy."""

import numpy as np
from vispy import plot as vp
from vispy.util.axis import (
    NullFormatter,
    FixedFormatter,
    FuncFormatter,
    StrMethodFormatter,
    PercentFormatter,
)

fig = vp.Fig(size=(800, 1000), show=False, keys="interactive")

x = np.linspace(-np.pi, np.pi, 201)
y = np.sin(x)
# this is the standard formatter
_ = fig[0, 0].plot(
    (x, y),
    width=3,
    color="k",
    title="Sine wave using ScalarFormatter",
    xlabel="Angle [rad]",
    ylabel="sin(x)",
)

# this is null formatter where there are no values
_ = fig[1, 0].plot(
    (x, y),
    width=3,
    color="k",
    title="Sine wave using NullFormatter",
    xlabel="Angle [rad]",
    ylabel="sin(x)",
)
fig[1, 0].xaxis.axis.ticker.formatter = NullFormatter()

# this is the fixed formatter which will display fixed values
_ = fig[2, 0].plot(
    (x, y),
    width=3,
    color="k",
    title="Sine wave using FixedFormatter",
    xlabel="Angle [rad]",
    ylabel="sin(x)",
)
fig[2, 0].xaxis.axis.ticker.formatter = FixedFormatter(
    ["-3", "-2", "-1", "0", "1", "2", "3"]
)

# this is the string formatter, here values will be surrounded by > and <
_ = fig[3, 0].plot(
    (x, y),
    width=3,
    color="k",
    title="Sine wave using StrMethodFormatter",
    xlabel="Angle [rad]",
    ylabel="sin(x)",
)
fig[3, 0].xaxis.axis.ticker.formatter = StrMethodFormatter(">{x}<")

# this is the function formatter where values are formatted by specified function
_ = fig[4, 0].plot(
    (x, y),
    width=3,
    color="k",
    title="Sine wave using FuncFormatter",
    xlabel="Angle [rad]",
    ylabel="sin(x)",
)
fig[4, 0].xaxis.axis.ticker.formatter = FuncFormatter(lambda x: f"[{x:.2f}]")

# this is the percent formatter where values will be formatted as percentage
_ = fig[5, 0].plot(
    (x, y),
    width=3,
    color="k",
    title="Sine wave using PercentFormatter",
    xlabel="Angle [rad]",
    ylabel="sin(x)",
)
fig[5, 0].xaxis.axis.ticker.formatter = PercentFormatter(xmax=np.pi)

if __name__ == "__main__":
    fig.show(run=True)
