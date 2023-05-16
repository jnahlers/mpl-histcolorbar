<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/jnahlers/mpl-histcolorbar/blob/main/docs/_static/logo.png?raw=true">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/jnahlers/mpl-histcolorbar/blob/main/docs/_static/logo.png?raw=true">
  <img alt="mpl-histcolorbar logo" src="https://github.com/jnahlers/mpl-histcolorbar/blob/main/docs/_static/logo.png?raw=true">
</picture>

<p align="center"><img width=90% src="https://github.com/jnahlers/mpl-histcolorbar/blob/main/docs/_static/logo.png"></p>


# mpl-histcolorbar
[![PyPI version](https://badge.fury.io/py/mpl-histcolorbar.svg)](https://badge.fury.io/py/mpl-histcolorbar)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/mpl-histcolorbar.svg)](https://anaconda.org/conda-forge/mpl-histcolorbar)
[![Coverage Status](https://coveralls.io/repos/github/keflavich/mpl-histcolorbar/badge.svg?branch=master)](https://coveralls.io/github/keflavich/mpl-histcolorbar?branch=master)
[![Documentation Status](https://readthedocs.org/projects/mpl-histcolorbar/badge/?version=latest)](https://mpl-histcolorbar.readthedocs.io/en/latest/?badge=latest)

A drop-in replacement for matplotlib's colorbar that shows the frequency of each color in the mappable.

## Getting started

mpl-histcolorbar is available as [`mpl-histcolorbar`](https://pypi.org/project/mpl-histcolorbar/) on PyPI:

```bash
pip install mpl-histcolorbar
```

or [`mpl-histcolorbar`](https://anaconda.org/conda-forge/mpl-histcolorbar) on conda-forge:

```bash
conda install -c conda-forge mpl-histcolorbar
```

## Usage

```python
import numpy as np
import matplotlib.pyplot as plt
from mpl-histcolorbar import histcolorbar

im = np.random.normal(size=(100, 100))
fig, ax = plt.subplots()
ax.imshow(im)
hcb = histcolorbar(fig, ax, im)
```

Documentation is available at [mpl-histcolorbar.readthedocs.io](https://mpl-histcolorbar.readthedocs.io/en/latest/).


## License
Original code is licensed under the [MIT license](https://opensource.org/licenses/MIT). This project directly derives 
from [matplotlib](https://matplotlib.org/), and any use of this project is subject to
the [matplotlib license agreement](https://matplotlib.org/stable/users/project/license.html).  
