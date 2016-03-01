import pytest

from h5preserve import RegistryContainer

class TestLoad(object):
    def test_not_loadable(self, experiment_data):
        registries = RegistryContainer()
        with pytest.raises(TypeError) as excinfo:
            registries.load(experiment_data)
        assert (
            "<class 'conftest.Experiment'> is not something that can be loaded." == str(excinfo.value)
        )


    @pytest.mark.xfail
    def test_unknown_namespace(self, tmpdir, registry_container):
        assert 0

    def test_label_not_in_namespace(
        self, h5preserve_experiment_repr, no_loader_experiment_registry
        ):
        registries = RegistryContainer(no_loader_experiment_registry)
        with pytest.raises(RuntimeError) as excinfo:
            registries.load(h5preserve_experiment_repr)
        assert (
            "Label Experiment not in namespace experiment." == str(excinfo.value)
        )

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
