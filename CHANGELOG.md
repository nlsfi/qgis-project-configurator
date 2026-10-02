# Changelog

## Unreleased

## 1.2.0 - 2026-10-02

- Rename product version to style variant in configuration files and in cli option. Cli option is now `--style-variant` instead of `--product-version`
- Rename the `hidden` style value to `exclude` for excluding layers from a project
- Add usage examples and PostGIS instructions to docs
- Fix plugin package missing from the build

## 0.1.3 - 2026-10-02

- Add cli support for creating config templates
- Add initial metadata support to config format
- Add cli command for querying metadata from config file
- Add cli support for displaying library & qgis version
- Unify cli commands under a single entrypoint
- Add option to use flow style syntax for layers in config template

## [0.1.2] - 2026-09-09

- Fix changelog formatting
- Properly configure qpdt version numbering

## [0.1.1] - 2026-09-08

- Fix findings in qgis plugin repository checks
- Enhance pre-commit and ci/cd with bandit to closer match qgis plugin repo infra

## [0.1.0] - 2026-06-25

- First project version including support for project generation and style exports

[0.1.0]: <https://github.com/nlsfi/qgis-project-configurator/releases/tag/v0.1.0>
[0.1.1]: <https://github.com/nlsfi/qgis-project-configurator/releases/tag/v0.1.1>
[0.1.2]: <https://github.com/nlsfi/qgis-project-configurator/releases/tag/v0.1.2>
