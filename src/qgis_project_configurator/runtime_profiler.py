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

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from qgis.core import QgsApplication


class ProjectManagerProfiler:
    PROFILER_GROUP = "QGIS project configurator"

    def __init__(self) -> None:
        self._profiler = QgsApplication.profiler()

    def start(self, name: str) -> None:
        self._profiler.start(group=self.PROFILER_GROUP, name=name)

    def end(self) -> None:
        self._profiler.end(group=self.PROFILER_GROUP)

    def clear(self) -> None:
        self._profiler.clear(group=self.PROFILER_GROUP)


profiler = ProjectManagerProfiler()

P = ParamSpec("P")
R = TypeVar("R")


def profile_function(name: str) -> Callable[[Callable[P, R]], Callable[P, R]]:  # noqa: D103
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            profiler.start(name)
            try:
                result = func(*args, **kwargs)
            finally:
                profiler.end()

            return result

        return wrapper

    return decorator
