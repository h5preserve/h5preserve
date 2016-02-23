import pytest

@pytest.mark.xfail
class TestFile(object):
    def test_context_manager(self, tmpdir, registry_container):
        assert 0
    def test_create(self, tmpdir, registry_container):
        assert 0
    def test_close(self, tmpdir, registry_container):
        assert 0

