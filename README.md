<p align="center">
  <img alt="mpl-histcolorbar logo" width=60% src="https://github.com/jnahlers/mpl-histcolorbar/blob/main/docs/_static/logo.png">
</p>

# mpl-histcolorbar
[![PyPI version](https://badge.fury.io/py/mpl-histcolorbar.svg)](https://badge.fury.io/py/mpl-histcolorbar)
[![Coverage Status](https://coveralls.io/repos/github/keflavich/mpl-histcolorbar/badge.svg?branch=master)](https://coveralls.io/github/keflavich/mpl-histcolorbar?branch=master)
[![Documentation Status](https://readthedocs.org/projects/mpl-histcolorbar/badge/?version=latest)](https://mpl-histcolorbar.readthedocs.io/en/latest/?badge=latest)

A drop-in replacement for matplotlib's colorbar that shows the frequency of each color in the mappable.

## Getting started

mpl-histcolorbar is available as [`mpl_histcolorbar`](https://pypi.org/project/mpl_histcolorbar/) on PyPI:

```bash
pip install mpl_histcolorbar
```

## Usage

```python
import numpy as np
import matplotlib.pyplot as plt
from mpl_histcolorbar import histcolorbar

rng = np.random.default_rng(seed=42)
data = rng.standard_normal(size=(25, 100))
fig, ax = plt.subplots()
im = ax.imshow(data)
hcb = histcolorbar(fig, im, location="bottom")
```

![Example](https://github.com/jnahlers/mpl-histcolorbar/blob/main/docs/_static/readme_example.png)

Documentation is available at [mpl-histcolorbar.readthedocs.io](https://mpl-histcolorbar.readthedocs.io/en/latest/).


## License
Original code is licensed under the [MIT license](https://opensource.org/licenses/MIT). This project directly derives 
from [matplotlib](https://matplotlib.org/), and any use of this project is subject to
the [matplotlib license agreement](https://matplotlib.org/stable/users/project/license.html).  
