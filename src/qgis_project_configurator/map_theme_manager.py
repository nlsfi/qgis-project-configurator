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

from qgis.core import QgsMapThemeCollection, QgsProject

from qgis_project_configurator.types import MapThemes

LOGGER = logging.getLogger(__name__)


class MapThemeManager:
    def __init__(
        self,
        project: QgsProject,
    ) -> None:
        self.project = project
        self.theme_collection = self.project.mapThemeCollection()

    def add_themes(self, themes: MapThemes) -> None:
        if not self.theme_collection:
            return
        for theme_name, layers in themes.items():
            theme_record = QgsMapThemeCollection.MapThemeRecord()
            for layer in layers:
                LOGGER.info(f"adding layer {layer.name()} to map theme {theme_name}")
                layer_record = QgsMapThemeCollection.MapThemeLayerRecord(layer)
                theme_record.addLayerRecord(layer_record)
            self.theme_collection.insert(theme_name, theme_record)
