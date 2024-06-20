# coding: utf-8
"""
Testing utilities for testing h5preserve and h5preserve-using projects
"""

from itertools import product

from . import RegistryContainer
from .additional_registries import BUILTIN_REGISTRIES


def yield_single_locked(registry_container, skip_builtin=False):
    """
    Generator creating a RegistryContainer with one dumper locked to a specific
    version
    """
    if skip_builtin:
        registries = yield_non_builtin_registries(registry_container)
    else:
        registries = iter(registry_container)
    for registry in registries:
        for cls, versions in registry.dumpers.items():
            for version in versions:
                new_container = RegistryContainer(*registry_container)
                yield new_container.lock_version(cls, version)


def yield_all_locked(registry_container, skip_builtin=False):
    """
    Generator creating a RegistryContainer with all dumpers locked
    """
    cls_versions = []

    if skip_builtin:
        registries = yield_non_builtin_registries(registry_container)
    else:
        registries = iter(registry_container)
    for registry in registries:
        for cls, versions in registry.dumpers.items():
            version_list = []
            for version in versions:
                version_list.append((cls, version))
            cls_versions.append(version_list)
    for locked_set in product(cls_versions):
        new_container = RegistryContainer(*registry_container)
        for cls, version in locked_set:
            new_container.lock_version(cls, version)
        yield new_container


def yield_non_builtin_registries(registry_container):
    """
    Iterate over user-defined registries, skipping builtin
    """
    for registry in registry_container:
        if registry not in BUILTIN_REGISTRIES:
            yield registry
