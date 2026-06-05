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


class NoChangesFoundError(ValueError):
    """Raised when no changes are found from the changelog."""

    def __init__(self) -> None:
        super().__init__("no changes found")


changelog_file = Path("CHANGELOG.md")
to_find = f"## [{v}]"

found = False
results = []

for line in changelog_file.read_text(encoding="utf-8").splitlines():
    if found and line.startswith("## "):
        break
    elif found:
        results.append(line)
    elif line.startswith(to_find):
        found = True

if len(results) == 0:
    raise NoChangesFoundError

if results[0] == "":
    results = results[1:]
if results[-1] == "":
    results = results[:-1]

sys.stdout.write("\n".join(results) + "\n")
