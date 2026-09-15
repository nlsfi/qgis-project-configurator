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
from pathlib import Path
from typing import Protocol

from qgis.core import QgsProject

from qgis_project_configurator.cli.cli_utils import LoggingProcessingFeedback, run_qgis
from qgis_project_configurator.create_template import (
    ConfigStyle,
    create_configuration_template,
)


class CreateTemplateArgs(Protocol):
    project: Path
    config: Path
    style_directory: Path | None
    compact: bool


def setup_parser(subparsers: argparse._SubParsersAction) -> None:
    """Registers the create-template subcommand."""
    parser = subparsers.add_parser(
        "create-template", help="Create a template configuration file."
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
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Use compact syntax for layers",
    )
    parser.set_defaults(func=_create_template)


@run_qgis
def _create_template(args: CreateTemplateArgs) -> None:
    project_instance = QgsProject.instance()
    if project_instance is None:
        raise RuntimeError("Could not get a QGIS project instance")
    success = project_instance.read(str(args.project))
    if not success:
        raise RuntimeError("Could not read QGIS project")
    config = args.config
    style_directory = args.style_directory
    config_style = ConfigStyle.COMPACT_LAYERS if args.compact else ConfigStyle.DEFAULT
    create_configuration_template(
        output_file=config,
        style_folder=style_directory,
        feedback=LoggingProcessingFeedback(),
        config_style=config_style,
        project=project_instance,
    )
