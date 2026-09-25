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
    QgsMapLayer,
    QgsProcessingFeedback,
    QgsProject,
    QgsVectorLayer,
)

from qgis_project_configurator.map_theme_manager import MapThemeManager
from qgis_project_configurator.models import (
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
from qgis_project_configurator.runtime_profiler import profile_function, profiler

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
    def _load_layer_style(self, style_file: Path, layer: QgsMapLayer) -> None:
        if style_file.exists():
            LOGGER.info("Loading style from: %s", style_file)
            message, success = layer.loadNamedStyle(str(style_file))
            if not success:
                LOGGER.error("Loading style failed: %s", message)
        else:
            LOGGER.error("Style file not found: %s", style_file)

    @profile_function("set scale")
    def _set_layer_scale(self, layer: QgsMapLayer, scale: Scale) -> None:
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

        if parent_group is None:  # in QGIS4 bool(QgsLayerTree()) always False
            parent_group = self.project.layerTreeRoot()
            if parent_group is None:  # in QGIS4 bool(QgsLayerTree()) always False
                feedback.reportError("cannot initialize layer tree")
                return

        if isinstance(node, LayerGroup):
            feedback.pushInfo(f"{level * 2 * NON_BREAK_SPACE}{node.name}")
            group = parent_group.addGroup(node.name)
            if group is None:
                feedback.reportError(f"Cannot create group {node.name}")
                return
            group.setExpanded(False)
            for child in node.children:
                self._add_layer_tree_node(
                    child, group, level=level + 1, feedback=feedback
                )

        elif isinstance(node, EmbeddedLayerGroup):
            feedback.pushInfo(
                f"{level * 2 * NON_BREAK_SPACE}{node.name} - embedded group from {node.source}"  # noqa: E501
            )
            LOGGER.info("Embedding group %s from %s", node.name, node.source)
            embedded_group = self.project.createEmbeddedGroup(
                node.name,
                str(node.source),
                invisibleLayers=[],
            )
            if embedded_group is not None:
                parent_group.addChildNode(embedded_group)
                self._added_map_layers += 1
                feedback.setProgress(self._progress())

        elif isinstance(node, VectorLayer):
            profiler.start(node.name)
            if isinstance(node.data_source, GpkgSource):
                layer = self._load_gpkg_layer(node.name, node.data_source)
            elif isinstance(node.data_source, PostgisSource):
                layer = self._load_postgis_layer(node.name, node.data_source)
            else:
                profiler.end()
                return  # TODO: Only gpkg / postgis vector layers supported
            if layer.isValid():
                feedback.pushInfo(f"{level * 2 * NON_BREAK_SPACE}{node.name}")
            else:
                feedback.reportError(
                    f"{level * 2 * NON_BREAK_SPACE}{node.name} - Invalid layer"
                )

            if node.style_file is not None:
                self._load_layer_style(
                    style_file=node.style_file,
                    layer=layer,
                )
            self._set_layer_scale(layer, node.scale)
            self._add_layer_to_map_themes(layer, node.map_theme_names)

            added_layer = self.project.addMapLayer(layer, addToLegend=False)
            if added_layer is None:
                feedback.reportError("Adding layer to project failed")
                profiler.end()
                return

            if parent_group is not None:
                profiled_add_layer = profile_function("add layer to the tree")(
                    parent_group.addLayer
                )
                profiled_add_layer(layer)

            self._minimize_layer(layer)

            profiler.end()
            self._added_map_layers += 1
            feedback.setProgress(self._progress())

    def _minimize_layer(self, layer: QgsMapLayer) -> None:
        tree_root = self.project.layerTreeRoot()
        if tree_root is not None:
            tree_layer = tree_root.findLayer(layer.id())
            if tree_layer is not None:
                tree_layer.setExpanded(False)

    @profile_function("set themes")
    def _add_layer_to_map_themes(
        self, layer: QgsMapLayer, theme_names: MapThemeNames
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
