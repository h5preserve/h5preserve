import pytest

import numpy as np
from h5py import Group, Dataset, SoftLink, ExternalLink

from h5preserve import RegistryContainer, HardLink, new_registry_list

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

class TestDump(object):
    def test_hardlink(self, empty_registry):
        registries = RegistryContainer(empty_registry)
        hard_link = HardLink("/example")
        assert hard_link == registries.dump(hard_link)

    def test_h5py_group(self, empty_registry, h5py_file_with_group):
        registries = RegistryContainer(empty_registry)
        group = h5py_file_with_group["example"]
        assert group == registries.dump(group)

    def test_h5py_dataset(self, empty_registry, h5py_file_with_dataset):
        registries = RegistryContainer(empty_registry)
        dataset = h5py_file_with_dataset["example"]
        assert dataset == registries.dump(dataset)

    def test_h5py_soft_link(self, empty_registry):
        registries = RegistryContainer(empty_registry)
        soft_link = SoftLink("/example")
        assert soft_link == registries.dump(soft_link)

    def test_h5py_external_link(self, empty_registry):
        registries = RegistryContainer(empty_registry)
        external_link = ExternalLink("example.hdf5", "/example")
        assert external_link == registries.dump(external_link)

    def test_ndarray(self, empty_registry):
        registries = RegistryContainer(empty_registry)
        ndarray = np.random.rand(1000)
        assert all(ndarray == registries.dump(ndarray))

    @pytest.mark.xfail
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

    def test_no_version(self, experiment_registry, experiment_data):
        registries = RegistryContainer(experiment_registry)
        registries.lock_version(type(experiment_data), 10)
        with pytest.raises(RuntimeError) as excinfo:
            registries._obj_to_h5preserve(experiment_data)
        assert (
            "<class 'conftest.Experiment'> does not have version 10." == str(excinfo.value)
        )

    def test_version(self, experiment_registry, experiment_data):
        registries = RegistryContainer(experiment_registry)
        registries.lock_version(type(experiment_data), 1)
        assert registries._obj_to_h5preserve(experiment_data)._version == 1

    def test_none(self, None_version_experiment_registry, experiment_data):
        registries = RegistryContainer(None_version_experiment_registry)
        assert registries._obj_to_h5preserve(experiment_data)._version == None

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

class TestToFile(object):
    @pytest.mark.xfail
    def test_hardlink(self, tmpdir, registry_container):
        assert 0

    @pytest.mark.xfail
    def test_group(self, tmpdir, registry_container):
        assert 0

    @pytest.mark.xfail
    def test_dataset(self, tmpdir, registry_container):
        assert 0

    def test_h5py_soft_link(self, h5py_file_with_group):
        soft_link = SoftLink("example")
        registries = new_registry_list()
        registries.to_file(h5py_file_with_group, "alias", soft_link)
        assert h5py_file_with_group.get("alias", getlink=True).path == "example"

    def test_h5py_external_link(self, h5py_file_with_group):
        external = ExternalLink("external.hdf5", "example")
        registries = new_registry_list()
        registries.to_file(h5py_file_with_group, "alias", external)
        assert h5py_file_with_group.get("alias", getlink=True).path == "example"
        assert h5py_file_with_group.get("alias", getlink=True).filename == "external.hdf5"

    @pytest.mark.xfail
    def test_unknown_type(self):
        with pytest.raises(TypeError) as excinfo:
            registries.to_file("fail")
        assert (
            "Unknown h5preserve type str." == str(excinfo.value)
        )
