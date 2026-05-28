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

from processing.gui.AlgorithmDialog import AlgorithmDialog

from qgis_project_configurator_plugin.ui.create_project_panel_widget import (
    CreateProjectPanelWidget,
)

LOGGER = logging.getLogger(__name__)


class CreateProjectDialog(AlgorithmDialog):
    def __init__(self, alg, parent=None) -> None:
        super().__init__(alg, parent=parent)

    def getParametersPanel(self, alg, parent) -> CreateProjectPanelWidget:
        return CreateProjectPanelWidget(parent)
