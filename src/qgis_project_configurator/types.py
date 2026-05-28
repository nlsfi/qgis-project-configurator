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

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from qgis.core import QgsVectorLayer


@dataclass(frozen=True)
class PostgisSource:
    type: str
    service: str
    schema: str
    geom_column: str
    table: str


@dataclass(frozen=True)
class GpkgSource:
    type: str
    path: Path
    table: str


DataSource = PostgisSource | GpkgSource


@dataclass(frozen=True)
class Scale:
    min: int | float | None
    max: int | float | None


MapThemeNames = list[str]


MapThemes = dict[str, list[QgsVectorLayer]]


@dataclass(frozen=True)
class VectorLayer:
    name: str
    style_file: Path | None
    data_source: DataSource
    scale: Scale
    map_theme_names: MapThemeNames


@dataclass(frozen=True)
class LayerGroup:
    name: str
    children: list["LayerTreeNode"]


@dataclass(frozen=True)
class EmbeddedLayerGroup:
    name: str
    source: Path


LayerTreeNode = VectorLayer | LayerGroup | EmbeddedLayerGroup


LayerTree = list[LayerTreeNode]


@dataclass(frozen=True)
class ProjectEntry:
    scope: str
    key: str
    value: Any


ProjectProperties = list[ProjectEntry]


@dataclass(frozen=True)
class PrintLayout:
    layout_file: Path
    atlas_coverage_layer_name: str | None


PrintLayouts = list[PrintLayout]


@dataclass(frozen=True)
class CompiledConfig:
    layer_tree: LayerTree
    project_properties: ProjectProperties
    layouts: PrintLayouts

    def count_map_layers(self) -> int:
        def count(node: LayerTreeNode) -> int:
            if isinstance(node, LayerGroup):
                return sum(count(child_node) for child_node in node.children)
            if isinstance(node, (VectorLayer, EmbeddedLayerGroup)):
                return 1
            return 0

        return sum(count(node) for node in self.layer_tree)
