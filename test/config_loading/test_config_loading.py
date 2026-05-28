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

from qgis_project_configurator.config import get_config

YAML_PATH = Path(__file__).parent.parent / "resources/yaml"


def test_simple_config_loads():
    config = get_config(YAML_PATH / "component_2.yaml")
    assert config["key_component_2"] == "value_component_2"


def test_included_config_loads():
    config = get_config(YAML_PATH / "include.yaml")
    assert config["component_1"]["key_component_1"] == "value_component_1"


def test_include_within_included_config_loads():
    config = get_config(YAML_PATH / "include.yaml")
    assert (
        config["component_1"]["component_2"]["key_component_2"] == "value_component_2"
    )
