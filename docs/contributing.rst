.. mpl-histcolorbar contributing

Contributing
=============

Contributions are always welcome! If you have any questions, comments, or
suggestions, please feel free to open an issue or pull request on `GitHub <https://github.com/jnahlers/mpl-histcolorbar>`_. This page
is intended to explain the rationale behind the design of the package, and to provide
some guidance for contributors.

Design
------
mpl-histcolorbar provides a drop-in replacement for matplotlib's colorbar that
displays a histogram of the data used to generate the colorbar.

Testing
-------
Testing is done using `pytest`. To run the tests, simply run `pytest` from the
root directory of the repository.

Documentation
-------------
Documentation is built using `sphinx`. To build the documentation, run
:code:`make html` from the `docs` directory. The documentation is built in the
`docs/_build/html` directory.

Packaging
---------
The package is built using PyPA's
`build <https://packaging.python.org/en/latest/key_projects/#build>`_. To build the
package, run :code:`python -m build` from the root directory of the repository. The
package is built in the `dist` directory.

Versioning
----------
This project uses `semantic versioning`. For the versions available, see the
`tags on this repository`.
