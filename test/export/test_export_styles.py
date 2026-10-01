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

# Copyright (C) 2026 QGIS Project Configurator Contributors.
#
# This file is part of QGIS Project Configurator.
#
# QGIS Project Configurator is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
# ... (rest of license) ...

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from qgis_project_configurator.export_styles import export_layer_styles


def test_export_layer_styles(mocker: MockerFixture) -> None:
    mock_read_entry = mocker.patch(
        "qgis_project_configurator.export_styles.read_project_entry"
    )
    mock_exporter_cls = mocker.patch(
        "qgis_project_configurator.export_styles.StyleExporter"
    )

    mocker.patch("qgis_project_configurator.export_styles.ConfigCompiler")
    mocker.patch("qgis_project_configurator.export_styles.load_config")

    mock_read_entry.side_effect = [
        Path("/path/to/config.yaml"),
        "default",
        "fake_source.gpkg",
    ]

    mock_project = MagicMock()
    mock_layers = [MagicMock()]

    export_layer_styles(layers=mock_layers, project=mock_project)

    mock_exporter_instance = mock_exporter_cls.return_value
    mock_exporter_instance.export_layer_styles.assert_called_once_with(
        layers=mock_layers
    )


@pytest.mark.parametrize(
    "mocked_project_reads",
    [
        ["/invalid/path/as/string.yaml", "default", "gpkg"],
        [Path("/path/to/config.yaml"), 123, "gpkg"],
        [Path("/path/to/config.yaml"), "default", ["invalid_data_source_as_list"]],
    ],
    ids=["invalid_path_type", "invalid_default_type", "invalid_source_type"],
)
def test_export_layer_styles_does_not_export_with_wrong_params(
    mocker: MockerFixture,
    mocked_project_reads: list,
) -> None:
    mock_read_entry = mocker.patch(
        "qgis_project_configurator.export_styles.read_project_entry"
    )
    mock_exporter_cls = mocker.patch(
        "qgis_project_configurator.export_styles.StyleExporter"
    )

    mock_read_entry.side_effect = mocked_project_reads

    export_layer_styles(layers=[], project=MagicMock())

    mock_exporter_cls.assert_not_called()
