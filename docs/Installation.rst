Installing h5preserve
=====================

h5preserve is distributed via PyPI_, and behaves like a normal python package; you can install it with pip by running::

    pip install h5preserve

Further information about how to use pip to install Python packages can be found
at https://packaging.python.org/tutorials/installing-packages/.

Note that h5preserve uses h5py, which may require a C compiler and the hdf5 library to install.  On common systems (Windows, MacOS, most Linux), there are pre-built wheels for h5py, which will automatically be installed when installing h5preserve if they are available. Other systems should see the [h5py installation instructions](http://docs.h5py.org/en/latest/build.html) for more information about how to install h5py.

If you have any problems installing h5preserve, please file a issue at https://github.com/h5preserve/h5preserve/issues.

.. _PyPI: https://pypi.org/project/h5preserve/
