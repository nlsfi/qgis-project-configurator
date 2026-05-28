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
    QgsProcessingOutputFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterFolderDestination,
)

from qgis_project_configurator.create_template import create_configuration_template


class CreateTemplateMapConfig(QgsProcessingAlgorithm):
    OUTPUT = "OUTPUT"
    STYLE_FOLDER = "STYLE_FOLDER"

    def __init__(self) -> None:
        super().__init__()

    def name(self) -> str:
        return "create-template-map-configuration"

    def displayName(self) -> str:
        return "Create a template map configuration"

    def initAlgorithm(self, config=None) -> None:
        parameters = [
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                "Configuration file path",
                fileFilter="Map Configuration file (*.yaml)",
            ),
            QgsProcessingParameterFolderDestination(
                self.STYLE_FOLDER,
                "Export styles to a folder",
                optional=True,
                defaultValue="",
            ),
        ]
        for parameter in parameters:
            success = self.addParameter(parameter)
            # TODO: raise a custom exception, catch & cancel the process,
            # display an appropriate error message.
            if not success:
                pass
        success = self.addOutput(
            QgsProcessingOutputFile(self.OUTPUT, "Configuration file path")
        )
        if not success:
            pass

    def flags(self):  # noqa: ANN201
        return Qgis.ProcessingAlgorithmFlag.CanCancel

    def prepareAlgorithm(self, parameters, context, feedback) -> bool:
        """Prepare stage of the processing algorithm.

        This runs in the main tread.
        """
        self.output_path = Path(
            self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        )
        output_style_folder = self.parameterAsFileOutput(
            parameters, self.STYLE_FOLDER, context
        )
        output_style_folder = Path(output_style_folder) if output_style_folder else None

        create_configuration_template(self.output_path, output_style_folder, feedback)

        return True

    def processAlgorithm(self, parameters, context, feedback) -> dict[str, str]:
        """Processing method run in a background thread."""
        return {self.OUTPUT: str(self.output_path)}

    def postProcessAlgorithm(self, context, feedback) -> dict:
        """Post processing stage of the algorithm."""
        return {}

    def shortHelpString(self) -> str:
        return (
            "<p>This tool creates a template map configuration. Parameters:</p>"
            "<ul>"
            "<li><b>Configuration file path</b>: File where to save configuration template</li>"  # noqa: E501
            "<li><b>Export styles to a folder</b> [optional]:  Define a folder if you want to save styles. "  # noqa: E501
            "If not given no styles for layers are defined in the configuration</li>"
            "</ul>"
        )

    def createInstance(self):  # noqa: ANN201
        return CreateTemplateMapConfig()
