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
from qgis.PyQt.QtWidgets import QAction, QMainWindow

from qgis_project_configurator_plugin import classFactory
from qgis_project_configurator_plugin.processing import ProjectManagerProcessingProvider

if TYPE_CHECKING:
    from collections.abc import Iterator

    from qgis.gui import QgisInterface

    from qgis_project_configurator_plugin.plugin import Plugin

MODULE = "qgis_project_configurator_plugin.plugin"


@pytest.fixture
def plugin_loaded(qgis_iface: "QgisInterface") -> "Iterator[Plugin]":
    plugin = classFactory(qgis_iface)
    plugin.initGui()

    yield plugin

    plugin.unload()


def test_plugin_loads_without_errors(plugin_loaded: "Plugin") -> None:
    assert plugin_loaded.toolbar is not None
    assert plugin_loaded.toolbar.objectName() == "qgis-project-manager-toolbar"


def test_plugin_creates_and_registers_actions(plugin_loaded: "Plugin") -> None:
    assert isinstance(plugin_loaded.create_project_action, QAction)
    assert plugin_loaded.create_project_action.text() == "Create project"

    assert isinstance(plugin_loaded.export_styles_action, QAction)
    assert (
        plugin_loaded.export_styles_action.text() == "Export styles for selected layers"
    )

    assert isinstance(plugin_loaded.create_template_config_action, QAction)
    assert (
        plugin_loaded.create_template_config_action.text()
        == "Create template map config"
    )


def test_init_processing_registers_provider(plugin_loaded: "Plugin") -> None:
    assert isinstance(
        plugin_loaded.processing_provider, ProjectManagerProcessingProvider
    )


@pytest.mark.parametrize(
    ("failure_mode", "expected_message"),
    [
        ("registry_none", "Cannot access processing registry"),
        ("add_provider_fails", "Cannot add plugin processing provider"),
        ("toolbar_none", "Cannot create plugin toolbar"),
    ],
)
def test_init_gui_raises_errors(
    qgis_iface: "QgisInterface",
    mocker: MockerFixture,
    failure_mode: str,
    expected_message: str,
) -> None:
    plugin = classFactory(qgis_iface)

    mock_registry = MagicMock()
    mock_registry.addProvider.return_value = True
    registry_patch = mocker.patch(
        f"{MODULE}.QgsApplication.processingRegistry",
        return_value=mock_registry,
    )

    match failure_mode:
        case "registry_none":
            registry_patch.return_value = None
        case "add_provider_fails":
            mock_registry.addProvider.return_value = False
        case "toolbar_none":
            mocker.patch.object(qgis_iface, "addToolBar", return_value=None)

    with pytest.raises(RuntimeError, match=expected_message):
        plugin.initGui()


def test_unload_cleans_up_resources(
    qgis_iface: "QgisInterface", mocker: MockerFixture
) -> None:
    plugin = classFactory(qgis_iface)

    mock_registry = MagicMock()
    mocker.patch(
        f"{MODULE}.QgsApplication.processingRegistry",
        return_value=mock_registry,
    )
    # Use actual QMainWindow for PyQt to accept it in QAction
    main_window = QMainWindow()
    mock_remove_toolbar = mocker.patch.object(main_window, "removeToolBar")
    mocker.patch.object(qgis_iface, "mainWindow", return_value=main_window)

    plugin.initGui()

    assert plugin.toolbar is not None
    provider = plugin.processing_provider

    plugin.unload()

    assert plugin.toolbar is None
    mock_remove_toolbar.assert_called_once()
    mock_registry.removeProvider.assert_called_once_with(provider)


@pytest.mark.parametrize(
    ("failure_mode", "expected_message"),
    [
        ("main_window_none", "Cannot access QGIS main window"),
        ("registry_none", "Cannot access processing registry"),
        ("remove_provider_fails", "Cannot remove plugin processing provider"),
    ],
)
def test_unload_raises_errors(
    qgis_iface: "QgisInterface",
    mocker: MockerFixture,
    failure_mode: str,
    expected_message: str,
) -> None:
    plugin = classFactory(qgis_iface)

    main_window = QMainWindow()
    mocker.patch.object(main_window, "removeToolBar")
    mock_main_window_call = mocker.patch.object(
        qgis_iface, "mainWindow", return_value=main_window
    )

    mock_registry = MagicMock()
    mock_registry.removeProvider.return_value = True
    registry_patch = mocker.patch(
        f"{MODULE}.QgsApplication.processingRegistry",
        return_value=mock_registry,
    )

    plugin.initGui()

    match failure_mode:
        case "main_window_none":
            mock_main_window_call.return_value = None
        case "registry_none":
            registry_patch.return_value = None
        case "remove_provider_fails":
            mock_registry.removeProvider.return_value = False

    with pytest.raises(RuntimeError, match=expected_message):
        plugin.unload()
