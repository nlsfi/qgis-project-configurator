# Configuration & usage example

This directory contains an [example configuration](./config.yaml),
[styles](./styles) and some data to try out qgis-project-configurator.

## Requirements

- QGIS
  - While the configuration file makes no assumptions about QGIS version, the
    example styles are for QGIS version > 4.2
- At least one of the following:
  - Installation of the QGIS plugin (for graphical use within QGIS)
  - Installation of the python package (for command line use)
  - Currently the easiest way to obtain both is to
    [setup a development environment](../DEVELOPMENT.md)
- *Optionally* a container engine & compose provider
  - This is needed *only* if you want to use the included
    [compose.yaml](./compose.yaml) & try out postgis as a data source (see
    [postgis setup](#postgis-setup))

## Plugin usage

### Create project

- In the plugin toolbar, select "Create project"
- A window opens up
- Select the example configuration file with the "Configuration file" file
  selector
- Options for "Style variant" and "Data source" get populated from the
  configuration file content
- Select one of the style variants and data sources
  - Choose "example-gpkg" unless you have [postgis setup](#postgis-setup)
- Click "Run" to create the project
- The plugin builds the project
  - Once done, the map view is not automatically adjusted: right click a layer
    or layer group & select "Zoom to layer" or "Zoom to group" to see the data

### Export styles

- In the previously created project, select the layers you want to export styles
  for
  - Select the layers in the default "Layers" panel of QGIS
  - Ctrl+click to select multiple layers
- Once you have the layers selected in the layer panel (highlighted blue in the
  default QGIS theme), click "Export Styles" in the plugin toolbar
- A confirmation window opens up, listing the layers you are about to export
  styles for
- Click "OK" to export the styles

### Create template configuration

- In any QGIS project, click "Create template map config" in the plugin toolbar
- A window opens up
- Select where you want to write the template configuration
- Select if and where you want to export layer styles
- Select the configuration syntax style (compact / multi-line layers)
- Click "Run" to create the template configuration
- The plugin creates the template configuration
  - Note that the template only handles the layer tree & styles
  - You have to manually edit the configuration file at least to include valid
    data sources

## Command line usage

The qgis-project-configurator command line is usable through the
`qgis-project-configurator` command as well as the `qpc` shorthand.

For usage, options and available subcommands see:

```bash
qpc --help
```

### Create project

For usage & available options see:

```bash
qpc create-project --help
```

An example command:

```bash
qpc create-project --config config.yaml --data-source example-gpkg --style-variant detailed --project example-project.qgs --store-metadata
```

To use the `example-db` datasource, see [postgis setup](#postgis-setup).

### Create template configuration

For usage & available options see:

```bash
qpc create-template --help
```

An example command:

```bash
qpc create-template --project example-project.qgs --config example.yaml --compact
```

### Query metadata

For usage & available options see:

```bash
qpc get-metadata --help
```

An example command:

```bash
qpc get-metadata config.yaml --key nested_metadata
```

## Postgis setup

Make sure docker or podman with a compose provider is installed.

Start the database (this automatically loads `data.gpkg` into the database):

```bash
podman compose up -d
```

The `db` service referenced by the `example-db` datasource in the example
configuration is defined in [`./pg_service.conf`](./pg_service.conf). Point the
`PGSERVICEFILE` environment variable to this file, for example:

```bash
export PGSERVICEFILE=/path/to/pg_service.conf
```

Now you can use the `example-db` datasource, for example:

```bash
qpc create-project --config config.yaml --data-source example-db --style-variant detailed --project example-project.qgs --store-metadata
```
