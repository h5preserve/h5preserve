# coding: utf-8
"""
h5preserve is a thin wrapper around h5py, providing easier serialisation of
native python types.

:copyright: (c) 2016 James Tocknell
:license: 3-clause BSD
"""
from collections import (
    MutableMapping, namedtuple, defaultdict, MutableSequence, Mapping
)
from warnings import warn

import h5py

# versioneer stuff
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

ALLOWED_DATASET_KEYS = {
    "attrs", "shape", "dtype", "data", "chunks", "maxshape", "fillvalue",
    "size",
}
H5PRESERVE_ATTR_NAMESPACE = "_h5preserve_namespace"
H5PRESERVE_ATTR_LABEL = "_h5preserve_label"
H5PRESERVE_ATTR_VERSION = "_h5preserve_version"

UNKNOWN_NAMESPACE = "Unknown namespace {}."
UNSUPPORTED_H5PY_TYPE = "Unsupported h5py type {}."
UNKNOWN_H5PRESERVE_TYPE = "Unknown h5preserve type {}."
NOT_DUMPABLE = "{} is not something that can be dumped."
NO_VERSION = "{} does not have version {}."
INVALID_DUMPER = "Dumper for {} with version {} returned incorrect type."
NOT_LOADABLE = "{} is not something that can be loaded."
LABEL_NOT_IN_NAMESPACE = "Label {} not in namespace {}."
NO_SUITABLE_LOADER = "Cannot find suitable loader for label {} with version {}"
INVALID_DATASET_OPTION = "{} is not a valid dataset option."

_DumperMap = namedtuple("_DumperMap", "label func")


class RegistryContainer(MutableSequence):
    """
    Ordered container of registries which manages interaction with the hdf5
    file.

    Parameters
    ----------
    *registries : list of Registry
        the list of registries to be associated with this container
    """
    def __init__(self, *registries):
        self._version_lock = {}
        self._registries = {}
        self._indexed_registries = []
        if registries:
            self.extend(registries)

    def __getitem__(self, index):
        return self._indexed_registries[index]

    def __setitem__(self, index, item):
        self._indexed_registries[index] = item.name
        self._registries[item.name] = item

    def __delitem__(self, index):
        name = self._indexed_registries[index]
        del self._registries[name]
        del self._indexed_registries[index]

    def __len__(self):
        return len(self._registries)

    def insert(self, index, item):
        self._registries[item.name] = item
        self._indexed_registries.insert(index, item.name)

    def from_file(self, h5py_obj):
        """
        Return native python object from hdf5 file

        Parameters
        ----------
        h5py_obj : a ``h5py`` object, e.g. group, dataset
        """
        namespace = h5py_obj.attrs.get(H5PRESERVE_ATTR_NAMESPACE)
        if namespace is None:
            if isinstance(h5py_obj, h5py.Group):
                return H5PreserveGroup(h5py_group=h5py_obj, registries=self)
            else:
                warn(
                    "No type information about object, returning native h5py"
                    "object"
                )
                return h5py_obj
        if namespace in self._registries:
            return self.load(self._h5py_to_h5preserve(h5py_obj))
        else:
            raise RuntimeError(UNKNOWN_NAMESPACE.format(namespace))

    def _h5py_to_h5preserve(self, h5py_obj):
        """
        convert h5py object to h5preserve representation
        """
        attrs = dict(h5py_obj.attrs)
        if isinstance(h5py_obj, h5py.Group):
            return GroupContainer(
                attrs,
                **{
                    name: self._h5py_to_h5preserve(item)
                    for name, item in h5py_obj.items()
                }
            )
        elif isinstance(h5py_obj, h5py.Dataset):
            return DatasetContainer(
                attrs,
                data=h5py_obj[()],
                shape=h5py_obj.shape,
                fillvalue=h5py_obj.fillvalue,
                dtype=h5py_obj.dtype,
                size=h5py_obj.size,
            )
        raise TypeError(UNSUPPORTED_H5PY_TYPE.format(type(h5py_obj)))

    def to_file(self, h5py_group, key, val):
        """
        Dump native python object to hdf5 file

        Parameters
        ----------
        h5py_group : ``h5py.Group``
            the group to add the object to
        key : string
            the name for the object
        val
            the object to add
        """
        h5preserve_repr = self.dump(val)
        # pylint: disable=protected-access
        if isinstance(h5preserve_repr, GroupContainer):
            new_group = h5py_group.create_group(key)
            new_group.attrs.update(h5preserve_repr.attrs)
            new_group.attrs.update({
                H5PRESERVE_ATTR_NAMESPACE: h5preserve_repr._namespace,
                H5PRESERVE_ATTR_LABEL: h5preserve_repr._label,
                H5PRESERVE_ATTR_VERSION: h5preserve_repr._version
            })
            for obj_name, obj_val in val.items():
                self.to_file(new_group, obj_name, obj_val)
        elif isinstance(h5preserve_repr, DatasetContainer):
            new_dataset = h5py_group.create_dataset(
                key, **h5preserve_repr
            )
            new_dataset.attrs.update(h5preserve_repr.attrs)
            new_dataset.attrs.update({
                H5PRESERVE_ATTR_NAMESPACE: h5preserve_repr._namespace,
                H5PRESERVE_ATTR_LABEL: h5preserve_repr._label,
                H5PRESERVE_ATTR_VERSION: h5preserve_repr._version
            })
        else:
            raise TypeError(
                UNKNOWN_H5PRESERVE_TYPE.format(type(h5preserve_repr))
            )

    def dump(self, obj):
        """
        Dump native python object to h5preserve representation

        Parameters
        ----------
        obj
            the object to dump
        """
        val_type = type(obj)
        for registry in self:
            if val_type in self._registries[registry].dumpers:
                namespace = registry
                dumpers = self._registries[registry].dumpers[val_type]
                break
        else:
            raise TypeError(NOT_DUMPABLE.format(type(obj)))

        if val_type in self._version_lock:
            version = self._version_lock[val_type]
            try:
                label, dumper = dumpers[version]
            except KeyError:
                raise RuntimeError(NO_VERSION.format(val_type, version))
        else:
            if None in dumpers:
                version = None
            else:
                version = sorted(dumpers, reverse=True)[0]
            label, dumper = dumpers[version]
        return self._obj_to_h5preserve(
            dumper(obj, self), namespace, label, version
        )

    def _obj_to_h5preserve(self, obj, namespace, label, version):
        """convert python object to h5preserve representation"""
        # pylint: disable=no-self-use
        # pylint: disable=protected-access
        if isinstance(obj, ContainerBase):
            obj._namespace = namespace
            obj._label = label
            obj._version = version
            return obj
        elif isinstance(obj, Mapping):
            dataset = DatasetContainer(**obj)
            dataset._namespace = namespace
            dataset._label = label
            dataset._version = version
            return dataset
        raise TypeError(INVALID_DUMPER.format(label, version))

    def load(self, obj):
        """
        Load native python object from h5preserve representation

        Parameters
        ----------
        obj
            the object to dump
        """
        # pylint: disable=protected-access
        if not isinstance(obj, ContainerBase):
            raise TypeError(NOT_LOADABLE.format(type(obj)))
        if obj._namespace not in self:
            raise RuntimeError(UNKNOWN_NAMESPACE.format(obj._namespace))
        loaders = self._registries[obj._namespace].loaders
        if obj._label not in loaders:
            raise RuntimeError(
                LABEL_NOT_IN_NAMESPACE.format(obj._label, obj._namespace)
            )
        loaders = loaders[obj._label]
        if None in loaders:
            loader = loaders[None]
        elif all in loaders:
            loader = loaders[all]
        elif obj._version in loaders:
            loader = loaders[obj._version]
        else:
            try:
                loader = loaders[any]
            except KeyError:
                raise RuntimeError(
                    NO_SUITABLE_LOADER.format(obj._label, obj._version)
                )
        return loader(obj, self)

    def lock_version(self, cls, version):
        """
        Lock output version for a specific class

        Parameters
        ----------
        cls : any class
            the class to lock the version of
        version : integer, any, all, None
            the version which will always be used
        """
        self._version_lock[cls] = version


class ContainerBase(MutableMapping):
    # pylint: disable=abstract-method,missing-docstring
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        self._namespace = attrs.pop(H5PRESERVE_ATTR_NAMESPACE, None)
        self._label = attrs.pop(H5PRESERVE_ATTR_LABEL, None)
        self._version = attrs.pop(H5PRESERVE_ATTR_VERSION, None)
        self.attrs = attrs


class GroupContainer(ContainerBase):
    """
    Representation of an hdf5 group for use in h5preserve.

    Parameters
    ----------
    attrs : Mapping
        mapping containing the attributes of the group
    **kwargs
        datasets or subgroups to add to the group
    """
    def __init__(self, attrs=None, **kwargs):
        super(GroupContainer, self).__init__(attrs)
        self._group_members = {}
        self.update(kwargs)

    def __getitem__(self, key):
        return self._group_members[key]

    def __setitem__(self, key, val):
        self._group_members[key] = val

    def __delitem__(self, key):
        self._group_members.__delitem__(key)

    def __iter__(self):
        return iter(self._group_members)

    def __len__(self):
        return len(self._group_members)


class DatasetContainer(ContainerBase):
    """
    Representation of an hdf5 group for use in h5preserve.

    Parameters
    ----------
    attrs : Mapping
        mapping containing the attributes of the group
    **kwargs
        properties of the group, which get passed to create group
    """
    def __init__(self, attrs=None, **kwargs):
        super(DatasetContainer, self).__init__(attrs)
        self._dataset_members = {}
        self.update(kwargs)

    def __getitem__(self, key):
        if key == "attrs":
            return self.attrs
        return self._dataset_members[key]

    def __setitem__(self, key, val):
        if key in ALLOWED_DATASET_KEYS:
            self._dataset_members[key] = val
        else:
            raise TypeError(INVALID_DATASET_OPTION.format(key))

    def __delitem__(self, key):
        self._dataset_members.__delitem__(key)

    def __iter__(self):
        return iter(self._dataset_members)

    def __len__(self):
        return len(self._dataset_members)


class Registry(object):
    """
    Register of functions for converting between hdf5 and python.

    This is the core of h5preserve, containing the information about how to
    convert to and from hdf5 files, what version to use, and the namespace of
    created data.

    Parameters
    ----------
    name : string
        name of registry for identification purposes
    """
    def __init__(self, name):
        self._name = name
        self._frozen = False
        self.dumpers = defaultdict(dict)
        self.loaders = defaultdict(dict)

    @property
    def name(self):
        """str: name of the registry"""
        return self._name

    def freeze(self):
        """
        Freeze the registry, preventing further changes to the registry.
        """
        self._frozen = True

    def dumper(self, cls, label, version):
        """
        Decorator function to create a dumper function.

        Parameters
        ----------
        cls : any class
            the class which this dumper operates on
        label : string
            the label or tag associated with this class
        version : integer, any, all, None
            The version of the output that this function returns.
        """
        def add_dumper(new_dumper):
            # pylint: disable=missing-docstring
            self.dumpers[cls][version] = _DumperMap(
                label=label, func=new_dumper
            )
        return add_dumper

    def loader(self, label, version):
        """
        Decorator function to create a loader function.

        Parameters
        ----------
        label : string
            the label or tag associated with this class
        version : integer, any, all, None
            The version of the output that this function reads.
        """
        def add_loader(new_loader):
            # pylint: disable=missing-docstring
            self.loaders[label][version] = new_loader
        return add_loader


class H5PreserveGroup(MutableMapping):
    """
    Thin wrapper around :class:`h5py.Group` to automatically use h5preserve
    when accessing the group contents.

    Parameters
    ----------
    h5py_group : ``h5py.Group``
    registries : RegistryContainer
        the collection of registries that you want to use to read from the hdf5
        file
    """
    def __init__(self, h5py_group, registries):
        self._h5py_group = h5py_group
        self.registries = registries

    def __getitem__(self, key):
        return self.registries.from_file(self._h5py_group[key])

    def __setitem__(self, key, val):
        self.registries.to_file(self._h5py_group, key, val)

    def __delitem__(self, key):
        del self._h5py_group[key]

    def __iter__(self):
        for key in self._h5py_group:
            yield key

    def __len__(self):
        return len(self._h5py_group)

    @property
    def h5py_group(self):
        """
        h5py.Group: the instance of ``h5py.Group`` which ``H5PreserveGroup``
        wraps
        """
        return self._h5py_group

    def create_group(self, name):
        """
        Creates a new group in the associated hdf5 file

        Parameters
        ----------
        name : string, or other identifier accepted by h5py
            name of the new group

        Returns
        -------
        H5PreserveGroup
            The new group wrapped by H5PreserveGroup
        """
        return H5PreserveGroup(
            self._h5py_group.create_group(name), self.registries
        )

    def require_group(self, name):
        """
        Returns the group associated with ``name``, creating it if necessary.

        Parameters
        ----------
        name : string, or other identifier accepted by h5py
            name of the desired group

        Returns
        -------
        H5PreserveGroup
            The group wrapped by H5PreserveGroup
        """
        return H5PreserveGroup(
            self._h5py_group.require_group(name), self.registries
        )


class H5PreserveFile(H5PreserveGroup):
    """
    Thin wrapper around ``h5py.File`` to automatically use h5preserve when
    accessing the file contents.

    Acts like ``h5preserve.H5PreserveGroup``, but allows access to the
    associated ``h5py.File`` instance via ``h5py_file``.

    Parameters
    ----------
    filename : string, or other identifier accepted by ``h5py.File``
    registries : RegistryContainer
        the collection of registries that you want to use to read from the hdf5
        file
    **kwargs
        additional keyword arguments to pass to ``h5py.File``
    """
    def __init__(self, filename, registries, **kwargs):
        self._h5py_file = h5py.File(filename, **kwargs)
        super(H5PreserveFile, self).__init__(
            h5py_group=self._h5py_file["/"],
            registries=registries
        )

    def close(self):
        # pylint: disable=missing-docstring
        self._h5py_file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False

    @property
    def h5py_file(self):
        """
        h5py.File: the instance of ``h5py.File`` which ``H5PreserveFile`` wraps
        """
        return self._h5py_file


def open(filename, registries, **kwargs):
    """
    Open a hdf5 file wrapped with h5preserve.

    Parameters
    ----------
    filename : string, or other identifier accepted by ``h5py.File``
    registries : RegistryContainer
        the collection of registries that you want to use to read from the hdf5
        file
    **kwargs
        additional keyword arguments to pass to ``h5py.File``
    """
    return H5PreserveFile(filename, registries, **kwargs)


def new_registry_list(*registries):
    """
    Create a new list of registries which includes builtin registries

    Parameters
    ----------
    *registries : list of Registry
        the list of registries to be associated with this container
    """
    return RegistryContainer(*registries)
