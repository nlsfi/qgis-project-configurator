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

from qgis.core import QgsLayerTreeLayer, QgsProject

from qgis_project_configurator.config import ConfigCompiler, get_config
from qgis_project_configurator.layer_manager import LayerManager
from qgis_project_configurator.map_theme_manager import MapThemeManager
from qgis_project_configurator.project_manager import read_project_entry

LOGGER = logging.getLogger(__name__)


def export_layer_styles(layers: list[QgsLayerTreeLayer], project: QgsProject) -> None:
    """Export layer styles."""
    LOGGER.info("exporting selected layer styles")
    config_path = read_project_entry(
        project, scope="qgis_project_configurator", key="config_path"
    )
    if not isinstance(config_path, Path):
        LOGGER.error(f"Config file path does not exist: {config_path}")
        return
    product_version = read_project_entry(
        project, scope="qgis_project_configurator", key="product_version"
    )
    if not isinstance(product_version, str):
        LOGGER.error(f"Product version malformatted: {product_version}")
        return
    data_source = read_project_entry(
        project, scope="qgis_project_configurator", key="data_source"
    )
    if not isinstance(data_source, (str, Path)):
        LOGGER.error(f"Data source malformatted: {data_source}")
        return
    if config_path and product_version and data_source:
        compiled_config = ConfigCompiler(
            raw_config=get_config(config_path),
            config_dir=config_path.parent,
            data_source=data_source,
            project_dir=Path("placeholder"),  # TODO: not needed here
            product_version=product_version,
        ).compile()
        LayerManager(
            project=project,
            config=compiled_config,
            map_theme_manager=MapThemeManager(project),  # TODO: not needed here
        ).export_layer_styles(layers=layers)
    else:
        LOGGER.error("project lacks needed metadata")
