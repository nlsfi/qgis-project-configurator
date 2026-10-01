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

from qgis_project_configurator.models import ProjectEntry
from qgis_project_configurator.project_manager import ProjectManager


@pytest.fixture
def project_manager():
    return ProjectManager(
        project=MagicMock(),
        project_properties=[ProjectEntry(scope="scope", key="key", value="value")],
        config_path=Path("/path/to/config.yaml"),
        style_variant="default",
        data_source="gpkg",
    )


def test_write_project_properties_no_metadata(project_manager: ProjectManager):
    project_manager.write_project_properties()

    project_manager.project.writeEntry.assert_called_once_with(
        scope="scope", key="key", value="value"
    )


def test_write_project_properties_store_metadata(project_manager: ProjectManager):
    project_manager.write_project_properties(store_metadata=True)

    project_manager.project.writeEntry.assert_any_call(
        scope="scope", key="key", value="value"
    )
    project_manager.project.writeEntry.assert_any_call(
        scope="qgis_project_configurator",
        key="config_path",
        value="/path/to/config.yaml",
    )
    project_manager.project.writeEntry.assert_any_call(
        scope="qgis_project_configurator",
        key="style_variant",
        value="default",
    )
    project_manager.project.writeEntry.assert_any_call(
        scope="qgis_project_configurator",
        key="data_source",
        value="gpkg",
    )
