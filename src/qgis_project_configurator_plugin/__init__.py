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

from qgis.utils import plugins

if typing.TYPE_CHECKING:
    from qgis_project_configurator_plugin.plugin import Plugin


def classFactory(_) -> "Plugin":  # noqa: ANN001, N802
    """Class factory."""
    from qgis_project_configurator_plugin.plugin import Plugin  # noqa: PLC0415

    return Plugin()


def get_instance() -> "Plugin | None":
    """Get instance."""
    return plugins.get(__name__)
