import pytest

from h5preserve import H5PreserveFile, new_registry_list

class TestFile(object):
    @pytest.mark.xfail
    def test_context_manager(self, tmpdir, registry_container):
        assert 0
    @pytest.mark.xfail
    def test_create(self, tmpdir, registry_container):
        assert 0
    @pytest.mark.xfail
    def test_close(self, tmpdir, registry_container):
        assert 0

    def test_roundtrip(self, h5py_file):
        assert h5py_file == H5PreserveFile(
            h5py_file, new_registry_list()
        ).h5py_file

