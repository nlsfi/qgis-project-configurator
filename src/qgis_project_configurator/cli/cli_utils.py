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

import logging
from collections.abc import Callable
from functools import wraps

from qgis.core import QgsApplication, QgsProcessingFeedback

LOGGER = logging.getLogger(__name__)


class LoggingProcessingFeedback(QgsProcessingFeedback):
    def setProgressText(self, text: str) -> None:  # noqa: N802
        LOGGER.info(text)
        super().setProgressText(text)

    def pushInfo(self, info: str) -> None:  # noqa: N802
        LOGGER.info(info)
        super().pushInfo(info)

    def pushCommandInfo(self, info: str) -> None:  # noqa: N802
        LOGGER.debug(info)
        super().pushCommandInfo(info)

    def pushDebugInfo(self, info: str) -> None:  # noqa: N802
        LOGGER.debug(info)
        super().pushDebugInfo(info)

    def pushConsoleInfo(self, info: str) -> None:  # noqa: N802
        LOGGER.debug(info)
        super().pushConsoleInfo(info)

    def reportError(self, error: str, fatalError: bool = False) -> None:  # noqa: FBT001, FBT002, N802, N803
        if fatalError:
            LOGGER.critical(error)
        else:
            LOGGER.error(error)
        super().reportError(error)


def run_qgis(func: Callable):  # noqa: ANN201, D103
    @wraps(func)
    def wrapper(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        LOGGER.info("creating qgis")
        qgs = QgsApplication([], GUIenabled=False)
        LOGGER.info("initializing qgis")
        qgs.initQgis()

        return_value = func(*args, **kwargs)

        LOGGER.info("Exiting qgis")
        qgs.exitQgis()

        return return_value

    return wrapper
