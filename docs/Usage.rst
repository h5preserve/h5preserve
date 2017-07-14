.. _usage:

Usage
=====
To understand how h5preserve works, you need to remember the following
concepts:

dumper
    A function which converts your object to a representation ready to be
    written to an HDF5 file. Has an associated class, version and class label.

loader
    A function which converts a representation of a HDF5 object (group, dataset
    etc.) to an instance of a specified class. Has an associated version and class label.

registry
    A collection of dumpers and loaders, providing a common namespace.
    h5preserve comes with a few which convert common Python types.

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

Whilst for this simple case it's probably overkill to use h5preserve, h5preserve deals
quite easily changing requirements, such as adding additional properties to
`Experiment` via versioning, splitting `Experiment` into multiple classes via
recursively converting python objects, or even more complex requirements via
being able to only read and convert when needed, or to dump subsets of a class
before dumping the whole class.

The rest of this guide provides information about how to deal with specific
topics (versioning, advanced loading and dumping), but these topics are not
required to use h5preserve.

How Versioning Works
--------------------
Valid versions for dumpers are either integers or `None`.
Valid versions for loaders are integers, `None`, `any` or `all`.
The order in which loaders are used are:

    1. `None` if available
    2. `all` if available
    3. The version which is stored in the file (if available)
    4. `any` if available

Dumpers are similar:

    1. If a version of a dumper is locked, use that one
    2. `None` if available
    3. The latest version of the dumper available

Using `None` should not be done lightly, as it forces that the dumper and loader
not change in any way, as there is no way of overriding which loader h5preserve
uses when `None` is available. It may be better to have a dumper with an integer
version and use a loader with a version of `all`, which can be modified at the
python level, and not require modification of the existing file.

Locking Dumper Version
......................

Controlling how Classes are Dumped
----------------------------------

Using On-Demand Loading
-----------------------

Using Delayed Dumping
---------------------

Built-in Loaders, Dumpers and Registries
----------------------------------------
