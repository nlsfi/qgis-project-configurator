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
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QMessageBox

from qgis_project_configurator_plugin.algorithms.create_project import (
    CreateProjectAlgorithm,
)


@pytest.fixture
def algorithm():
    return CreateProjectAlgorithm()


def test_algorithm_metadata(algorithm: CreateProjectAlgorithm):
    assert algorithm.name() == "create-visualization-project"
    assert algorithm.displayName() == "Create a visualization project"
    assert algorithm.flags() == Qgis.ProcessingAlgorithmFlag.CanCancel

    new_instance = algorithm.createInstance()
    assert isinstance(new_instance, CreateProjectAlgorithm)


def test_init_algorithm_registers_parameters(
    algorithm: CreateProjectAlgorithm, mocker: MockerFixture
):
    mock_add_parameter = mocker.patch.object(
        algorithm, "addParameter", return_value=True
    )
    algorithm.initAlgorithm()

    assert mock_add_parameter.call_count == 3


def test_qgis_processing_params_parsed_into_create_project_params(
    algorithm: CreateProjectAlgorithm, mocker: MockerFixture
):
    mock_context = MagicMock()
    mock_parameters = {}

    mocker.patch.object(
        algorithm, "parameterAsFile", return_value="/path/to/config.yaml"
    )
    mocker.patch.object(
        algorithm,
        "parameterAsString",
        side_effect=["selected_style_variant", "selected_data_source"],
    )

    params = algorithm._get_params(mock_parameters, mock_context)

    assert params.config_path == Path("/path/to/config.yaml")
    assert params.style_variant == "selected_style_variant"
    assert params.data_source == "selected_data_source"


class TestProjectPreparation:
    def test_prepare_project_raises_if_qgis_project_none(
        self, algorithm: CreateProjectAlgorithm, mocker: MockerFixture
    ):
        mocker.patch(
            "qgis_project_configurator_plugin.algorithms.create_project.QgsProject.instance",
            return_value=None,
        )

        with pytest.raises(RuntimeError, match="Cannot access QGIS project"):
            algorithm._check_for_empty_project_or_create_new()

    def test_prepare_project_returns_instance_if_qgis_project_already_empty(
        self, algorithm: CreateProjectAlgorithm, mocker: MockerFixture
    ):
        mock_project = MagicMock()
        mock_project.mapLayers.return_value = {}  # Empty layers dict
        mocker.patch(
            "qgis_project_configurator_plugin.algorithms.create_project.QgsProject.instance",
            return_value=mock_project,
        )

        result = algorithm._check_for_empty_project_or_create_new()

        assert result == mock_project

    def test_prepare_project_returns_false_if_qgis_project_not_empty_and_user_cancels(
        self, algorithm: CreateProjectAlgorithm, mocker: MockerFixture
    ):
        mock_project = MagicMock()
        mock_project.mapLayers.return_value = {"layer1": "dummy_layer"}  # Not empty
        mocker.patch(
            "qgis_project_configurator_plugin.algorithms.create_project.QgsProject.instance",
            return_value=mock_project,
        )
        mocker.patch(
            "qgis_project_configurator_plugin.algorithms.create_project.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Cancel,
        )

        result = algorithm._check_for_empty_project_or_create_new()

        assert result is False

    def test_prepare_project_returns_project_instance_if_qgis_project_not_empty_and_user_closes_project(
        self, algorithm: CreateProjectAlgorithm, mocker: MockerFixture
    ):
        mock_project = MagicMock()
        mock_project.mapLayers.return_value = {"layer1": "dummy_layer"}
        mocker.patch(
            "qgis_project_configurator_plugin.algorithms.create_project.QgsProject.instance",
            return_value=mock_project,
        )
        mocker.patch(
            "qgis_project_configurator_plugin.algorithms.create_project.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Close,
        )
        mock_new_project = mocker.patch(
            "qgis_project_configurator_plugin.algorithms.create_project.iface.newProject",
            return_value=True,
        )

        result = algorithm._check_for_empty_project_or_create_new()

        mock_new_project.assert_called_once_with(promptToSaveFlag=True)
        assert result == mock_project


class TestPrepareAlgorithm:
    def test_prepare_algorithm_raises_if_feedback_none(
        self, algorithm: CreateProjectAlgorithm
    ):
        with pytest.raises(RuntimeError, match="Cannot access feedback"):
            algorithm.prepareAlgorithm({}, MagicMock(), feedback=None)

    def test_prepare_algorithm_cancelled_if_project_check_cancelled(
        self, algorithm: CreateProjectAlgorithm, mocker: MockerFixture
    ):
        mock_feedback = MagicMock()
        mocker.patch.object(
            algorithm, "_check_for_empty_project_or_create_new", return_value=False
        )

        result = algorithm.prepareAlgorithm({}, MagicMock(), mock_feedback)

        assert result is False
        mock_feedback.pushWarning.assert_called_once_with("Cancelling.")

    def test_prepare_algorithm_raises_if_no_map_canvas(
        self, algorithm: CreateProjectAlgorithm, mocker: MockerFixture
    ):
        mock_feedback = MagicMock()
        mock_project = MagicMock()

        mocker.patch.object(
            algorithm,
            "_check_for_empty_project_or_create_new",
            return_value=mock_project,
        )
        mocker.patch.object(algorithm, "_get_params")
        mocker.patch(
            "qgis_project_configurator_plugin.algorithms.create_project.load_config"
        )
        mocker.patch(
            "qgis_project_configurator_plugin.algorithms.create_project.iface.mapCanvas",
            return_value=None,
        )

        with pytest.raises(RuntimeError, match="Cannot access map canvas"):
            algorithm.prepareAlgorithm({}, MagicMock(), mock_feedback)

    def test_prepare_algorithm_success(
        self, algorithm: CreateProjectAlgorithm, mocker: MockerFixture
    ):
        mock_feedback = MagicMock()
        mock_context = MagicMock()
        mock_project = MagicMock()
        mock_canvas = MagicMock()
        mock_config = MagicMock()

        mocker.patch.object(
            algorithm,
            "_check_for_empty_project_or_create_new",
            return_value=mock_project,
        )
        mock_params = MagicMock(
            config_path=Path("/fake/config.yaml"),
            style_variant="style",
            data_source="db",
        )
        mocker.patch.object(algorithm, "_get_params", return_value=mock_params)
        mocker.patch(
            "qgis_project_configurator_plugin.algorithms.create_project.load_config",
            return_value=mock_config,
        )
        mocker.patch(
            "qgis_project_configurator_plugin.algorithms.create_project.iface.mapCanvas",
            return_value=mock_canvas,
        )
        mock_lib_create = mocker.patch(
            "qgis_project_configurator_plugin.algorithms.create_project.lib_create_project"
        )

        result = algorithm.prepareAlgorithm({}, mock_context, mock_feedback)

        assert result is True
        assert mock_canvas.freeze.call_count == 2
        mock_canvas.freeze.assert_any_call(True)
        mock_canvas.freeze.assert_any_call(False)
        mock_lib_create.assert_called_once_with(
            project=mock_project,
            config=mock_config,
            data_source="db",
            style_variant="style",
            config_path=Path("/fake/config.yaml"),
            target_project_path=Path("placeholder"),
            store_metadata=True,
            feedback=mock_feedback,
        )

    def test_prepare_algorithm_unfreezes_on_exception(
        self, algorithm: CreateProjectAlgorithm, mocker: MockerFixture
    ):
        mock_feedback = MagicMock()
        mock_project = MagicMock()
        mock_canvas = MagicMock()

        mocker.patch.object(
            algorithm,
            "_check_for_empty_project_or_create_new",
            return_value=mock_project,
        )
        mocker.patch.object(algorithm, "_get_params")
        mocker.patch(
            "qgis_project_configurator_plugin.algorithms.create_project.load_config"
        )
        mocker.patch(
            "qgis_project_configurator_plugin.algorithms.create_project.iface.mapCanvas",
            return_value=mock_canvas,
        )

        mocker.patch(
            "qgis_project_configurator_plugin.algorithms.create_project.lib_create_project",
            side_effect=ValueError("Test crash"),
        )

        with pytest.raises(ValueError, match="Test crash"):
            algorithm.prepareAlgorithm({}, MagicMock(), mock_feedback)

        mock_canvas.freeze.assert_any_call(False)
