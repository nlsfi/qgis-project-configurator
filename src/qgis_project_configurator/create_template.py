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

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from qgis.core import (
    QgsLayerTreeLayer,
    QgsLayerTreeNode,
    QgsProcessingFeedback,
    QgsProject,
)

from qgis_project_configurator.qgis_utils import save_style


@dataclass
class StyleFolderConfig:
    absolute: Path
    relative: Path


def _embedded_node_to_config(node: QgsLayerTreeNode) -> dict[str, Any]:
    return {
        "embedded_group": node.name(),
        "source": node.customProperty("embedded_project"),
    }


def _group_node_to_config(
    node: QgsLayerTreeNode,
    style_folder_config: StyleFolderConfig | None,
    feedback: QgsProcessingFeedback,
) -> dict[str, Any]:
    return {
        "group": node.name(),
        "children": [
            config
            for n in node.children()
            if (config := _tree_node_to_config(n, style_folder_config, feedback))
            is not None
        ],
    }


def _layer_node_to_config(
    node: QgsLayerTreeLayer,
    style_folder_config: StyleFolderConfig | None,
    feedback: QgsProcessingFeedback,
) -> dict[str, str]:
    layer = node.layer()
    feedback.pushInfo(layer.name())

    formatted_style_path = ""
    if style_folder_config:
        style_filename = f"{layer.name()}.qml"
        style_save_success = save_style(
            layer, style_folder_config.absolute / style_filename
        )
        if style_save_success:
            formatted_style_path = (
                f"./{Path(style_folder_config.relative / style_filename).as_posix()}"
            )
        else:
            feedback.pushWarning(f"Failed to save style for layer: {layer.name()}")

    uri = layer.dataProvider().uri()
    return {
        "vector_layer": layer.name(),
        "style": formatted_style_path,
        "table": uri.table(),
    }


def _tree_node_to_config(
    node: QgsLayerTreeNode,
    style_folder_config: StyleFolderConfig | None,
    feedback: QgsProcessingFeedback,
) -> dict | None:
    if node.nodeType() == QgsLayerTreeNode.NodeType.NodeGroup:
        if node.customProperty("embedded") == 1:
            return _embedded_node_to_config(node)
        return _group_node_to_config(node, style_folder_config, feedback)
    if isinstance(
        node, QgsLayerTreeLayer
    ):  # same as node.nodeType() == QgsLayerTreeNode.NodeType.NodeLayer:
        if node.customProperty("embedded") == 1:
            return None  # Are there actually any single embedded layers?
        return _layer_node_to_config(node, style_folder_config, feedback)

    return None


def create_configuration_template(
    output_file: Path, style_folder: Path | None, feedback: QgsProcessingFeedback
) -> dict:
    """Create a config template."""
    project = QgsProject.instance()
    layer_tree = project.layerTreeRoot()

    if style_folder:
        style_folder.mkdir(parents=True, exist_ok=True)

        relative = Path(os.path.relpath(style_folder, output_file.parent))
        style_folder_config = StyleFolderConfig(style_folder, relative)
    else:
        style_folder_config = None

    config = {
        "data_sources": {
            "<data-source-name>": {
                "type": "postgis",
                "service": None,
                "schema": "public",
                "geom_column": "geom",
            }
        },
        "layer_tree": [
            config
            for node in layer_tree.children()
            if (config := _tree_node_to_config(node, style_folder_config, feedback))
            is not None
        ],
        "product_versions": [],
        "project_properties": {},
        "layouts": [],
    }

    _write_to_yaml(config, output_file)

    return config


def _write_to_yaml(config: dict[str, Any], output_file: Path) -> None:
    with output_file.open("w") as yaml_file:
        yaml.dump(config, yaml_file, sort_keys=False, default_flow_style=False)
