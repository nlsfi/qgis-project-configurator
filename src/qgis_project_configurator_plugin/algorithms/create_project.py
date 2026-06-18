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

from qgis.core import (
    Qgis,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFile,
    QgsProcessingParameterString,
    QgsProject,
)
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.utils import iface

from qgis_project_configurator.config import get_config
from qgis_project_configurator.create_project import (
    create_project as lib_create_project,
)
from qgis_project_configurator_plugin.tools.parameters import CreateProjectParams
from qgis_project_configurator_plugin.ui.create_project_dialog import (
    CreateProjectDialog,
)


class CreateProjectAlgorithm(QgsProcessingAlgorithm):
    CONFIG_PATH = "CONFIG_PATH"
    PRODUCT_VERSION = "PRODUCT_VERSION"
    DATA_SOURCE = "DATA_SOURCE"

    def __init__(self) -> None:
        super().__init__()

    def name(self) -> str:
        return "create-visualization-project"

    def displayName(self) -> str:
        return "Create a visualization project"

    def initAlgorithm(self, config=None) -> None:
        parameters = [
            QgsProcessingParameterFile(self.CONFIG_PATH, "Configuration file path"),
            QgsProcessingParameterString(self.PRODUCT_VERSION, "Product version"),
            QgsProcessingParameterString(self.DATA_SOURCE, "Data Source"),
        ]
        for parameter in parameters:
            success = self.addParameter(parameter)
            # TODO: raise a custom exception, catch & cancel the process,
            # display an appropriate error message.
            if not success:
                pass

    def flags(self) -> Qgis.ProcessingAlgorithmFlag:
        return Qgis.ProcessingAlgorithmFlag.CanCancel

    def _get_params(self, parameters, context) -> CreateProjectParams:
        return CreateProjectParams(
            config_path=Path(
                self.parameterAsFile(parameters, self.CONFIG_PATH, context)
            ),
            product_version=self.parameterAsString(
                parameters, self.PRODUCT_VERSION, context
            ),
            data_source=self.parameterAsString(parameters, self.DATA_SOURCE, context),
        )

    def _check_for_empty_project_or_create_new(self) -> bool | QgsProject:
        if len(QgsProject.instance().mapLayers()) > 0:
            msg_box = QMessageBox.question(
                iface.mainWindow(),
                "Project not empty",
                "Close the existing project or Cancel",
                QMessageBox.StandardButton.Close | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Close,
            )
            if msg_box == QMessageBox.StandardButton.Cancel:
                return False

            success = iface.newProject(promptToSaveFlag=True)
            if not success:
                pass  # TODO: handle fail?
        return QgsProject.instance()

    def prepareAlgorithm(self, parameters, context, feedback) -> bool:
        """Prepare stage of the processing algorithm.

        This runs in the main tread.
        Misuse the method to run the whole algorithm in the prepare stage. This
        is done because of:
          a. Postgresql layers can't be created in the background thread
            (possibly a bug)
          b. Layers can't be added to the project in the background thread and
            if layers are created in the background thread and added to be
            loaded using the context.addLayerToLoadOnCompletion() there is no
            simple way to control the layer tree structure and to which group
            the layers are added.
        """
        project = self._check_for_empty_project_or_create_new()
        if project is False:
            feedback.pushWarning("Cancelling.")
            return False

        params = self._get_params(parameters, context)
        config = get_config(params.config_path)

        iface.mapCanvas().freeze(True)  # noqa: FBT003
        try:
            lib_create_project(
                project=project,
                config=config,
                data_source=params.data_source,
                product_version=params.product_version,
                config_path=params.config_path,
                target_project_path=Path("placeholder"),  # TODO: path not needed here
                store_metadata=True,
                feedback=feedback,
            )
        finally:
            iface.mapCanvas().freeze(False)  # noqa: FBT003
        return True

    def processAlgorithm(self, parameters, context, feedback) -> dict:
        """Processing method run in a background thread.

        Postgresql layers can't be created in the background thread so run the
        whole algorihm in the prepare stage.
        """
        return {}

    def postProcessAlgorithm(self, context, feedback) -> dict:
        """Post processing stage of the algorithm."""
        return {}

    def createCustomParametersWidget(self, parent=None):  # noqa: ANN201
        return CreateProjectDialog(self, parent=parent)

    def shortHelpString(self) -> str:
        return (
            "<p>This tool creates a QGIS project from a map configuration. Parameters:</p>"  # noqa: E501
            "<ul>"
            "<li><b>Configuration file</b>: Select the map configuration yaml.</li>"
            "<li><b>Product version</b>: </li>"
            "<li><b>Data source</b>: Select the datasource from the options defined in the configuration file. The datasource could be overridden with a custom geopackage.</li>"  # noqa: E501
            '<li><b>Geopackage</b>: Custom geopackage used as a data source. "Custom geopackage" must be selected as a Data source. Optional if predefined data source is used</li>'  # noqa: E501
            "</ul>"
        )

    def createInstance(self):  # noqa: ANN201
        return CreateProjectAlgorithm()
