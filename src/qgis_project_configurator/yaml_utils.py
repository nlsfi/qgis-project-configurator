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
from typing import IO, Any

import yaml


class Loader(yaml.SafeLoader):
    def __init__(self, stream: IO[Any]) -> None:
        # use file path as root directory, fallback to cwd
        if hasattr(stream, "name"):
            self.root_directory = Path(stream.name).parent
        else:
            self.root_directory = Path.cwd()
        super().__init__(stream)


def _include_constructor(loader: Loader, node: yaml.nodes.ScalarNode) -> Any:  # noqa: ANN401
    include_path_relative = loader.construct_scalar(node)
    include_path = (loader.root_directory / include_path_relative).resolve()
    # recursively load the included file to handle include within include
    with include_path.open("r", encoding="utf-8") as f:
        return yaml.load(f, Loader)  # noqa: S506


Loader.add_constructor("!include", _include_constructor)
