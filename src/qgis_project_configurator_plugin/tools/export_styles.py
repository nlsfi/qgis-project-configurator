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

from qgis.core import QgsProject
from qgis.utils import iface

from qgis_project_configurator.export_styles import export_layer_styles
from qgis_project_configurator_plugin.ui.export_styles_dialog import ExportStylesDialog


def export_styles() -> None:  # noqa: D103
    export_styles_dialog = ExportStylesDialog(iface.mainWindow())

    if export_styles_dialog.exec():
        params = export_styles_dialog.get_params()
        export_layer_styles(params.selected_layers, project=QgsProject.instance())
