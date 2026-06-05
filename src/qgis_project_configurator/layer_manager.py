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
    QgsDataSourceUri,
    QgsLayerTree,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsProcessingFeedback,
    QgsProject,
    QgsVectorLayer,
)

from qgis_project_configurator.map_theme_manager import MapThemeManager
from qgis_project_configurator.qgis_utils import save_style
from qgis_project_configurator.runtimeprofiler import profile_function, profiler
from qgis_project_configurator.types import (
    CompiledConfig,
    EmbeddedLayerGroup,
    GpkgSource,
    LayerGroup,
    LayerTreeNode,
    MapThemeNames,
    MapThemes,
    PostgisSource,
    Scale,
    VectorLayer,
)

NON_BREAK_SPACE = "\xa0"

LOGGER = logging.getLogger(__name__)


class LayerManager:
    def __init__(
        self,
        project: QgsProject,
        config: CompiledConfig,
        map_theme_manager: MapThemeManager,
    ) -> None:
        self.project = project
        self.config = config
        self.layers_by_map_themes: MapThemes = {}
        self.map_theme_manager = map_theme_manager

        self._map_layer_count = self.config.count_map_layers()
        self._added_map_layers = 0

    def _progress(self) -> float:
        return (
            self._added_map_layers / self._map_layer_count * 100
            if self._map_layer_count
            else 0
        )

    def _load_postgis_layer(
        self, layer_name: str, source: PostgisSource
    ) -> QgsVectorLayer:
        uri = QgsDataSourceUri()
        uri.setParam("service", source.service)
        uri.setDataSource(
            source.schema,
            source.table,
            source.geom_column,
        )
        return QgsVectorLayer(
            path=uri.uri(expandAuthConfig=False),
            baseName=layer_name,
            providerLib="postgres",
        )

    def _load_gpkg_layer(self, layer_name: str, source: GpkgSource) -> QgsVectorLayer:
        uri = f"{source.path!s}|layername={source.table}"
        return QgsVectorLayer(
            path=uri,
            baseName=layer_name,
            providerLib="ogr",
        )

    @profile_function("load style")
    def _load_layer_style(self, style_file: Path, layer: QgsVectorLayer) -> None:
        if style_file.exists():
            LOGGER.info(f"loading style from: {style_file}")
            message, success = layer.loadNamedStyle(str(style_file))
            if not success:
                LOGGER.error(f"loading style failed: {message}")
        else:
            LOGGER.error(f"style file not found: {style_file}")

    @profile_function("set scale")
    def _set_layer_scale(self, layer: QgsVectorLayer, scale: Scale) -> None:
        layer.setScaleBasedVisibility(True)
        layer.setMinimumScale(scale.min or 0)
        layer.setMaximumScale(scale.max or 0)

    # recursively add layer tree nodes
    def _add_layer_tree_node(  # noqa: C901, PLR0912 TODO: refactor to separate functions
        self,
        node: LayerTreeNode,
        parent_group: QgsLayerTreeGroup | QgsLayerTree | None = None,
        level: int | None = None,
        *,
        feedback: QgsProcessingFeedback,  # keyword argument only
    ) -> None:
        if level is None:
            level = 0
        if feedback.isCanceled():
            return

        if not parent_group:
            parent_group = self.project.layerTreeRoot()
            if not parent_group:
                feedback.reportError("cannot initialize layer tree")
                return

        if isinstance(node, LayerGroup):
            feedback.pushInfo(f"{level * 2 * NON_BREAK_SPACE}{node.name}")
            group = parent_group.addGroup(node.name)
            group.setExpanded(False)
            for child in node.children:
                self._add_layer_tree_node(
                    child, group, level=level + 1, feedback=feedback
                )

        elif isinstance(node, EmbeddedLayerGroup):
            feedback.pushInfo(
                f"{level * 2 * NON_BREAK_SPACE}{node.name} - embedded group from {node.source}"  # noqa: E501
            )
            LOGGER.info(f"embedding group {node.name} from {node.source}")
            embedded_group = self.project.createEmbeddedGroup(
                node.name,
                str(node.source),
                invisibleLayers=[],
            )
            if embedded_group:
                parent_group.addChildNode(embedded_group)
                self._added_map_layers += 1
                feedback.setProgress(self._progress())

        elif isinstance(node, VectorLayer):
            profiler.start(node.name)
            if isinstance(node.data_source, GpkgSource):
                layer = self._load_gpkg_layer(node.name, node.data_source)
            elif isinstance(node.data_source, PostgisSource):
                layer = self._load_postgis_layer(node.name, node.data_source)

            if layer.isValid():
                feedback.pushInfo(f"{level * 2 * NON_BREAK_SPACE}{node.name}")
            else:
                feedback.reportError(
                    f"{level * 2 * NON_BREAK_SPACE}{node.name} - Invalid layer"
                )

            if node.style_file:
                self._load_layer_style(
                    style_file=node.style_file,
                    layer=layer,
                )
            self._set_layer_scale(layer, node.scale)
            self._add_layer_to_map_themes(layer, node.map_theme_names)

            added_layer = self.project.addMapLayer(layer, addToLegend=False)
            if added_layer is None:
                feedback.reportError("Adding layer to project failed")
                return

            if parent_group is not None:
                profiled_add_layer = profile_function("add layer to the tree")(
                    parent_group.addLayer
                )
                profiled_add_layer(layer)

            self.project.layerTreeRoot().findLayer(layer.id()).setExpanded(False)

            profiler.end()
            self._added_map_layers += 1
            feedback.setProgress(self._progress())

    @profile_function("set themes")
    def _add_layer_to_map_themes(
        self, layer: QgsVectorLayer, theme_names: MapThemeNames
    ) -> None:
        for theme_name in theme_names:
            if not self.layers_by_map_themes.get(theme_name):
                self.layers_by_map_themes[theme_name] = []
            self.layers_by_map_themes[theme_name].append(layer)

    @profile_function("Load layers")
    def load_layers(self, feedback: QgsProcessingFeedback) -> None:
        feedback.pushInfo("Loading layers:")
        for node in self.config.layer_tree:
            self._add_layer_tree_node(node, feedback=feedback)

        self.map_theme_manager.add_themes(self.layers_by_map_themes)

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
