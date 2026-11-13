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

import qgis_plugin_tools
from qgis.core import QgsApplication
from qgis.processing import execAlgorithmDialog
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMainWindow
from qgis_plugin_tools.tools import custom_logging
from qgis_plugin_tools.tools.decorations import log_if_fails

import qgis_project_configurator_plugin
from qgis_project_configurator.qgis_utils import iface
from qgis_project_configurator_plugin import env
from qgis_project_configurator_plugin.processing import ProjectManagerProcessingProvider
from qgis_project_configurator_plugin.tools.export_styles import export_styles

LOGGER = logging.getLogger(__name__)


class Plugin:
    def __init__(self) -> None:
        self._teardown_loggers = lambda: None
        self.processing_provider = None

    def initGui(self) -> None:  # noqa: N802
        """Init gui."""
        global iface  # noqa: PLW0602

        self._teardown_loggers = custom_logging.setup_loggers(
            qgis_project_configurator_plugin.__name__,
            qgis_plugin_tools.__name__,
            message_log_name="QGIS Project Configurator",
        )

        self.initProcessing()

        toolbar = iface.addToolBar("QGIS project manager toolbar")
        if toolbar is None:
            msg = "Cannot create plugin toolbar"
            raise RuntimeError(msg)
        toolbar.setObjectName("qgis-project-manager-toolbar")

        self.create_project_action = QAction(
            QIcon(""),
            "Create project",
            iface.mainWindow(),
        )
        self.create_project_action.triggered.connect(
            lambda: execAlgorithmDialog(
                "nlsmapprojectmanager:create-visualization-project"
            )
        )

        self.export_styles_action = QAction(
            QIcon(""),
            "Export styles for selected layers",
            iface.mainWindow(),
        )
        self.export_styles_action.triggered.connect(export_styles)

        self.create_template_config_action = QAction(
            QIcon(""),
            "Create template map config",
            iface.mainWindow(),
        )
        self.create_template_config_action.triggered.connect(
            lambda: execAlgorithmDialog(
                "nlsmapprojectmanager:create-template-map-configuration"
            )
        )

        toolbar.addAction(self.create_project_action)
        toolbar.addAction(self.export_styles_action)
        toolbar.addAction(self.create_template_config_action)

        self.toolbar = toolbar

        if hasattr(iface, "initializationCompleted"):
            iface.initializationCompleted.connect(self.iface_initialization_completed)

        if bool(env.IS_DEVELOPMENT_MODE):
            self.iface_initialization_completed()

        LOGGER.info("Plugin initialized")

    def initProcessing(self) -> None:
        self.processing_provider = ProjectManagerProcessingProvider()  # type: ignore[assignment]
        processing_registry = QgsApplication.processingRegistry()
        if processing_registry is None:
            msg = "Cannot access processing registry"
            raise RuntimeError(msg)
        success = processing_registry.addProvider(self.processing_provider)
        if not success:
            msg = "Cannot add plugin processing provider"
            raise RuntimeError(msg)

    def unload(self) -> None:
        """Unload plugin."""
        if self.toolbar:
            main_window = iface.mainWindow()
            if not isinstance(main_window, QMainWindow):
                msg = "Cannot access QGIS main window"
                raise RuntimeError(msg)
            main_window.removeToolBar(self.toolbar)
            self.toolbar = None

        processing_registry = QgsApplication.processingRegistry()
        if processing_registry is None:
            msg = "Cannot access processing registry"
            raise RuntimeError(msg)
        success = processing_registry.removeProvider(self.processing_provider)  # noqa: QGS202
        if not success:
            msg = "Cannot remove plugin processing provider"
            raise RuntimeError(msg)
        self._teardown_loggers()
        self._teardown_loggers = lambda: None

    @log_if_fails
    def iface_initialization_completed(self) -> None:
        """Run additional setup for the plugin.

        Executed after initializationCompleted signal is emitted.
        """
