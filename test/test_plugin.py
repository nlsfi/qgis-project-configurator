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

from typing import TYPE_CHECKING

import pytest

from qgis_project_configurator_plugin import classFactory

if TYPE_CHECKING:
    from collections.abc import Iterator

    from pytest_qgis import QgisInterface

    from qgis_project_configurator_plugin.plugin import Plugin


@pytest.fixture
def plugin_loaded(qgis_iface: "QgisInterface") -> "Iterator[Plugin]":
    plugin = classFactory(qgis_iface)
    plugin.initGui()

    yield plugin

    plugin.unload()


def test_plugin_loads_without_errors(plugin_loaded: "Plugin") -> None:
    assert plugin_loaded.toolbar is not None
    # TODO: write more meaningful test, example from qgis-project-copier-template
