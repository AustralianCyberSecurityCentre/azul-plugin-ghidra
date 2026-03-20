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

A default entrypoint has been defined in `pyproject.toml`, which will run `main()` in `azul_plugin_ghidra/main.py`

```bash
$ azul-plugin-ghidra
Pavlov probably thought about feeding his dogs every time someone rang a bell.
```

## Python Package management

This python package is managed using a `pyproject.toml` file.

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

Dependencies are managed in the pyproject.toml and debian.txt file.

Version pinning is achieved using the `uv.lock` file.
Because the `uv.lock` file is configured to use a private UV registry, external developers using UV will need to delete the existing `uv.lock` file and update the project configuration to point to the publicly available PyPI registry instead.

To add new dependencies it's recommended to use uv with the command `uv add <new-package>`
    or for a dev package `uv add --dev <new-dev-package>`

The tool used for linting and managing styling is `ruff` and it is configured via `pyproject.toml`

The debian.txt file manages the debian dependencies that need to be installed on development systems and docker images.

Sometimes the debian.txt file is insufficient and in this case the Dockerfile may need to be modified directly to
install complex dependencies.

