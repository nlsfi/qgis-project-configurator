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

from collections.abc import Iterator
from pathlib import Path

import pytest

from qgis_project_configurator.config_compiler import ConfigCompiler
from qgis_project_configurator.models import (
    EmbeddedLayerGroup,
    LayerGroup,
    LayerTree,
    PostgisSource,
    VectorLayer,
)
from qgis_project_configurator.yaml_loader import load_config

# The generator and validation need pydantic, a dev dependency
pydantic = pytest.importorskip("pydantic")

import generate_config_docs  # noqa: E402

EXAMPLE_CONFIG = Path(__file__).parent.parent / "docs" / "example" / "config.yaml"


def _validate(config: dict) -> None:
    generate_config_docs.config_type_adapter().validate_python(config, strict=True)


def _nodes(tree: LayerTree) -> Iterator[VectorLayer | EmbeddedLayerGroup]:
    for node in tree:
        if isinstance(node, LayerGroup):
            yield from _nodes(node.children)
        else:
            yield node


def test_generated_files_are_up_to_date():
    for path, content in generate_config_docs.generate_outputs().items():
        assert path.read_text(encoding="utf-8") == content, (
            "Run: uv run python scripts/generate_config_docs.py"
        )


def test_example_config_is_valid():
    _validate(load_config(EXAMPLE_CONFIG))


def test_base_config_is_valid(base_config: dict):
    _validate(base_config)


@pytest.mark.parametrize(
    "invalid_part",
    [
        pytest.param(
            {"layer_tree": [{"vector_layer": "a", "styel": "./a.qml"}]},
            id="unknown key",
        ),
        pytest.param({"layer_tree": [{"name": "a"}]}, id="node without kind"),
        pytest.param(
            {
                "layer_tree": [
                    {
                        "group": "g",
                        "children": [{"vector_layer": "a", "scale": {"min": "big"}}],
                    }
                ]
            },
            id="wrong type in nested node",
        ),
        pytest.param(
            {
                "data_sources": {
                    "db": {
                        "type": "oracle",
                        "service": "db",
                        "schema": "public",
                        "geom_column": "geom",
                    }
                }
            },
            id="unknown data source type",
        ),
        pytest.param(
            {"project_properties": {"Scope": {"key": 1.5}}},
            id="decimal project property",
        ),
        pytest.param({"project_properties": {"crs": "EPSG:3067"}}, id="crs as text"),
        pytest.param({"project_properties": {"crs": True}}, id="crs as boolean"),
    ],
)
def test_invalid_config_fails(base_config: dict, invalid_part: dict):
    with pytest.raises(pydantic.ValidationError):
        _validate(base_config | invalid_part)


def test_config_without_data_sources_fails(base_config: dict):
    del base_config["data_sources"]

    with pytest.raises(pydantic.ValidationError):
        _validate(base_config)


def test_example_config_compiles_as_documented(tmp_path: Path):
    compiled = ConfigCompiler(
        raw_config=load_config(EXAMPLE_CONFIG),
        config_dir=EXAMPLE_CONFIG.parent,
        data_source="db",
        project_dir=tmp_path,
        product_version="secret",
    ).compile()

    nodes = {node.name: node for node in _nodes(compiled.layer_tree)}
    assert list(nodes) == [
        "populated_places",
        "roads",
        "rivers",
        "lakes",
        "countries",
        "basemaps",
    ]
    layers = {
        name: node for name, node in nodes.items() if isinstance(node, VectorLayer)
    }
    # Group defaults: mappings merge, lists replace
    assert layers["populated_places"].scale.min == 2000000
    assert layers["populated_places"].scale.max == 500000
    assert layers["countries"].scale.min == 3000000
    assert layers["countries"].map_theme_names == ["all"]
    assert layers["roads"].map_theme_names == ["all", "traffic"]
    # Partial data source override
    rivers_source = layers["rivers"].data_source
    assert isinstance(rivers_source, PostgisSource)
    assert rivers_source.schema == "hydrography"
    assert rivers_source.service == "naturalearth"
    assert rivers_source.table == "rivers"
    # Style per product version
    assert (
        layers["lakes"].style_file
        == (EXAMPLE_CONFIG.parent / "styles" / "lakes.qml").resolve()
    )
    # Embedded group source is relative to the created project
    assert nodes["basemaps"] == EmbeddedLayerGroup(
        name="basemaps", source=(tmp_path / "basemaps.qgz").resolve()
    )
    assert compiled.project_properties[0].scope == "crs"
    assert compiled.project_properties[0].value == 3067


def test_example_config_hides_layer_in_public_version(tmp_path: Path):
    compiled = ConfigCompiler(
        raw_config=load_config(EXAMPLE_CONFIG),
        config_dir=EXAMPLE_CONFIG.parent,
        data_source="db",
        project_dir=tmp_path,
        product_version="public",
    ).compile()

    assert "lakes" not in {node.name for node in _nodes(compiled.layer_tree)}
