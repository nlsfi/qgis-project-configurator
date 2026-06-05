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

import sys
from pathlib import Path

v = sys.argv[1]

# changelog

changelog_file = Path("CHANGELOG.md")
version_header = f"## [{v}]"
new_section = "## Unreleased\n\n"

changelog_file.write_text(
    changelog_file.read_text(encoding="utf-8").replace(
        version_header, new_section + version_header, 1
    ),
    encoding="utf-8",
)

# init

init_file = Path("src/qgis-project-configurator/__init__.py")
init_line_to_replace = f'__version__ = "{v}"'

init_file.write_text(
    init_file.read_text(encoding="utf-8").replace(
        init_line_to_replace, f'__version__ = "{v}.post0"', 1
    ),
    encoding="utf-8",
)
