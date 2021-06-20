"""Various axis utilities."""
import itertools
import logging
import math
import numpy as np

LOGGER = logging.getLogger(__name__)


class Ticker:
    """Base ticker class."""


class Formatter:
    """Base tick formatter class."""

    # some classes classes may want to see all the locs to help format individual ones
    locs = []
    axis = None

    def __call__(self, x):
        """Return the format for tick value *x* at position pos."""
        raise NotImplementedError("Derived must override")

    def format_ticks(self, values):
        """Return the tick labels for all the ticks at once."""
        self.set_locs(values)
        return [self(value) for value in values]

    def format_data(self, value):
        """Return the full string representation of the value with the position unspecified."""
        return self.__call__(value)

    def set_locs(self, locs):
        """
        Set the locations of the ticks.

        This method is called before computing the tick labels because some
        formatters need to know all tick locations to do so.
        """
        self.locs = locs

    # def format_data_short(self, value):
    #     """Return a short string version of the tick value.
    #
    #     Defaults to the position-independent long value.
    #     """
    #     return self.format_data(value)

    def get_offset(self):
        """Get offset."""
        return ""


class NullFormatter(Formatter):
    """Always return the empty string."""

    def __call__(self, x):
        # docstring inherited
        return ""


class FixedFormatter(Formatter):
    """Return fixed strings for tick labels based only on position, not value.

    .. note::
        `.FixedFormatter` should only be used together with `.FixedLocator`.
        Otherwise, the labels may end up in unexpected positions.
    """

    def __init__(self, seq):
        """Set the sequence *seq* of strings that will be used for labels."""
        self.seq = seq
        self.offset_string = ""

    def __call__(self, x):
        """
        Return the label that matches the position, regardless of the value.

        For positions ``pos < len(seq)``, return ``seq[i]`` regardless of
        *x*. Otherwise return empty string. ``seq`` is the sequence of
        strings that this object was initialized with.
        """
        x = int(x)
        if x > len(self.seq):
            return ""
        return self.seq[x]

    def get_offset(self):
        """Get offset value."""
        return self.offset_string

    def set_offset_string(self, ofs):
        """Set offset value"""
        self.offset_string = ofs


class FuncFormatter(Formatter):
    """
    Use a user-defined function for formatting.

    The function should take in two inputs (a tick value ``x`` and a
    position ``pos``), and return a string containing the corresponding
    tick label.
    """

    def __init__(self, func):
        self.func = func
        self.offset_string = ""

    def __call__(self, x):
        """Return the value of the user defined function."""
        return self.func(x)

    def get_offset(self):
        """Get offset value."""
        return self.offset_string

    def set_offset_string(self, ofs):
        """Set offset value."""
        self.offset_string = ofs


class StrMethodFormatter(Formatter):
    """Use a new-style format string (as used by `str.format`) to format the tick.

    The field used for the tick value must be labeled *x*.
    """

    def __init__(self, fmt):
        self.fmt = fmt

    def __call__(self, x):
        """
        Return the formatted label string.

        *x* and *pos* are passed to `str.format` as keyword arguments
        with those exact names.
        """
        return self.fmt.format(x=x)


class ScalarFormatter(Formatter):
    """Format tick values as a number.

    Notes
    -----
    In addition to the parameters above, the formatting of scientific vs.
    floating point representation can be configured via `.scientific`
    and `.power_limits`).

    **Offset notation and scientific notation**

    Offset notation and scientific notation look quite similar at first sight.
    Both split some information from the formatted tick values and display it
    at the end of the axis.

    - The scientific notation splits up the order of magnitude, i.e. a
      multiplicative scaling factor, e.g. ``1e6``.

    - The offset notation separates an additive constant, e.g. ``+1e6``. The
      offset notation label is always prefixed with a ``+`` or ``-`` sign
      and is thus distinguishable from the order of magnitude label.
    """

    _use_offset, offset, _power_limits = None, None, None

    def __init__(
        self,
        use_offset: bool = False,
        offset_threshold: int = 4,
        power_limits=(-5, 6),
    ):
        self._offset_threshold = offset_threshold
        self.use_offset = use_offset
        self.order_of_magnitude = 0
        self.format = ""
        self._scientific = True
        self.power_limits = power_limits

    @property
    def scientific(self):
        """Get flag whether scientific notation is used."""
        return self._scientific

    @scientific.setter
    def scientific(self, value: bool):
        self._scientific = value

    @property
    def power_limits(self):
        """Get power limits."""
        return self._power_limits

    @power_limits.setter
    def power_limits(self, limits):
        """Set size thresholds for scientific notation.

        Parameters
        ----------
        limits : (int, int)
            A tuple *(min_exp, max_exp)* containing the powers of 10 that
            determine the switchover threshold. For a number representable as
            :math:`a \times 10^\mathrm{exp}`` with :math:`1 <= |a| < 10`,
            scientific notation will be used if ``exp <= min_exp`` or
            ``exp >= max_exp``.

            The default limits are controlled by :rc:`axes.formatter.limits`.

            In particular numbers with *exp* equal to the thresholds are
            written in scientific notation.

            Typically, *min_exp* will be negative and *max_exp* will be
            positive.

            For example, ``formatter.set_powerlimits((-3, 4))`` will provide
            the following formatting:
            :math:`1 \times 10^{-3}, 9.9 \times 10^{-3}, 0.01,`
            :math:`9999, 1 \times 10^4`.

        See Also
        --------
        ScalarFormatter.scientific
        """
        if len(limits) != 2:
            raise ValueError("'limits' must be a sequence of length 2")
        self._power_limits = limits

    @property
    def use_offset(self):
        """Return whether automatic mode for offset notation is active.

        This returns True if ``set_useOffset(True)``; it returns False if an
        explicit offset was set, e.g. ``set_useOffset(1000)``.

        See Also
        --------
        ScalarFormatter.set_useOffset
        """
        return self._use_offset

    @use_offset.setter
    def use_offset(self, value: bool):
        """Set whether to use offset notation.

        When formatting a set numbers whose value is large compared to their
        range, the formatter can separate an additive constant. This can
        shorten the formatted numbers so that they are less likely to overlap
        when drawn on an axis.

        Parameters
        ----------
        value : bool or float
            - If False, do not use offset notation.
            - If True (=automatic mode), use offset notation if it can make
              the residual numbers significantly shorter. The exact behavior
              is controlled by :rc:`axes.formatter.offset_threshold`.
            - If a number, force an offset of the given value.

        Examples
        --------
        With active offset notation, the values

        ``100_000, 100_002, 100_004, 100_006, 100_008``

        will be formatted as ``0, 2, 4, 6, 8`` plus an offset ``+1e5``, which
        is written to the edge of the axis.
        """
        if value in [True, False]:
            self.offset = 0
            self._use_offset = value
        else:
            self._use_offset = False
            self.offset = value

    def __call__(self, x, pos=None):
        """
        Return the format for tick value *x* at position *pos*.
        """
        if len(self.locs) == 0:
            return ""
        else:
            xp = (x - self.offset) / (10.0 ** self.order_of_magnitude)
            if abs(xp) < 1e-8:
                xp = 0
            return self.format % xp

    def format_data(self, value):
        """Return the full string representation of the value with the position unspecified."""
        e = math.floor(math.log10(abs(value)))
        s = round(value / 10 ** e, 10)
        exponent = "%d" % e
        significand = "%d" % s if s % 1 == 0 else "%1.10f" % s
        if e == 0:
            return significand
        else:
            return f"{significand}e{exponent}"

    def get_offset(self):
        """Return scientific notation, plus offset."""
        if len(self.locs) == 0:
            return ""
        s = ""
        if self.order_of_magnitude or self.offset:
            offset_str = ""
            sci_not_str = ""
            if self.offset:
                offset_str = self.format_data(self.offset)
                if self.offset > 0:
                    offset_str = "+" + offset_str
            if self.order_of_magnitude:
                sci_not_str = "1e%d" % self.order_of_magnitude
            s = "".join((sci_not_str, offset_str))
        return s

    def set_locs(self, locs):
        """
        Set the locations of the ticks.

        This method is called before computing the tick labels because some
        formatters need to know all tick locations to do so.
        """
        self.locs = locs
        if len(self.locs) > 0:
            if self.use_offset:
                self._compute_offset()
            self._set_order_of_magnitude()
            self._set_format()

    def _compute_offset(self):
        locs = self.locs
        # Restrict to visible ticks.
        vmin, vmax = sorted(self.axis.domain)
        locs = np.asarray(locs)
        locs = locs[(vmin <= locs) & (locs <= vmax)]
        if not len(locs):
            self.offset = 0
            return
        lmin, lmax = locs.min(), locs.max()
        # Only use offset if there are at least two ticks and every tick has
        # the same sign.
        if lmin == lmax or lmin <= 0 <= lmax:
            self.offset = 0
            return
        # min, max comparing absolute values (we want division to round towards
        # zero so we work on absolute values).
        abs_min, abs_max = sorted([abs(float(lmin)), abs(float(lmax))])
        sign = math.copysign(1, lmin)
        # What is the smallest power of ten such that abs_min and abs_max are
        # equal up to that precision?
        # Note: Internally using oom instead of 10 ** oom avoids some numerical
        # accuracy issues.
        oom_max = np.ceil(math.log10(abs_max))
        oom = 1 + next(
            oom
            for oom in itertools.count(oom_max, -1)
            if abs_min // 10 ** oom != abs_max // 10 ** oom
        )
        if (abs_max - abs_min) / 10 ** oom <= 1e-2:
            # Handle the case of straddling a multiple of a large power of ten
            # (relative to the span).
            # What is the smallest power of ten such that abs_min and abs_max
            # are no more than 1 apart at that precision?
            oom = 1 + next(
                oom
                for oom in itertools.count(oom_max, -1)
                if abs_max // 10 ** oom - abs_min // 10 ** oom > 1
            )
        # Only use offset if it saves at least _offset_threshold digits.
        n = self._offset_threshold - 1
        self.offset = (
            sign * (abs_max // 10 ** oom) * 10 ** oom
            if abs_max // 10 ** oom >= 10 ** n
            else 0
        )

    def _set_order_of_magnitude(self):
        # if scientific notation is to be used, find the appropriate exponent
        # if using an numerical offset, find the exponent after applying the
        # offset. When lower power limit = upper <> 0, use provided exponent.
        if not self._scientific:
            self.order_of_magnitude = 0
            return
        if self._power_limits[0] == self._power_limits[1] != 0:
            # fixed scaling when lower power limit = upper <> 0.
            self.order_of_magnitude = self._power_limits[0]
            return
        # restrict to visible ticks
        vmin, vmax = sorted(self.axis.domain)
        locs = np.asarray(self.locs)
        locs = locs[(vmin <= locs) & (locs <= vmax)]
        locs = np.abs(locs)
        if not len(locs):
            self.order_of_magnitude = 0
            return
        if self.offset:
            oom = math.floor(math.log10(vmax - vmin))
        else:
            if locs[0] > locs[-1]:
                val = locs[0]
            else:
                val = locs[-1]
            if val == 0:
                oom = 0
            else:
                oom = math.floor(math.log10(val))
        if oom <= self._power_limits[0]:
            self.order_of_magnitude = oom
        elif oom >= self._power_limits[1]:
            self.order_of_magnitude = oom
        else:
            self.order_of_magnitude = 0

    def _set_format(self):
        # set the format string to format all the ticklabels
        if len(self.locs) < 2:
            # Temporarily augment the locations with the axis end points.
            _locs = [*self.locs, *self.axis.domain]
        else:
            _locs = self.locs
        locs = (np.asarray(_locs) - self.offset) / 10.0 ** self.order_of_magnitude
        loc_range = np.ptp(locs)
        # Curvilinear coordinates can yield two identical points.
        if loc_range == 0:
            loc_range = np.max(np.abs(locs))
        # Both points might be zero.
        if loc_range == 0:
            loc_range = 1
        if len(self.locs) < 2:
            # We needed the end points only for the loc_range calculation.
            locs = locs[:-2]
        loc_range_oom = int(math.floor(math.log10(loc_range)))
        # first estimate:
        sigfigs = max(0, 3 - loc_range_oom)
        # refined estimate:
        thresh = 1e-3 * 10 ** loc_range_oom
        while sigfigs >= 0:
            if np.abs(locs - np.round(locs, decimals=sigfigs)).max() < thresh:
                sigfigs -= 1
            else:
                break
        sigfigs += 1
        self.format = "%1." + str(sigfigs) + "f"


class PercentFormatter(Formatter):
    """Format numbers as a percentage.

    Parameters
    ----------
    xmax : float
        Determines how the number is converted into a percentage.
        *xmax* is the data value that corresponds to 100%.
        Percentages are computed as ``x / xmax * 100``. So if the data is
        already scaled to be percentages, *xmax* will be 100. Another common
        situation is where *xmax* is 1.0.
    decimals : None or int
        The number of decimal places to place after the point.
        If *None* (the default), the number will be computed automatically.
    symbol : str or None
        A string that will be appended to the label. It may be
        *None* or empty to indicate that no symbol should be used. LaTeX
        special characters are escaped in *symbol* whenever latex mode is
        enabled, unless *is_latex* is *True*.
    """

    def __init__(self, xmax=100, decimals=None, symbol="%"):
        self.xmax = xmax + 0.0
        self.decimals = decimals
        self._symbol = symbol

    def __call__(self, x):
        """Format the tick as a percentage with the appropriate scaling."""
        ax_min, ax_max = self.axis.domain
        display_range = abs(ax_max - ax_min)
        return self.format_pct(x, display_range)

    def format_pct(self, x, display_range):
        """
        Format the number as a percentage number with the correct
        number of decimals and adds the percent symbol, if any.

        If ``self.decimals`` is `None`, the number of digits after the
        decimal point is set based on the *display_range* of the axis
        as follows:

        +---------------+----------+------------------------+
        | display_range | decimals |          sample        |
        +---------------+----------+------------------------+
        | >50           |     0    | ``x = 34.5`` => 35%    |
        +---------------+----------+------------------------+
        | >5            |     1    | ``x = 34.5`` => 34.5%  |
        +---------------+----------+------------------------+
        | >0.5          |     2    | ``x = 34.5`` => 34.50% |
        +---------------+----------+------------------------+
        |      ...      |    ...   |          ...           |
        +---------------+----------+------------------------+

        This method will not be very good for tiny axis ranges or
        extremely large ones. It assumes that the values on the chart
        are percentages displayed on a reasonable scale.
        """
        x = self.convert_to_pct(x)
        if self.decimals is None:
            # conversion works because display_range is a difference
            scaled_range = self.convert_to_pct(display_range)
            if scaled_range <= 0:
                decimals = 0
            else:
                # Luckily Python's built-in ceil rounds to +inf, not away from
                # zero. This is very important since the equation for decimals
                # starts out as `scaled_range > 0.5 * 10**(2 - decimals)`
                # and ends up with `decimals > 2 - log10(2 * scaled_range)`.
                decimals = math.ceil(2.0 - math.log10(2.0 * scaled_range))
                if decimals > 5:
                    decimals = 5
                elif decimals < 0:
                    decimals = 0
        else:
            decimals = self.decimals
        s = "{x:0.{decimals}f}".format(x=x, decimals=int(decimals))

        return s + self.symbol

    def convert_to_pct(self, x):
        """Convert value to percentage."""
        return 100.0 * (x / self.xmax)

    @property
    def symbol(self):
        r"""
        The configured percent symbol as a string.

        If LaTeX is enabled via :rc:`text.usetex`, the special characters
        ``{'#', '$', '%', '&', '~', '_', '^', '\', '{', '}'}`` are
        automatically escaped in the string.
        """
        symbol = self._symbol
        if not symbol:
            symbol = ""
        return symbol

    @symbol.setter
    def symbol(self, symbol):
        self._symbol = symbol


# class Locator:
#     """Determine the tick locations;
#
#     Note that the same locator should not be used across multiple
#     `~matplotlib.axis.Axis` because the locator stores references to the Axis
#     data and view limits.
#     """
#
#     # Some automatic tick locators can generate so many ticks they
#     # kill the machine when you try and render them.
#     # This parameter is set to cause locators to raise an error if too
#     # many ticks are generated.
#     MAX_TICKS = 1000
#
#     def tick_values(self, vmin, vmax):
#         """
#         Return the values of the located ticks given **vmin** and **vmax**.
#
#         .. note::
#             To get tick locations with the vmin and vmax values defined
#             automatically for the associated :attr:`axis` simply call
#             the Locator instance::
#
#                 >>> print(type(loc))
#                 <type 'Locator'>
#                 >>> print(loc())
#                 [1, 2, 3, 4]
#
#         """
#         raise NotImplementedError("Derived must override")
#
#     def set_params(self, **kwargs):
#         """
#         Do nothing, and raise a warning. Any locator class not supporting the
#         set_params() function will call this.
#         """
#         raise NotImplementedError("Must implement method")
#
#     def __call__(self):
#         """Return the locations of the ticks."""
#         # note: some locators return data limits, other return view limits,
#         # hence there is no *one* interface to call self.tick_values.
#         raise NotImplementedError("Derived must override")
#
#     def raise_if_exceeds(self, locs):
#         """
#         Log at WARNING level if *locs* is longer than `Locator.MAXTICKS`.
#
#         This is intended to be called immediately before returning *locs* from
#         ``__call__`` to inform users in case their Locator returns a huge
#         number of ticks, causing Matplotlib to run out of memory.
#
#         The "strange" name of this method dates back to when it would raise an
#         exception instead of emitting a log.
#         """
#         if len(locs) >= self.MAX_TICKS:
#             LOGGER.warning(
#                 "Locator attempting to generate %s ticks ([%s, ..., %s]), "
#                 "which exceeds Locator.MAX_TICKS (%s).",
#                 len(locs),
#                 locs[0],
#                 locs[-1],
#                 self.MAX_TICKS,
#             )
#         return locs
#
#     def nonsingular(self, v0, v1):
#         """Adjust a range as needed to avoid singularities.
#
#         This method gets called during autoscaling, with ``(v0, v1)`` set to
#         the data limits on the axes if the axes contains any data, or
#         ``(-inf, +inf)`` if not.
#
#         - If ``v0 == v1`` (possibly up to some floating point slop), this
#           method returns an expanded interval around this value.
#         - If ``(v0, v1) == (-inf, +inf)``, this method returns appropriate
#           default view limits.
#         - Otherwise, ``(v0, v1)`` is returned without modification.
#         """
#         return non_singular(v0, v1, expander=0.05)
#
#     def view_limits(self, vmin, vmax):
#         """
#         Select a scale for the range from vmin to vmax.
#
#         Subclasses should override this method to change locator behaviour.
#         """
#         return non_singular(vmin, vmax)
#
#
# class IndexLocator(Locator):
#     """
#     Place a tick on every multiple of some base number of points
#     plotted, e.g., on every 5th point.  It is assumed that you are doing
#     index plotting; i.e., the axis is 0, len(data).  This is mainly
#     useful for x ticks.
#     """
#
#     def __init__(self, base, offset):
#         """Place ticks every *base* data point, starting at *offset*."""
#         self._base = base
#         self.offset = offset
#
#     def set_params(self, base=None, offset=None):
#         """Set parameters within this locator"""
#         if base is not None:
#             self._base = base
#         if offset is not None:
#             self.offset = offset
#
#     def __call__(self):
#         """Return the locations of the ticks"""
#         dmin, dmax = self.axis.domain
#         return self.tick_values(dmin, dmax)
#
#     def tick_values(self, vmin, vmax):
#         """Get tick values."""
#         return self.raise_if_exceeds(
#             np.arange(vmin + self.offset, vmax + 1, self._base)
#         )
#
#
# class FixedLocator(Locator):
#     """Tick locations are fixed.  If nbins is not None,
#     the array of possible positions will be subsampled to
#     keep the number of ticks <= nbins +1.
#     The subsampling will be done so as to include the smallest
#     absolute value; for example, if zero is included in the
#     array of possibilities, then it is guaranteed to be one of
#     the chosen ticks.
#     """
#
#     def __init__(self, locs, n_bins=None):
#         self.locs = np.asarray(locs)
#         self.n_bins = max(n_bins, 2) if n_bins is not None else None
#
#     def set_params(self, nbins=None):
#         """Set parameters within this locator."""
#         if nbins is not None:
#             self.n_bins = nbins
#
#     def __call__(self):
#         return self.tick_values(None, None)
#
#     def tick_values(self, vmin, vmax):
#         """
#         Return the locations of the ticks.
#
#         .. note::
#
#             Because the values are fixed, vmin and vmax are not used in this
#             method.
#
#         """
#         if self.n_bins is None:
#             return self.locs
#         step = max(int(np.ceil(len(self.locs) / self.n_bins)), 1)
#         ticks = self.locs[::step]
#         for i in range(1, step):
#             ticks1 = self.locs[i::step]
#             if np.abs(ticks1).min() < np.abs(ticks).min():
#                 ticks = ticks1
#         return self.raise_if_exceeds(ticks)
#
#
# class NullLocator(Locator):
#     """No ticks."""
#
#     def __call__(self):
#         return self.tick_values(None, None)
#
#     def tick_values(self, vmin, vmax):
#         """
#         Return the locations of the ticks.
#
#         .. note::
#
#             Because the values are Null, vmin and vmax are not used in this
#             method.
#         """
#         return []
#
#
# class LinearLocator(Locator):
#     """
#     Determine the tick locations
#
#     The first time this function is called it will try to set the
#     number of ticks to make a nice tick partitioning.  Thereafter the
#     number of ticks will be fixed so that interactive navigation will
#     be nice
#
#     """
#
#     _num_ticks = 11
#
#     def __init__(self, num_ticks=None, presets=None):
#         """
#         Use presets to set locs based on lom.  A dict mapping vmin, vmax->locs
#         """
#         self.num_ticks = num_ticks
#         self.presets = {} if presets is None else presets
#
#     @property
#     def num_ticks(self):
#         """Get num ticks."""
#         return self._num_ticks if self._num_ticks is not None else 11
#
#     @num_ticks.setter
#     def num_ticks(self, num_ticks):
#         self._num_ticks = num_ticks
#
#     def set_params(self, num_ticks=None, presets=None):
#         """Set parameters within this locator."""
#         if presets is not None:
#             self.presets = presets
#         if num_ticks is not None:
#             self.num_ticks = num_ticks
#
#     def __call__(self):
#         """Return the locations of the ticks."""
#         vmin, vmax = self.axis.get_view_interval()
#         return self.tick_values(vmin, vmax)
#
#     def tick_values(self, vmin, vmax):
#         """Get tick values."""
#         vmin, vmax = non_singular(vmin, vmax, expander=0.05)
#         if vmax < vmin:
#             vmin, vmax = vmax, vmin
#
#         if (vmin, vmax) in self.presets:
#             return self.presets[(vmin, vmax)]
#
#         if self.num_ticks == 0:
#             return []
#         tick_locs = np.linspace(vmin, vmax, self.num_ticks)
#         return self.raise_if_exceeds(tick_locs)
#
#     def view_limits(self, vmin, vmax, mode: str = "round_numbers"):
#         """Try to choose the view limits intelligently."""
#
#         if vmax < vmin:
#             vmin, vmax = vmax, vmin
#
#         if vmin == vmax:
#             vmin -= 1
#             vmax += 1
#
#         if mode == "round_numbers":
#             exponent, remainder = divmod(
#                 math.log10(vmax - vmin), math.log10(max(self.num_ticks - 1, 1))
#             )
#             exponent -= remainder < 0.5
#             scale = max(self.num_ticks - 1, 1) ** (-exponent)
#             vmin = math.floor(scale * vmin) / scale
#             vmax = math.ceil(scale * vmax) / scale
#         return non_singular(vmin, vmax)
