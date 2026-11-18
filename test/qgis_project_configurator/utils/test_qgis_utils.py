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
from pytest_mock import MockerFixture
from qgis.core import QgsMapLayer

from qgis_project_configurator.qgis_utils import (
    get_qgis_project_instance,
    read_project_entry,
    save_style,
)

MODULE = "qgis_project_configurator.qgis_utils"


class TestReadProjectEntry:
    def test_returns_default_if_type_conversion_fails(self):
        mock_project = MagicMock()
        mock_project.readEntry.return_value = ("some_value", False)

        result = read_project_entry(
            mock_project, "my_scope", "my_key", default_value="fallback"
        )

        assert result == "fallback"
        mock_project.readEntry.assert_called_once_with("my_scope", "my_key", "fallback")

    def test_returns_resolved_path_if_value_is_existing_file(self, tmp_path: Path):
        temp_file = tmp_path / "test_config.yaml"
        temp_file.touch()
        mock_project = MagicMock()
        mock_project.readEntry.return_value = (str(temp_file), True)

        result = read_project_entry(mock_project, "my_scope", "my_key")

        assert isinstance(result, Path)
        assert result == temp_file.resolve()

    def test_returns_string_if_value_is_not_an_existing_file(self):
        mock_project = MagicMock()
        mock_project.readEntry.return_value = ("a_normal_string", True)

        result = read_project_entry(mock_project, "my_scope", "my_key")

        assert result == "a_normal_string"


class TestSaveStyle:
    def test_save_style_calls_layer_with_correct_flags_and_returns_bool(
        self, tmp_path: Path
    ):
        mock_layer = MagicMock()
        mock_layer.saveNamedStyle.return_value = ("Style saved successfully", True)
        style_file = tmp_path / "layer_style.qml"

        result = save_style(mock_layer, style_file)

        assert result is True
        expected_categories = (
            QgsMapLayer.StyleCategory.Symbology | QgsMapLayer.StyleCategory.Labeling
        )
        mock_layer.saveNamedStyle.assert_called_once_with(
            str(style_file), expected_categories
        )


class TestGetQgisProjectInstance:
    def test_returns_project_if_available(self, mocker: MockerFixture):
        mock_project = MagicMock()
        mocker.patch(
            f"{MODULE}.QgsProject.instance",
            return_value=mock_project,
        )

        result = get_qgis_project_instance()

        assert result == mock_project

    def test_raises_runtime_error_if_none(self, mocker: MockerFixture):
        mocker.patch(
            f"{MODULE}.QgsProject.instance",
            return_value=None,
        )

        with pytest.raises(RuntimeError, match="Cannot access QGIS project instance"):
            get_qgis_project_instance()
