from __future__ import print_function
from invoke import run, ctask as task, Collection
from invoke.executor import Executor

PACKAGE = "h5preserve"
DESCRIPTION = "DESCRIPTION.rst"
CHANGELOG = "CHANGELOG.rst"
DESCRIPTION_FILES = [
    "pypi-intro.rst",
    #CHANGELOG,
]

@task
def make_changelog(ctx):
    print("Building changelog")
    output = run("gitchangelog", hide="out")
    with open(CHANGELOG, mode="w") as f:
        f.write(output.stdout)

@task
def make_description(ctx):
    print("Building description")
    run("pandoc {files} -o {description}".format(
        files=' '.join(DESCRIPTION_FILES),
        description=DESCRIPTION
    ))

@task
def prerelease(ctx):
    #ctx.invoke_execute(ctx, "make_changelog")
    ctx.invoke_execute(ctx, "make_description")

@task(prerelease)
def sdist(ctx):
    print("Building sdist")
    run("python setup.py sdist")

@task(sdist)
def wheel(ctx, version):
    print("Building wheel")
    run("cm-culture dist/{package}-{version}.tar.gz".format(package=PACKAGE, version=version))

@task(prerelease)
def release(ctx):
    try:
        from h5preserve import __version__ as version
    except ImportError:
        raise RuntimeError("Unable to find version")
    print("Releasing version {version}".format(version=version))
    ctx.invoke_execute(ctx, "wheel", version=version)


### FROM https://github.com/pyinvoke/invoke/issues/170 ###
# Define and configure root namespace
# ===================================

# NOTE: `namespace` or `ns` name is required!
namespace = Collection(
    make_description, sdist, wheel, release, prerelease, make_changelog
)

def invoke_execute(context, command_name, **kwargs):
    """
    Helper function to make invoke-tasks execution easier.
    """
    results = Executor(namespace, config=context.config).execute((command_name, kwargs))
    target_task = context.root_namespace[command_name]
    return results[target_task]

namespace.configure({
    'root_namespace': namespace,
    'invoke_execute': invoke_execute,
})
