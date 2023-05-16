import math

import matplotlib as mpl
import matplotlib.colorbar as cbar
from matplotlib.colorbar import Colorbar
from matplotlib import _api, cbook, colors

import numpy as np


def histcolorbar(
        fig, mappable, cax=None, ax=None, use_gridspec=True, **kwargs):

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

    # need to remove kws that cannot be passed to Colorbar
    NON_HISTCOLORBAR_KEYS = ['fraction', 'pad', 'shrink', 'aspect', 'anchor',
                         'panchor']
    hcb_kw = {k: v for k, v in kwargs.items() if k not in NON_HISTCOLORBAR_KEYS}

    hcb = HistColorbar(cax, mappable, **hcb_kw)

    if not userax:
        fig.sca(current_ax)
    fig.stale = True
    return hcb, cax


def _calculate_histogram(mappable, bins='auto'):
    hist, bin_edges = np.histogram(mappable.get_array(), bins=bins)
    return hist, bin_edges


class HistColorbar(Colorbar):
    """
    An extension of the matplotlib colorbar that shows a histogram of the color values.
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

        # Calculate the histogram
        self._hist, self._bin_edges = _calculate_histogram(mappable, bins)

        # Calculate the width of the colorbar
        if separate_hist:
            hist_width = np.max(self._hist)
            cb_width = math.ceil(hist_width / hist_fraction) - 1
        else:
            hist_width = np.max(self._hist)
            cb_width = 0
        self._hist_width = hist_width
        self._cb_width = cb_width
        self._max = cb_width + hist_width

        self._hist_color = hist_color
        if hist_color is not None:
            # Get the cmap, and set its bad to the hist_color
            cmap = mappable.get_cmap()
            cmap.set_bad(hist_color)

        # Set the values to be the center of the bins
        values = (self._bin_edges[:-1] + self._bin_edges[1:]) / 2

        Colorbar.__init__(self, ax, mappable, alpha=alpha,
                          values=values,
                          orientation=orientation, ticklocation=ticklocation, spacing=spacing, ticks=ticks,
                          format=format, drawedges=drawedges, filled=filled, label=label, location=location)

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
            self.ax.set_xlim(0, self._max)
            self.ax.set_ylim(lower, upper)
        else:
            self.ax.set_ylim(0, self._max)
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

            # Set up the histogram tiles
            if self._hist_color is None:
                hist_values = self._values[ind]
            else:
                hist_values = np.full(self._values[ind].shape, np.nan)

            C_hist = np.tile(hist_values, (np.max(self._hist), 1))
            C_hist = np.swapaxes(C_hist, 0, 1)

            # Mask the tiles that are outside the histogram
            mask = np.arange(np.max(self._hist)) < self._hist[:, np.newaxis]
            C_hist = np.ma.array(C_hist, mask=~mask)

            # Set up the colorbar tiles
            C_cb = np.tile(self._values[ind], (self._cb_width, 1))
            C_cb = np.swapaxes(C_cb, 0, 1)

            # Combine the tiles
            C = np.ma.concatenate((C_cb, C_hist), axis=1)

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
