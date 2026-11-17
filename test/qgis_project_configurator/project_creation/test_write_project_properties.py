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

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from qgis.core import QgsCoordinateReferenceSystem

from qgis_project_configurator.models import ProjectEntry
from qgis_project_configurator.project_manager import ProjectManager


@pytest.fixture
def mock_project() -> MagicMock:
    return MagicMock()


@pytest.fixture
def project_manager(mock_project: MagicMock) -> ProjectManager:
    return ProjectManager(
        project=mock_project,
        project_properties=[ProjectEntry(scope="scope", key="key", value="value")],
        config_path=Path("/path/to/config.yaml"),
        style_variant="default",
        data_source="gpkg",
    )


def test_write_project_properties_no_metadata(
    project_manager: ProjectManager, mock_project: MagicMock
) -> None:
    project_manager.write_project_properties()

    mock_project.writeEntry.assert_called_once_with(
        scope="scope", key="key", value="value"
    )


def test_write_project_properties_store_metadata(
    project_manager: ProjectManager, mock_project: MagicMock
) -> None:
    project_manager.write_project_properties(store_metadata=True)

    mock_project.writeEntry.assert_any_call(scope="scope", key="key", value="value")
    mock_project.writeEntry.assert_any_call(
        scope="qgis_project_configurator",
        key="config_path",
        value="/path/to/config.yaml",
    )
    mock_project.writeEntry.assert_any_call(
        scope="qgis_project_configurator",
        key="style_variant",
        value="default",
    )
    mock_project.writeEntry.assert_any_call(
        scope="qgis_project_configurator",
        key="data_source",
        value="gpkg",
    )


def test_set_project_crs(
    project_manager: ProjectManager, mock_project: MagicMock
) -> None:
    project_manager.project_properties = [ProjectEntry("crs", "/", 3067)]
    project_manager.write_project_properties()
    mock_project.setCrs.assert_called_once_with(
        QgsCoordinateReferenceSystem.fromEpsgId(3067)
    )
