# coding: utf-8
import pytest

from collections import namedtuple

import six

import numpy as np
import h5py
from h5py import File

from h5preserve import (
    Registry, RegistryContainer, new_registry_list, GroupContainer,
    DatasetContainer, OnDemandGroupContainer,
    wrap_on_demand, OnDemandContainer,
)
from h5preserve.additional_registries import (
    none_python_registry, builtin_numbers_registry,
    builtin_text_registry
)


### Classes for testng ###
class Experiment(object):
    def __init__(self, data, time_started):
        self.data = data
        self.time_started = time_started

    def __eq__(self, other):
        return (
            all(self.data == other.data) and
            self.time_started == other.time_started
        )

class OnDemandExperiment(object):
    def __init__(self, data, time_started):
        self._data = data
        self.time_started = time_started

    def __eq__(self, other):
        return (
            all(self.data == other.data) and
            self.time_started == other.time_started
        )

    @property
    def data(self):
        if isinstance(self._data, OnDemandContainer):
            self._data = self._data()
        return self._data

    def _h5preserve_update(self):
        wrap_on_demand(self, "dataset", self._data)


Experiments = namedtuple("Experiments", ["runs", "name"])

def _better_eq(self, other):
    if not isinstance(other, self.__class__):
        return False
    elif len(self) != len(other):
        return False
    for i in range(len(self)):
        result = self[i] == other[i]
        try:
            bool(result)
        except ValueError:
            if not result.all():
                return False
        else:
            if not result:
                return False
    return True


InternalData = namedtuple("InternalData", [
    "derivs", "params", "angles", "v_r_normal", "v_phi_normal", "rho_normal",
    "v_r_taylor", "v_phi_taylor", "rho_taylor",
])
InternalData.__eq__ = _better_eq

InitialConditions = namedtuple("InitialConditions", [
    "norm_kepler_sq", "c_s", "eta_O", "eta_A", "eta_H", "beta", "init_con",
    "angles",
])
InitialConditions.__eq__ = _better_eq

Solution = namedtuple("Solution", [
    "angles", "solution", "flag", "coordinate_system",
    "internal_data", "initial_conditions", "t_roots", "y_roots",
])
Solution.__eq__ = _better_eq
###


@pytest.fixture
def empty_registry():
    return Registry("empty registry")

@pytest.fixture
def frozen_empty_registry():
    registry = empty_registry()
    registry.freeze()
    return registry

@pytest.fixture
def experiment_registry():
    registry = Registry("experiment")

    @registry.dumper(Experiment, "Experiment", version=1)
    def _exp_dump(experiment):
        return DatasetContainer(
            data = experiment.data,
            attrs = {
                "time started": experiment.time_started
            }
        )

    @registry.loader("Experiment", version=1)
    def _exp_load(dataset):
        return Experiment(
            data=dataset["data"],
            time_started=dataset["attrs"]["time started"]
        )

    return registry

@pytest.fixture
def experiment_registry_as_group():
    registry = Registry("experiment")

    @registry.dumper(Experiment, "Experiment", version=1)
    def _exp_dump(experiment):
        return GroupContainer(
            dataset=DatasetContainer(data = experiment.data),
            attrs = {
                "time started": experiment.time_started
            }
        )

    @registry.loader("Experiment", version=1)
    def _exp_load(dataset):
        return Experiment(
            data=dataset["dataset"]["data"],
            time_started=dataset.attrs["time started"]
        )

    return registry

@pytest.fixture
def experiment_registry_as_on_demand_group():
    registry = Registry("experiment")

    @registry.dumper(OnDemandExperiment, "Experiment", version=1)
    def _exp_dump(experiment):
        return OnDemandGroupContainer(
            dataset=DatasetContainer(data = experiment.data),
            attrs = {
                "time started": experiment.time_started
            }
        )

    @registry.loader("Experiment", version=1)
    def _exp_load(dataset):
        return OnDemandExperiment(
            data=dataset["dataset"]["data"],
            time_started=dataset.attrs["time started"]
        )

    return registry

@pytest.fixture
def experiment_experiments_registry():
    registry = Registry("experiments")

    @registry.dumper(Experiment, "Experiment", version=1)
    def _exp_dump(experiment):
        return GroupContainer(
            dataset=DatasetContainer(data = experiment.data),
            attrs = {
                "time started": experiment.time_started
            }
        )

    @registry.loader("Experiment", version=1)
    def _exp_load(dataset):
        return Experiment(
            data=dataset["dataset"]["data"],
            time_started=dataset.attrs["time started"]
        )

    @registry.dumper(Experiments, "Experiments", version=1)
    def _exp_dump(experiments):
        return GroupContainer(
            runs=GroupContainer(**experiments.runs),
            attrs = {
                "name": experiments.name
            }
        )

    @registry.loader("Experiments", version=1)
    def _exp_load(group):
        return Experiments(
            runs={run: exp for run, exp in group["runs"].items()},
            name=group.attrs["name"]
        )

    return registry

@pytest.fixture
def invalid_dumper_experiment_registry():
    registry = Registry("incorrect dumper experiment")

    @registry.dumper(Experiment, "Experiment", version=1)
    def _exp_dump(experiment):
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
    def _exp_dump(experiment):
        return DatasetContainer(
            data = experiment.data,
            attrs = {
                "time started": experiment.time_started
            }
        )

    @registry.loader("Experiment", version=1)
    def _exp_load(dataset):
        return Experiment(
            data=dataset["data"],
        )

    return registry

@pytest.fixture
def None_version_experiment_registry():
    registry = Registry("None experiment")

    @registry.dumper(Experiment, "Experiment", version=None)
    def _exp_dump(experiment):
        return DatasetContainer(
            data = experiment.data,
            attrs = {
                "time started": experiment.time_started
            }
        )

    @registry.loader("Experiment", version=None)
    def _exp_load(dataset):
        return Experiment(
            data=dataset["data"],
            time_started=dataset["attrs"]["time started"]
        )

    return registry

@pytest.fixture
def no_loader_experiment_registry():
    registry = Registry("experiment")

    @registry.dumper(Experiment, "Experiment", version=1)
    def _exp_dump(experiment):
        return DatasetContainer(
            data = experiment.data,
            attrs = {
                "time started": experiment.time_started
            }
        )

    return registry

@pytest.fixture
def frozen_experiment_registry():
    registry = experiment_registry()
    registry.freeze()
    return registry

@pytest.fixture
def experiment_data():
    return Experiment(
        data=np.random.rand(100),
        time_started="1970-01-01 00:00:00"
    )

@pytest.fixture
def on_demand_experiment_data():
    return OnDemandExperiment(
        data=np.random.rand(100),
        time_started="1970-01-01 00:00:00"
    )

@pytest.fixture
def multi_experiment_data():
    return Experiments(runs={
        "1": Experiment(
            data=np.random.rand(100),
            time_started="1970-01-01 00:00:00"
        ),
        "2": Experiment(
            data=np.random.rand(100),
            time_started="1970-01-02 00:00:00"
        ),
        "3": Experiment(
            data=np.random.rand(100),
            time_started="1970-01-03 00:00:00"
        ),
        "4": Experiment(
            data=np.random.rand(100),
            time_started="1970-01-04 00:00:00"
        ),
        "5": Experiment(
            data=np.random.rand(100),
            time_started="1970-01-05 00:00:00"
        ),
        "6": Experiment(
            data=np.random.rand(100),
            time_started="1970-01-06 00:00:00"
        ),
    }, name="test"
    )

@pytest.fixture
def solution_registry():
    registry = Registry("solution")

    @registry.dumper(InternalData, "InternalData", version=1)
    def _internal_dump(internal_data):
        return GroupContainer(
            derivs = internal_data.derivs,
            params = internal_data.params,
            angles = internal_data.angles,
            v_r_normal = internal_data.v_r_normal,
            v_phi_normal = internal_data.v_phi_normal,
            rho_normal = internal_data.rho_normal,
            v_r_taylor = internal_data.v_r_taylor,
            v_phi_taylor = internal_data.v_phi_taylor,
            rho_taylor = internal_data.rho_taylor,
        )

    @registry.loader("InternalData", version=1)
    def _internal_load(group):
        return InternalData(
            derivs = group["derivs"]["data"],
            params = group["params"]["data"],
            angles = group["angles"]["data"],
            v_r_normal = group["v_r_normal"]["data"],
            v_phi_normal = group["v_phi_normal"]["data"],
            rho_normal = group["rho_normal"]["data"],
            v_r_taylor = group["v_r_taylor"]["data"],
            v_phi_taylor = group["v_phi_taylor"]["data"],
            rho_taylor = group["rho_taylor"]["data"],
        )

    @registry.dumper(InitialConditions, "InitialConditions", version=1)
    def _initial_dump(initial_conditions):
        return GroupContainer(
            attrs={
                "norm_kepler_sq": initial_conditions.norm_kepler_sq,
                "c_s": initial_conditions.c_s,
                "eta_O": initial_conditions.eta_O,
                "eta_A": initial_conditions.eta_A,
                "eta_H": initial_conditions.eta_H,
                "beta": initial_conditions.beta,
                "init_con": initial_conditions.init_con,
            }, angles = initial_conditions.angles,
        )

    @registry.loader("InitialConditions", version=1)
    def _initial_load(group):
        return InitialConditions(
            norm_kepler_sq = group.attrs["norm_kepler_sq"],
            c_s = group.attrs["c_s"],
            eta_O = group.attrs["eta_O"],
            eta_A = group.attrs["eta_A"],
            eta_H = group.attrs["eta_H"],
            beta = group.attrs["beta"],
            init_con = group.attrs["init_con"],
            angles = group["angles"]["data"],
        )

    @registry.dumper(Solution, "Solution", version=1)
    def _solution_dumper(solution):
        return GroupContainer(
            attrs={
                "flag": solution.flag,
                "coordinate_system": solution.coordinate_system,
            },
            angles = solution.angles,
            solution = solution.solution,
            internal_data = solution.internal_data,
            initial_conditions = solution.initial_conditions,
            t_roots = solution.t_roots,
            y_roots = solution.y_roots,
        )

    @registry.loader("Solution", version=1)
    def _solution_loader(group):
        return Solution(
            flag = group.attrs["flag"],
            coordinate_system = group.attrs["coordinate_system"],
            angles = group["angles"]["data"],
            solution = group["solution"]["data"],
            t_roots = group["t_roots"]["data"],
            y_roots = group["y_roots"]["data"],
            internal_data = group["internal_data"],
            initial_conditions = group["initial_conditions"],
        )

    return registry

@pytest.fixture
def internal_data_data():
    return InternalData(
        derivs = np.random.rand(1000, 8),
        params = np.random.rand(1000, 8),
        angles = np.random.rand(1000),
        v_r_normal = np.random.rand(1000),
        v_phi_normal = np.random.rand(1000),
        rho_normal = np.random.rand(1000),
        v_r_taylor = np.random.rand(1000),
        v_phi_taylor = np.random.rand(1000),
        rho_taylor = np.random.rand(1000),
    )

@pytest.fixture
def initial_conditions_data():
    return InitialConditions(
        norm_kepler_sq = 10,
        c_s = 1.0,
        eta_O = 0.3,
        eta_A = 0.001,
        eta_H = 5e-15,
        beta = 5/3,
        init_con = np.random.rand(8),
        angles = np.random.rand(1000),
    )

@pytest.fixture
def solution_data():
    return Solution(
        flag = 0,
        coordinate_system = "some thing",
        angles = np.random.rand(1000),
        solution = np.random.rand(1000, 8),
        t_roots = np.random.rand(15),
        y_roots = np.random.rand(15,8),
        internal_data = internal_data_data(),
        initial_conditions = initial_conditions_data(),
    )

@pytest.fixture(params=[
    (experiment_registry(), experiment_data()),
    (experiment_registry_as_group(), experiment_data()),
    (experiment_registry_as_on_demand_group(), on_demand_experiment_data()),
    (frozen_experiment_registry(), experiment_data()),
    (None_version_experiment_registry(), experiment_data()),
    (solution_registry(), internal_data_data()),
    (solution_registry(), initial_conditions_data()),
    (solution_registry(), solution_data()),
    (builtin_numbers_registry, 1),
    (builtin_numbers_registry, 1.0),
    (builtin_text_registry, b"abcd"),
    (builtin_text_registry, u"abcd"),
    (experiment_experiments_registry(), multi_experiment_data()),
])
def obj_registry(request):
    return {
        "registries": RegistryContainer(request.param[0]),
        "dumpable_object": request.param[1]
    }

@pytest.fixture(params=[
    (experiment_registry(), experiment_data()),
    (experiment_registry_as_on_demand_group(), on_demand_experiment_data()),
    (frozen_experiment_registry(), experiment_data()),
    (None_version_experiment_registry(), experiment_data()),
    (solution_registry(), internal_data_data()),
    (solution_registry(), initial_conditions_data()),
    (solution_registry(), solution_data()),
    (builtin_numbers_registry, 1),
    (builtin_numbers_registry, 1.0),
    (frozen_empty_registry(), 1),
    (frozen_empty_registry(), 1.0),
    (builtin_text_registry, b"abcd"),
    (builtin_text_registry, u"abcd"),
    (frozen_empty_registry(), b"abcd"),
    (frozen_empty_registry(), u"abcd"),
])
def obj_registry_with_defaults(request):
    return {
        "registries": new_registry_list(request.param[0]),
        "dumpable_object": request.param[1]
    }

if hasattr(h5py, "Empty"):

    @pytest.fixture(params=[
        (none_python_registry, None),
    ])
    def obj_registry_with_none(request):
        return {
            "registries": RegistryContainer(request.param[0]),
            "dumpable_object": request.param[1]
        }

    @pytest.fixture(params=[
        (none_python_registry, None),
        (frozen_empty_registry(), None),
    ])
    def obj_registry_with_none_with_defaults(request):
        return {
            "registries": new_registry_list(request.param[0]),
            "dumpable_object": request.param[1]
        }

@pytest.fixture
def h5py_file(tmpdir):
    file = File(str(tmpdir.join("test.hdf5")))
    def fin():
        file.close()
    return file

@pytest.fixture
def h5py_file_with_group(h5py_file):
    h5py_file.create_group("example")
    return h5py_file

@pytest.fixture
def h5py_file_with_dataset(h5py_file):
    h5py_file.create_dataset("example", data=np.random.rand(1000))
    return h5py_file

@pytest.fixture
def h5py_file_with_experiment(h5py_file):
    h5py_file.create_dataset("example", data=np.random.rand(1000))
    h5py_file["example"].attrs.update()
    return h5py_file

@pytest.fixture
def h5preserve_experiment_repr():
    return DatasetContainer(
        attrs={
            "time started": "2000-01-01",
            "_h5preserve_namespace": "experiment",
            "_h5preserve_label": "Experiment",
            "_h5preserve_version": 1,
        },
        data=np.random.rand(1000)
    )
