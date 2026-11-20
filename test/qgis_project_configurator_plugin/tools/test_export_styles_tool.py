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

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from qgis_project_configurator_plugin.tools.export_styles import export_styles

if TYPE_CHECKING:
    from qgis.gui import QgisInterface

MODULE = "qgis_project_configurator_plugin.tools.export_styles"


def test_export_styles_raises_if_main_window_none(
    mocker: MockerFixture, qgis_iface: "QgisInterface"
) -> None:
    mocker.patch.object(qgis_iface, "mainWindow", return_value=None)

    with pytest.raises(RuntimeError, match="Cannot access main window"):
        export_styles()


def test_export_styles_returns_early_if_dialog_cancelled(
    mocker: MockerFixture, qgis_iface: "QgisInterface"
) -> None:
    mock_main_window = MagicMock()
    mocker.patch.object(qgis_iface, "mainWindow", return_value=mock_main_window)

    mock_dialog_class = mocker.patch(f"{MODULE}.ExportStylesDialog")
    mock_dialog_instance = mock_dialog_class.return_value
    mock_dialog_instance.exec.return_value = False

    mock_get_project = mocker.patch(f"{MODULE}.get_qgis_project_instance")
    mock_export_layer_styles = mocker.patch(f"{MODULE}.export_layer_styles")

    export_styles()

    mock_dialog_class.assert_called_once_with(mock_main_window)
    mock_get_project.assert_not_called()
    mock_export_layer_styles.assert_not_called()


def test_export_styles_success(
    mocker: MockerFixture, qgis_iface: "QgisInterface"
) -> None:
    mock_main_window = MagicMock()
    mocker.patch.object(qgis_iface, "mainWindow", return_value=mock_main_window)

    mock_dialog_class = mocker.patch(f"{MODULE}.ExportStylesDialog")
    mock_dialog_instance = mock_dialog_class.return_value

    mock_dialog_instance.exec.return_value = True

    mock_params = MagicMock()
    mock_params.selected_layers = ["layer_a", "layer_b"]
    mock_dialog_instance.get_params.return_value = mock_params

    mock_project = MagicMock()
    mocker.patch(f"{MODULE}.get_qgis_project_instance", return_value=mock_project)

    mock_export_layer_styles = mocker.patch(f"{MODULE}.export_layer_styles")

    export_styles()

    mock_dialog_class.assert_called_once_with(mock_main_window)
    mock_dialog_instance.get_params.assert_called_once()

    mock_export_layer_styles.assert_called_once_with(
        ["layer_a", "layer_b"],
        project=mock_project,
    )
