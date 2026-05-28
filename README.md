# QGIS Project Configurator

A QGIS plugin and command line tool for managing QGIS projects using
configuration files.

## Development

### Setting up python

Setup a python virtual environment that is aware of qgis, for example with
[`qgis-venv-creator`](https://github.com/GispoCoding/qgis-venv-creator):

```console
create-qgis-venv
```

Activate the venv:

```console
source .venv/bin/activate
```

Windows:

```console
.\.venv\Scripts\activate
```

Install dependencies:

```console
pip install -r requirements-dev.txt
```

Install pre-commit hooks:

```console
prek install
```

Install the package in editable mode:

```console
pip install -e .
```

Now you can use the cli for creating projects:

```console
create-project --help
```

### Developing the QGIS plugin

Developing the QGIS plugin is done with
[qgis-plugin-dev-tools](https://github.com/nlsfi/qgis-plugin-dev-tools). the
following assumes you have set up the development environment as above, and are
in the activated virtual environment.

Copy `.env.example` to `.env` and add at the path to your QGIS installation.

Build the plugin:

```console
qpdt build
```

Start qgis with the plugin:

```console
qpdt start
```
