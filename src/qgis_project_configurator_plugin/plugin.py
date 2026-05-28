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

from typing import cast

from qgis.core import QgsApplication
from qgis.gui import QgisInterface
from qgis.processing import execAlgorithmDialog
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.utils import iface as _iface
from qgis_plugin_tools.tools.custom_logging import setup_logger, teardown_logger
from qgis_plugin_tools.tools.resources import plugin_name

from qgis_project_configurator_plugin.processing import ProjectManagerProcessingProvider
from qgis_project_configurator_plugin.tools.export_styles import export_styles

iface: QgisInterface = cast("QgisInterface", _iface)


class Plugin:
    name = plugin_name()

    def __init__(self) -> None:
        setup_logger(Plugin.name)

        self.processing_provider = None

    def initGui(self) -> None:
        self.initProcessing()

        toolbar = iface.addToolBar("QGIS project manager toolbar")
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

    def initProcessing(self) -> None:
        self.processing_provider = ProjectManagerProcessingProvider()  # type: ignore [assignment]
        success = QgsApplication.processingRegistry().addProvider(
            self.processing_provider
        )
        if not success:
            pass  # TODO: handle fail?

    def unload(self) -> None:
        iface.mainWindow().removeToolBar(self.toolbar)
        self.toolbar = None

        success = QgsApplication.processingRegistry().removeProvider(
            self.processing_provider
        )
        if not success:
            pass  # TODO: handle fail?
        teardown_logger(Plugin.name)
