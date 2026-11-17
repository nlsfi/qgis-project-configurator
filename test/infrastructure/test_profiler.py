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

# Copyright (C) 2026 QGIS Project Configurator Contributors.
#
# This file is part of QGIS Project Configurator.
#
# QGIS Project Configurator is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
# ... (rest of license) ...

import pytest
from pytest_mock import MockerFixture

from qgis_project_configurator.runtime_profiler import (
    QgisProjectConfiguratorProfiler,
    profile_function,
    profiler,
)


def test_profiler_safe_when_qgs_profiler_none(mocker: MockerFixture):
    mocker.patch("qgis.core.QgsApplication.profiler", return_value=None)

    safe_profiler = QgisProjectConfiguratorProfiler()

    safe_profiler.start("test")
    safe_profiler.end()
    safe_profiler.clear()


def test_profiler_executes_qgs_profiler_when_qgs_profiler_not_none(
    mocker: MockerFixture,
):
    mock_qgis_profiler = mocker.MagicMock()
    mocker.patch("qgis.core.QgsApplication.profiler", return_value=mock_qgis_profiler)
    active_profiler = QgisProjectConfiguratorProfiler()

    active_profiler.start("my_test_operation")
    active_profiler.end()
    active_profiler.clear()

    mock_qgis_profiler.start.assert_called_once_with(
        group=QgisProjectConfiguratorProfiler.PROFILER_GROUP, name="my_test_operation"
    )
    mock_qgis_profiler.end.assert_called_once_with(
        group=QgisProjectConfiguratorProfiler.PROFILER_GROUP
    )
    mock_qgis_profiler.clear.assert_called_once_with(
        group=QgisProjectConfiguratorProfiler.PROFILER_GROUP
    )


def test_profile_decorator_success(mocker: MockerFixture):
    mock_start = mocker.patch.object(profiler, "start")
    mock_end = mocker.patch.object(profiler, "end")

    @profile_function("my_test_func")
    def dummy_func(a: int, b: int) -> int:
        return a + b

    result = dummy_func(2, 3)

    assert result == 5
    mock_start.assert_called_once_with("my_test_func")
    mock_end.assert_called_once()


def test_profile_decorator_with_exception(mocker: MockerFixture):
    mock_start = mocker.patch.object(profiler, "start")
    mock_end = mocker.patch.object(profiler, "end")

    @profile_function("crashing_func")
    def crashing_func() -> None:
        msg = "Error msg"
        raise ValueError(msg)

    with pytest.raises(ValueError, match="Error msg"):
        crashing_func()

    mock_start.assert_called_once_with("crashing_func")
    mock_end.assert_called_once()
