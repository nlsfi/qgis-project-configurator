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
from qgis_project_configurator.types import PrintLayout


def test_layout_config(base_config: dict, tmp_path: Path):
    base_config["layouts"] = [
        {
            "layout_file": "./layouts/file.qpt",
            "atlas_coverage_layer": "layer_name",
        }
    ]
    config_dir = tmp_path / "config"
    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=config_dir,
        data_source="db",
        project_dir=tmp_path,
    ).compile()
    assert compiled.layouts == [
        PrintLayout(
            layout_file=config_dir / "layouts/file.qpt",
            atlas_coverage_layer_name="layer_name",
        ),
    ]
