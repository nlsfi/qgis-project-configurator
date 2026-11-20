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

# qgis 3 / 4 import workaround
#
# Note that QGIS' processing plugin is injected by qgis startup: it's
# non-importable to the type checker. The blanket "type: ignore" is used to
# accommodate both qgis 3 and 4 development without mismatching more specific
# type ignores
try:
    # Original qgis 3 import.
    from processing.gui.AlgorithmDialog import (  # type: ignore # noqa: PGH003 # ty: ignore[unused-ignore-comment]
        AlgorithmDialog,
    )
except ImportError:
    # aliased import for qgis 4 (functionally the same class)
    from processing.gui.algorithm_widget import (  # type: ignore # noqa: PGH003 # ty: ignore[unused-ignore-comment]
        AlgorithmWidget as AlgorithmDialog,
    )

from typing import TYPE_CHECKING

from qgis_project_configurator_plugin.ui.create_project_panel_widget import (
    CreateProjectPanelWidget,
)

if TYPE_CHECKING:
    from qgis.core import QgsProcessingAlgorithm
    from qgis.PyQt.QtWidgets import QWidget

LOGGER = logging.getLogger(__name__)


class CreateProjectDialog(AlgorithmDialog):
    """Algorithm dialog for creating a project."""

    def __init__(
        self, algorithm: "QgsProcessingAlgorithm", parent: "QWidget | None" = None
    ) -> None:
        super().__init__(algorithm, parent=parent)

    def getParametersPanel(  # noqa: N802
        self, _algorithm: "QgsProcessingAlgorithm", parent: "QWidget | None"
    ) -> CreateProjectPanelWidget:
        """Return the custom parameters panel widget."""
        return CreateProjectPanelWidget(parent)
