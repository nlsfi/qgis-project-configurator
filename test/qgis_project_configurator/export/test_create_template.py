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
# ...

from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml
from pytest_mock import MockerFixture
from qgis.core import (
    QgsLayerTreeLayer,
    QgsLayerTreeNode,
    QgsProcessingFeedback,
    QgsProject,
)

from qgis_project_configurator.create_template import (
    ConfigStyle,
    create_configuration_template,
)

MODULE = "qgis_project_configurator.create_template"


def _create_mock_group(
    name: str, children: list, embedded_source: str | None = None
) -> MagicMock:
    properties = (
        {"embedded": 1, "embedded_project": embedded_source}
        if embedded_source
        else {"embedded": 0}
    )

    group = MagicMock(spec=QgsLayerTreeNode)
    group.configure_mock(
        **{
            "nodeType.return_value": QgsLayerTreeNode.NodeType.NodeGroup,
            "name.return_value": name,
            "children.return_value": children,
            "customProperty.side_effect": properties.get,
        }
    )
    return group


def _create_mock_layer(
    name: str,
    table: str = "test_table",
    is_embedded: bool = False,
    is_missing_layer: bool = False,
    is_missing_provider: bool = False,
) -> MagicMock:
    properties = {"embedded": 1} if is_embedded else {"embedded": 0}

    node = MagicMock(spec=QgsLayerTreeLayer)
    node.configure_mock(
        **{
            "name.return_value": name,
            "customProperty.side_effect": properties.get,
        }
    )

    if is_missing_layer:
        node.layer.return_value = None
        return node

    layer = MagicMock()
    layer.name.return_value = name

    if is_missing_provider:
        layer.dataProvider.return_value = None
    else:
        provider = MagicMock()
        provider.uri().table.return_value = table
        layer.dataProvider.return_value = provider

    node.layer.return_value = layer
    return node


@pytest.fixture
def mock_feedback() -> MagicMock:
    return MagicMock(spec=QgsProcessingFeedback)


@pytest.fixture
def mock_project() -> MagicMock:
    project = MagicMock(spec=QgsProject)
    project.layerTreeRoot.return_value.children.return_value = []
    return project


def test_raises_if_layer_tree_missing(
    mock_feedback: MagicMock, mock_project: MagicMock
) -> None:
    mock_project.layerTreeRoot.return_value = None

    with pytest.raises(RuntimeError, match="Cannot access layer tree"):
        create_configuration_template(
            output_file=Path("out.yaml"),
            style_folder=None,
            feedback=mock_feedback,
            project=mock_project,
        )


def test_successful_tree_parsing_and_yaml_creation(
    tmp_path: Path,
    mock_feedback: MagicMock,
    mock_project: MagicMock,
    mocker: MockerFixture,
) -> None:
    output_file = tmp_path / "config.yaml"
    style_folder = tmp_path / "styles"

    mock_save_style = mocker.patch(f"{MODULE}.save_style", return_value=True)

    layer_node = _create_mock_layer("buildings", table="buildings")
    group_node = _create_mock_group("Infrastructure", children=[layer_node])
    embedded_group = _create_mock_group(
        "BaseMap", children=[], embedded_source="./basemap.qgs"
    )

    mock_project.layerTreeRoot.return_value.children.return_value = [
        group_node,
        embedded_group,
    ]

    result = create_configuration_template(
        output_file=output_file,
        style_folder=style_folder,
        feedback=mock_feedback,
        project=mock_project,
    )

    assert style_folder.exists()
    mock_save_style.assert_called_once()

    expected_tree = [
        {
            "group": "Infrastructure",
            "children": [
                {
                    "vector_layer": "buildings",
                    "style": "./styles/buildings.qml",
                    "table": "buildings",
                }
            ],
        },
        {
            "embedded_group": "BaseMap",
            "source": "./basemap.qgs",
        },
    ]
    assert result["layer_tree"] == expected_tree

    with output_file.open() as f:
        parsed_yaml = yaml.safe_load(f)
        assert parsed_yaml["layer_tree"] == expected_tree


def test_invalid_layers_are_skipped_with_warnings(
    tmp_path: Path, mock_feedback: MagicMock, mock_project: MagicMock
) -> None:
    missing_layer = _create_mock_layer("broken_layer", is_missing_layer=True)
    missing_provider = _create_mock_layer("no_data", is_missing_provider=True)
    embedded_layer = _create_mock_layer("embedded", is_embedded=True)

    mock_project.layerTreeRoot.return_value.children.return_value = [
        missing_layer,
        missing_provider,
        embedded_layer,
    ]

    result = create_configuration_template(
        output_file=tmp_path / "config.yaml",
        style_folder=None,
        feedback=mock_feedback,
        project=mock_project,
    )

    assert result["layer_tree"] == []

    mock_feedback.pushWarning.assert_any_call(
        "Layer for node 'broken_layer' could not be resolved. Skipping."
    )
    mock_feedback.pushWarning.assert_any_call(
        "Data provider for layer 'no_data' could not be resolved. Skipping."
    )


def test_style_save_failure_leaves_style_path_empty(
    tmp_path: Path,
    mock_feedback: MagicMock,
    mock_project: MagicMock,
    mocker: MockerFixture,
) -> None:
    mocker.patch(f"{MODULE}.save_style", return_value=False)

    layer_node = _create_mock_layer("water")
    mock_project.layerTreeRoot.return_value.children.return_value = [layer_node]

    result = create_configuration_template(
        output_file=tmp_path / "config.yaml",
        style_folder=tmp_path / "styles",
        feedback=mock_feedback,
        project=mock_project,
    )

    assert result["layer_tree"][0]["style"] == ""
    mock_feedback.pushWarning.assert_called_with(
        "Failed to save style for layer: water"
    )


def test_compact_config_writes_compact_layers(
    tmp_path: Path, mock_feedback: MagicMock, mock_project: MagicMock
) -> None:
    output_file = tmp_path / "compact.yaml"
    layer_node = _create_mock_layer("roads", table="roads")
    group_node = _create_mock_group(name="infrastructure", children=[layer_node])
    mock_project.layerTreeRoot.return_value.children.return_value = [group_node]

    create_configuration_template(
        output_file=output_file,
        style_folder=None,
        feedback=mock_feedback,
        config_style=ConfigStyle.COMPACT_LAYERS,
        project=mock_project,
    )

    with output_file.open() as f:
        yaml_text = f.read()

    expected_layer_tree = """layer_tree:
- group: infrastructure
  children:
  - {vector_layer: roads, style: '', table: roads}"""
    assert expected_layer_tree in yaml_text
