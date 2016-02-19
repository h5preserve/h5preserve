import pytest

import numpy as np

from h5preserve import Registry, RegistryContainer, new_registry_list


class Experiment(object):
    def __init__(self, data, time_started):
        self.data = data
        self.time_started = time_started

    def __eq__(self, other):
        return (
            all(self.data == other.data) and
            self.time_started == other.time_started
        )

@pytest.fixture
def empty_registry():
    return Registry("empty registry")

@pytest.fixture
def frozen_empty_registry():
    registry = empty_registry()
    registry.freeze()
    return registry

@pytest.fixture
def expriment_registry():
    registry = Registry("experiment")

    @registry.dumper(Experiment, "Experiment", version=1)
    def _exp_dump(experiment, additional_dumpers):
        return {
            "data": experiment.data,
            "attrs": {
                "time started": experiment.time_started
            }
        }

    @registry.loader("Experiment", version=1)
    def _exp_load(dataset, additional_loaders):
        return Experiment(
            data=dataset["data"],
            time_started=dataset["attrs"]["time started"]
        )

    return registry

@pytest.fixture
def invalid_dumper_experiment_registry():
    registry = Registry("incorrect dumper experiment")

    @registry.dumper(Experiment, "Experiment", version=1)
    def _exp_dump(experiment, additional_dumpers):
        return (
            experiment.data, {
                "time started": experiment.time_started
            }
        )

    return registry

@pytest.fixture
def invalid_loader_experiment_registry():
    registry = Registry("incorrect loader experiment")

    @registry.dumper(Experiment, "Experiment", version=1)
    def _exp_dump(experiment, additional_dumpers):
        return {
            "data": experiment.data,
            "attrs": {
                "time started": experiment.time_started
            }
        }

    @registry.loader("Experiment", version=1)
    def _exp_load(dataset, additional_loaders):
        return Experiment(
            data=dataset["data"],
        )

    return registry

@pytest.fixture
def frozen_expriment_registry():
    registry = expriment_registry()
    registry.freeze()
    return registry

@pytest.fixture
def experiment_data():
    return Experiment(
        data=np.random.rand(100),
        time_started="1970-01-01 00:00:00"
    )

@pytest.fixture(params=[
    (expriment_registry(), experiment_data()),
    (frozen_expriment_registry(), experiment_data()),
])
def obj_registry(request):
    return {
        "registries": RegistryContainer(request.param[0]),
        "dumpable_object": request.param[1]
    }

@pytest.fixture(params=[
    (expriment_registry(), experiment_data()),
    (frozen_expriment_registry(), experiment_data()),
])
def obj_registry_with_defaults(request):
    return {
        "registries": new_registry_list(request.param[0]),
        "dumpable_object": request.param[1]
    }
