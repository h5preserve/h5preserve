# coding: utf-8
"""
h5preserve is a thin wrapper around h5py, providing easier serialisation of
native python types.

:copyright: (c) 2016 James Tocknell
:license: 3-clause BSD
"""
from collections import (
    MutableMapping, namedtuple, defaultdict, MutableSequence,
)
from warnings import warn

import six

from numpy import ndarray
import h5py

# versioneer stuff
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

ALLOWED_DATASET_KEYS = {
    "attrs", "shape", "dtype", "data", "chunks", "maxshape", "fillvalue",
    "size", "compression", "compression_opts", "scaleoffset", "shuffle",
    "fletcher32", "fillvalue", "track_times",
}

EXTERNAL_DUMPED_TYPES = {
    h5py.Group,
    h5py.Dataset,
    h5py.SoftLink,
    h5py.ExternalLink,
    ndarray,
}

H5PY_ATTR_WRITABLE_TYPES = {
    int,
    float,
    list,
    tuple,
    ndarray,
}
H5PY_ATTR_WRITABLE_TYPES.add(six.text_type)
H5PY_ATTR_WRITABLE_TYPES.add(six.binary_type)

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
NO_PATH = "No path defined for hard link."
ATTR_NOT_DUMPED = "Attribute {}={} has not been dumped."

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
        Return an representation of a hdf5 object from a hdf5 file

        Parameters
        ----------
        h5py_obj : a ``h5py`` object, e.g. group, dataset
        """
        namespace = h5py_obj.attrs.get(H5PRESERVE_ATTR_NAMESPACE)
        if namespace is None:
            if isinstance(h5py_obj, h5py.Group):
                return H5PreserveGroup(h5py_group=h5py_obj, registries=self)
            warn(
                "No type information about object, returning native h5py"
                "object"
            )
            return h5py_obj
        elif namespace in self._registries:
            return self._h5py_to_h5preserve(h5py_obj)
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
        Dump h5preserve object to hdf5 file

        Parameters
        ----------
        h5py_group : ``h5py.Group``
            the group to add the object to
        key : string
            the name for the object
        val
            the object to add
        """
        if isinstance(val, ContainerBase):
            self._write_containers_to_file(h5py_group, key, val)
        elif isinstance(val, HardLink):
            if val.h5py_obj is None:
                # pylint: disable=protected-access
                val._set_file(h5py_group.file)
            h5py_group[key] = val.h5py_obj
        elif isinstance(val, h5py.SoftLink):
            h5py_group[key] = val
        elif isinstance(val, h5py.ExternalLink):
            h5py_group[key] = val
        elif isinstance(val, ndarray):
            h5py_group[key] = val
        else:
            raise TypeError(
                UNKNOWN_H5PRESERVE_TYPE.format(type(val))
            )

    def _write_containers_to_file(self, h5py_group, key, val):
        """
        Write instances of ContainerBase to an hdf5 file
        """
        for item_name, item in val.attrs.items():
            if not isinstance(item, tuple(H5PY_ATTR_WRITABLE_TYPES)):
                raise TypeError(ATTR_NOT_DUMPED.format(item_name, item))
        if isinstance(val, GroupContainer):
            new_obj = h5py_group.create_group(key)
            new_obj.attrs.update(val.attrs)
            for obj_name, obj_val in val.items():
                self.to_file(new_obj, obj_name, obj_val)
        elif isinstance(val, DatasetContainer):
            new_obj = h5py_group.create_dataset(
                key, **val
            )
            new_obj.attrs.update(val.attrs)
        # pylint: disable=protected-access
        if val._label is not None:
            new_obj.attrs[H5PRESERVE_ATTR_LABEL] = val._label
        if val._namespace is not None:
            new_obj.attrs[H5PRESERVE_ATTR_NAMESPACE] = val._namespace
        if val._version is not None:
            new_obj.attrs[H5PRESERVE_ATTR_VERSION] = val._version
        # pylint: enable=protected-access

    def dump(self, obj):
        """
        Dump native python object to h5preserve representation

        Parameters
        ----------
        obj
            the object to dump
        """
        # pylint: disable=unidiomatic-typecheck
        if isinstance(obj, HardLink):
            return obj
        elif type(obj) in EXTERNAL_DUMPED_TYPES:
            return obj
        # pylint: enable=unidiomatic-typecheck
        converted_obj = self._obj_to_h5preserve(obj)
        if isinstance(converted_obj, tuple(RECURSIVE_DUMPING_TYPES)):
            for key, val in converted_obj.items():
                converted_obj[key] = self.dump(val)
        return converted_obj

    def _obj_to_h5preserve(self, obj):
        """convert python object to h5preserve representation"""
        if isinstance(obj, ContainerBase):
            return obj
        val_type = type(obj)
        for registry in self:
            # pylint: disable=protected-access
            if val_type in self._registries[registry].dumpers:
                namespace = registry
                dumpers = self._registries[registry].dumpers[val_type]
                break
        else:
            raise TypeError(NOT_DUMPABLE.format(val_type))

        # pylint: disable=protected-access
        if val_type in self._version_lock:
            version = self._version_lock[val_type]
        # pylint: enable=protected-access
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
        obj = dumper(obj)
        if isinstance(obj, ContainerBase):
            # pylint: disable=protected-access
            obj._namespace = namespace
            obj._label = label
            obj._version = version
            # pylint: enable=protected-access
            return obj
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
        elif obj._namespace is None:
            return obj
        elif obj._namespace not in self:
            raise RuntimeError(UNKNOWN_NAMESPACE.format(obj._namespace))
        # pylint: enable=protected-access

        if isinstance(obj, GroupContainer):
            new_obj = GroupContainer(
                attrs=obj.attrs,
                **{key: self.load(item) for key, item in obj.items()}
            )
            # pylint: disable=protected-access
            new_obj._namespace = obj._namespace
            new_obj._label = obj._label
            new_obj._version = obj._version
            # pylint: enable=protected-access
            obj = new_obj

        return self._get_loader(obj)(obj)

    def _get_loader(self, obj):
        """
        get the loader for obj
        """
        # pylint: disable=protected-access
        loaders = self._registries[obj._namespace].loaders
        if obj._label not in loaders:
            raise RuntimeError(
                LABEL_NOT_IN_NAMESPACE.format(obj._label, obj._namespace)
            )
        loaders = loaders[obj._label]
        if obj._version is None and None in loaders:
            return loaders[None]
        elif all in loaders:
            return loaders[all]
        elif obj._version in loaders:
            return loaders[obj._version]
        try:
            return loaders[any]
        except KeyError:
            raise RuntimeError(
                NO_SUITABLE_LOADER.format(obj._label, obj._version)
            )

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

    def __repr__(self):
        return "GroupContainer(attrs={attrs!r}, {group_items})".format(
            attrs=self.attrs,
            group_items=", ".join(
                "{key!r}={val!r}".format(key=key, val=val)
                for key, val in self._group_members.items()
                if val is not None
            )
        )


class DatasetContainer(ContainerBase):
    """
    Representation of an hdf5 dataset for use in h5preserve.

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

    def __repr__(self):
        return "DatasetContainer(attrs={attrs!r}, {dataset})".format(
            attrs=self.attrs,
            dataset=", ".join(
                "{key!r}={val!r}".format(key=key, val=val)
                for key, val in self._dataset_members.items()
                if val is not None
            )
        )


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
        version : integer, None
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
        return self.registries.load(
            self.registries.from_file(self._h5py_group[key])
        )

    def __setitem__(self, key, val):
        self.registries.to_file(
            self._h5py_group,
            key,
            self.registries.dump(val)
        )

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
    h5py_file : a ``h5py.File``
        the hdf5 file to wrap
    registries : RegistryContainer
        the collection of registries that you want to use to read from the hdf5
        file
    """
    def __init__(self, h5py_file, registries):
        self._h5py_file = h5py_file
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


class HardLink(object):
    # pylint: disable=too-few-public-methods
    """
    Represent a h5py hard link to be created via h5preserve.

    Parameters
    ----------
    obj : string, h5py.Group or h5py.Dataset
        the h5py object that the hard link points to, can either be an h5py
        object, or a string with the absolute path of the object
    """
    def __init__(self, obj):
        if isinstance(obj, str):
            self._path = obj
            self._h5py_obj = None
        else:
            self._h5py_obj = obj
            self._path = None

    @property
    def h5py_obj(self):
        """
        h5py.Group or h5py.Dataset: the object which the hard link will point
        to
        """
        return self._h5py_obj

    @property
    def path(self):
        """
        The path this object points to
        """
        return self._path

    def _set_file(self, f):
        """
        set file associated with the hard link
        """
        if self._path is not None:
            self._h5py_obj = f[self._path]
        else:
            raise RuntimeError(NO_PATH)

    def __repr__(self):
        if self._path is not None:
            return "HardLink(path={path})".format(path=self.path)
        else:
            return "HardLink(h5py_obj={obj})".format(obj=self.h5py_obj)


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
    return H5PreserveFile(h5py.File(filename, **kwargs), registries)


def new_registry_list(*registries):
    """
    Create a new list of registries which includes builtin registries.

    Parameters
    ----------
    *registries : list of Registry
        the list of registries to be associated with this container
    """
    from .additional_registries import (
        none_python_registry, builtin_numbers_registry,
        builtin_text_registry, sequence_as_dataset_registry,
    )
    return RegistryContainer(
        none_python_registry,
        builtin_numbers_registry,
        builtin_text_registry,
        sequence_as_dataset_registry,
        *registries
    )

RECURSIVE_DUMPING_TYPES = {
    GroupContainer
}
