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
    QgsLayerTreeLayer,
    QgsProject,
    QgsVectorLayer,
)

from qgis_project_configurator.models import (
    CompiledConfig,
    LayerGroup,
    LayerTreeNode,
    VectorLayer,
)
from qgis_project_configurator.qgis_utils import save_style

NON_BREAK_SPACE = "\xa0"

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
        name_to_style = {}

        def recurse(node: LayerTreeNode, path: list | None = None) -> None:
            path = path or []
            path = [*path, node.name]
            if isinstance(node, VectorLayer):
                name_to_style["/".join(path)] = node.style_file
                return
            if isinstance(node, LayerGroup):
                for child in node.children:
                    recurse(child, path)

        for node in self.config.layer_tree:
            recurse(node)
        return name_to_style

    def _export_layer_style(self, layer: QgsVectorLayer, style_path: Path) -> None:
        success = save_style(layer, style_path)
        if success:
            LOGGER.info(f"Saved style for {layer.name()} to path {style_path}")
        else:
            LOGGER.error(f"Failed to save style for {layer.name()} ({style_path})")

    def _layer_path_in_toc(self, layer: QgsLayerTreeLayer) -> str:
        root_node = QgsProject.instance().layerTreeRoot()
        layer_node = root_node.findLayer(layer)
        path = [layer.name()]
        while layer_node := layer_node.parent():
            if group_name := layer_node.name():
                path.append(group_name)

        return "/".join(reversed(path))

    def export_layer_styles(self, layers: list[QgsLayerTreeLayer]) -> None:
        style_map = self._map_layer_names_to_style_files()
        for layer in layers:
            layer_path = self._layer_path_in_toc(layer)
            style_file = style_map.get(layer_path)
            if style_file is None:
                LOGGER.error(f"No style file configured for layer {layer.name()}")
            else:
                self._export_layer_style(layer, style_file)
