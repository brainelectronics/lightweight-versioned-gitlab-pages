# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
RegEx for release version from file
r"^\#\# \[\d{1,}[.]\d{1,}[.]\d{1,}\] \- \d{4}\-\d{2}-\d{2}$"
-->

## Released
## [0.1.2] - 2023-01-03
### Fixed
- Install `twine` before using it during the `deploy` steps, see #2

## [0.1.1] - 2023-01-03
### Fixed
- Syntax to view and push created tag during `tagging` stage fixed, see #1
- Don't run `test`, `build`, `lint` and `docs` steps on tags

## [0.1.0] - 2023-01-03
### Added
- Everything is new
	- created initial package structure
	- added necessary files
	- enabled CI/CD checks, tagging and deploy steps

<!-- Links -->
[0.1.2]: https://gitlab.com/brainelectronics/lightweight-versioned-gitlab-pages/-/tags/0.1.2
[0.1.1]: https://gitlab.com/brainelectronics/lightweight-versioned-gitlab-pages/-/tags/0.1.1
[0.1.0]: https://gitlab.com/brainelectronics/lightweight-versioned-gitlab-pages/-/tags/0.1.0
