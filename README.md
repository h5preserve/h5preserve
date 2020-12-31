[![Documentation Status](https://readthedocs.org/projects/h5preserve/badge/?version=latest)](https://h5preserve.readthedocs.org/en/latest/?badge=latest)
[![Build Status](https://dev.azure.com/jamestocknell/h5preserve/_apis/build/status/h5preserve.h5preserve?branchName=master)](https://dev.azure.com/jamestocknell/h5preserve/_build/latest?definitionId=4&branchName=master)
[![Coverage Status](https://codecov.io/github/h5preserve/h5preserve/coverage.svg?branch=master)](https://codecov.io/github/h5preserve/h5preserve?branch=master)
[![Version](https://img.shields.io/pypi/v/h5preserve.svg)](https://pypi.python.org/pypi/h5preserve/)
[![License](https://img.shields.io/pypi/l/h5preserve.svg)](https://pypi.python.org/pypi/h5preserve/)
[![Wheel](https://img.shields.io/pypi/wheel/h5preserve.svg)](https://pypi.python.org/pypi/h5preserve/)
[![Format](https://img.shields.io/pypi/format/h5preserve.svg)](https://pypi.python.org/pypi/h5preserve/)
[![Supported versions](https://img.shields.io/pypi/pyversions/h5preserve.svg)](https://pypi.python.org/pypi/h5preserve/)
[![Supported implemntations](https://img.shields.io/pypi/implementation/h5preserve.svg)](https://pypi.python.org/pypi/h5preserve/)
[![PyPI](https://img.shields.io/pypi/status/h5preserve.svg)](https://pypi.python.org/pypi/h5preserve/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.593007.svg)](https://doi.org/10.5281/zenodo.593007)
[![Paper](http://joss.theoj.org/papers/10.21105/joss.00581/status.svg)](https://doi.org/10.21105/joss.00581)

h5preserve is a thin wrapper around [h5py](http://www.h5py.org/), inspired by
[camel](http://eev.ee/blog/2015/10/15/dont-use-pickle-use-camel/).

Bug reports and suggestions should be filed at
[https://github.com/h5preserve/h5preserve/issues](https://github.com/h5preserve/h5preserve/issues).

# Installing h5preserve
h5preserve is distributed via [PyPI](https://pypi.org/project/h5preserve/), and
can be [installed via pip](https://packaging.python.org/tutorials/installing-packages/) with:
```
pip install h5preserve
```

Note that h5preserve uses h5py, which may require a C compiler and the hdf5 library to install. See the
[h5py installation instructions](http://docs.h5py.org/en/latest/build.html) for more information about
how to install h5py.

To install a development version of h5preserve, clone this repository and use:
```
pip install -e .
```
