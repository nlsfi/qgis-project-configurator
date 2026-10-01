# Configuration guide

A configuration file is a YAML file that describes a QGIS project: data sources,
layers and groups, styles, project properties and print layouts. One file can
make many projects: you select a data source and a product version when you
create the project.

```bash
qpc create-project --config config.yaml --project out/project.qgz \
  --data-source db --product-version public
```

- Every key: [configuration reference](./configuration-reference.md)
- A full example: [example/config.yaml](./example/config.yaml)
- JSON Schema: [schema/config.schema.json](../schema/config.schema.json)

## Top level keys

| Key | Use |
| --- | --- |
| `data_sources` | Named data sources. `--data-source` selects one. |
| `product_versions` | Product version names. `--product-version` selects one. |
| `layer_tree` | Groups and layers, from top to bottom. |
| `project_properties` | Values written with `QgsProject.writeEntry`. |
| `layouts` | Print layout templates (.qpt). |
| `metadata` | Free-form values. Read them with `qpc get-metadata`. |

## Data sources

Each data source has a `type`: `postgis` or `gpkg`.

```yaml
data_sources:
  db: { type: postgis, service: naturalearth, schema: public, geom_column: geom }
  gpkg: { type: gpkg, path: ./data/naturalearth.gpkg }
```

A layer sets its table with `table`. The layer then loads from the selected data
source.

A `table` in a data source replaces the `table` of every layer. So leave it out,
or set it to null.

A layer or a group can change the data source with `data_source_overrides`. It is
merged over `data_sources`, so give only the keys that change:

```yaml
- vector_layer: rivers
  table: rivers
  data_source_overrides:
    db: { schema: hydrography }
```

If `--data-source` is a path to a .gpkg file, all layers load from that file.
The layer's `table` is the layer name in the file. `data_source_overrides` is not
used, and layers without `table` are left out.

## Layer tree

Each item is one of these. The first key tells which:

- `group`: a layer group with `children`. A group with no layers left is not
  added.
- `vector_layer`: a vector layer.
- `embedded_group`: a group embedded from another QGIS project (`source`).

### Defaults

A group can give `defaults` for all layers inside it, also in sub groups:

```yaml
- group: all
  defaults:
    scale: { min: 3000000 }
    map_themes: [ all ]
  children:
    - vector_layer: roads
      table: roads
      map_themes: [ all, traffic ]
```

The merge rules:

- A sub group's defaults are merged over its parent's defaults.
- A layer's own keys are merged over the defaults.
- Mappings (like `scale`) merge key by key.
- Lists (like `map_themes`) and other values replace. They are not appended.

### Styles and product versions

`style` is a .qml file. `style_overrides` gives a style per product version.
The value `hidden` leaves the layer out:

```yaml
- vector_layer: lakes
  table: lakes
  style: hidden
  style_overrides:
    secret: ./styles/lakes.qml
```

Here `lakes` is only in the `secret` product version. Without
`--product-version`, `style_overrides` is not used.

## Project properties

The first key is the scope. Nested keys are joined with `/` to make the key:

```yaml
project_properties:
  WMSServiceTitle: Natural Earth  # scope WMSServiceTitle, key /
  MyScope:
    group:
      value: 1                    # scope MyScope, key group/value
  crs: 3067                       # special: sets the project CRS (EPSG code)
```

A value is text, a whole number, `true` / `false`, or a list of text.
QGIS does not accept decimal numbers or lists of numbers here.

## Paths

- `style`, `style_overrides`, `layout_file` and gpkg `path` are relative to the
  folder of the main config file.
- An embedded group's `source` is relative to the folder of the created project.
- An `!include` path is relative to the folder of the file that has the
  `!include`.

## Splitting the file with `!include`

Any value can come from another YAML file:

```yaml
layer_tree:
  - group: water
    children: !include ./water_layers.yaml
```

Paths inside the included file follow the table above. A style path in an
included file is still relative to the main config file.

## Editor support

The JSON Schema gives autocomplete, hover help and error checks in editors.

In VS Code:

1. Install the
   [YAML extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml).
2. Put this line at the top of the config file. `main` is the newest schema.

   ```yaml
   # yaml-language-server: $schema=https://raw.githubusercontent.com/nlsfi/qgis-project-configurator/main/schema/config.schema.json
   ```

   `qpc create-template` adds this line with the schema of the installed
   version, for example `v0.2.0` in place of `main`. After you update qpc,
   update the version in the line.

3. Tell the extension about `!include` in `settings.json`:

   ```json
   "yaml.customTags": [ "!include scalar" ]
   ```

The editor can not read an included file. It can show a type error on a value
that is an `!include`.

The schema is stricter than the tool: unknown keys and data source types other
than `postgis` and `gpkg` are errors. This finds typos early.

## For developers

The format is defined in `src/qgis_project_configurator/config_format.py`.
The schema and the reference are generated from it. After a change, run:

```bash
uv run python scripts/generate_config_docs.py
```

A test fails if the generated files are not up to date.
