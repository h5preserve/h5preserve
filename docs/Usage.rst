.. _usage:

Usage
=====
To understand how :py:mod:`h5preserve` works, you need to remember the following
concepts:

dumper
    A function which converts your object to a representation ready to be
    written to an HDF5 file. Has an associated class, version and class label.

loader
    A function which converts a representation of a HDF5 object (group, dataset
    etc.) to an instance of a specified class. Has an associated version and class label.

registry
    A collection of dumpers and loaders, providing a common namespace.
    :py:mod:`h5preserve` comes with a few which convert common Python types.

registry collection
    A collection of registries. Deals with choosing the correct registry, dumper
    and loader to use, including version locking.

So a complete example based on the :ref:`quickstart` example is::

    import numpy as np
    from h5preserve import open as h5open, Registry, new_registry_list

    registry = Registry("experiment")

    class Experiment:
        def __init__(self, data, time_started):
            self.data = data
            self.time_started = time_started

    @registry.dumper(Experiment, "Experiment", version=1)
    def _exp_dump(experiment):
        return {
            "data": experiment.data,
            "attrs": {
                "time started": experiment.time_started
            }
        }

    @registry.loader("Experiment", version=1)
    def _exp_load(dataset):
        return Experiment(
            data=dataset["data"],
            time_started=dataset["attrs"]["time started"]
        )

    my_cool_experiment = Experiment(np.array([1,2,3,4,5]), 10)

    with open("my_data_file.hdf5", new_registry_list(registry)) as f:
        f["cool experiment"] = my_cool_experiment

    with open("my_data_file.hdf5", new_registry_list(registry)) as f:
        my_cool_experiment_loaded = f["cool experiment"]

    print(
        my_cool_experiment_loaded.time_started ==
        my_cool_experiment.time_started
    )

Whilst for this simple case it's probably overkill to use :py:mod:`h5preserve`, :py:mod:`h5preserve` deals
quite easily changing requirements, such as adding additional properties to
:py:class:`Experiment` via versioning, splitting :py:class:`Experiment` into multiple classes via
recursively converting python objects, or even more complex requirements via
being able to only read and convert when needed, or to dump subsets of a class
before dumping the whole class.

The rest of this guide provides information about how to deal with specific
topics (versioning, advanced loading and dumping), but these topics are not
required to use :py:mod:`h5preserve`.

How Versioning Works
--------------------
Valid versions for dumpers are either integers or :py:obj:`None`.
Valid versions for loaders are integers, :py:obj:`None`, :py:obj:`any` or :py:obj:`all`.
The order in which loaders are used are:

    1. :py:obj:`None` if available
    2. :py:obj:`all` if available
    3. The version which is stored in the file (if available)
    4. :py:obj:`any` if available

Dumpers are similar:

    1. If a version of a dumper is locked, use that one
    2. :py:obj:`None` if available
    3. The latest version of the dumper available

Using :py:obj:`None` should not be done lightly, as it forces that the dumper and loader
not change in any way, as there is no way of overriding which loader :py:mod:`h5preserve`
uses when :py:obj:`None` is available. It may be better to have a dumper with an integer
version and use a loader with a version of :py:obj:`all`, which can be modified at the
python level, and not require modification of the existing file.

Locking Dumper Version
......................
It is possible to force which dumper version is going to used, via
:py:meth:`RegistryContainer.lock_version`. An example how to do this, given :py:class:`Experiment`
is a class you want to dump version 1 of, and :py:obj:`registries` is a instance of
:py:class:`~h5preserve.RegistryContainer` which contains a :py:class:`~h5preserve.Registry` that can dump :py:class:`Experiment` is::

    registries.lock_version(Experiment, 1)

Controlling how Classes are Dumped
----------------------------------
:py:mod:`h5preserve` will recursively dump arguments passed to :py:class:`~h5preserve.GroupContainer` or
:py:class:`~h5preserve.DatasetContainer` (as well as any variations on those classes), as long as
the arguments are supported by :py:mod:`h5py` for writing (e.g. numpy arrays), or there
exists a dumper for each of the arguments. Hence, dumpers should only need to
worry about name which each attribute of the class is saved to, and whether they
should be saved as group/dataset attributes or as groups/datasets (currently
there is no support for loaders/dumpers that only write group/dataset attributes
without creating a new group/dataset).

Using On-Demand Loading
-----------------------
The purpose of on-demand loading is to deal with cases where recursively loading
a group takes up too much memory. On-demand loading requires modifications to
the class which contains the objects which are to be loaded on-demand. The
modifications are:

 * Wrapping attributes and other objects which should be loaded on-demand with
   the :py:func:`~h5preserve.wrap_on_demand` function when set, and unwrapping the objects when
   needed.
 * Adding :py:func:`cls._h5preserve_update` as a callback function to be called when the
   class is dumped. This callback must wrap any of the above objects which
   are to be loaded on-demand with :py:func:`~h5preserve.wrap_on_demand` as above.

:py:func:`~h5preserve.wrap_on_demand` returns an instance of :py:class:`~h5preserve.OnDemandWrapper`, which can be called
with no arguments to return the original object (similar to a weakref).

An example of the necessary code for class which subclasses
:py:class:`collections.abc.MutableMapping` and which stores its members in :py:attr:`_mapping` is::

    def __getitem__(self, key):
        value = self._mapping[key]
        if isinstance(value, OnDemandWrapper):
            value = value()
            self._mapping[key] = value # acting as cache, this can be skipped if desired
        return value

    def __setitem__(self, key, val):
        self._mapping[key] = wrap_on_demand(self, key, val)

    def _h5preserve_update(self):
        for key, val in self.items():
            self._mapping[key] = wrap_on_demand(self, key, val)

A workaround where a group/dataset takes up too much memory but on-demand
loading is not set up is to open the file via :py:mod:`h5py` or use the :py:attr:`~h5preserve.H5PreserveFile.h5py_file` or
:py:attr:`~h5preserve.H5PreserveGroup.h5py_group` attribute to access the underlying :py:class:`h5py.Group`. Using this group you
can then access a subset of the groups that would be loaded, which you can pass
to :py:class:`~h5preserve.H5PreserveGroup` to use your loaders.

Using Delayed Dumping
---------------------
Delayed dumping is similar to on-demand loading, however it needs less changes
to the containing class. Assigning an instance of :py:class:`~h5preserve.DelayedContainer` in the
necessary location in the class is sufficient in preparing :py:mod:`h5preserve` for
delayed dumping of the object. When the data is ready to be dumped, calling
:py:meth:`~h5preserve.DelayedContainer.write_container` dumps the data to the file as if it has been dumped when the
containing class had been dumped. In a class where it is an attribute which is
to be dumped later, the following is sufficient::

    class ContainerClass:
        def __init__(self, data=None):
            if data is None:
                data = DelayedContainer()
            self._data = data

        @property
        def data(self):
            return self._data

        @data.setter
        def data(self, data):
            if isinstance(self._data, DelayedContainer):
                self._data.write_container(soln)
                self._data = data
            else:
                raise RuntimeError("Cannot change data")

Built-in Loaders, Dumpers and Registries
----------------------------------------
:py:mod:`h5preserve` comes with a number of predefined loader/dumper pairs for built-in
python types. The defaults for :py:func:`~h5preserve.new_registry_list` automatically include these
registries. If you do not wish to use the predefined registries, you should
instead instantiate :py:class:`~h5preserve.RegistryContainer` manually.

The following table outlines the supported types, and how they are encoded in
the HDF5 file.

.. list-table::
    :header-rows: 1

    * - Type
      - Encoding
    * - :py:obj:`None`
      - :py:class:`h5py.Empty`
    * - :py:obj:`int`
      - a dataset
    * - :py:obj:`float`
      - a dataset
    * - :py:obj:`bool`
      - a dataset
    * - :py:obj:`bytes` (py2 :py:obj:`str`)
      - a dataset
    * - :py:obj:`unicode` (py3 :py:obj:`str`)
      - a dataset
    * - :py:obj:`tuple`
      - a dataset
    * - :py:obj:`list`
      - a dataset

