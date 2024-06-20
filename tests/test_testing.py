import pytest
from h5preserve import open as hp_open
import h5preserve.testing as testing

class TestYieldSingleLocked:
    def test_only_single_lock(self, obj_registry):
        for new_reg in testing.yield_single_locked(obj_registry["registries"]):
            assert len(new_reg._version_lock) == 1
