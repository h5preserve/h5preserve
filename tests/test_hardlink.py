import pytest

from h5preserve import HardLink

class TestHardLink(object):
    def test_no_path(self, h5py_file_with_group):
        group = h5py_file_with_group["example"]
        link = HardLink(group)
        with pytest.raises(RuntimeError) as excinfo:
            link._set_file(h5py_file_with_group)
        assert (
            "No path defined for hard link." == str(excinfo.value)
        )

    def test_set_file(self, h5py_file_with_group):
        link = HardLink("example")
        group = h5py_file_with_group["example"]
        link._set_file(h5py_file_with_group)
        assert link.h5py_obj == group

    def test_create_with_path(self):
        link = HardLink("example")
        assert "example" == link._path
        assert link._h5py_obj is None

    def test_create_with_h5py_obj(self, h5py_file_with_group):
        group = h5py_file_with_group["example"]
        link = HardLink(group)
        assert link._path is None
        assert link._h5py_obj == group

    def test_passthrough_path(self):
        path = "example"
        assert path == HardLink(path)._path

    def test_passthrough_h5py_group(self, h5py_file_with_group):
        group = h5py_file_with_group["example"]
        assert HardLink(group).h5py_obj == group

    def test_passthrough_h5py_dataset(self, h5py_file_with_dataset):
        dataset = h5py_file_with_dataset["example"]
        assert HardLink(dataset).h5py_obj == dataset

    def test_passthrough_h5py_file(self, h5py_file):
        file = h5py_file
        assert HardLink(file).h5py_obj == file
