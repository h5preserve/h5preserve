---
title: 'h5preserve: Thin wrapper around h5py, inspired by camel'
tags:
  - hdf5
authors:
 - name: James Tocknell
   orcid: 0000-0001-6637-6922
   affiliation: 1
affiliations:
 - name: Macquarie University
   index: 1
date: 13 July 2017
bibliography: paper.bib
---

# Summary
[h5preserve](https://h5preserve.readthedocs.io) is a wrapper around [h5py](http://www.h5py.org/) [@h5pybook] and [hdf5](https://www.hdfgroup.org/HDF5/) [@hdf5], providing easier serialisation of native python types. Its design is inspired by [Camel](https://camel.readthedocs.io/), and follows its [philosophy](https://camel.readthedocs.io/en/latest/camel.html#camel-s-philosophy).

The purpose of h5preserve is to provide a simple serialisation library to hdf5 files. Hence h5preserve has support for complex numerical data, multidimensional arrays etc., which other serialisation formats may not represent as effectively. h5preserve makes it easy to split out the interaction with hdf5 files from the main logic of your code. Since h5preserve is designed to hide the underlying hdf5 file, large files where memory usage is a concern do not work well with h5preserve. In this case, h5preserve provides easy access to the underlying h5py objects, or you may want to look at using [pytables](http://www.pytables.org/) [@pytables], which provides a more database-like interface to hdf5 files.

# References
  
