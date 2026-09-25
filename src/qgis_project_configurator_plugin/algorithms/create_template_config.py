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

import typing
from pathlib import Path
from typing import Any

from qgis.core import (
    Qgis,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingOutputFile,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterFolderDestination,
)

from qgis_project_configurator.create_template import (
    ConfigStyle,
    create_configuration_template,
)


class CreateTemplateMapConfig(QgsProcessingAlgorithm):
    OUTPUT = "OUTPUT"
    STYLE_FOLDER = "STYLE_FOLDER"
    USE_COMPACT_CONFIG = "USE_COMPACT_CONFIG"

    def __init__(self) -> None:
        super().__init__()

    def name(self) -> str:
        return "create-template-map-configuration"

    @typing.override
    def displayName(self) -> str:
        return "Create a template map configuration"

    @typing.override
    def initAlgorithm(
        self, _configuration: dict[str | None, Any] | None = None
    ) -> None:
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
            QgsProcessingParameterBoolean(
                self.USE_COMPACT_CONFIG,
                "Use compact syntax style for layers",
                defaultValue=False,
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

    @typing.override
    def flags(self) -> Qgis.ProcessingAlgorithmFlag:
        return Qgis.ProcessingAlgorithmFlag.CanCancel

    @typing.override
    def prepareAlgorithm(
        self,
        parameters: dict[str | None, typing.Any],
        context: "QgsProcessingContext",
        feedback: "QgsProcessingFeedback | None",
    ) -> bool:
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

        use_compact = self.parameterAsBool(parameters, self.USE_COMPACT_CONFIG, context)
        config_style = (
            ConfigStyle.COMPACT_LAYERS if use_compact else ConfigStyle.DEFAULT
        )

        create_configuration_template(
            self.output_path,
            output_style_folder,
            feedback,
            config_style,
        )

        return True

    @typing.override
    def processAlgorithm(
        self,
        _parameters: dict[str | None, typing.Any],
        _context: "QgsProcessingContext",
        _feedback: "QgsProcessingFeedback | None",
    ) -> dict[str, str]:
        """Run processing method in a background thread."""
        return {self.OUTPUT: str(self.output_path)}

    @typing.override
    def postProcessAlgorithm(
        self,
        _context: "QgsProcessingContext",
        _feedback: "QgsProcessingFeedback | None",
    ) -> dict:
        """Run post processing stage of the algorithm."""
        return {}

    @typing.override
    def shortHelpString(self) -> str:
        return (
            "<p>This tool creates a template map configuration. Parameters:</p>"
            "<ul>"
            "<li><b>Configuration file path</b>: File where to save configuration template</li>"  # noqa: E501
            "<li><b>Export styles to a folder</b> [optional]:  Define a folder if you want to save styles. "  # noqa: E501
            "If not given no styles for layers are defined in the configuration</li>"
            "<li><b>Use compact syntax style for layers</b>: Formats layers on a single line in the resulting YAML.</li>"  # noqa: E501
            "</ul>"
        )

    @typing.override
    def createInstance(self) -> "CreateTemplateMapConfig":
        return CreateTemplateMapConfig()
