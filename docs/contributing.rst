.. mpl-histcolorbar contributing

Contributing
=============

Contributions are always welcome! If you have any questions, comments, or
suggestions, please feel free to open an issue or pull request on `GitHub <https://github.com/jnahlers/mpl-histcolorbar>`_. This page
is intended to explain the rationale behind the design of the package, and to provide
some guidance for contributors.

Design
------
mpl-histcolorbar is intended as a drop-in replacement for matplotlib's colorbar. As such, the API is
intended to be compatible with matplotlib's colorbar.

A matplotlib colorbar is drawn using `pcolormesh <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.pcolormesh.html>`_, which "creates a pseudocolor
plot with a non-regular rectangular grid." As a standard colorbar only varies in one
dimension, the pcolormesh is a 1xN grid, where N is the number of colors in the
colormap. The basis of the histcolorbar is to extend this to an MxN grid, where M is
(related to) the maximum of the histogram of the scalarmappable data used to generate
the colorbar.

A matplotlib colorbar is drawn using :code:`pcolormesh`, which "creates a pseudocolor
plot with a non-regular rectangular grid." As a standard colorbar only varies in one
dimension, the pcolormesh is a 1xN grid, where N is the number of colors in the
colormap. The basis of the histcolorbar is to extend this to an MxN grid, where M is
(related to) the maximum of the histogram of the scalarmappable data used to generate
the colorbar.

Testing
-------
Testing is done using `pytest <https://docs.pytest.org/>`_. To run the tests, simply
run :code:`pytest` from the root directory of the repository.

Documentation
-------------
Documentation is built using `sphinx <https://www.sphinx-doc.org/en/master/>`_. To build
the documentation, run :code:`make html` from the ``docs`` directory. The documentation
is built in the ``docs/_build/html`` directory.

Packaging
---------
The package is built using PyPA's
`build <https://packaging.python.org/en/latest/key_projects/#build>`_. To build the
package, run :code:`python -m build` from the root directory of the repository. The
package is built in the ``dist`` directory. Use
`twine <https://packaging.python.org/en/latest/key_projects/#twine>`_ to upload the
package to PyPI. To upload the package, run :code:`twine upload dist/*` from the root
directory of the repository.
