# Pypi

For information about packaging on PyPi see https://packaging.python.org/en/latest/tutorials/packaging-projects/.
First, clear /dist and then build the project using `py -m build` (requires that you install the package `build').
Then, using twine prepare a test release with `py -m twine upload --repository testpypi dist/*`,
 this will prepare a link to the testing version index of pypi.
Install and test package from this index.
If all goes well, then prepate a release for the offical index, using `py -m twine upload dist/*`.

## Checklist
 - run tests and ensure all tests pass
    - remenber to adjust the run slow test variable in tests/__init__.py
 - move version number in pyproject.toml
 - update version in __init__.py of pmkoalas
 - ensure the module `build` is up to date on local python
 - check that all submodules are mentioned in the pyproject toml section 'tool.setuptools'.
 - clear dist
 - build project

## Versioning 

We should follow the versioning guide for python packaging.
See: https://packaging.python.org/en/latest/discussions/versioning/

