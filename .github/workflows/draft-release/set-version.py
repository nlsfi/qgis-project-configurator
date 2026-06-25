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

import datetime
import sys
from pathlib import Path

v = sys.argv[1]


d = datetime.datetime.now(tz=datetime.UTC).date()

# changelog

changelog_file = Path("CHANGELOG.md")

changelog_is_valid = False
unreleased_changes = []
for line in changelog_file.read_text(encoding="utf-8").splitlines():
    if line.startswith("##") and line == "## Unreleased":
        changelog_is_valid = True

    if changelog_is_valid:
        if line == "## Unreleased":
            continue
        if line.startswith("##"):
            break
        unreleased_changes.append(line)

if not changelog_is_valid:
    msg = "changelog not in correct format"
    raise ValueError(msg)

if not list(filter(bool, unreleased_changes)):
    msg = "Unreleased section must not be empty"
    raise ValueError(msg)

link_line = (
    f"[{v}]: https://github.com/nlsfi/qgis-project-configurator/releases/tag/v{v}\n"
)

changelog_file.write_text(
    changelog_file.read_text(encoding="utf-8").replace(
        "## Unreleased", f"## [{v}] - {d}", 1
    )
    + link_line,
    encoding="utf-8",
)

# init

init_file = Path("src/qgis_project_configurator/__init__.py")

init_line_to_replace = None

for line in init_file.read_text(encoding="utf-8").splitlines():
    if line.startswith("__version__ ="):
        init_line_to_replace = line
        break
else:
    msg = "init file not in correct format"
    raise ValueError(msg)

init_file.write_text(
    init_file.read_text(encoding="utf-8").replace(
        init_line_to_replace, f'__version__ = "{v}"', 1
    ),
    encoding="utf-8",
)
