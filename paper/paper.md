---
title: 'h5preserve: Thin wrapper around h5py, inspired by camel'
tags:
  - hdf5
authors:
 - name: James Tocknell
   orcid: 0000-0001-6637-6922
   affiliation: 1
affiliations:
 - name: Macquarie University, Sydney, Australia
   index: 1
date: 13 July 2017
bibliography: paper.bib
---

# Introduction
[h5preserve](https://h5preserve.readthedocs.io) is a wrapper around
[h5py](http://www.h5py.org/) [@collette_python_2013] and
[hdf5](https://www.hdfgroup.org/HDF5/) [@the_hdf_group_hierarchical_1997],
providing easier reading and writing of native and user-created python types to
hdf5 files, transparently dealing with multiple versions of the data. The two
python libraries most similar to h5preserve are
[pickle](https://docs.python.org/3/library/pickle.html) and
[Camel](https://camel.readthedocs.io/) [@eevee_lexy_munroe_camel].


# Origin of h5preserve
h5preserve was created by the author after two previous attempts to write libraries
which would allow easy addition of new and changed data structures produced by some
modelling and visualisation code he wrote for his thesis (both of which failed
due to evolving complexity). Inspired by
[Camel](https://camel.readthedocs.io/) [@eevee_lexy_munroe_camel],
h5preserve focuses on providing an simple interface to read and write different
and evolving versions of data structures produced by the modelling and analysis
of in-memory datasets.

# Why use h5preserve
The security flaws in pickle are well known (these are explicitly called out at the very
top of the [pickle](https://docs.python.org/3/library/pickle.html)
documentation in a big red warning) and design flaws in pickle have been brought up in
both PyCon talks [@alex_gaynor_pickles_2014] and blog posts [@lexy_munroe_dont_2015]
by well known members of the Python community, which inspired the creation of
[Camel](https://camel.readthedocs.io/) [@eevee_lexy_munroe_camel]. camel uses
YAML as the output format, which is ideal for textual data, but not for
numerical data or multidimensional arrays. h5preserve takes the design elements
of camel, and ports them to hdf5, making it easy to use the design philosophy
of camel, with the multidimensional array support of hdf5.

Being built on hdf5, and with scientific and numerical use in mind,
h5preserve has support for complex numerical data and multidimensional
arrays via numpy [@van_der_walt_numpy_2011],
which other serialisation formats (e.g. CSV, JSON or YAML)
may not represent as effectively. h5preserve makes it easy to split out the
interaction with hdf5 files from the main logic of your code, allowing for the
creation of data classes via libraries such as
[namedtuples](https://docs.python.org/3/library/collections.html#collections.namedtuple)
without the need to reimplement or modify existing libraries.

# Why not to use h5preserve
As h5preserve is designed to hide the underlying hdf5 file, large files where memory usage is a concern do not work well with h5preserve. In this case, h5preserve provides easy access to the underlying h5py objects, or you may want to look at using [pytables](http://www.pytables.org/) [@pytables], which provides a more database-like interface to hdf5 files.

# References
  
