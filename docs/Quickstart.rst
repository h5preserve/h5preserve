.. _quickstart:

Quickstart
==========

Assume you have a class which represents some experiment you've run::

    class Experiment:
        def __init__(self, data, time_started):
            self.data = data
            self.time_started = time_started

where :py:obj:`data` is some numpy array containing the experimental data, and
:py:obj:`time_started` is a string containing time and data when the experiment was
started (we're using a string in this case, but it could be an :py:mod:`datetime`
object from the python standard library, or some other representation of time).

To save an instance of :py:class:`Experiment` to a group in a file, you could do::

    grp["MyExperiment"] = experiment.data
    grp["MyExperiment"].attrs["time started"] = experiment.time_started

and read it back with::

    experiment = Experiment(grp["MyExperiment"][:], grp["MyExperiment"].attrs["time started"])

which is fine but:

#. You could forget to slice/convert the dataset to a numpy array, and then try
   to use the dataset in a numerical expression. Also, if you are using a
   special subclass of numpy array, slicing will not return a instance of that
   class.
#. Similarly, hdf5 attributes can only represent certain types, and if you
   forget to convert back to the native python type...
#. Your experiment changes, and you need add or remove metadata, or your
   experiment becomes comprised of multiple datasets. You could keep track of
   versions, but it's another piece of metadata, and you will need to validate
   that the version in the file matches what is written.

This represents time spent coding up validation code, which has to be tested,
and so forth. For short scripts, this can become come to dominate the code.
Instead, using :py:mod:`h5preserve`, you can write a dump function, and a load
function, and let :py:mod:`h5preserve` deal with the rest. For the above example,
reading and writing become::

    grp["MyExperiment"] = experiment
    experiment = grp["MyExperiment"]

with our dump function being::

    @registry.dumper(Experiment, "Experiment", version=1)
    def _exp_dump(experiment):
        return {
            "data": experiment.data,
            "attrs": {
                "time started": experiment.time_started
            }
        }

and our load function being::

    @registry.loader("Experiment", version=1)
    def _exp_load(dataset):
        return Experiment(
            data=dataset["data"],
            time_started=dataset["attrs"]["time started"]
        )
