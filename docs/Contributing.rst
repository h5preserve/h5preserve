.. _contributing:

Contributing to h5preserve
##########################
We welcome contributions to h5preserve, subject to our
`code of conduct <https://github.com/h5preserve/h5preserve/blob/master/code_of_conduct.md>`_
whether it is improvements to the documentation or examples, bug reports or code
improvements.

Reporting Bugs
--------------
Bugs should be reported to https://github.org/h5preserve/h5preserve. Please
include what version of Python this occurs on, as well as which operating
system. Information about your h5py and HDF5 configuration is also helpful.

Patches and Pull Requests
-------------------------
The main repository is https://github.org/h5preserve/h5preserve, please make pull
requests against that repository, and the branch that pull requests should be
made on is master (backporting fixes will be done separately if necessary).

Running the tests
-----------------
h5preserve uses tox_ to run its tests. See https://tox.readthedocs.io/en/latest/
for more information about tox, but the simplest method is to run::

    tox

in the top level of the git repository.

.. _tox: https://tox.readthedocs.io/en/latest/
