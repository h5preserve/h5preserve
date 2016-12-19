# coding: utf-8
"""
Additional registries for h5preserve
"""
import six

from numpy import asarray
import h5py

from . import Registry, DatasetContainer


def as_dataset_dumper(obj):
    # pylint: disable=missing-docstring
    return DatasetContainer(data=obj)


def as_dataset_loader(dataset):
    # pylint: disable=missing-docstring
    return dataset["data"]


none_python_registry = Registry("Python: None")
builtin_numbers_registry = Registry("Python: builtin numbers")
builtin_text_registry = Registry("Python: builtin text")
sequence_as_dataset_registry = Registry("Python: sequence as dataset")
bool_python_registry = Registry("Python: bool")

if hasattr(h5py, "Empty"):
    # pylint: disable=missing-docstring,unused-argument,no-member
    @none_python_registry.dumper(type(None), "None", version=None)
    def _none_dumper(none):
        return DatasetContainer(dtype=float)

    @none_python_registry.loader("None", version=None)
    def _none_loader(empty):
        return None

builtin_numbers_registry.dumper(int, "int", version=None)(as_dataset_dumper)
builtin_numbers_registry.loader("int", version=None)(as_dataset_loader)
builtin_numbers_registry.dumper(float, "float", version=None)(
    as_dataset_dumper
)
builtin_numbers_registry.loader("float", version=None)(as_dataset_loader)

bool_python_registry.dumper(bool, "bool", version=None)(as_dataset_dumper)
bool_python_registry.loader("bool", version=None)(as_dataset_loader)

if six.PY2:
    builtin_text_registry.dumper(str, "ascii", version=None)(
        as_dataset_dumper
    )
    builtin_text_registry.dumper(unicode, "text", version=None)(
        as_dataset_dumper
    )
else:
    builtin_text_registry.dumper(bytes, "ascii", version=None)(
        as_dataset_dumper
    )
    builtin_text_registry.dumper(str, "text", version=None)(
        as_dataset_dumper
    )
builtin_text_registry.loader("ascii", version=None)(as_dataset_loader)
builtin_text_registry.loader("text", version=None)(as_dataset_loader)


@sequence_as_dataset_registry.dumper(list, "list", version=None)
def _list_dumper(l):
    # pylint: disable=missing-docstring
    return DatasetContainer(data=asarray(l))


@sequence_as_dataset_registry.loader("list", version=None)
def _list_loader(dataset):
    # pylint: disable=missing-docstring
    return list(dataset)


@sequence_as_dataset_registry.dumper(tuple, "tuple", version=None)
def _tuple_dumper(t):
    # pylint: disable=missing-docstring
    return DatasetContainer(data=asarray(t))


@sequence_as_dataset_registry.loader("tuple", version=None)
def _tuple_loader(dataset):
    # pylint: disable=missing-docstring
    return tuple(dataset)


none_python_registry.freeze()
builtin_numbers_registry.freeze()
builtin_text_registry.freeze()
sequence_as_dataset_registry.freeze()
bool_python_registry.freeze()

BUILTIN_REGISTRIES = (
    none_python_registry,
    builtin_numbers_registry,
    builtin_text_registry,
    sequence_as_dataset_registry,
    bool_python_registry,
)
