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

import logging
from copy import deepcopy
from pathlib import Path
from typing import Literal

import yaml

from qgis_project_configurator.types import (
    CompiledConfig,
    DataSource,
    EmbeddedLayerGroup,
    GpkgSource,
    LayerGroup,
    LayerTree,
    MapThemeNames,
    PostgisSource,
    PrintLayout,
    PrintLayouts,
    ProjectEntry,
    ProjectProperties,
    Scale,
    VectorLayer,
)
from qgis_project_configurator.yaml_utils import Loader

LOGGER = logging.getLogger(__name__)


def get_config(path: Path):  # noqa: ANN201
    """Load a configuration file using custom YAML loader."""
    with path.open() as f:
        return yaml.load(f, Loader)  # noqa: S506 (using a custom loader)


def _merge_dicts(defaults: dict, override: dict) -> dict:
    """Merge two dicts, override wins."""
    merged = deepcopy(defaults)
    for key, value in override.items():
        # If key exists in both & both values are dicts, merge recursively
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _merge_dicts(merged[key], value)
        # Otherwise overwrite or add the value from override
        else:
            merged[key] = deepcopy(value)
    return merged


class ConfigCompiler:
    def __init__(
        self,
        raw_config: dict,
        config_dir: Path,
        data_source: str | Path,
        project_dir: Path,
        product_version: str | None = None,
    ) -> None:
        self.raw_config = raw_config
        self.config_dir = config_dir
        self.data_source = data_source
        self.product_version = product_version
        self.project_dir = project_dir

    def compile(self) -> CompiledConfig:
        return CompiledConfig(
            layer_tree=self._compile_layer_tree(self.raw_config.get("layer_tree", [])),
            project_properties=self._compile_project_properties(
                self.raw_config.get("project_properties", {})
            ),
            layouts=self._compile_layouts(self.raw_config.get("layouts", [])),
        )

    def _compile_layer_tree(
        self, tree: list, parent_defaults: dict | None = None
    ) -> LayerTree:
        compiled: LayerTree = []
        parent_defaults = parent_defaults or {}
        for node in tree:
            # Get defaults & merge with parent defaults
            node_defaults = node.get("defaults", {})
            node_defaults = _merge_dicts(
                defaults=parent_defaults, override=node_defaults
            )
            # Support partial overrides for data sources everywhere
            # I.e. merge data_source overrides with top level data_sources
            node_defaults["data_source_overrides"] = _merge_dicts(
                defaults=self.raw_config["data_sources"],
                override=node_defaults.get("data_source_overrides", {}),
            )
            if "group" in node:
                subtree = node.get("children", [])
                compiled_group = LayerGroup(
                    name=node["group"],
                    children=self._compile_layer_tree(subtree, node_defaults),
                )
                # only append group if it has children
                if len(compiled_group.children) > 0:
                    compiled.append(compiled_group)
            elif "vector_layer" in node:
                layer_config = _merge_dicts(defaults=node_defaults, override=node)
                compiled_layer = self._compile_vector_layer(layer_config)
                if compiled_layer:
                    compiled.append(compiled_layer)
            elif "embedded_group" in node:
                compiled_embedded_group = EmbeddedLayerGroup(
                    name=node["embedded_group"],
                    source=self._resolve_relative_path(
                        node["source"], relative_to=self.project_dir
                    ),
                )
                if compiled_embedded_group:
                    compiled.append(compiled_embedded_group)
        return compiled

    def _compile_vector_layer(self, layer_config: dict) -> VectorLayer | None:
        layer_name: str | None = layer_config.get("vector_layer")
        if layer_name is None:  # Do we want to fail here instead?
            LOGGER.error("no layer name specified")
            return None
        style: str | None = layer_config.get("style")
        style_overrides: dict | None = layer_config.get("style_overrides")
        scale: dict | None = layer_config.get("scale")
        data_source_overrides: dict | None = layer_config.get("data_source_overrides")
        table: str | None = layer_config.get("table")
        map_themes: list | None = layer_config.get("map_themes")

        compiled_style_file = self._compile_style_file(style, style_overrides)
        if compiled_style_file == "hidden":
            LOGGER.info(f"layer {layer_name} hidden, excluded")
            return None
        compiled_data_source = self._compile_data_source(table, data_source_overrides)
        if not compiled_data_source:
            LOGGER.warning(f"data source not defined for layer {layer_name}, excluded")
            return None
        compiled_scale = self._compile_scale(scale)
        compiled_map_themes = self._compile_map_themes(map_themes)

        return VectorLayer(
            name=layer_name,
            style_file=compiled_style_file,
            data_source=compiled_data_source,
            scale=compiled_scale,
            map_theme_names=compiled_map_themes,
        )

    def _compile_style_file(
        self, style: str | None, style_overrides: dict | None
    ) -> None | Literal["hidden"] | Path:
        style_file = None
        if style_overrides and self.product_version:
            style_file = style_overrides.get(self.product_version)
            if not style_file:
                style_file = style
        elif style:
            style_file = style
        if not style_file or style_file == "hidden":
            return style_file
        return self._resolve_relative_path(style_file)

    def _compile_data_source(
        self, table: str | None, data_source_overrides: dict | None
    ) -> DataSource | None:
        def construct_source_dict() -> dict | None:
            # TODO: refactor source-dict creation
            source_dict = None
            # geopackage override
            if isinstance(self.data_source, Path) and table:
                source_dict = {
                    "type": "gpkg",
                    # resolve path as is
                    "path": self.data_source.resolve(),
                    "table": table,
                }
            # multiple data sources configured for layer (or layer group defaults)
            elif data_source_overrides and self.data_source in data_source_overrides:
                source_dict = data_source_overrides[self.data_source].copy()
                # use table key only if source specific config does not define it
                if table and source_dict.get("table") is None:
                    source_dict["table"] = table
            # only table specified
            # TODO: this branch should never run: we always merge data_sources
            # to data_source_overrides
            elif isinstance(self.data_source, str) and table:
                source_dict = self.raw_config["data_sources"][self.data_source].copy()
                source_dict["table"] = table
            # finally apply relative path in case of gpkg file path defined in config
            if (
                source_dict
                and isinstance(self.data_source, str)
                and source_dict["type"] == "gpkg"
            ):
                source_dict["path"] = self._resolve_relative_path(source_dict["path"])  # type: ignore [arg-type, valid-type]
            return source_dict

        def map_source_dict_to_class(source_dict: dict) -> DataSource:
            if source_dict["type"] == "gpkg":
                return GpkgSource(
                    type="gpkg",
                    path=source_dict["path"],
                    table=source_dict["table"],
                )
            return PostgisSource(
                type=source_dict["type"],
                service=source_dict["service"],
                schema=source_dict["schema"],
                geom_column=source_dict["geom_column"],
                table=source_dict["table"],
            )

        source_dict = construct_source_dict()
        if not source_dict:
            return None

        return map_source_dict_to_class(source_dict)

    def _compile_scale(self, scale: dict | None) -> Scale:
        scale = scale or {}
        return Scale(
            min=scale.get("min"),
            max=scale.get("max"),
        )

    def _compile_map_themes(self, map_themes: list | None) -> MapThemeNames:
        return map_themes or []

    def _compile_project_properties(
        self, raw_properties: dict, entry_path: list[str] | None = None
    ) -> ProjectProperties:
        """Transform project properties dict to a flat list of ProjectEntries."""
        compiled_properties: ProjectProperties = []
        entry_path = entry_path or []
        for key, value in raw_properties.items():
            # Store the path of each project entry. This means mapping the dict
            # hierarchy to the path-like keys expected by QgsProject.writeEntry()
            current_entry_path = [*entry_path, key]
            if isinstance(value, dict):
                # Recurse to allow for arbitrary nesting of keys in config
                compiled_properties.extend(
                    self._compile_project_properties(value, current_entry_path)
                )
            else:
                # Construct a project entry
                compiled_properties.append(
                    ProjectEntry(
                        # Map the first key to scope
                        scope=current_entry_path[0],
                        # Construct the path-like key from the rest, or use
                        # scope root ("/")
                        key="/".join(current_entry_path[1:]) or "/",
                        value=value,
                    )
                )
        return compiled_properties

    def _compile_layouts(self, raw_layouts: list[dict]) -> PrintLayouts:
        compiled_layouts: PrintLayouts = []
        for layout in raw_layouts:
            compiled_layouts.append(
                PrintLayout(
                    layout_file=self._resolve_relative_path(layout["layout_file"]),
                    atlas_coverage_layer_name=layout.get("atlas_coverage_layer", None),
                )
            )
        return compiled_layouts

    def _resolve_relative_path(
        self, subpath: Path | str, relative_to: Path | None = None
    ) -> Path:
        """Resolve a subpath, by default relative to the config dir."""
        relative_to = relative_to or self.config_dir
        return (relative_to / subpath).resolve()
