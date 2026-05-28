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

import json
import logging
from dataclasses import asdict
from pathlib import Path

from qgis.core import QgsProcessingFeedback, QgsProject

from qgis_project_configurator.config import ConfigCompiler
from qgis_project_configurator.layer_manager import LayerManager
from qgis_project_configurator.layout_manager import LayoutManager
from qgis_project_configurator.map_theme_manager import MapThemeManager
from qgis_project_configurator.project_manager import ProjectManager
from qgis_project_configurator.runtimeprofiler import profiler

LOGGER = logging.getLogger(__name__)


def create_project(  # noqa: PLR0913 TODO: refactor to use CreateProjectParams
    project: QgsProject,
    config: dict,
    data_source: str | Path,
    product_version: str,
    config_path: Path,
    target_project_path: Path,
    feedback: QgsProcessingFeedback,
    *,
    store_metadata: bool = False,
    dry_run: bool = False,
) -> None:
    """The main method for creating a qgis project.

    To be used both in plugin and library code.
    """
    profiler.clear()

    compiled_config = ConfigCompiler(
        raw_config=config,
        config_dir=config_path.parent,
        data_source=data_source,
        project_dir=target_project_path.parent,
        product_version=product_version,
    ).compile()
    if dry_run:
        LOGGER.info(
            f"""Compiled config:\n {
                json.dumps(asdict(compiled_config), indent=2, default=str)
            }"""
        )
        return
    layer_manager = LayerManager(
        project=project,
        config=compiled_config,
        map_theme_manager=MapThemeManager(project),
    )
    layout_manager = LayoutManager(
        project=project,
        layouts=compiled_config.layouts,
    )
    project_manager = ProjectManager(
        project=project,
        project_properties=compiled_config.project_properties,
        config_path=config_path,
        data_source=data_source,
        product_version=product_version,
    )
    layer_manager.load_layers(feedback)
    layout_manager.load_layouts(feedback)
    project_manager.write_project_properties(store_metadata=store_metadata)


def write_project(project: QgsProject, project_path: Path) -> None:
    """Write project to file, creating necessary directories if they do not exist."""
    if not project_path.parent.exists():
        project_path.parent.mkdir(parents=True, exist_ok=True)
    write_success = project.write(str(project_path))
    if not write_success:
        LOGGER.error(f"Could not write to project: {project_path}")
        return
    LOGGER.info(f"Project written to {project_path}")
