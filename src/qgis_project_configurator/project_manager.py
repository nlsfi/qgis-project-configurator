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
from dataclasses import asdict
from pathlib import Path

from qgis.core import QgsCoordinateReferenceSystem, QgsProject

from qgis_project_configurator.types import ProjectEntry, ProjectProperties

LOGGER = logging.getLogger(__name__)


def read_project_entry(
    project: QgsProject, scope: str, key: str, default_value: None = None
) -> None | Path | str:
    """Read an entry from a QGIS project.

    Automatically transforms paths to pathlib.Path.
    """
    value, type_conversion_success = project.readEntry(
        scope,
        key,
        default_value,
    )
    if not type_conversion_success:
        return default_value
    # If the value is a file path, return as python path
    if Path(value).exists():
        return Path(value).resolve()
    # In other cases return value as is
    return value


class ProjectManager:
    def __init__(
        self,
        project: QgsProject,
        project_properties: ProjectProperties,
        config_path: Path,
        product_version: str,
        data_source: Path | str,
    ) -> None:
        self.project = project
        self.project_properties = project_properties
        self.config_path = config_path
        self.product_version = product_version
        self.data_source = data_source

    def write_project_entry(self, entry: ProjectEntry) -> None:
        LOGGER.info(f"Writing project entry: {asdict(entry)}")
        self.project.writeEntry(scope=entry.scope, key=entry.key, value=entry.value)

    def write_project_properties(self, *, store_metadata: bool = False) -> None:
        for entry in self.project_properties:
            # Crs is a special case. Refactor if these become common.
            if entry.scope == "crs":
                LOGGER.info(f"Setting project crs to: epsg {entry.value}")
                self.project.setCrs(
                    QgsCoordinateReferenceSystem.fromEpsgId(entry.value)
                )
            else:
                self.write_project_entry(entry)
        if store_metadata:
            self._write_project_creation_metadata()

    def _write_project_creation_metadata(self) -> None:
        LOGGER.info("writing project creation metadata into project")
        self.write_project_entry(
            ProjectEntry(
                scope="qgis_project_configurator",
                key="config_path",
                value=str(self.config_path.resolve()),
            )
        )
        self.write_project_entry(
            ProjectEntry(
                scope="qgis_project_configurator",
                key="product_version",
                value=self.product_version,
            )
        )
        data_source = (
            str(self.data_source.resolve())
            if isinstance(self.data_source, Path)
            else self.data_source
        )
        self.write_project_entry(
            ProjectEntry(
                scope="qgis_project_configurator", key="data_source", value=data_source
            )
        )
