# Azul Plugin Ghidra

Extracting Features From A Binary Using Ghidra Headless.

# Maintenance

As of the 5th of November 2025, Ghidra 12.0 is the most recent version. Ghidra's most recent release files can be accessed
here: https://github.com/NationalSecurityAgency/ghidra/releases 

To bump version numbers, only install-ghidra.sh needs to be updated.

## Installation

```bash
pip install azul-plugin-ghidra
```

### Development editable install

When doing an editable install of a core package so it can be modified it is recommended to use the command:

```bash
# editable_mode=strict ensures that pylance will still work in vscode.
 pip install -e . --config-settings editable_mode=strict
```

## Usage

A default entrypoint has been defined in `setup.py`, which will run `main()` in `azul_plugin_ghidra/main.py`

```bash
$ azul-plugin-ghidra
Pavlov probably thought about feeding his dogs every time someone rang a bell.
```

## Python Package management

This python package is managed using a `setup.py` and `pyproject.toml` file.

Standardisation of installing and testing the python package is handled through tox.
Tox commands include:

```bash
# Run all standard tox actions
tox
# Run linting only
tox -e style
# Run tests only
tox -e test
```

## Dependency management

Dependencies are managed in the requirements.txt, requirements_test.txt and debian.txt file.

The requirements files are the python package dependencies for normal use and specific ones for tests
(e.g pytest, black, flake8 are test only dependencies).

The debian.txt file manages the debian dependencies that need to be installed on development systems and docker images.

Sometimes the debian.txt file is insufficient and in this case the Dockerfile may need to be modified directly to
install complex dependencies.


