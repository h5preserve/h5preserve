import pytest

import numpy as np
from h5py import Group, Dataset

from h5preserve import RegistryContainer

def is_matching_hdf5_object(new, old):
    """
    Check if two objects have the same hdf5 representation
    """
    if type(new) != type(old):
        return False
    elif isinstance(new, Dataset):
        if new[:] != old[:]:
            return False
        elif new.attrs != old.attrs:
            return False
        return True
    elif isinstance(new, Group):
        if new.keys() != old.keys():
            return False
        elif new.attrs != old.attrs:
            return False
        for key in new.keys():
            if not is_matching_hdf5_object(new[key], old[key]):
                return False
        return True
    return new == old

@pytest.mark.xfail
class TestDump(object):
    def test_hardlink(self, tmpdir, registry_container):
        assert 0
    def test_h5py_group(self, tmpdir, registry_container):
        assert 0
    def test_h5py_dataset(self, tmpdir, registry_container):
        assert 0
    def test_h5py_soft_link(self, tmpdir, registry_container):
        assert 0
    def test_h5py_external_link(self, tmpdir, registry_container):
        assert 0
    def test_ndarray(self, tmpdir, registry_container):
        assert 0
    def test_recursion(self, tmpdir, registry_container):
        assert 0

class TestObjToH5preserve(object):
    def test_not_dumpable(self, empty_registry, experiment_data):
        registries = RegistryContainer(empty_registry)
        with pytest.raises(TypeError) as excinfo:
            registries._obj_to_h5preserve(experiment_data)
        assert (
            "<class 'conftest.Experiment'> is not something that can be dumped." == str(excinfo.value)
        )

    def test_no_version(self, expriment_registry, experiment_data):
        registries = RegistryContainer(expriment_registry)
        registries.lock_version(type(experiment_data), 10)
        with pytest.raises(RuntimeError) as excinfo:
            registries._obj_to_h5preserve(experiment_data)
        assert (
            "<class 'conftest.Experiment'> does not have version 10." == str(excinfo.value)
        )

    @pytest.mark.xfail
    def test_none(self, tmpdir, registry_container):
        assert 0

    @pytest.mark.xfail
    def test_any(self, tmpdir, registry_container):
        assert 0

    @pytest.mark.xfail
    def test_all(self, tmpdir, registry_container):
        assert 0

    @pytest.mark.xfail
    def test_container_base(self, tmpdir, registry_container):
        assert 0

    @pytest.mark.xfail
    def test_mapping(self, tmpdir, registry_container):
        assert 0

    def test_invalid_dumper(
        self, invalid_dumper_experiment_registry, experiment_data
    ):
        registries = RegistryContainer(invalid_dumper_experiment_registry)
        with pytest.raises(TypeError) as excinfo:
            registries._obj_to_h5preserve(experiment_data)
        assert (
            "Dumper for Experiment with version 1 returned incorrect type." == str(excinfo.value)
        )

@pytest.mark.xfail
class TestToFile(object):
    def test_hardlink(self, tmpdir, registry_container):
        assert 0
    def test_group(self, tmpdir, registry_container):
        assert 0
    def test_dataset(self, tmpdir, registry_container):
        assert 0
    def test_h5py_soft_link(self, tmpdir, registry_container):
        assert 0
    def test_h5py_external_link(self, tmpdir, registry_container):
        assert 0
    def test_unknown_type(self, tmpdir, registry_container):
        assert 0
