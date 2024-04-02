# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.2] - 2024-04-02

### Added
- Add coverage tests on and add official support for Python 3.12.

### Fixed
- Fix scripts for recent versions of FElupe (>=7.19.0): Remove the `fig`-argument in `CharacteristicCurve.plot()`.
- Fix scripts with a missing leading `f""` for a formatted string.

## [1.0.1] - 2024-03-10

### Fixed
- Fix support for recent versions of FElupe (>=7.19.0) in a backward-compatible way.

## [1.0.0] - 2023-08-22

### Added
- Initial release.
- Start using a changelog.