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

from qgis.core import (
    QgsPrintLayout,
    QgsProcessingFeedback,
    QgsProject,
    QgsReadWriteContext,
)
from qgis.PyQt.QtXml import QDomDocument

from qgis_project_configurator.runtimeprofiler import profile_function
from qgis_project_configurator.types import PrintLayouts

LOGGER = logging.getLogger(__name__)


class LayoutManager:
    def __init__(self, project: QgsProject, layouts: PrintLayouts) -> None:
        self.project = project
        self.layouts = layouts
        self.qgs_layout_manager = self.project.layoutManager()

    @profile_function("Load layouts")
    def load_layouts(self, feedback: QgsProcessingFeedback) -> None:
        if not self.qgs_layout_manager:
            LOGGER.error("Could not access layout manager")
            return
        for layout_config in self.layouts:
            if feedback.isCanceled():
                return

            feedback.pushInfo(f"Loading layout from {layout_config.layout_file}")
            qgs_print_layout = QgsPrintLayout(self.project)
            qgs_print_layout.initializeDefaults()
            with layout_config.layout_file.open() as f:
                template_xml = f.read()
            doc = QDomDocument()
            doc.setContent(template_xml)
            _layout_items, success = qgs_print_layout.loadFromTemplate(
                doc, QgsReadWriteContext()
            )
            if not success:
                feedback.reportError("Cannot load layout")
                return
            if layout_config.atlas_coverage_layer_name:
                atlas = qgs_print_layout.atlas()
                if not atlas:
                    feedback.reportError("cannot access atlas")
                    return
                atlas.setEnabled(True)
                # Note that setting atlas coverage layer relies on unique layer
                # name
                layer = self.project.mapLayersByName(
                    layout_config.atlas_coverage_layer_name
                )[0]
                atlas.setCoverageLayer(layer)
            self.qgs_layout_manager.addLayout(qgs_print_layout)
