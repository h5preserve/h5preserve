from invoke import run, task

@task
def make_description(readme="README.md", description="DESCRIPTION.rst"):
    run("pandoc {readme} -o {description}".format(
        readme=readme,
        description=description
    ))

@task(make_description)
def sdist():
    run("python setup.py sdist")

@task(sdist)
def wheel():
    run("cm-culture dist/")
