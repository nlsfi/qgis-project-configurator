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

from qgis_project_configurator.config import ConfigCompiler
from qgis_project_configurator.types import (
    GpkgSource,
    PostgisSource,
    Scale,
    VectorLayer,
)


def test_layer_default_style_resolved_no_product_version(
    base_config: dict, tmp_path: Path
):
    base_config["layer_tree"] = [
        {
            "vector_layer": "layer",
            "style": "./style.qml",
            "style_overrides": {"public": "./green.qml", "secret": "hidden"},
            "table": "table",
        },
    ]
    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source="db",
        project_dir=tmp_path,
    ).compile()
    assert compiled.layer_tree[0].style_file == tmp_path / "style.qml"


def test_layer_default_style_resolved_with_product_version(
    base_config: dict, tmp_path: Path
):
    base_config["layer_tree"] = [
        {
            "vector_layer": "layer",
            "style": "./style.qml",
            "style_overrides": {"public": "./green.qml", "secret": "hidden"},
            "table": "table",
        },
    ]
    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source="db",
        project_dir=tmp_path,
        product_version="this-has-no-style",
    ).compile()
    assert compiled.layer_tree[0].style_file == tmp_path / "style.qml"


def test_layer_style_overrides_resolved(base_config: dict, tmp_path: Path):
    base_config["layer_tree"] = [
        {
            "vector_layer": "layer",
            "style": "./style.qml",
            "style_overrides": {"public": "./green.qml", "secret": "hidden"},
            "table": "table",
        },
    ]
    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source="db",
        project_dir=tmp_path,
        product_version="public",
    ).compile()
    assert compiled.layer_tree[0].style_file == tmp_path / "green.qml"


def test_hidden_layer_excluded(base_config: dict, tmp_path: Path):
    base_config["layer_tree"] = [
        {
            "vector_layer": "layer",
            "style": "./style.qml",
            "style_overrides": {"public": "./green.qml", "secret": "hidden"},
            "table": "table",
        },
        {
            "vector_layer": "layer2",
            "style": "./style2.qml",
            "style_overrides": {"public": "./green.qml", "secret": "./red.qml"},
            "table": "table2",
        },
    ]
    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source="db",
        project_dir=tmp_path,
        product_version="secret",
    ).compile()
    assert len(compiled.layer_tree) == 1
    assert compiled.layer_tree[0].name == "layer2"


def test_layer_postgis_source_constructed_from_table(base_config: dict, tmp_path: Path):
    base_config["data_sources"] = {
        "db": {
            "type": "postgis",
            "service": "db",
            "schema": "public",
            "geom_column": "geom",
        },
    }
    base_config["layer_tree"] = [
        {
            "vector_layer": "layer",
            "table": "table",
        },
    ]
    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source="db",
        project_dir=tmp_path,
    ).compile()
    assert compiled.layer_tree[0].data_source == PostgisSource(
        type="postgis",
        service="db",
        schema="public",
        geom_column="geom",
        table="table",
    )


def test_layer_gpkg_source_constructed_from_table(base_config: dict, tmp_path: Path):
    base_config["data_sources"] = {
        "gpkg": {
            "type": "gpkg",
            "path": "./data.gpkg",
        },
    }
    base_config["layer_tree"] = [
        {
            "vector_layer": "layer",
            "table": "table",
        },
    ]
    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source="gpkg",
        project_dir=tmp_path,
    ).compile()
    assert compiled.layer_tree[0].data_source == GpkgSource(
        type="gpkg",
        path=tmp_path / "data.gpkg",
        table="table",
    )


def test_embedded_group_project_path_resolved(base_config: dict, tmp_path: Path):
    base_config["layer_tree"] = [
        {
            "embedded_group": "group",
            "source": "./project.qgs",
        },
    ]
    project_dir = tmp_path / "project_dir"
    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source="db",
        project_dir=project_dir,
    ).compile()
    assert compiled.layer_tree[0].source == project_dir / "project.qgs"


def test_geopackage_override_path_resolved(base_config: dict, tmp_path: Path):
    base_config["layer_tree"] = [
        {
            "vector_layer": "layer",
            "table": "table",
        },
    ]
    gpkg_path = tmp_path / "data.gpkg"
    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source=gpkg_path,
        project_dir=tmp_path,
    ).compile()
    assert compiled.layer_tree[0].data_source == GpkgSource(
        type="gpkg", path=gpkg_path, table="table"
    )


def test_layer_source_specific_config_overrides_table(
    base_config: dict, tmp_path: Path
):
    base_config["layer_tree"] = [
        {
            "vector_layer": "layer",
            "table": "table_1",
            "data_source_overrides": {
                "db": {
                    "type": "postgis",
                    "service": "db",
                    "schema": "public",
                    "geom_column": "geometry",
                    "table": "table_2",
                }
            },
        },
    ]
    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source="db",
        project_dir=tmp_path,
    ).compile()
    assert compiled.layer_tree[0].data_source.table == "table_2"


def test_layer_source_specific_config_overrides_default_data_sources(
    base_config: dict, tmp_path: Path
):
    base_config["data_sources"] = {
        "db": {
            "type": "postgis",
            "service": "service",
            "schema": "public",
            "geom_column": "geometry",
        },
    }
    base_config["layer_tree"] = [
        {
            "vector_layer": "layer",
            "table": "table_1",
            "data_source_overrides": {
                "db": {
                    "type": "postgis",
                    "service": "service_2",
                    "schema": "secret",
                    "geom_column": "geom",
                    "table": "table_2",
                }
            },
        },
    ]
    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source="db",
        project_dir=tmp_path,
    ).compile()
    assert compiled.layer_tree[0].data_source == PostgisSource(
        type="postgis",
        service="service_2",
        schema="secret",
        geom_column="geom",
        table="table_2",
    )


def test_group_default_scale_applies_to_layer(base_config: dict, tmp_path: Path):
    base_config["layer_tree"] = [
        {
            "group": "all",
            "defaults": {"scale": {"min": 10}},
            "children": [
                {
                    "vector_layer": "layer",
                    "table": "table",
                },
            ],
        }
    ]
    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source="db",
        project_dir=tmp_path,
    ).compile()
    assert compiled.layer_tree[0].children[0].scale == Scale(min=10, max=None)


def test_group_default_sources_apply_to_layer(base_config: dict, tmp_path: Path):
    base_config["data_sources"] = {
        "db": {
            "type": "postgis",
            "service": "service",
            "schema": "public",
            "geom_column": "geometry",
            "table": None,
        },
    }

    base_config["layer_tree"] = [
        {
            "group": "all",
            "defaults": {
                "data_source_overrides": {
                    "db": {
                        "type": "postgis",
                        "service": "group_service",
                        "schema": "group_schema",
                        "geom_column": "group_geometry",
                    }
                }
            },
            "children": [
                {
                    "vector_layer": "layer",
                    "table": "layer_table",
                },
            ],
        }
    ]
    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source="db",
        project_dir=tmp_path,
    ).compile()
    assert compiled.layer_tree[0].children[0].data_source == PostgisSource(
        type="postgis",
        service="group_service",
        schema="group_schema",
        geom_column="group_geometry",
        table="layer_table",
    )


def test_layer_map_themes(base_config: dict, tmp_path: Path):
    base_config["layer_tree"] = [
        {"vector_layer": "layer", "table": "table", "map_themes": ["all", "index"]}
    ]
    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source="db",
        project_dir=tmp_path,
    ).compile()
    assert compiled.layer_tree[0].map_theme_names == ["all", "index"]


def test_group_default_map_themes_apply_to_layer(base_config: dict, tmp_path: Path):
    base_config["layer_tree"] = [
        {
            "group": "all",
            "defaults": {"map_themes": ["all"]},
            "children": [
                {
                    "vector_layer": "layer",
                    "table": "layer_table",
                },
            ],
        }
    ]
    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source="db",
        project_dir=tmp_path,
    ).compile()
    assert compiled.layer_tree[0].children[0].map_theme_names == ["all"]


def test_merged_group_defaults_apply_to_layer(base_config: dict, tmp_path: Path):
    base_config["layer_tree"] = [
        {
            "group": "all",
            "defaults": {
                "map_themes": ["all"],
                "data_source_overrides": {
                    "db": {
                        "type": "postgis",
                        "service": "another_service",
                        "schema": "public",
                        "geom_column": "geometry",
                    }
                },
            },
            "children": [
                {
                    "group": "group_10k",
                    "defaults": {
                        "scale": {"min": 10000},
                        "map_themes": ["all", "10k"],
                        "data_source_overrides": {"db": {"schema": "secret"}},
                    },
                    "children": [
                        {"vector_layer": "layer", "table": "table"},
                    ],
                },
            ],
        }
    ]
    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source="db",
        project_dir=tmp_path,
    ).compile()
    assert compiled.layer_tree[0].children[0].children[0] == VectorLayer(
        name="layer",
        data_source=PostgisSource(
            type="postgis",
            service="another_service",
            schema="secret",
            geom_column="geometry",
            table="table",
        ),
        scale=Scale(min=10000, max=None),
        map_theme_names=["all", "10k"],
        style_file=None,
    )


def test_layer_data_source_overrides_merges_with_global_data_sources(
    base_config: dict, tmp_path: Path
):
    base_config["data_sources"] = {
        "db": {
            "type": "postgis",
            "service": "service",
            "schema": "public",
            "geom_column": "geometry",
            "table": None,
        }
    }
    base_config["layer_tree"] = [
        {
            "vector_layer": "layer",
            "table": "table",
            "data_source_overrides": {"db": {"table": "layer_table"}},
        },
    ]
    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source="db",
        project_dir=tmp_path,
    ).compile()
    assert compiled.layer_tree[0].data_source == PostgisSource(
        type="postgis",
        service="service",
        schema="public",
        geom_column="geometry",
        table="layer_table",
    )


def test_nested_data_source_overrides_merge_with_global_data_sources(
    base_config: dict, tmp_path: Path
):
    base_config["data_sources"] = {
        "db": {
            "type": "postgis",
            "service": "service",
            "schema": "public",
            "geom_column": "geometry",
            "table": None,
        }
    }
    base_config["layer_tree"] = [
        {
            "group": "all",
            "defaults": {
                "data_source_overrides": {
                    "db": {
                        "service": "group_service",
                        "geom_column": "geom",
                    }
                },
            },
            "children": [
                {
                    "group": "group_10k",
                    "defaults": {
                        "data_source_overrides": {
                            "db": {"schema": "secret", "service": "10k"}
                        },
                    },
                    "children": [
                        {
                            "vector_layer": "layer",
                            "table": "table",
                            "data_source_overrides": {"db": {"table": "layer_table"}},
                        },
                    ],
                },
            ],
        }
    ]
    compiled = ConfigCompiler(
        raw_config=base_config,
        config_dir=tmp_path,
        data_source="db",
        project_dir=tmp_path,
    ).compile()
    assert compiled.layer_tree[0].children[0].children[0].data_source == PostgisSource(
        type="postgis",
        service="10k",
        schema="secret",
        geom_column="geom",
        table="layer_table",
    )
