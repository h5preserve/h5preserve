# coding: utf-8
"""
Additional registries for h5preserve
"""
import h5py

from . import Registry, GroupContainer, DatasetContainer

none_python_registry = Registry("Python: None")
dict_as_group_registry = Registry("Python: dict as group")

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

none_python_registry.freeze()
dict_as_group_registry.freeze()
