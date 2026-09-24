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

from unittest.mock import MagicMock, patch

from qgis_project_configurator.layer_manager import LayerManager
from qgis_project_configurator.models import CompiledConfig


@patch("qgis_project_configurator.layer_manager.QgsVectorLayer")
def test_layer_tree_structure(
    mock_qgs_vector_layer: MagicMock,
    compiled_config: CompiledConfig,
    mock_theme_manager: MagicMock,
):
    mock_project = MagicMock()
    mock_root_node = MagicMock()
    mock_project.layerTreeRoot.return_value = mock_root_node
    mock_project.addMapLayer.return_value = MagicMock()
    mock_created_layer = MagicMock()
    mock_created_layer.isValid.return_value = True
    mock_qgs_vector_layer.return_value = mock_created_layer
    mock_feedback = MagicMock()
    mock_feedback.isCanceled.return_value = False

    layer_manager = LayerManager(mock_project, compiled_config, mock_theme_manager)

    layer_manager.load_layers(feedback=mock_feedback)

    mock_root_node.addGroup.assert_called_once_with("Infrastructure")

    mock_infrastructure_group = mock_root_node.addGroup.return_value

    mock_infrastructure_group.addLayer.assert_called_once_with(mock_created_layer)
    mock_root_node.addLayer.assert_called_once_with(mock_created_layer)
