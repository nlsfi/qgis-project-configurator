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

from qgis_project_configurator.config import ConfigCompiler
from qgis_project_configurator.types import ProjectEntry


def test_flat_project_properties_mapped_to_entries(base_config: dict, tmp_path: Path):
    base_config["project_properties"] = {
        "property_1": "value",
        "property_2": 2,
    }

    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source="db",
        project_dir=tmp_path,
    ).compile()
    assert compiled.project_properties == [
        ProjectEntry(scope="property_1", key="/", value="value"),
        ProjectEntry(scope="property_2", key="/", value=2),
    ]


def test_nested_project_properties_mapped_to_entries(base_config: dict, tmp_path: Path):
    base_config["project_properties"] = {
        "property_1": {
            "key_1": {
                "nested_key": "nested_value",
                "nested_key_2": True,
            },
            "key_2": ["value", 2],
        },
        "property_2": 2,
    }

    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source="db",
        project_dir=tmp_path,
    ).compile()
    assert compiled.project_properties == [
        ProjectEntry(scope="property_1", key="key_1/nested_key", value="nested_value"),
        ProjectEntry(scope="property_1", key="key_1/nested_key_2", value=True),
        ProjectEntry(scope="property_1", key="key_2", value=["value", 2]),
        ProjectEntry(scope="property_2", key="/", value=2),
    ]
