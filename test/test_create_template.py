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

from importlib import metadata
from pathlib import Path

import pytest
import yaml
from qgis.core import QgsProcessingFeedback, QgsProject

from qgis_project_configurator.config_format import MAIN_SCHEMA_URL, schema_url
from qgis_project_configurator.create_template import create_configuration_template


def test_template_starts_with_schema_modeline(tmp_path: Path):
    output_file = tmp_path / "config.yaml"

    config = create_configuration_template(
        output_file=output_file,
        style_folder=None,
        feedback=QgsProcessingFeedback(),
        project=QgsProject.instance(),
    )

    text = output_file.read_text()
    assert text.splitlines()[0] == f"# yaml-language-server: $schema={schema_url()}"
    assert yaml.safe_load(text) == config


@pytest.mark.parametrize(
    ("version", "expected"),
    [
        (
            "0.2.0",
            "https://raw.githubusercontent.com/nlsfi/qgis-project-configurator/v0.2.0/schema/config.schema.json",
        ),
        ("0.1.2.post0", MAIN_SCHEMA_URL),
        ("0.3.0.dev1", MAIN_SCHEMA_URL),
    ],
)
def test_schema_url_of_version(
    monkeypatch: pytest.MonkeyPatch, version: str, expected: str
):
    monkeypatch.setattr(metadata, "version", lambda _: version)

    assert schema_url() == expected


def test_schema_url_without_package_metadata(monkeypatch: pytest.MonkeyPatch):
    def version(name: str) -> str:
        raise metadata.PackageNotFoundError(name)

    monkeypatch.setattr(metadata, "version", version)

    assert schema_url() == MAIN_SCHEMA_URL
