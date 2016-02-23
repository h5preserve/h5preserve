import pytest

class TestLoad(object):
    @pytest.mark.xfail
    def test_not_loadable(self, tmpdir, registry_container):
        assert 0

    @pytest.mark.xfail
    def test_unknown_namespace(self, tmpdir, registry_container):
        assert 0

    @pytest.mark.xfail
    def test_label_not_in_namespace(self, tmpdir, registry_container):
        assert 0

    @pytest.mark.xfail
    def test_no_suitable_loader(self, tmpdir, registry_container):
        assert 0

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
    def test_recursive(self, tmpdir, registry_container):
        assert 0

class TestFromFile(object):
    @pytest.mark.xfail
    def test_no_loadable_type(self, tmpdir, registry_container):
        assert 0
    @pytest.mark.xfail
    def test_unknown_namespace(self, tmpdir, registry_container):
        assert 0

    @pytest.mark.xfail
    def test_recursive(self, tmpdir, registry_container):
        assert 0


class TestH5pyToH5preserve(object):
    @pytest.mark.xfail
    def test_group(self, tmpdir, registry_container):
        assert 0
    @pytest.mark.xfail
    def test_dataset(self, tmpdir, registry_container):
        assert 0

    @pytest.mark.xfail
    def test_unsupported_type(self, tmpdir, registry_container):
        assert 0
