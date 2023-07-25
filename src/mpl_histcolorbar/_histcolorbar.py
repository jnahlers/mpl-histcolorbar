__all__ = ['histcolorbar', 'HistColorbar']

import copy
import math

import matplotlib as mpl
import matplotlib.colorbar as cbar
from matplotlib.colorbar import Colorbar
from matplotlib import _api, cbook, colors

import numpy as np


def histcolorbar(fig, mappable, cax=None, ax=None, use_gridspec=True, **kwargs):
    """Add a `HistColorbar` to a plot.

    This function is based on `matplotlib.figure.Figure.colorbar`, and accepts all
    the same arguments with the addition of an argument that takes the `Figure` to
    which the histcolorbar will be added, as well as keyword arguments specific
    to a histcolorbar.

    Parameters
    ----------
    fig : `matplotlib.figure.Figure`
        The figure to which the `HistColorbar` will be added.
    mappable : `matplotlib.cm.ScalarMappable`
        The `ScalarMappable` described by this histcolorbar.
    cax : `matplotlib.axes.Axes`, optional
        Axes into which the histcolorbar will be drawn.  If `None`, then a new
        Axes is created and the space for it will be stolen from the Axes(s)
        specified in *ax*.
    ax : `matplotlib.axes.Axes` or iterable or `numpy.ndarray` of Axes, optional
        The one or more parent Axes from which space for a new histcolorbar Axes
        will be stolen. This parameter is only used if *cax* is not set.

        Defaults to the Axes that contains the mappable used to create the
        histcolorbar.
    use_gridspec : bool, optional
        If *cax* is ``None``, a new *cax* is created as an instance of
        Axes.  If *ax* is positioned with a subplotspec and *use_gridspec*
        is ``True``, then *cax* is also positioned with a subplotspec.
    **kwargs
        Additional keyword arguments are described in the docstring of
        `HistColorbar`.

    Returns
    -------
    histcolorbar : `mpl_histcolorbar.HistColorbar`
    """
    if ax is None:
        ax = getattr(mappable, "axes", None)

    if (fig.get_layout_engine() is not None and
            not fig.get_layout_engine().colorbar_gridspec):
        use_gridspec = False
    # Store the value of gca so that we can set it back later on.
    if cax is None:
        if ax is None:
            _api.warn_deprecated("3.6", message=(
                'Unable to determine Axes to steal space for HistColorbar. '
                'Using gca(), but will raise in the future. '
                'Either provide the *cax* argument to use as the Axes for '
                'the HistColorbar, provide the *ax* argument to steal space '
                'from it, or add *mappable* to an Axes.'))
            ax = fig.gca()
        current_ax = fig.gca()
        userax = False
        if (use_gridspec
                and isinstance(ax, mpl.axes._base._AxesBase)
                and ax.get_subplotspec()):
            cax, kwargs = cbar.make_axes_gridspec(ax, **kwargs)
        else:
            cax, kwargs = cbar.make_axes(ax, **kwargs)
        cax.grid(visible=False, which='both', axis='both')
    else:
        userax = True

    # Need to remove keyword arguments that cannot be passed to HistColorbar
    NON_HISTCOLORBAR_KEYS = ['fraction', 'pad', 'shrink', 'aspect', 'anchor',
                         'panchor']
    hcb_kw = {k: v for k, v in kwargs.items() if k not in NON_HISTCOLORBAR_KEYS}

    hcb = HistColorbar(cax, mappable, **hcb_kw)

    if not userax:
        fig.sca(current_ax)
    fig.stale = True
    return hcb, cax


class HistColorbar(Colorbar):
    """
    A subclass of matplotlib's `Colorbar` that shows a histogram of the color values.

    Parameters
    ----------
    ax : `matplotlib.axes.Axes`
        The axes object in which the colorbar is drawn.
    mappable : `matplotlib.cm.ScalarMappable`
        The mappable object which the colorbar applies its colormap to.
    bins : int or sequence of scalars or str, optional
        If bins is an int, it defines the number of equal-width bins in the
        given range (10, by default). If bins is a sequence, it defines the
        bin edges, including the rightmost edge, allowing for non-uniform bin
        widths. If bins is a string, it defines the method used to calculate
        the optimal bin width, as defined by `numpy.histogram_bin_edges`.
        The default value of 'auto' uses the same bins as `numpy.histogram`.
    separate_hist : bool, optional
        If True, the HistColorbar will consist of a histogram and a colorbar stacked on
        top of each other. If False, only the histogram will be shown.
    hist_fraction : float, optional
        The fraction of the HistColorbar that will be taken up by the histogram. This is
        only used if separate_hist is True. The default value is 0.5.
    hist_color : str or tuple, optional
        The color of the histogram. The default value is None, which will color the
        histogram using the colors of the colormap. If separate_hist is False, this
        parameter is ignored.
    alpha : float, optional
        The alpha value of the histogram. The default value is None, which will use the
        alpha value of the colormap.
    """
    def __init__(self, ax, mappable, *,
                 bins='auto',
                 separate_hist=False,
                 hist_fraction=0.5,
                 hist_color=None,
                 alpha=None,
                 orientation=None,
                 ticklocation='auto',
                 spacing='uniform',
                 ticks=None,
                 format=None,
                 drawedges=False,
                 filled=True,
                 label='',
                 location=None,
                 ):
        # Calculate a histogram of the values in the mappable.
        # As there may be nan's in the mappable, we need to exclude them when
        # calculating the histogram.
        data = mappable.get_array()
        self._hist, self._bin_edges = np.histogram(data[np.isfinite(data)], bins=bins)

        # By default, a colorbar is oriented vertically in matplotlib.
        # A default matpotlib colorbar (which is drawn using a pcolormesh) has a
        # width of 1, as there is no need to pixelate the colorbar in the horizontal
        # direction in a standard colorbar. However, we aim to effectively pixelate
        # the colorbar (in the horizontal direction), in order to draw a more complex
        # shape (the histogram). Therefore, we need to decide on a width for the
        # new pcolormesh.
        if not separate_hist:
            # If the HistColorbar consists of only the histogram, the histogram will
            # completely fill the HistColorbar, so the width of the colorbar is the
            # maximum histogram count (the 'height' (i.e. width) of the largest bar
            # of the histogram bar chart).
            hist_width = np.max(self._hist)
            cb_width = 0
        else:
            # If the HistColorbar consists of both the histogram and a simple colorbar,
            # the width of the HistColorbar will depend on the fraction of the
            # HistColorbar taken up by the histogram, compared to the simple colorbar.
            hist_width = np.max(self._hist)
            cb_width = math.ceil((hist_width / hist_fraction) - hist_width)
        self._hist_width = hist_width
        self._cb_width = cb_width
        self._max_width = cb_width + hist_width

        self._hist_color = hist_color

        # Set the values to be the center of the bins
        values = (self._bin_edges[:-1] + self._bin_edges[1:]) / 2

        # To save on duplication of code, we now call the Colorbar constructor.
        # If we want to inject any more changes in the construction, we need to do so
        # in functions called by the Colorbar constructor. In particular,
        # _draw_all().
        Colorbar.__init__(self, ax, mappable, alpha=alpha, values=values,
                          orientation=orientation, ticklocation=ticklocation,
                          spacing=spacing, ticks=ticks, format=format,
                          drawedges=drawedges, filled=filled, label=label,
                          location=location)

    def _draw_all(self):
        """
        Calculate any free parameters based on the current cmap and norm,
        and do all the drawing.
        """
        if self.orientation == 'vertical':
            if mpl.rcParams['ytick.minor.visible']:
                self.minorticks_on()
        else:
            if mpl.rcParams['xtick.minor.visible']:
                self.minorticks_on()
        self._long_axis().set(label_position=self.ticklocation,
                              ticks_position=self.ticklocation)
        self._short_axis().set_ticks([])
        self._short_axis().set_ticks([], minor=True)

        # If we want the histogram part of the histcolorbar to be a solid color,
        # rather than having the colors of the colorbar, we need to pass that color
        # to the pcolormesh somehow, even if the color is not part of the colormap
        # used by pcolormesh.
        # When a masked array is used for the mesh data passed to the
        # pcolormesh, the masked values are drawn using the Bad color of the colormap.
        # A matplotlib colorbar has three special colors: Over, Under, and Bad
        # (see https://matplotlib.org/stable/tutorials/colors/colorbar_only.html).
        # A colorbar may be used to show Over and Under values, using triangular
        # extensions at the top and bottom of the colorbar. As we may want to implement
        # extension handling for the HistColorbar, we don't mess with the Over and
        # Under colors. However, a colorbar does not usually show Bad values (these are
        # usually labelled in a legend of some sort, or just explained in the caption
        # of the figure, see
        # https://stackoverflow.com/questions/61210808/python-matplotlib-how-to-add-bad-color-to-the-legend
        # for an example). Therefore, we are free to mess with the Bad color of the
        # colormap. We therefore set the colormap's Bad to the hist_color, and then
        # replace the histogram values with nans.
        # We need to make a copy of the colormap, as we don't want to change the
        # colormap used in rendering the underlying mappable, only the HistColorbar.
        self.cmap = copy.deepcopy(self.cmap)
        if self._hist_color is not None:
            hist_alpha = self.alpha if self.alpha is not None else 1
            self.cmap.set_bad(color=self._hist_color, alpha=hist_alpha)

        # Set self._boundaries and self._values, including extensions.
        # self._boundaries are the edges of each square of color, and
        # self._values are the value to map into the norm to get the
        # color:
        self._process_values()
        # Set self.vmin and self.vmax to first and last boundary, excluding
        # extensions:
        self.vmin, self.vmax = self._boundaries[self._inside][[0, -1]]
        # Compute the X/Y mesh.
        X, Y = self._mesh()
        # draw the extend triangles, and shrink the inner axes to accommodate.
        # also adds the outline path to self.outline spine:
        self._do_extends()
        lower, upper = self.vmin, self.vmax
        if self._long_axis().get_inverted():
            # If the axis is inverted, we need to swap the vmin/vmax
            lower, upper = upper, lower
        if self.orientation == 'vertical':
            self.ax.set_xlim(0, self._max_width)
            self.ax.set_ylim(lower, upper)
        else:
            self.ax.set_ylim(0, self._max_width)
            self.ax.set_xlim(lower, upper)

        # set up the tick locators and formatters.  A bit complicated because
        # boundary norms + uniform spacing requires a manual locator.
        self.update_ticks()

        if self._filled:
            ind = np.arange(len(self._values))
            if self._extend_lower():
                ind = ind[1:]
            if self._extend_upper():
                ind = ind[:-1]

            # If the user has specified a color for the histogram, we use the Bad
            # color of the colormap for the histogram tiles. Those tiles therefore
            # need to be filled with nans.
            if self._hist_color is None:
                hist_values = self._values[ind]
            else:
                hist_values = np.full(self._values[ind].shape, np.nan)

            # Set up the histogram tiles
            C_hist = np.tile(hist_values, (np.max(self._hist), 1))
            C_hist = np.swapaxes(C_hist, 0, 1)

            # Set up the colorbar tiles
            C_cb = np.tile(self._values[ind], (self._cb_width, 1))
            C_cb = np.swapaxes(C_cb, 0, 1)

            # Combine the tiles
            C = np.concatenate((C_cb, C_hist), axis=1)

            # The alpha of tiles outside the histcolorbar needs to be set to zero.
            # Begin by masking those tiles
            hist_mask = np.arange(np.max(self._hist)) >= self._hist[:, np.newaxis]
            mask = np.concatenate((np.full(C_cb.shape, False), hist_mask), axis=1)
            if self.alpha is not None:
                alpha_array = np.ones(C.shape)*self.alpha
            else:
                alpha_array = np.ones(C.shape)
            alpha_array[mask] = 0
            self.alpha = alpha_array
            # C = np.ma.array(C, mask=~mask)

            self._add_solids(X, Y, C)

    def _mesh(self):
        """
        Return the coordinate arrays for the colorbar pcolormesh/patches.

        These are scaled between vmin and vmax, and already handle colorbar
        orientation.
        """
        y, _ = self._proportional_y()
        # Use the vmin and vmax of the colorbar, which may not be the same
        # as the norm. There are situations where the colormap has a
        # narrower range than the colorbar and we want to accommodate the
        # extra contours.
        if (isinstance(self.norm, (colors.BoundaryNorm, colors.NoNorm))
                or self.boundaries is not None):
            # not using a norm.
            y = y * (self.vmax - self.vmin) + self.vmin
        else:
            # Update the norm values in a context manager as it is only
            # a temporary change and we don't want to propagate any signals
            # attached to the norm (callbacks.blocked).
            with self.norm.callbacks.blocked(), \
                    cbook._setattr_cm(self.norm,
                                      vmin=self.vmin,
                                      vmax=self.vmax):
                y = self.norm.inverse(y)
        self._y = y

        # Number of histogram counts
        width = self._hist_width + self._cb_width
        x = np.arange(0, width + 1, 1)

        X, Y = np.meshgrid(x, y)
        if self.orientation == 'vertical':
            return (X, Y)
        else:
            return (Y, X)
