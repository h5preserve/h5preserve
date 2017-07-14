Usage
=====

Using On-Demand Loading
-----------------------

Using Delayed Dumping
---------------------

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

Built-in Loaders, Dumpers and Registries
----------------------------------------
