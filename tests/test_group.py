import pytest

from h5preserve import H5PreserveGroup, new_registry_list

class TestGroup(object):
    def test_create_group(self, h5py_file_with_group):
        group = h5py_file_with_group["example"]
        h5preserve_group = H5PreserveGroup(group, new_registry_list())
        h5preserve_subgroup = h5preserve_group.create_group("subexample")
        assert h5preserve_subgroup.h5py_group == group["subexample"]

    def test_require_group_no_exist(self, h5py_file_with_group):
        group = h5py_file_with_group["example"]
        h5preserve_group = H5PreserveGroup(group, new_registry_list())
        h5preserve_subgroup = h5preserve_group.require_group("subexample")
        assert h5preserve_subgroup.h5py_group == group["subexample"]

    def test_require_group_exist(self, h5py_file_with_group):
        group = h5py_file_with_group["example"]
        h5preserve_group = H5PreserveGroup(
            h5py_file_with_group, new_registry_list()
        )
        h5preserve_subgroup = h5preserve_group.require_group("example")
        assert h5preserve_subgroup.h5py_group == group

    def test_roundtrip(self, h5py_file_with_group):
        group = h5py_file_with_group["example"]
        assert group == H5PreserveGroup(
            group, new_registry_list()
        ).h5py_group
