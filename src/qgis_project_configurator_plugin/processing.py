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

from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

from qgis_project_configurator_plugin.algorithms.create_project import (
    CreateProjectAlgorithm,
)
from qgis_project_configurator_plugin.algorithms.create_template_config import (
    CreateTemplateMapConfig,
)


class ProjectManagerProcessingProvider(QgsProcessingProvider):
    """The provider of our plugin."""

    def loadAlgorithms(self) -> None:
        """Load each algorithm into the current provider."""
        self.addAlgorithm(CreateProjectAlgorithm())
        self.addAlgorithm(CreateTemplateMapConfig())

    def id(self) -> str:
        """The ID of your plugin, used for identifying the provider.

        This string should be a unique, short, character only string,
        eg "qgis" or "gdal". This string should not be localised.
        """
        return "nlsmapprojectmanager"

    def name(self) -> str:
        """The human friendly name of your plugin in Processing.

        This string should be as short as possible (e.g. "Lastools", not
        "Lastools version 1.0.1 64-bit") and localised.
        """
        return self.tr("NLS Project Manager")

    def icon(self) -> QIcon:
        """Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """  # noqa: D205
        return QgsProcessingProvider.icon(self)
