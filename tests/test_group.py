import pytest

@pytest.mark.xfail
class TestGroup(object):
    def test_create_group(self, tmpdir, registry_container):
        assert 0
    def test_require_group_no_exist(self, tmpdir, registry_container):
        assert 0
    def test_require_group_exist(self, tmpdir, registry_container):
        assert 0
