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

from qgis_project_configurator.cli import (
    create_project,
    create_template,
    get_metadata,
    version,
)


def main() -> None:  # noqa: D103
    parser = argparse.ArgumentParser(description="QGIS Project Configurator CLI")
    parser.add_argument(
        "--version",
        action="version",
        version=version.get_version(),
        help="Show application version and exit.",
    )
    parser.add_argument(
        "--qgis-version",
        action="version",
        version=version.get_qgis_version(),
        help="Show qgis version and exit.",
    )

    subparsers = parser.add_subparsers(title="commands", dest="command", required=True)  # noqa: SC200

    create_project.setup_parser(subparsers)
    create_template.setup_parser(subparsers)
    get_metadata.setup_parser(subparsers)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
