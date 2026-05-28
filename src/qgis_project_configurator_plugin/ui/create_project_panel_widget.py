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
from importlib import resources
from pathlib import Path

from qgis.core import QgsProcessingException
from qgis.gui import QgsFileWidget, QgsPanelWidget, QgsProcessingParametersGenerator
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QComboBox, QLabel, QWidget

from qgis_project_configurator.config import get_config

ui_path = resources.files(__package__) / "create_project_panel_widget.ui"
CreateProjectPanelWidgetBase, _ = uic.loadUiType(ui_path)

LOGGER = logging.getLogger(__name__)

CUSTOM_GPKG_LABEL = "Custom Geopackage"


class CreateProjectPanelWidget(QgsPanelWidget, CreateProjectPanelWidgetBase):  # type: ignore [valid-type, misc]
    config_file_widget: QgsFileWidget
    data_source_combo_box: QComboBox
    product_version_combo_box: QComboBox
    geopackage_file_widget: QgsFileWidget
    geopackage_file_label: QLabel

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.config: dict | None = None

        # Widget configurations
        self.geopackage_file_widget.setFilter("Geopackage files (*.gpkg)")
        self.config_file_widget.setFilter("YAML files (*.yaml *.yml)")

        self.config_file_widget.fileChanged.connect(self.on_config_file_change)
        self.data_source_combo_box.currentTextChanged.connect(
            self.on_data_source_change
        )

        # Form initialization
        self.geopackage_file_widget.hide()
        self.geopackage_file_label.hide()

    def on_config_file_change(self, config_file: str) -> None:
        if config_file and Path(config_file).exists():
            self.config = get_config(Path(config_file))
        else:
            self.config = None
        self.populate_combo_boxes()

    def _set_override_geopackage_visible(self, visible: bool) -> None:  # noqa: FBT001
        self.geopackage_file_label.setVisible(visible)
        self.geopackage_file_widget.setVisible(visible)

    def on_data_source_change(self) -> None:
        self._set_override_geopackage_visible(self._is_geopackage_override_used())

    def _is_geopackage_override_used(self) -> bool:
        return self.data_source_combo_box.currentText() == CUSTOM_GPKG_LABEL

    def get_current_data_source(self):  # noqa: ANN201
        if self._is_geopackage_override_used():
            return self.geopackage_file_widget.filePath()
        return self.data_source_combo_box.currentText()

    def populate_combo_boxes(self) -> None:
        self.data_source_combo_box.clear()
        self.product_version_combo_box.clear()
        if self.config is None:
            return

        data_sources = self.config.get("data_sources", {})
        product_versions = self.config.get("product_versions", {})

        for data_source_name in data_sources:
            self.data_source_combo_box.addItem(data_source_name)
        self.data_source_combo_box.addItem(CUSTOM_GPKG_LABEL)

        for version in product_versions:
            self.product_version_combo_box.addItem(version)

    def setParameters(self, parameters) -> None:
        self.config_file_widget.setFilePath(parameters.get("CONFIG_PATH"))
        self.product_version_combo_box.setCurrentText(parameters.get("PRODUCT_VERSION"))

        data_source = parameters.get("DATA_SOURCE")
        data_source_index = self.data_source_combo_box.findText(data_source)
        if data_source_index != -1:
            self.data_source_combo_box.setCurrentIndex(data_source_index)
        else:
            self.data_source_combo_box.setCurrentText(CUSTOM_GPKG_LABEL)

    def createProcessingParameters(
        self,
        flags=QgsProcessingParametersGenerator.Flags(),  # noqa: B008
    ) -> dict | None:
        try:
            return {
                "CONFIG_PATH": self.config_file_widget.filePath(),
                "PRODUCT_VERSION": self.product_version_combo_box.currentText(),
                "DATA_SOURCE": self.get_current_data_source(),
            }
        except Exception as e:
            raise QgsProcessingException(f"Invalid parameters: {e}") from e
