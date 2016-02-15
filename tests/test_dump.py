

import numpy as np
from h5py import Group, Dataset

from h5preserve import Registry, RegistryContainer, open as hp_open

### 

REGISTRY = Registry("TestRegistry")
REGISTRIES = RegistryContainer(REGISTRY)

def is_matching_hdf5_object(new, old):
    """
    Check if two objects have the same hdf5 representation
    """
    if type(new) != type(old):
        return False
    elif isinstance(new, Dataset):
        if new[:] != old[:]:
            return False
        elif new.attrs != old.attrs:
            return False
        return True
    elif isinstance(new, Group):
        if new.keys() != old.keys():
            return False
        elif new.attrs != old.attrs:
            return False
        for key in new.keys():
            if not is_matching_hdf5_object(new[key], old[key]):
                return False
        return True
    return new == old

class ExperimentExample1(object):
    def __init__(self, data, time_started):
        self.data = data
        self.time_started = time_started

    def __eq__(self, other):
        return (
            all(self.data == other.data) and
            self.time_started == other.time_started
        )

@REGISTRY.dumper(ExperimentExample1, "ExperimentExample1", version=1)
def _exp_dump(experiment, additional_dumpers):
    return {
        "data": experiment.data,
        "attrs": {
            "time started": experiment.time_started
        }
    }

@REGISTRY.loader("ExperimentExample1", version=1)
def _exp_load(dataset, additional_loaders):
    return ExperimentExample1(
        data=dataset["data"],
        time_started=dataset["attrs"]["time started"]
    )

def test_roundtrip(tmpdir):
    experiment = ExperimentExample1(
        data=np.random.rand(100),
        time_started="1970-01-01 00:00:00"
    )
    tmpfile = str(tmpdir.join("test_roundtrip.h5"))
    with hp_open(tmpfile, registries=REGISTRIES) as f:
        f["first"] = experiment

    with hp_open(tmpfile, registries=REGISTRIES) as f:
        assert f["first"] == experiment
