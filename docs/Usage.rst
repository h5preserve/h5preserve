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

So a complete example based on the :ref:`quickstart` example is:

.. testcode::

    import numpy as np
    from h5preserve import (
        open as h5open, Registry, new_registry_list, DatasetContainer
    )

    registry = Registry("experiment")

    class Experiment:
        def __init__(self, data, time_started):
            self.data = data
            self.time_started = time_started

    @registry.dumper(Experiment, "Experiment", version=1)
    def _exp_dump(experiment):
        return DatasetContainer(
            data=experiment.data,
            attrs={
                "time started": experiment.time_started
            }
        )

    @registry.loader("Experiment", version=1)
    def _exp_load(dataset):
        return Experiment(
            data=dataset["data"],
            time_started=dataset["attrs"]["time started"]
        )

    my_cool_experiment = Experiment(np.array([1,2,3,4,5]), 10)

    with h5open("my_data_file.hdf5", new_registry_list(registry), mode='w') as f:
        f["cool experiment"] = my_cool_experiment

    with h5open("my_data_file.hdf5", new_registry_list(registry), mode='r') as f:
        my_cool_experiment_loaded = f["cool experiment"]

    print(
        my_cool_experiment_loaded.time_started ==
        my_cool_experiment.time_started
    )

.. testoutput::
    :hide:

    True

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

A versioning example
....................
Imagine a class like :py:class:`Experiment` above; you have some data, and some
metadata (to keep the example simple, we're only going to have one piece of
metadata, and no data):

.. code-block:: python

    class ModelOutput:
        def __init__(self, a):
            self.a = a

:py:obj:`a` represents some input parameter to our model. We also write the
associated dumper and loader:

.. invisible-code-block: python

    import numpy as np
    from h5preserve import (
        open as h5open, Registry, new_registry_list, DatasetContainer
    )

    registry = Registry("experiment")

.. code-block:: python

    @registry.dumper(ModelOutput, "ModelOutput", version=1)
    def _exp_dump(modeloutput):
        return DatasetContainer(
            attrs={
                "a": modeloutput.a
            }
        )

    @registry.loader("ModelOutput", version=1)
    def _exp_load(dataset):
        return ModelOutput(
            a=dataset["attrs"]["a"]
        )

However, later on we realise we should have used :py:obj:`b` instead of
:py:obj:`a`. This could be because we want to radians instead of degrees,
using :py:obj:`b` is more meaningful in the model, or some other reason we
have, something which motivates a change to the class. We change our class:

.. code-block:: python

    class ModelOutput:
        def __init__(self, b):
            self.b = b

and create a new dumper and loader for version 2 of this class:

.. code-block:: python

    @registry.dumper(ModelOutput, "ModelOutput", version=2)
    def _exp_dump(modeloutput):
        return DatasetContainer(
            attrs={
                "b": modeloutput.b
            }
        )

    @registry.loader("ModelOutput", version=2)
    def _exp_load(dataset):
        return ModelOutput(
            b=dataset["attrs"]["b"]
        )

But then, how do we load our old data? Let's assume that :math:`b = 2 a`. So
we'd write a loader for version 1 which converts :py:obj:`a` to :py:obj:`b`:

.. code-block:: python

    @registry.loader("ModelOutput", version=1)
    def _exp_load(dataset):
        return ModelOutput(
            b = 2 * dataset["attrs"]["a"]
        )

What about a dumper? We can write one also, but it may be that we add additional
metadata instead of changing its representation, so we can't store all our
metadata in the version 1 format, so we can't write a dumper for version 1.

One thing :py:mod:`h5preserve` cannot do is check that your code is forward or
backwards compatible between different versions, that has to be managed by the
user (there's some code on providing some tools to help with automated testing
of loaders and dumpers being written, but that will still require having
something to test against).


Locking Dumper Version
......................
It is possible to force which dumper version is going to used, via
:py:meth:`RegistryContainer.lock_version`. An example how to do this, given :py:class:`Experiment`
is a class you want to dump version 1 of, and :py:obj:`registries` is a instance of
:py:class:`~h5preserve.RegistryContainer` which contains a :py:class:`~h5preserve.Registry` that can dump :py:class:`Experiment` is:

.. invisible-code-block: python

    class Experiment:
        def __init__(self, data, time_started):
            self.data = data
            self.time_started = time_started

.. code-block:: python

    registries = new_registry_list(registry)

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

Using :py:class:`~h5preserve.DatasetContainer` and :py:class:`~h5preserve.GroupContainer`
.........................................................................................
The :ref:`quickstart` example above used :py:class:`~h5preserve.DatasetContainer`;
:py:class:`~h5preserve.DatasetContainer` takes keyword arguments which are passed on to
:py:func:`h5py.Group.create_dataset`, as well as an :py:obj:`attrs` keyword
argument which is used to set attributes on the associated HDF5 dataset.

:py:class:`~h5preserve.GroupContainer` behaves similar to
:py:class:`~h5preserve.DatasetContainer`; it
also takes keyword arguments, as well as an additional :py:obj:`attrs` keyword
argument. However, these keywords names are used as the name for the subgroup or
dataset created from the keyword arguments. Modifying the :ref:`quickstart`
example to have it use a group instead of a dataset is simple, we just change
the loader as shown below:

.. code-block:: python

    @registry.dumper(Experiment, "Experiment", version=1)
    def _exp_dump(experiment):
        return GroupContainer(
            experiment_data=experiment.data,
            attrs={
                "time started": experiment.time_started
            }
        )

The start time is now written to an attribute on the HDF5 group, and
:py:obj:`experiment.data` is written to either a dataset or group, depending on
what type it is. If it was as above a numpy array, then it would be written as a
dataset (but it would not have :py:obj:`"time started"` as an attribute).
Loading from a group is the same as loading from a dataset:

.. code-block:: python

    @registry.loader("Experiment", version=1)
    def _exp_load(group):
        return Experiment(
            data=group["experiment_data"],
            time_started=group["attrs"]["time started"]
        )

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
:py:class:`collections.abc.MutableMapping` and which stores its members in :py:attr:`_mapping` is:

.. code-block:: python

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
to be dumped later, the following is sufficient:

.. code-block:: python

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
      - Included by default
    * - :py:obj:`None`
      - :py:class:`h5py.Empty`
      - True
    * - :py:obj:`int`
      - a dataset
      - True
    * - :py:obj:`float`
      - a dataset
      - True
    * - :py:obj:`bool`
      - a dataset
      - True
    * - :py:obj:`bytes` (py2 :py:obj:`str`)
      - a dataset
      - True
    * - :py:obj:`unicode` (py3 :py:obj:`str`)
      - a dataset
      - True
    * - :py:obj:`tuple`
      - a dataset
      - True
    * - :py:obj:`list`
      - a dataset
      - True

Manually Creating the Registry Container
........................................
To create the Registry Container manually, replace all calls to
:py:func:`~h5preserve.new_registry_list` with :py:class:`~h5preserve.RegistryContainer`.
This will allow you to select which built-in registries (if any) you which to
use. For example, if you only want to convert :py:obj:`None` to
:py:class:`h5py.Empty`, you would do:

.. code-block:: python

    from h5preserve import Registry, RegistryContainer
    from h5preserve.additional_registries import none_python_registry

    registry = Registry("my cool registry")

    registries = RegistryContainer(registry, none_python_registry)

You could then pass :py:obj:`registries` to :py:obj:`h5preserve.open`, or lock
to a specific version, or anything else you'd do after calling
:py:func:`~h5preserve.new_registry_list`.
