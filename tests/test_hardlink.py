import pytest

@pytest.mark.xfail
class TestHardLink(object):
    def test_no_path(self, tmpdir, registry_container):
        assert 0
    def test_create_with_path(self, tmpdir, registry_container):
        assert 0
    def test_create_with_h5py_obj(self, tmpdir, registry_container):
        assert 0
    def test_passthrough_path(self, tmpdir, registry_container):
        assert 0
    def test_passthrough_h5py_obj(self, tmpdir, registry_container):
        assert 0
