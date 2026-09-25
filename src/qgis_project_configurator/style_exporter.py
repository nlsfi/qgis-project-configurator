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
from pathlib import Path

from qgis.core import (
    QgsMapLayer,
    QgsProject,
)

from qgis_project_configurator.models import (
    CompiledConfig,
    LayerGroup,
    LayerTreeNode,
    VectorLayer,
)
from qgis_project_configurator.qgis_utils import save_style

LOGGER = logging.getLogger(__name__)


class StyleExporter:
    def __init__(
        self,
        project: QgsProject,
        config: CompiledConfig,
    ) -> None:
        self.project = project
        self.config = config

    def _map_layer_names_to_style_files(self) -> dict[str, Path | None]:
        style_files_by_layer_path = {}

        def _collect_layer_styles(
            node: LayerTreeNode, path: list | None = None
        ) -> None:
            path = path or []
            path = [*path, node.name]
            if isinstance(node, VectorLayer):
                style_files_by_layer_path["/".join(path)] = node.style_file
                return
            if isinstance(node, LayerGroup):
                for child in node.children:
                    _collect_layer_styles(child, path)

        for node in self.config.layer_tree:
            _collect_layer_styles(node)
        return style_files_by_layer_path

    def _export_layer_style(self, layer: QgsMapLayer, style_path: Path) -> None:
        success = save_style(layer, style_path)
        if success:
            LOGGER.info("Saved style for %s to path %s", layer.name(), style_path)
        else:
            LOGGER.error("Failed to save style for %s (%s)", layer.name(), style_path)

    def _layer_path_in_layer_tree(self, layer: QgsMapLayer) -> str:
        root_node = self.project.layerTreeRoot()
        if root_node is None:
            msg = "Cannot get layer tree root"
            raise RuntimeError(msg)
        layer_node = root_node.findLayer(layer)
        if layer_node is None:
            msg = f"Layer {layer.name()} not found in layer tree"
            raise RuntimeError(msg)
        path = [layer.name()]
        while (layer_node := layer_node.parent()) is not None:
            if group_name := layer_node.name():
                path.append(group_name)
        return "/".join(reversed(path))

    def export_layer_styles(self, layers: list[QgsMapLayer]) -> None:
        style_map = self._map_layer_names_to_style_files()
        for layer in layers:
            layer_path = self._layer_path_in_layer_tree(layer)
            style_file = style_map.get(layer_path)
            if style_file is None:
                LOGGER.error("No style file configured for layer %s", layer.name())
            else:
                self._export_layer_style(layer, style_file)
