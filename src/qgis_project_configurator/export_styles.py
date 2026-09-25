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

from qgis.core import QgsMapLayer, QgsProject

from qgis_project_configurator.config_compiler import ConfigCompiler
from qgis_project_configurator.qgis_utils import read_project_entry
from qgis_project_configurator.style_exporter import StyleExporter
from qgis_project_configurator.yaml_loader import load_config

LOGGER = logging.getLogger(__name__)


def export_layer_styles(layers: list[QgsMapLayer], project: QgsProject) -> None:
    """Export layer styles."""
    LOGGER.info("exporting selected layer styles")
    config_path = read_project_entry(
        project, scope="qgis_project_configurator", key="config_path"
    )
    if not isinstance(config_path, Path):
        LOGGER.error("Config file path does not exist: %s", config_path)
        return
    product_version = read_project_entry(
        project, scope="qgis_project_configurator", key="product_version"
    )
    if not isinstance(product_version, str):
        LOGGER.error("Product version malformatted: %s", product_version)
        return
    data_source = read_project_entry(
        project, scope="qgis_project_configurator", key="data_source"
    )
    if not isinstance(data_source, (str, Path)):
        LOGGER.error("Data source malformatted: %s", data_source)
        return
    if config_path and product_version and data_source:
        compiled_config = ConfigCompiler(
            raw_config=load_config(config_path),
            config_dir=config_path.parent,
            data_source=data_source,
            project_dir=Path("placeholder"),  # TODO: not needed here
            product_version=product_version,
        ).compile()
        StyleExporter(
            project=project,
            config=compiled_config,
        ).export_layer_styles(layers=layers)
    else:
        LOGGER.error("project lacks needed metadata")
