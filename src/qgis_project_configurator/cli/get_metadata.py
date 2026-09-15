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
from json import dumps
from pathlib import Path
from typing import Protocol

from qgis_project_configurator.config import get_config


class GetMetadataArgs(Protocol):
    config: Path
    key: str | None


def setup_parser(subparsers: argparse._SubParsersAction) -> None:
    """Registers the get-metadata subcommand."""
    parser = subparsers.add_parser(
        "get-metadata", help="Get metadata from a configuration file."
    )
    parser.add_argument(
        "config",
        type=Path,
        help="Config file to read.",
    )
    parser.add_argument(
        "--key",
        help="Get the value for a specific key.",
    )
    parser.set_defaults(func=_get_metadata)


def _get_metadata(args: GetMetadataArgs) -> None:
    config = get_config(args.config)
    if isinstance(config, dict):
        metadata = config.get("metadata", {})
        if args.key:
            value = metadata.get(args.key)
            if value is not None:
                print(value)
        else:
            print(dumps(metadata, indent=2, default=str))
