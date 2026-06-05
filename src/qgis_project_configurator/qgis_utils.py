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

from qgis.core import QgsMapLayer


def save_style(layer: QgsMapLayer, style_path: Path) -> bool:
    """Save layer style to file."""
    _msg, style_saved = layer.saveNamedStyle(
        str(style_path),
        QgsMapLayer.StyleCategory.Symbology | QgsMapLayer.StyleCategory.Labeling,
    )
    return style_saved
