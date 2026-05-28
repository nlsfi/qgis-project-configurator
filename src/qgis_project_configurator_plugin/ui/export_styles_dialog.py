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

from qgis.core import QgsProject
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QListWidget, QWidget
from qgis.utils import iface
from qgis_plugin_tools.tools.resources import plugin_name

from qgis_project_configurator.export_styles import export_layer_styles
from qgis_project_configurator_plugin.tools.parameters import ExportStylesParams

ui_path = resources.files(__package__) / "export_styles_dialog.ui"
ExportStylesDialogBase, _ = uic.loadUiType(ui_path)

LOGGER = logging.getLogger(plugin_name())


class ExportStylesDialog(QDialog, ExportStylesDialogBase):  # type: ignore [valid-type, misc]
    button_box: QDialogButtonBox
    selected_layers_list_widget: QListWidget

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.selected_layers = iface.layerTreeView().selectedLayers()
        self.populate_selected_layers_list()

    def handle_ok_click(self) -> None:
        export_layer_styles(self.selected_layers, project=QgsProject.instance())

    def populate_selected_layers_list(self) -> None:
        for layer in self.selected_layers:
            self.selected_layers_list_widget.addItem(layer.name())

    def get_params(self) -> ExportStylesParams:
        return ExportStylesParams(self.selected_layers)
