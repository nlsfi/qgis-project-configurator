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

import pytest


@pytest.fixture
def base_config():
    return {
        "data_sources": {
            "db": {
                "type": "postgis",
                "service": "db",
                "schema": "public",
                "geom_column": "geom",
                "table": None,
            },
            "gpkg": {
                "type": "gpkg",
                "path": "../../example_data/db1/naturalearth.gpkg",
                "table": None,
            },
        },
        "product_versions": ["secret", "public"],
        "layer_tree": [
            {
                "group": "all",
                "defaults": {"scale": {"min": 3000000}},
                "children": [
                    {
                        "group": "infrastructure",
                        "defaults": {"scale": {"min": 2000000}},
                        "children": [
                            {
                                "vector_layer": "populated_places",
                                "style": "./populated_places.qml",
                                "table": "populated_places",
                                "scale": {"min": 2000000, "max": 500000},
                            },
                            {
                                "vector_layer": "roads",
                                "style": "./roads.qml",
                                "table": "roads",
                            },
                            {
                                "vector_layer": "urban_areas",
                                "style": "./urban_areas.qml",
                                "table": "urban_areas",
                                "scale": {"min": 500000},
                            },
                        ],
                    },
                    {
                        "group": "water",
                        "children": [
                            {
                                "vector_layer": "rivers",
                                "style": "./rivers.qml",
                                "data_source_overrides": {
                                    "db": {
                                        "type": "postgis",
                                        "service": "db",
                                        "schema": "public",
                                        "geom_column": "geom",
                                        "table": "rivers",
                                    },
                                    "gpkg": {
                                        "type": "gpkg",
                                        "path": "../../example_data/db1/naturalearth.gpkg",
                                        "table": "rivers",
                                    },
                                },
                            },
                            {
                                "vector_layer": "lakes",
                                "style": "hidden",
                                "style_overrides": {"secret": "./lakes.qml"},
                                "table": "lakes",
                            },
                        ],
                    },
                    {
                        "vector_layer": "countries",
                        "style": "./countries.qml",
                        "style_overrides": {"secret": "./countries_green.qml"},
                        "table": "countries",
                    },
                ],
            }
        ],
        "project_properties": {
            "WMSServiceCapabilities": True,
            "WMSServiceTitle": "The title of the service",
            "WMSPrecision": 5,
            "WMSExtent": ["-17.5", "52.8", "54.4", "78.7"],
            "WMSMaxAtlasFeatures": 100,
            "crs": 4326,
        },
        "layouts": [
            {"layout_file": "./atlas_template.qpt", "atlas_coverage_layer": "countries"}
        ],
    }
