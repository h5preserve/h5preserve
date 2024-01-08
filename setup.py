import setuptools

import versioneer

DESCRIPTION_FILES = ["pypi-intro.rst"]

long_description = []
import codecs
for filename in DESCRIPTION_FILES:
    with codecs.open(filename, 'r', 'utf-8') as f:
        long_description.append(f.read())
long_description = "\n".join(long_description)


setuptools.setup(
    name = "h5preserve",
    version = versioneer.get_version(),
    packages = setuptools.find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = [
        "h5py",
    ],
    python_requires = '>=3.5',
    author = "James Tocknell",
    author_email = "aragilar@gmail.com",
    description = "Thin wrapper around h5py, inspired by camel",
    long_description = long_description,
    license = "3-clause BSD",
    keywords = "hdf5",
    url = "https://h5preserve.readthedocs.io",
    project_urls={
        'Documentation': 'https://h5preserve.readthedocs.io',
        'Source': 'https://github.com/h5preserve/h5preserve/',
        'Tracker': 'https://github.com/h5preserve/h5preserve/issues',
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3 :: Only',
    ],
    cmdclass=versioneer.get_cmdclass(),
)
