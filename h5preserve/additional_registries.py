# coding: utf-8
"""
Additional registries for h5preserve
"""
import six

import h5py

from . import Registry, GroupContainer, DatasetContainer


def as_dataset_dumper(obj):
    # pylint: disable=missing-docstring
    return DatasetContainer(data=obj)


def as_dataset_loader(dataset):
    # pylint: disable=missing-docstring
    return dataset["data"]


none_python_registry = Registry("Python: None")
dict_as_group_registry = Registry("Python: dict as group")
builtin_numbers_registry = Registry("Python: builtin numbers")
builtin_text_registry = Registry("Python: builtin text")

if hasattr(h5py, "Empty"):
    # pylint: disable=missing-docstring,unused-argument,no-member
    @none_python_registry.dumper(type(None), "None", version=None)
    def _none_dumper(none):
        return DatasetContainer(dtype=float)

    @none_python_registry.loader("None", version=None)
    def _none_loader(empty):
        return None


@dict_as_group_registry.dumper(dict, "dict", version=None)
def _dict_dumper(d):
    # pylint: disable=missing-docstring
    return GroupContainer(**d)


@dict_as_group_registry.loader("dict", version=None)
def _dict_loader(group):
    # pylint: disable=missing-docstring
    new_dict = {}
    new_dict.update(group)
    if group.attrs:
        new_dict["attrs"] = group.attrs
    return new_dict

builtin_numbers_registry.dumper(int, "int", version=None)(as_dataset_dumper)
builtin_numbers_registry.loader("int", version=None)(as_dataset_loader)
builtin_numbers_registry.dumper(float, "float", version=None)(
    as_dataset_dumper
)
builtin_numbers_registry.loader("float", version=None)(as_dataset_loader)

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

none_python_registry.freeze()
dict_as_group_registry.freeze()
builtin_numbers_registry.freeze()
builtin_text_registry.freeze()
