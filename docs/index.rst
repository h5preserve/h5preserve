Welcome to h5preserve's documentation!
======================================
:py:mod:`h5preserve` is a wrapper around h5py_ and hdf5_, providing easier serialisation
of native python types. Its design is inspired by Camel_, and follows its
philosophy_.

Why use h5preserve?
-------------------
The purpose of :py:mod:`h5preserve` is to provide a simple serialisation library to
hdf5_ files. Hence :py:mod:`h5preserve` has support for complex numerical data,
multidimensional arrays etc., which other serialisation formats may not
represent as effectively. :py:mod:`h5preserve` makes it easy to split out the
interaction with hdf5_ files from the main logic of your code. Since
:py:mod:`h5preserve` is designed to hide the underlying hdf5_ file, large files where
memory usage is a concern do not work well with :py:mod:`h5preserve`. In this case,
:py:mod:`h5preserve` provides easy access to the underlying h5py_ objects, or you may
want to look at using pytables_, which provides a more database-like interface
to hdf5_ files.


Why the name?
-------------
The name comes from the "h5" label associated with hdf5_, and the idea of
preserving or pickling data.


Citing h5preserve
-----------------
If you find h5preserve useful in your research, please cite the `JOSS paper`_,
as well as h5preserve's dependencies, h5py_, numpy_ and hdf5_. Further
information about citing h5preserve, including specific releases, can be found
at :ref:`citing`.


Contents:

.. toctree::
    :maxdepth: 2

    Quickstart
    Installation
    Usage
    Reference
    Contributing
    Citing



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _h5py: https://www.h5py.org/
.. _hdf5: https://support.hdfgroup.org/HDF5/
.. _Camel: https://eev.ee/release/2015/10/15/dont-use-pickle-use-camel/
.. _philosophy: https://camel.readthedocs.io/en/latest/camel.html#camel-s-philosophy
.. _pytables: https://www.pytables.org/
.. _`JOSS Paper`: https://joss.theoj.org/papers/10.21105/joss.00581/
.. _numpy: https://numpy.org/
