import matplotlib as mpl
import matplotlib.colorbar as cbar
from matplotlib.colorbar import Colorbar
from matplotlib import _api, cbook, colors

import numpy as np


def _calculate_histogram(mappable, bins='auto'):
    hist, bin_edges = np.histogram(mappable.get_array(), bins=bins)
    return hist, bin_edges


class HistColorbar(Colorbar):
    """
    An extension of the matplotlib colorbar that shows a histogram of the color values.
    """
    def __init__(self, ax, mappable, *,
                 alpha=None,
                 values=None,
                 boundaries=None,
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
        self._hist, self._bin_edges = _calculate_histogram(mappable)

        # Adjust to allow one to qualitatively see all histogram bins, even when 0
        self._hist = self._hist + np.max(self._hist)

        self._max = np.max(self._hist)

        # Set the values to be the center of the bins
        values = (self._bin_edges[:-1] + self._bin_edges[1:]) / 2

        Colorbar.__init__(self, ax, mappable, alpha=alpha,
                          values=values, boundaries=boundaries,
                          orientation=orientation, ticklocation=ticklocation, spacing=spacing, ticks=ticks,
                          format=format, drawedges=drawedges, filled=filled, label=label, location=location)

    def _draw_all(self):
        """docstring for _draw_all"""
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
            C = np.tile(self._values[ind], (np.max(self._hist), 1))
            C = np.swapaxes(C, 0, 1)

            # Mask the tiles that are outside the histogram
            mask = np.arange(np.max(self._hist)) < self._hist[:, np.newaxis]
            C = np.ma.array(C, mask=~mask)

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
        x = np.arange(0, np.max(self._hist) + 1, 1)

        X, Y = np.meshgrid(x, y)
        if self.orientation == 'vertical':
            return (X, Y)
        else:
            return (Y, X)
