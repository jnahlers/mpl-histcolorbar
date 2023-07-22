import numpy as np
import matplotlib.pyplot as plt

from mpl_histcolorbar import histcolorbar


def test_nan_in_mappable():
    # Check that nan values in the mappable are ignored
    fig, ax = plt.subplots()
    array = np.arange(100, dtype=np.float32).reshape(10, 10)
    array[0, 0] = np.nan
    array[5, 5] = np.nan
    im = ax.imshow(array, cmap='viridis')
    histcolorbar(fig, im)


def test_inf_in_mappable():
    # Check that inf values in the mappable are ignored
    fig, ax = plt.subplots()
    array = np.arange(100, dtype=np.float32).reshape(10, 10)
    array[0, 0] = np.inf
    array[5, 5] = -np.inf
    im = ax.imshow(array, cmap='viridis')
    histcolorbar(fig, im)
