# Copyright (C) 2026 QGIS Project Configurator Contributors.
#
#
# This file is part of QGIS Project Configurator.
#
# QGIS Project Configurator is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# QGIS Project Configurator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with QGIS Project Configurator.  If not, see <https://www.gnu.org/licenses/>.

"""The YAML configuration file format.

These types describe the raw YAML, before compilation. The compiled result for
one data source and product version is in `models`.

The JSON Schema and the reference docs are generated from this module with
`scripts/generate_config_docs.py`. Attribute docstrings become field descriptions.
Keep this module free of third party and qgis imports.
"""

from typing import Any, Literal, NotRequired, Required, TypedDict

_REPOSITORY_URL = "https://raw.githubusercontent.com/nlsfi/qgis-project-configurator"
_SCHEMA_PATH = "schema/config.schema.json"

MAIN_SCHEMA_URL = f"{_REPOSITORY_URL}/main/{_SCHEMA_PATH}"
"""The schema on the main branch. The `$id` of the schema."""


class PostgisSourceConfig(TypedDict):
    """A PostGIS database connection."""

    type: Literal["postgis"]
    """Data source type."""
    service: str
    """Name of the PostgreSQL connection service (pg_service.conf)."""
    schema: str
    """Database schema of the tables."""
    geom_column: str
    """Name of the geometry column."""
    table: NotRequired[str | None]
    """
    Table name for every layer. It replaces the layer's own `table`.

    Usually left out or null, and each layer sets its `table`.
    """


class GpkgSourceConfig(TypedDict):
    """A GeoPackage file."""

    type: Literal["gpkg"]
    """Data source type."""
    path: str
    """Path to the .gpkg file, relative to the config file."""
    table: NotRequired[str | None]
    """
    Table name for every layer. It replaces the layer's own `table`.

    Usually left out or null, and each layer sets its `table`.
    """


class DataSourceOverride(TypedDict, total=False):
    """Data source settings for one layer or group.

    Merged over the data source with the same name in `data_sources`,
    so only the changed keys are needed.
    """

    type: Literal["postgis", "gpkg"]
    """Data source type."""
    service: str
    """Name of the PostgreSQL connection service (pg_service.conf)."""
    schema: str
    """Database schema of the table."""
    geom_column: str
    """Name of the geometry column."""
    path: str
    """Path to the .gpkg file, relative to the config file."""
    table: str | None
    """Table name. Wins over the layer's `table`."""


class ScaleConfig(TypedDict, total=False):
    """Scale range where the layer is visible.

    Values are scale denominators (1000 means 1:1000). Null or 0 means no limit.
    """

    min: float | None
    """Most zoomed out scale where the layer is visible (e.g. 3000000)."""
    max: float | None
    """Most zoomed in scale where the layer is visible (e.g. 500000)."""


class VectorLayerSettings(TypedDict, total=False):
    """Vector layer settings. Allowed on a layer and in group `defaults`."""

    style: str
    """
    Path to a .qml style file, relative to the config file.

    Use `hidden` to leave the layer out of the project.
    """
    style_overrides: dict[str, str]
    """
    Style per product version: product version name to .qml path or `hidden`.

    Wins over `style` when that product version is selected.
    """
    table: str
    """Table name in the selected data source."""
    scale: ScaleConfig
    """Scale based visibility."""
    data_source_overrides: dict[str, DataSourceOverride]
    """Data source settings per data source name. Merged over `data_sources`."""
    map_themes: list[str]
    """Names of the map themes where the layer is visible."""


class VectorLayerNode(VectorLayerSettings):
    """A vector layer in the layer tree."""

    vector_layer: Required[str]
    """Layer name."""


class GroupNode(TypedDict):
    """A layer group in the layer tree."""

    group: str
    """Group name. Groups with no layers left are not added to the project."""
    children: NotRequired[list["LayerTreeNode"]]
    """Layers and groups inside this group."""
    defaults: NotRequired[VectorLayerSettings]
    """
    Settings for all layers inside this group, also in sub groups.

    Merged with the defaults of parent groups. Nested mappings merge,
    lists and other values replace. A layer's own settings win.
    """


class EmbeddedGroupNode(TypedDict):
    """A layer group embedded from another QGIS project."""

    embedded_group: str
    """Name of the group in the source project."""
    source: str
    """Path to the source QGIS project, relative to the created project's folder."""


type LayerTreeNode = GroupNode | VectorLayerNode | EmbeddedGroupNode
"""
A layer tree item.

The key `group`, `vector_layer` or `embedded_group` sets its kind.
"""

type ProjectPropertyValue = (
    bool | int | str | list[str] | dict[str, ProjectPropertyValue]
)
"""
A project property value, or a mapping of nested keys.

Nested keys are joined with `/`: `A: { B: { C: 1 } }` writes key `B/C`
in scope `A`. A value directly under the scope is written to key `/`.
"""


class ProjectProperties(TypedDict, total=False):
    """Project properties: the first key is the scope, nested keys form the key path.

    Every key other than `crs` is a scope.
    """

    crs: int
    """EPSG code of the project CRS (e.g. 3067). Sets the CRS, not a property."""


# The type of the other keys, as PEP 728 `extra_items` sets it. typing.TypedDict
# takes `extra_items` from Python 3.15 on. Pydantic reads it, mypy does not.
ProjectProperties.__extra_items__ = ProjectPropertyValue  # type: ignore[attr-defined]


class LayoutConfig(TypedDict):
    """A print layout."""

    layout_file: str
    """Path to a .qpt layout template, relative to the config file."""
    atlas_coverage_layer: NotRequired[str]
    """Name of the layer to use as the atlas coverage layer."""


class ProjectConfig(TypedDict, total=False):
    """A QGIS Project Configurator configuration file.

    Any value can be replaced with `!include <path>` to read it from another
    YAML file. The path is relative to the including file.
    """

    data_sources: Required[dict[str, PostgisSourceConfig | GpkgSourceConfig]]
    """
    Data sources by name.

    The data source to use is selected when creating the project.
    """
    product_versions: list[str]
    """Product version names. Used to select styles with `style_overrides`."""
    layer_tree: list[LayerTreeNode]
    """Layers and groups of the project, from top to bottom."""
    project_properties: ProjectProperties
    """Values written to the project with `QgsProject.writeEntry`, and the CRS."""
    layouts: list[LayoutConfig]
    """Print layouts to add to the project."""
    metadata: dict[str, Any]
    """Free-form metadata. Read with `qpc get-metadata`."""
