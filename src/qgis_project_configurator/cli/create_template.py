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
import argparse
import sys
from pathlib import Path
from typing import Protocol

from qgis.core import QgsProject

from qgis_project_configurator.cli.cli_utils import LoggingProcessingFeedback, run_qgis
from qgis_project_configurator.create_template import create_configuration_template


class CreateTemplateArgs(Protocol):
    project: Path
    config: Path
    style_directory: Path | None


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CLI tool for creating a template configuration"
    )
    parser.add_argument(
        "--project",
        type=Path,
        help="QGIS project file to read from.",
        required=True,
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Config file to write to.",
        required=True,
    )

    parser.add_argument(
        "--style-directory",
        type=Path,
        help="Optional directory to write styles to.",
    )
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    return parser.parse_args()


@run_qgis
def _create_template(args: CreateTemplateArgs) -> None:
    project_instance = QgsProject.instance()
    if not project_instance:
        raise RuntimeError("Could not get a QGIS project instance")
    config = args.config
    style_directory = args.style_directory
    success = project_instance.read(str(args.project))
    if not success:
        raise RuntimeError("Could not read QGIS project")
    create_configuration_template(
        config, style_directory, LoggingProcessingFeedback(), project_instance
    )


def main() -> None:  # noqa: D103
    args = _parse_args()
    _create_template(args)
