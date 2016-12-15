import pytest

import h5py
from h5preserve import open as hp_open, H5PreserveFile

@pytest.mark.roundtrip
def test_roundtrip(tmpdir, obj_registry):
    tmpfile = str(tmpdir.join("test_roundtrip.h5"))
    with hp_open(tmpfile, registries=obj_registry["registries"]) as f:
        f["first"] = obj_registry["dumpable_object"]

    with hp_open(tmpfile, registries=obj_registry["registries"]) as f:
        roundtripped = f["first"]
        assert roundtripped == obj_registry["dumpable_object"]

@pytest.mark.roundtrip
def test_roundtrip_without_open(tmpdir, obj_registry):
    tmpfile = str(tmpdir.join("test_roundtrip.h5"))
    with H5PreserveFile(h5py.File(tmpfile), registries=obj_registry["registries"]) as f:
        f["first"] = obj_registry["dumpable_object"]

    with H5PreserveFile(h5py.File(tmpfile), registries=obj_registry["registries"]) as f:
        roundtripped = f["first"]
        assert roundtripped == obj_registry["dumpable_object"]

@pytest.mark.roundtrip
def test_roundtrip_with_defaults(tmpdir, obj_registry_with_defaults):
    obj_registry = obj_registry_with_defaults
    tmpfile = str(tmpdir.join("test_roundtrip.h5"))
    with hp_open(tmpfile, registries=obj_registry["registries"]) as f:
        f["first"] = obj_registry["dumpable_object"]

    with hp_open(tmpfile, registries=obj_registry["registries"]) as f:
        roundtripped = f["first"]
        assert roundtripped == obj_registry["dumpable_object"]

@pytest.mark.roundtrip
def test_roundtrip_without_open_with_defaults(tmpdir, obj_registry_with_defaults):
    obj_registry = obj_registry_with_defaults
    tmpfile = str(tmpdir.join("test_roundtrip.h5"))
    with H5PreserveFile(h5py.File(tmpfile), registries=obj_registry["registries"]) as f:
        f["first"] = obj_registry["dumpable_object"]

    with H5PreserveFile(h5py.File(tmpfile), registries=obj_registry["registries"]) as f:
        roundtripped = f["first"]
        assert roundtripped == obj_registry["dumpable_object"]

if hasattr(h5py, "Empty"):
    @pytest.mark.roundtrip
    def test_roundtrip_with_none(tmpdir, obj_registry_with_none):
        tmpfile = str(tmpdir.join("test_roundtrip.h5"))
        with hp_open(tmpfile, registries=obj_registry_with_none["registries"]) as f:
            f["first"] = obj_registry_with_none["dumpable_object"]

        with hp_open(tmpfile, registries=obj_registry_with_none["registries"]) as f:
            roundtripped = f["first"]
            assert roundtripped == obj_registry_with_none["dumpable_object"]

    @pytest.mark.roundtrip
    def test_roundtrip_without_open_with_none(tmpdir, obj_registry_with_none):
        tmpfile = str(tmpdir.join("test_roundtrip.h5"))
        with H5PreserveFile(h5py.File(tmpfile), registries=obj_registry_with_none["registries"]) as f:
            f["first"] = obj_registry_with_none["dumpable_object"]

        with H5PreserveFile(h5py.File(tmpfile), registries=obj_registry_with_none["registries"]) as f:
            roundtripped = f["first"]
            assert roundtripped == obj_registry_with_none["dumpable_object"]

    @pytest.mark.roundtrip
    def test_roundtrip_with_defaults_with_none(tmpdir, obj_registry_with_none_with_defaults):
        obj_registry_with_none = obj_registry_with_none_with_defaults
        tmpfile = str(tmpdir.join("test_roundtrip.h5"))
        with hp_open(tmpfile, registries=obj_registry_with_none["registries"]) as f:
            f["first"] = obj_registry_with_none["dumpable_object"]

        with hp_open(tmpfile, registries=obj_registry_with_none["registries"]) as f:
            roundtripped = f["first"]
            assert roundtripped == obj_registry_with_none["dumpable_object"]

    @pytest.mark.roundtrip
    def test_roundtrip_without_open_with_defaults_with_none(tmpdir, obj_registry_with_none_with_defaults):
        obj_registry_with_none = obj_registry_with_none_with_defaults
        tmpfile = str(tmpdir.join("test_roundtrip.h5"))
        with H5PreserveFile(h5py.File(tmpfile), registries=obj_registry_with_none["registries"]) as f:
            f["first"] = obj_registry_with_none["dumpable_object"]

        with H5PreserveFile(h5py.File(tmpfile), registries=obj_registry_with_none["registries"]) as f:
            roundtripped = f["first"]
            assert roundtripped == obj_registry_with_none["dumpable_object"]
