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
import logging
from pathlib import Path
from typing import Protocol

from qgis.core import QgsProject

from qgis_project_configurator.cli.cli_utils import LoggingProcessingFeedback, run_qgis
from qgis_project_configurator.create_project import create_project, write_project
from qgis_project_configurator.yaml_loader import load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
)

LOGGER = logging.getLogger(__name__)


class CreateProjectArgs(Protocol):
    project: Path
    config: Path
    data_source: str | Path
    product_version: str
    dry_run: bool
    store_metadata: bool


def setup_parser(subparsers: argparse._SubParsersAction) -> None:
    """Register the create-project subcommand."""
    parser = subparsers.add_parser("create-project", help="Create a QGIS project.")
    parser.add_argument(
        "--project",
        type=Path,
        help="QGIS project file to write to.",
        required=True,
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Config definition to read from.",
        required=True,
    )
    parser.add_argument(
        "--data-source",
        type=_str_or_path,
        help=(
            "Data source to load layers from. Either a source defined "
            "in the config file, or a file path to a geopackage."
        ),
        required=True,
    )
    parser.add_argument(
        "--product-version",
        type=str,
        help="Which version of a map product to generate.",
    )
    parser.add_argument(
        "--store-metadata",
        action="store_true",
        help=(
            "Store project creation metadata (config file location, "
            "product version) into the created qgis project."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Exit after compiling the configuration using the provided arguments.",
    )
    parser.set_defaults(func=_create_project)


def _str_or_path(value: str) -> str | Path:
    path = Path(value)
    if path.exists():
        return path
    return value


@run_qgis
def _create_project(args: CreateProjectArgs) -> None:
    project = QgsProject.instance()
    if not project:
        msg = "Could not get a QGIS project instance"
        raise RuntimeError(msg)
    project_path = args.project
    config_path = args.config
    data_source = args.data_source
    product_version = args.product_version
    dry_run = args.dry_run
    create_project(
        project=project,
        config=load_config(config_path),
        config_path=config_path,
        data_source=data_source,
        product_version=product_version,
        target_project_path=project_path,
        store_metadata=args.store_metadata,
        dry_run=dry_run,
        feedback=LoggingProcessingFeedback(),
    )
    if not dry_run:
        write_project(project, project_path)
