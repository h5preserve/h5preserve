from __future__ import print_function
from invoke import run, ctask as task, Collection
from invoke.executor import Executor

PACKAGE = "h5preserve"

@task
def make_description(ctx, readme="README.md", description="DESCRIPTION.rst"):
    print("pandoc {readme} -o {description}".format(readme=readme, description=description))

@task(make_description)
def sdist(ctx):
    print("python setup.py sdist")

@task(sdist)
def wheel(ctx, version):
    print("cm-culture dist/{package}-{version}.tar.gz".format(package=PACKAGE, version=version))

@task
def release(ctx, version):
    print("git tag {version}".format(version=version))
    ctx.invoke_execute(ctx, "sdist")
    ctx.invoke_execute(ctx, "wheel", version=version)


### FROM https://github.com/pyinvoke/invoke/issues/170 ###
# Define and configure root namespace
# ===================================

# NOTE: `namespace` or `ns` name is required!
namespace = Collection(
    make_description, sdist, wheel, release
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
