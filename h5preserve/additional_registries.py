# coding: utf-8
"""
Additional registries for h5preserve
"""
import h5py

from . import Registry

none_python_registry = Registry("Python: None")

if hasattr(h5py, "Empty"):
    # pylint: disable=missing-docstring,unused-argument,no-member
    @none_python_registry.dumper(type(None), "None", version=None)
    def _none_dumper(none):
        return h5py.Empty(dtype=float)

    @none_python_registry.loader("None", version=None)
    def _none_loader(empty):
        return None

none_python_registry.freeze()
