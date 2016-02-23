import pytest

class MappingTestingClass(object):
    def test_getitem(self):
        raise NotImplementedError("Missing __getitem__ test")
    def test_iter(self):
        raise NotImplementedError("Missing __iter__ test")
    def test_len(self):
        raise NotImplementedError("Missing __len__ test")

class MutableMappingTestingClass(MappingTestingClass):
    def test_setitem(self):
        raise NotImplementedError("Missing __setitem__ test")
    def test_delitem(self):
        raise NotImplementedError("Missing __delitem__ test")

class SequenceTestingClass(object):
    def test_getitem(self):
        raise NotImplementedError("Missing __getitem__ test")
    def test_len(self):
        raise NotImplementedError("Missing __len__ test")

class MutableSequenceTestingClass(MappingTestingClass):
    def test_setitem(self):
        raise NotImplementedError("Missing __setitem__ test")
    def test_delitem(self):
        raise NotImplementedError("Missing __delitem__ test")
    def test_insert(self):
        raise NotImplementedError("Missing __insert__ test")

@pytest.mark.xfail
class TestRegistryContainer(MutableSequenceTestingClass):
    pass

@pytest.mark.xfail
class TestGroupContainer(MutableMappingTestingClass):
    pass

@pytest.mark.xfail
class TestDatasetContainer(MutableMappingTestingClass):
    pass

@pytest.mark.xfail
class TestH5PreserveGroup(MutableMappingTestingClass):
    pass
